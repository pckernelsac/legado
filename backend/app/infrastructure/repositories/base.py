"""Repositorio genérico async sobre SQLAlchemy 2.0 con soporte de soft-delete."""
from __future__ import annotations

import uuid
from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.base import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class SQLAlchemyRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, entity_id: uuid.UUID, *, include_deleted: bool = False) -> ModelT | None:
        stmt = select(self.model).where(self.model.id == entity_id)
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted.is_(False))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def soft_delete(self, entity: ModelT) -> None:
        from datetime import datetime, timezone

        entity.is_deleted = True
        entity.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def list(
        self, *, limit: int = 50, offset: int = 0, include_deleted: bool = False
    ) -> list[ModelT]:
        stmt = select(self.model)
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted.is_(False))
        stmt = stmt.order_by(self.model.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, *, include_deleted: bool = False) -> int:
        stmt = select(func.count()).select_from(self.model)
        if not include_deleted:
            stmt = stmt.where(self.model.is_deleted.is_(False))
        result = await self.session.execute(stmt)
        return int(result.scalar_one())
