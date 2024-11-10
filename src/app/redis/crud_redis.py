from redis.asyncio import Redis
from src.app.redis.config_redis import get_redis


async def set_value(key: str, value: str):
    redis = await get_redis()
    res = await redis.set(key, value)
    return res

async def get_value(key):
    redis = await get_redis()
    res = await redis.get(key)
    return res

async def delete_value(key):
    redis = await get_redis()
    res = await redis.delete(key)
    return res