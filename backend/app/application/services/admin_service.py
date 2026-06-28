"""Servicio del panel de administración: métricas, usuarios y memoriales."""
from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.schemas.admin import (
    AdminMemorialOut,
    AdminStats,
    AdminUserOut,
)
from app.core.exceptions import NotFoundError
from app.infrastructure.models.enums import MemorialStatus, ModerationStatus
from app.infrastructure.models.memorial import Condolence, Memorial, VirtualCandle
from app.infrastructure.models.user import Role, User


class AdminService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def stats(self) -> AdminStats:
        async def _count(stmt) -> int:
            return int((await self.session.execute(stmt)).scalar_one())

        total_users = await _count(
            select(func.count()).select_from(User).where(User.is_deleted.is_(False))
        )
        total_memorials = await _count(
            select(func.count()).select_from(Memorial).where(Memorial.is_deleted.is_(False))
        )
        published = await _count(
            select(func.count())
            .select_from(Memorial)
            .where(
                Memorial.is_deleted.is_(False),
                Memorial.status == MemorialStatus.PUBLISHED,
            )
        )
        total_candles = await _count(
            select(func.count())
            .select_from(VirtualCandle)
            .where(VirtualCandle.is_deleted.is_(False))
        )
        total_condolences = await _count(
            select(func.count())
            .select_from(Condolence)
            .where(Condolence.is_deleted.is_(False))
        )
        pending = await _count(
            select(func.count())
            .select_from(Condolence)
            .where(
                Condolence.is_deleted.is_(False),
                Condolence.moderation_status == ModerationStatus.PENDING,
            )
        )
        return AdminStats(
            total_users=total_users,
            total_memorials=total_memorials,
            published_memorials=published,
            total_candles=total_candles,
            total_condolences=total_condolences,
            pending_condolences=pending,
        )

    async def list_users(self, *, limit: int, offset: int) -> list[AdminUserOut]:
        mem_count = (
            select(Memorial.owner_id, func.count().label("cnt"))
            .where(Memorial.is_deleted.is_(False))
            .group_by(Memorial.owner_id)
            .subquery()
        )
        stmt = (
            select(User, Role.name, func.coalesce(mem_count.c.cnt, 0))
            .join(Role, User.role_id == Role.id)
            .outerjoin(mem_count, mem_count.c.owner_id == User.id)
            .where(User.is_deleted.is_(False))
            .order_by(User.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await self.session.execute(stmt)).all()
        return [
            AdminUserOut(
                id=u.id,
                email=u.email,
                full_name=u.full_name,
                role=role_name,
                is_active=u.is_active,
                is_email_verified=u.is_email_verified,
                memorials_count=int(cnt),
                created_at=u.created_at,
                last_login_at=u.last_login_at,
            )
            for u, role_name, cnt in rows
        ]

    async def list_memorials(self, *, limit: int, offset: int) -> list[AdminMemorialOut]:
        stmt = (
            select(Memorial, User.email)
            .join(User, Memorial.owner_id == User.id)
            .where(Memorial.is_deleted.is_(False))
            .order_by(Memorial.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await self.session.execute(stmt)).all()
        return [
            AdminMemorialOut(
                id=m.id,
                public_slug=m.public_slug,
                full_name=m.full_name,
                owner_email=owner_email,
                status=m.status,
                view_count=m.view_count,
                candle_count=m.candle_count,
                condolence_count=m.condolence_count,
                created_at=m.created_at,
            )
            for m, owner_email in rows
        ]

    async def set_user_active(self, user_id: uuid.UUID, is_active: bool) -> None:
        user = await self.session.get(User, user_id)
        if user is None or user.is_deleted:
            raise NotFoundError("Usuario no encontrado.")
        user.is_active = is_active
        await self.session.flush()

    async def set_memorial_status(
        self, memorial_id: uuid.UUID, status: MemorialStatus
    ) -> None:
        memorial = await self.session.get(Memorial, memorial_id)
        if memorial is None or memorial.is_deleted:
            raise NotFoundError("Memorial no encontrado.")
        memorial.status = status
        await self.session.flush()

    async def get_memorial(self, memorial_id: uuid.UUID) -> Memorial:
        memorial = await self.session.get(Memorial, memorial_id)
        if memorial is None or memorial.is_deleted:
            raise NotFoundError("Memorial no encontrado.")
        return memorial
