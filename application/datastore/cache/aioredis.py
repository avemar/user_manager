import aioredis

from application.lib.utils.singleton import Singleton


class AioRedisCache(metaclass=Singleton):
    config_key = None

    def __init__(self, appconfig):
        self.settings = getattr(appconfig, self.config_key)

    async def init(self):
        self.host = self.settings["host"]
        self.port = self.settings.get("port", 6379)
        self.db = self.settings.get("db", 0)
        self.minsize = self.settings.get("pool_min_size", 1)
        self.maxsize = self.settings.get("pool_max_size", 20)
        await self._create()

    async def _create(self):
        self.client = await aioredis.create_redis_pool(
            address="redis://{}:{}".format(self.host, self.port),
            db=self.db,
            minsize=self.minsize,
            maxsize=self.maxsize,
        )

    async def close(self):
        await self.client.close()

    async def hset(self, name, key, value):
        return await self.client.hset(name, key, value)

    async def hexists(self, key, field):
        return await self.client.hexists(key, field)
