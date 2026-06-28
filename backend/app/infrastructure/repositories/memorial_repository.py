"""Repositorio de memoriales y contenido asociado, con cursor pagination."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.infrastructure.models.enums import (
    MediaStatus,
    MemorialStatus,
    ModerationStatus,
)
from app.infrastructure.models.memorial import (
    Condolence,
    FamilyMember,
    Memorial,
    MemorialMedia,
    QRCode,
    TimelineEvent,
    VirtualCandle,
)
from app.infrastructure.repositories.base import SQLAlchemyRepository


class MemorialRepository(SQLAlchemyRepository[Memorial]):
    model = Memorial

    async def get_by_slug(self, slug: str, *, with_content: bool = False) -> Memorial | None:
        stmt = select(Memorial).where(
            Memorial.public_slug == slug, Memorial.is_deleted.is_(False)
        )
        if with_content:
            stmt = stmt.options(
                selectinload(Memorial.media),
                selectinload(Memorial.timeline_events),
                selectinload(Memorial.family_members),
            )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_owner(
        self, owner_id: uuid.UUID, *, limit: int = 20, offset: int = 0
    ) -> list[Memorial]:
        stmt = (
            select(Memorial)
            .where(Memorial.owner_id == owner_id, Memorial.is_deleted.is_(False))
            .order_by(Memorial.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_owner(self, owner_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Memorial)
            .where(Memorial.owner_id == owner_id, Memorial.is_deleted.is_(False))
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def list_published_cursor(
        self, *, cursor: datetime | None = None, limit: int = 24
    ) -> list[Memorial]:
        """Cursor pagination (keyset) sobre created_at para feeds públicos."""
        stmt = select(Memorial).where(
            Memorial.status == MemorialStatus.PUBLISHED,
            Memorial.is_deleted.is_(False),
        )
        if cursor is not None:
            stmt = stmt.where(Memorial.created_at < cursor)
        stmt = stmt.order_by(Memorial.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def increment_views(self, memorial_id: uuid.UUID) -> None:
        memorial = await self.get(memorial_id)
        if memorial:
            memorial.view_count += 1
            await self.session.flush()


class CondolenceRepository(SQLAlchemyRepository[Condolence]):
    model = Condolence

    async def list_all(
        self, memorial_id: uuid.UUID, *, limit: int = 100, offset: int = 0
    ) -> list[Condolence]:
        """Todas las condolencias (cualquier estado) para moderación del dueño."""
        stmt = (
            select(Condolence)
            .where(
                Condolence.memorial_id == memorial_id,
                Condolence.is_deleted.is_(False),
            )
            .order_by(Condolence.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_approved(
        self, memorial_id: uuid.UUID, *, limit: int = 50, offset: int = 0
    ) -> list[Condolence]:
        stmt = (
            select(Condolence)
            .where(
                Condolence.memorial_id == memorial_id,
                Condolence.is_deleted.is_(False),
                Condolence.moderation_status.in_(
                    [ModerationStatus.APPROVED, ModerationStatus.AUTO_APPROVED]
                ),
            )
            .order_by(Condolence.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class CandleRepository(SQLAlchemyRepository[VirtualCandle]):
    model = VirtualCandle

    async def count_by_country(
        self, memorial_id: uuid.UUID
    ) -> list[tuple[str, str | None, int]]:
        """Agrega velas por país (solo las que ya tienen país resuelto)."""
        stmt = (
            select(
                VirtualCandle.country,
                func.max(VirtualCandle.country_code),
                func.count(),
            )
            .where(
                VirtualCandle.memorial_id == memorial_id,
                VirtualCandle.is_deleted.is_(False),
                VirtualCandle.country.is_not(None),
            )
            .group_by(VirtualCandle.country)
            .order_by(func.count().desc())
        )
        result = await self.session.execute(stmt)
        return [(c, cc, int(n)) for c, cc, n in result.all()]

    async def count_for_memorial(self, memorial_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(VirtualCandle)
            .where(
                VirtualCandle.memorial_id == memorial_id,
                VirtualCandle.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())


class MediaRepository(SQLAlchemyRepository[MemorialMedia]):
    model = MemorialMedia

    async def list_by_memorial(self, memorial_id: uuid.UUID) -> list[MemorialMedia]:
        # Excluye subidas no confirmadas (PENDING): solo media con objeto en MinIO.
        stmt = (
            select(MemorialMedia)
            .where(
                MemorialMedia.memorial_id == memorial_id,
                MemorialMedia.is_deleted.is_(False),
                MemorialMedia.status != MediaStatus.PENDING,
            )
            .order_by(MemorialMedia.position.asc(), MemorialMedia.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_memorial(self, memorial_id: uuid.UUID) -> int:
        """Cuenta media confirmada (no PENDING, no borrada) de un memorial."""
        stmt = (
            select(func.count())
            .select_from(MemorialMedia)
            .where(
                MemorialMedia.memorial_id == memorial_id,
                MemorialMedia.is_deleted.is_(False),
                MemorialMedia.status != MediaStatus.PENDING,
            )
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())


class QRRepository(SQLAlchemyRepository[QRCode]):
    model = QRCode

    async def list_by_memorial(self, memorial_id: uuid.UUID) -> list[QRCode]:
        stmt = (
            select(QRCode)
            .where(QRCode.memorial_id == memorial_id, QRCode.is_deleted.is_(False))
            .order_by(QRCode.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class FamilyRepository(SQLAlchemyRepository[FamilyMember]):
    model = FamilyMember

    async def list_by_memorial(self, memorial_id: uuid.UUID) -> list[FamilyMember]:
        stmt = (
            select(FamilyMember)
            .where(
                FamilyMember.memorial_id == memorial_id,
                FamilyMember.is_deleted.is_(False),
            )
            .order_by(FamilyMember.birth_year.asc().nullslast())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class TimelineRepository(SQLAlchemyRepository[TimelineEvent]):
    model = TimelineEvent

    async def list_by_memorial(self, memorial_id: uuid.UUID) -> list[TimelineEvent]:
        stmt = (
            select(TimelineEvent)
            .where(
                TimelineEvent.memorial_id == memorial_id,
                TimelineEvent.is_deleted.is_(False),
            )
            .order_by(
                TimelineEvent.position.asc(),
                TimelineEvent.event_date.asc().nullslast(),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
