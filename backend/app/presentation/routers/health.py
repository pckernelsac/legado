"""Health checks para orquestador y balanceador."""
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.database.session import engine

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness():
    checks = {"database": False, "redis": False}
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:  # noqa: BLE001
        pass
    try:
        await get_redis().ping()
        checks["redis"] = True
    except Exception:  # noqa: BLE001
        pass

    status = "ok" if all(checks.values()) else "degraded"
    return {"status": status, "checks": checks}
