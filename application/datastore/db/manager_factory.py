from application.datastore.db.manager import DBManager
from application.datastore.db import get_db_managers


class DBManagerNotFound(Exception):
    pass


class DBManagerFactory:
    @staticmethod
    def make_manager(db_name: str, db_type: str) -> DBManager:
        for db_manager in get_db_managers():
            if db_name == db_manager.DB_NAME and db_type == db_manager.DB_TYPE:
                return db_manager()

        raise DBManagerNotFound(
            f"No manager found with name {db_name} and type {db_type}"
        )
