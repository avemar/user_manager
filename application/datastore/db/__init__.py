from typing import List

from application.datastore.db.manager import DBManager
from application.lib.utils.config import DatabaseConfig
from application.lib.utils.various import snake_to_upper_camel


_db_managers: List[DBManager] = []


def get_db_managers():
    if _db_managers:
        return _db_managers

    db_config = DatabaseConfig()

    for db_name, db_types in db_config.connections.items():
        for db_type in db_types:
            attributes = {"DB_NAME": db_name, "DB_TYPE": db_type}
            db_manager_class_name = snake_to_upper_camel(db_name, db_type)
            _db_managers.append(type(db_manager_class_name, (DBManager,), attributes))

    return _db_managers
