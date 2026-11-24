import json

import redis.asyncio as redis

from app.core.config import settings


class Cache:
    def __init__(self) -> None:
        self._redis: redis.Redis | None = None

    async def _conn(self) -> redis.Redis:
        if self._redis is None:
            self._redis = redis.from_url(settings.redis_url)
        return self._redis

    async def get(self, key: str) -> dict | None:
        r = await self._conn()
        val = await r.get(key)
        return json.loads(val) if val else None

    async def set(self, key: str, value: dict, ttl: int = 300) -> None:
        r = await self._conn()
        await r.set(key, json.dumps(value), ex=ttl)


cache = Cache()
