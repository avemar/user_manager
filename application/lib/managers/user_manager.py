from typing import Dict, List, Tuple
from datetime import datetime

from application.datastore.db.connection_constants import (
    USER_MANAGER_DB,
    MASTER_TYPE,
    READ_ONLY_TYPE,
)
from application.datastore.db.manager_factory import DBManagerFactory
from application.datastore.query_executors.user import (
    UserQueryExecutor,
    UserIntegrityError,
    UserNotFoundDb,
)
from application.lib.crypt.pbkdf2 import CryptPbkdf2
from application.lib.cache import UserExistenceCache
from application.lib.utils.various import fire_and_forget


class UserAlreadyTaken(Exception):
    pass


class UserNotFound(Exception):
    pass


class WrongPassword(Exception):
    pass


class UserManager:
    _db_manager_factory = DBManagerFactory()

    @classmethod
    async def _is_user_taken(cls, key):
        return await UserExistenceCache().user_exists(key)

    @classmethod
    def _cache_user_existence(cls, key):
        fire_and_forget(
            func=UserExistenceCache().set_user_existence,
            key=key,
        )

    @classmethod
    async def insert_user(cls, user_data: Dict) -> int:
        is_user_taken = await cls._is_user_taken(user_data["email"])
        if is_user_taken:
            raise UserAlreadyTaken

        hashed_password, salt = CryptPbkdf2.encrypt_password(
            cleartext_password=user_data["password"],
        )
        async with await cls._db_manager_factory.make_manager(
            db_name=USER_MANAGER_DB, db_type=MASTER_TYPE
        ).acquire() as db_worker:
            try:
                user_id = await UserQueryExecutor.insert_user(
                    db_worker,
                    {
                        **user_data,
                        "hashed_password": hashed_password,
                        "salt": salt,
                    },
                )
            except UserIntegrityError:
                raise UserAlreadyTaken
            finally:
                cls._cache_user_existence(user_data["email"])

        return user_id

    @classmethod
    async def update_user(cls, user_data: Dict) -> Dict:
        hashed_password = salt = None
        if "password" in user_data:
            hashed_password, salt = CryptPbkdf2.encrypt_password(
                cleartext_password=user_data["password"],
            )
            user_data.update(
                {
                    "password": hashed_password,
                    "salt": salt,
                }
            )

        async with await cls._db_manager_factory.make_manager(
            db_name=USER_MANAGER_DB, db_type=MASTER_TYPE
        ).acquire() as db_worker:
            try:
                await UserQueryExecutor.update_user(
                    db_worker,
                    user_data,
                )
            except UserIntegrityError:
                raise UserAlreadyTaken
            except UserNotFoundDb:
                raise UserNotFound

            stored_user = await UserQueryExecutor.search_users(
                db_worker, filters={"user_ids": [user_data["id"]]}
            )

        return stored_user[0]

    @classmethod
    async def delete_user(cls, user_id: int):
        async with await cls._db_manager_factory.make_manager(
            db_name=USER_MANAGER_DB, db_type=MASTER_TYPE
        ).acquire() as db_worker:
            try:
                await UserQueryExecutor.update_user(
                    db_worker,
                    {"id": user_id, "status": "DISABLED"},
                )
            except UserNotFoundDb:
                raise UserNotFound

    @classmethod
    async def search_users(cls, filters: Dict) -> Tuple[List[Dict], int]:
        async with await cls._db_manager_factory.make_manager(
            db_name=USER_MANAGER_DB, db_type=READ_ONLY_TYPE
        ).acquire() as db_worker:
            users_num = await UserQueryExecutor.count_users(db_worker, filters=filters)

            # No users found
            if users_num == 0:
                return [], users_num

            stored_users = await UserQueryExecutor.search_users(
                db_worker, filters=filters
            )

            # No users with the current offset
            if stored_users is None:
                stored_users = []

            return stored_users, users_num

    @classmethod
    async def login_user(cls, user_data: Dict) -> Dict:
        async with await cls._db_manager_factory.make_manager(
            db_name=USER_MANAGER_DB, db_type=MASTER_TYPE
        ).acquire() as db_worker:
            stored_user = await UserQueryExecutor.search_users(
                db_worker,
                filters={
                    "email": user_data["email"],
                    "status": "ACTIVE",
                },
                include_secrets=True,
            )
            if stored_user is None:
                raise UserNotFound

            stored_user = stored_user[0]
            password_matches = CryptPbkdf2.check_password(
                cleartext_password=user_data["password"],
                hashed_password=stored_user["password"],
                salt=stored_user["salt"],
            )
            if not password_matches:
                raise WrongPassword

            last_login = datetime.utcnow().replace(microsecond=0)
            await UserQueryExecutor.update_user(
                db_worker,
                {
                    "id": stored_user["id"],
                    "last_login": last_login,
                },
            )
            stored_user["last_login"] = last_login

        return stored_user
