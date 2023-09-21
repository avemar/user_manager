import asyncio
from random import randint

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import OperationalError

from application.lib.log import logger
from application.datastore.db.connection_constants import MASTER_TYPE, READ_ONLY_TYPE


class Database:
    MAX_CREATE_ATTEMPTS = 3
    RETRY_SLEEP_RANGE = (5, 10)
    DB_TYPES = (MASTER_TYPE, READ_ONLY_TYPE)

    def __init__(self, settings, db_name, db_type):
        if db_type not in self.DB_TYPES:
            raise ValueError("Invalid db type {} for db {}".format(db_type, db_name))

        self.db_name = db_name
        self.db_type = db_type
        self.settings = settings
        self._engine = None

    async def init(self):
        self.db_uri = self.settings["db_uri"]
        self.debug = self.settings.get("debug", False)
        self.pool_size = self.settings.get("pool_size", 20)
        await self.create()

    async def create(self):
        if self._engine:
            return self._engine

        attempt = 1
        while True:
            try:
                self._engine = self._create_engine()
                return
            except Exception as e:
                logger.exception(e)
                if attempt >= self.MAX_CREATE_ATTEMPTS:
                    raise RuntimeError(
                        "Number of attempts exceeded when connecting to DB"
                    )

                attempt += 1
                sleep_time = randint(*self.RETRY_SLEEP_RANGE)
                logger.debug(
                    "New connection attempt in {} seconds.." "".format(sleep_time)
                )
                await asyncio.sleep(sleep_time)

    async def ensure_connected(self):
        await self.create()

    def _create_engine(self):
        logger.debug("Creating engine for {} {}".format(self.db_name, self.db_type))
        return create_async_engine(
            self.db_uri, pool_size=self.pool_size, pool_recycle=3600, echo=self.debug
        )

    async def close(self):
        logger.debug("Closing engine for {} {}".format(self.db_name, self.db_type))
        if self._engine:
            await self._engine.dispose()

        self._engine = None

    def should_close(self, exception):
        if isinstance(exception, OperationalError):
            if exception.orig.args[0] == 2006:
                logger.debug("Disposing db connection pool: MySQL has gone away")
                return True

        return False

    def connect(self):
        return self._engine.connect()
