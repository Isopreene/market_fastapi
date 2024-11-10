from config import settings
from redis.asyncio import from_url, Redis

REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"

redis_client = from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

async def get_redis() -> Redis:
    return redis_client