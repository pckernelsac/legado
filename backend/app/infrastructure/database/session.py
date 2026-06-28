"""
Gestión del engine async y sesiones de SQLAlchemy con connection pooling.

El pool está dimensionado para alta concurrencia: con DB_POOL_SIZE=20 y
DB_MAX_OVERFLOW=10 por worker, y 4 workers, se obtienen hasta 120 conexiones.
En producción se recomienda PgBouncer delante de PostgreSQL.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Engine síncrono (psycopg2) para las tareas Celery, que no corren en el loop async.
sync_engine = create_engine(
    settings.database_url_sync,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=settings.DB_POOL_RECYCLE,
)

SyncSessionFactory = sessionmaker(bind=sync_engine, expire_on_commit=False, autoflush=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia FastAPI: una sesión por request, con commit/rollback automático."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
