from typing import List, Dict, Tuple, Optional, Union

import sqlalchemy

from application.datastore.db.worker import DBWorker
from application.datastore.db.executor import QueryExecutor


class UserIntegrityError(Exception):
    pass


class UserNotFoundDb(Exception):
    pass


class UserQueryExecutor(QueryExecutor):
    @classmethod
    async def get_favourite_sports_by_customer_id(
        cls, db_worker: DBWorker, customer_id: int
    ) -> List[int]:
        query = f"""
            SELECT SQL_NO_CACHE sport_id
            FROM favourite_sports
            WHERE customer_id = :customer_id
        """
        favourite_sports = await db_worker.fetchall(
            sqlalchemy.text(query), {"customer_id": customer_id}
        )
        return [row[0] for row in favourite_sports]

    @classmethod
    async def delete_favourite_sports(
        cls, db_worker: DBWorker, sport_ids: List[int], customer_id: int
    ):
        query = f"""
            DELETE FROM favourite_sports
            WHERE customer_id = %(customer_id)s
            AND sport_id IN %(sport_ids)s
        """
        await db_worker.execute(
            query, {"sport_ids": sport_ids, "customer_id": customer_id}
        )

    @classmethod
    async def insert_user(
        cls,
        db_worker: DBWorker,
        user_data: Dict,
    ):
        query = f"""
            INSERT INTO users (name, email, password, salt)
            VALUES (:name, :email, :password, :salt)
        """
        try:
            inserted_id = await db_worker.execute(
                sqlalchemy.text(query),
                {
                    "name": user_data["name"],
                    "email": user_data["email"],
                    "password": user_data["hashed_password"],
                    "salt": user_data["salt"],
                },
            )
        except sqlalchemy.exc.IntegrityError:
            raise UserIntegrityError

        return inserted_id

    @classmethod
    async def update_user(
        cls,
        db_worker: DBWorker,
        user_data: Dict,
    ):
        set_clauses = []
        params = {}
        for field, value in user_data.items():
            if field != "id":
                set_clauses.append(f"{field} = :{field}")

            params[field] = value

        user = await cls._acquire_lock(db_worker, user_data["id"])
        if user is None:
            raise UserNotFoundDb

        query = f"""
            UPDATE users
            SET {",".join(set_clauses)}
            WHERE id = :id
        """
        try:
            await db_worker.execute(
                sqlalchemy.text(query),
                params,
            )
        except sqlalchemy.exc.IntegrityError:
            raise UserIntegrityError

    @classmethod
    async def _acquire_lock(
        cls,
        db_worker: DBWorker,
        user_id: int,
    ):
        query = f"""
            SELECT * FROM users WHERE id = :id FOR UPDATE
        """
        return await db_worker.fetchone(sqlalchemy.text(query), {"id": user_id})

    @classmethod
    async def count_users(cls, db_worker: DBWorker, filters: Dict) -> Union[int, None]:
        (
            stringified_where_clauses,
            _,
            _,
            parameters,
        ) = cls._get_stringified_where_sort_limit_clauses(filters=filters)
        query = f"""
            SELECT COUNT(id)
            FROM users
            {stringified_where_clauses};
        """
        users_num = await db_worker.fetchone(sqlalchemy.text(query), parameters)
        return users_num[0]

    @classmethod
    async def search_users(
        cls,
        db_worker: DBWorker,
        filters: Dict,
        include_secrets: bool = False,
    ) -> Optional[List]:
        (
            stringified_where_clauses,
            stringified_order_by_clauses,
            stringified_limit_clauses,
            parameters,
        ) = cls._get_stringified_where_sort_limit_clauses(filters=filters)
        column_names = [
            "id",
            "name",
            "email",
            "status",
            "last_login",
            "created_at",
            "last_modified",
        ]
        if include_secrets:
            column_names.extend(
                [
                    "password",
                    "salt",
                ]
            )

        query = f"""
            SELECT {",".join(column_names)}
            FROM users
            {stringified_where_clauses}
            {stringified_order_by_clauses}
            {stringified_limit_clauses};
        """
        users = await db_worker.fetchall(sqlalchemy.text(query), parameters)

        if not users:
            return None

        dict_results = []
        for row in users:
            dict_results.append(dict(zip(column_names, row)))

        return dict_results

    @classmethod
    def _get_stringified_where_sort_limit_clauses(
        cls, filters: Dict
    ) -> Tuple[str, str, str, Dict]:
        where_clauses = []
        parameters = {}

        if "user_ids" in filters:
            where_clauses.append("id IN :user_ids")
            parameters["user_ids"] = tuple(filters["user_ids"])

        if "name" in filters:
            where_clauses.append("name LIKE :name")
            parameters["name"] = "%" + filters["name"] + "%"

        if "email" in filters:
            where_clauses.append("email = :email")
            parameters["email"] = filters["email"]

        if "status" in filters:
            where_clauses.append("status = :status")
            parameters["status"] = filters["status"]

        if "created" in filters:
            if "datetime_from" in filters["created"]:
                where_clauses.append("created_at >= :created_datetime_from")
                parameters["created_datetime_from"] = filters["created"][
                    "datetime_from"
                ]

            if "datetime_to" in filters["created"]:
                where_clauses.append("created_at <= :created_datetime_to")
                parameters["created_datetime_to"] = filters["created"]["datetime_to"]

        if "updated" in filters:
            if "datetime_from" in filters["updated"]:
                where_clauses.append("last_modified >= :updated_datetime_from")
                parameters["updated_datetime_from"] = filters["updated"][
                    "datetime_from"
                ]

            if "datetime_to" in filters["updated"]:
                where_clauses.append("last_modified <= :updated_datetime_to")
                parameters["updated_datetime_to"] = filters["updated"]["datetime_to"]

        if "logged_in" in filters:
            if "datetime_from" in filters["logged_in"]:
                where_clauses.append("last_login >= :logged_in_datetime_from")
                parameters["logged_in_datetime_from"] = filters["logged_in"][
                    "datetime_from"
                ]

            if "datetime_to" in filters["logged_in"]:
                where_clauses.append("last_login <= :logged_in_datetime_to")
                parameters["logged_in_datetime_to"] = filters["logged_in"][
                    "datetime_to"
                ]

        stringified_where_clauses = " AND ".join(where_clauses)
        if stringified_where_clauses:
            stringified_where_clauses = "WHERE " + stringified_where_clauses

        if "sort_by" in filters:
            order_by_clauses = [
                f"{sorting_data['column']} {sorting_data['order']}"
                for sorting_data in filters["sort_by"]
            ]
            stringified_order_by_clauses = ", ".join(order_by_clauses)
            stringified_order_by_clauses = "ORDER BY " + stringified_order_by_clauses
        else:
            stringified_order_by_clauses = "ORDER BY id DESC"

        stringified_limit_clauses = ""
        if "limit" in filters and "offset" in filters:
            stringified_limit_clauses = "LIMIT :limit OFFSET :offset"
            parameters["limit"] = filters["limit"]
            parameters["offset"] = filters["offset"]

        return (
            stringified_where_clauses,
            stringified_order_by_clauses,
            stringified_limit_clauses,
            parameters,
        )
