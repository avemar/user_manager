from application.lib.utils.singleton import Singleton
from application.datastore.db.database import Database
from application.datastore.db.worker import DBWorker


class BaseDBManager(metaclass=Singleton):
    database = None
    DB_NAME = None
    DB_TYPE = None

    async def init(self):
        raise NotImplementedError

    async def acquire(self):
        raise NotImplementedError

    async def close(self):
        raise NotImplementedError


class DBManager(BaseDBManager):
    def __init__(self, config):
        connection_config = config.connections[self.DB_NAME][self.DB_TYPE]
        default = config.default
        for key in default:
            if key not in connection_config:
                connection_config[key] = default[key]

        self.database = Database(connection_config, self.DB_NAME, self.DB_TYPE)

    async def init(self):
        await self.database.init()

    async def acquire(self):
        return DBWorker(self.database)

    async def close(self):
        await self.database.close()
