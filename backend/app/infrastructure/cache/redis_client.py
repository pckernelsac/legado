"""
Cliente Redis async: cache de aplicación, lista de revocación de tokens (JWT
denylist) y contadores de rate limiting / account lockout.
"""
from __future__ import annotations

import json
from typing import Any

import redis.asyncio as redis

from app.core.config import settings

_pool = redis.ConnectionPool.from_url(
    settings.redis_url,
    max_connections=50,
    decode_responses=True,
)


def get_redis() -> redis.Redis:
    return redis.Redis(connection_pool=_pool)


class CacheService:
    """Wrapper de alto nivel sobre Redis para cache y seguridad."""

    def __init__(self, client: redis.Redis | None = None) -> None:
        self.client = client or get_redis()

    # --- Cache genérico -----------------------------------------------------
    async def get_json(self, key: str) -> Any | None:
        raw = await self.client.get(key)
        return json.loads(raw) if raw else None

    async def set_json(self, key: str, value: Any, ttl: int = 300) -> None:
        await self.client.set(key, json.dumps(value, default=str), ex=ttl)

    async def delete(self, *keys: str) -> None:
        if keys:
            await self.client.delete(*keys)

    async def invalidate_prefix(self, prefix: str) -> None:
        async for key in self.client.scan_iter(match=f"{prefix}*", count=200):
            await self.client.delete(key)

    # --- JWT denylist (revocación de access tokens) ------------------------
    async def revoke_jti(self, jti: str, ttl_seconds: int) -> None:
        await self.client.set(f"jwt:revoked:{jti}", "1", ex=max(ttl_seconds, 1))

    async def is_jti_revoked(self, jti: str) -> bool:
        return await self.client.exists(f"jwt:revoked:{jti}") == 1

    # --- Rate limiting / lockout (token bucket simple) ---------------------
    async def incr_with_ttl(self, key: str, ttl_seconds: int) -> int:
        pipe = self.client.pipeline()
        pipe.incr(key)
        pipe.expire(key, ttl_seconds)
        count, _ = await pipe.execute()
        return int(count)
