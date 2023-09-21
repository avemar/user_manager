from application.datastore.cache.aioredis import AioRedisCache

from application.lib.decorators.generic import handle_errors


class UserExistenceCache(AioRedisCache):
    config_key = "redis"
    hashset_name = "user_existence"

    async def user_exists(self, key: str) -> bool:
        return await self.hexists(self.hashset_name, key)

    @handle_errors
    async def set_user_existence(self, key: str):
        await self.hset(self.hashset_name, key, 0)
