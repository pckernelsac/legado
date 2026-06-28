"""Modelos del núcleo del producto: memoriales y su contenido."""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.identifiers import generate_public_slug
from app.infrastructure.database.base import BaseModel
from app.infrastructure.models.enums import (
    MediaStatus,
    MediaType,
    MemorialStatus,
    MemorialVisibility,
    ModerationStatus,
    QRFormat,
)


class Memorial(BaseModel):
    """Memorial digital de una persona."""

    __table_args__ = (
        Index("ix_memorial_owner_status", "owner_id", "status"),
        Index("ix_memorial_slug_active", "public_slug", "is_deleted"),
    )

    # Identificador público opaco — NUNCA se expone el UUID real.
    public_slug: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False, default=generate_public_slug
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    owner: Mapped["User"] = relationship(back_populates="memorials")  # noqa: F821

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True, index=True
    )

    # --- Datos biográficos --------------------------------------------------
    full_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    death_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    birth_place: Mapped[str | None] = mapped_column(String(200), nullable=True)
    death_place: Mapped[str | None] = mapped_column(String(200), nullable=True)
    profession: Mapped[str | None] = mapped_column(String(200), nullable=True)
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)
    epitaph: Mapped[str | None] = mapped_column(String(500), nullable=True)
    memorable_quotes: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # --- Multimedia principal ----------------------------------------------
    main_photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    cover_photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # --- Ubicación (mapa) ---------------------------------------------------
    location_lat: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    location_lng: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    location_address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    cemetery_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # --- Estado / visibilidad ----------------------------------------------
    status: Mapped[MemorialStatus] = mapped_column(
        String(20), default=MemorialStatus.DRAFT, nullable=False, index=True
    )
    visibility: Mapped[MemorialVisibility] = mapped_column(
        String(20), default=MemorialVisibility.PUBLIC, nullable=False
    )
    allow_condolences: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_moderate: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # --- SEO ----------------------------------------------------------------
    seo_title: Mapped[str | None] = mapped_column(String(160), nullable=True)
    seo_description: Mapped[str | None] = mapped_column(String(320), nullable=True)

    # --- Métricas (desnormalizadas para lectura rápida) ---------------------
    view_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    candle_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    condolence_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # --- Relaciones ---------------------------------------------------------
    media: Mapped[list["MemorialMedia"]] = relationship(
        back_populates="memorial", cascade="all, delete-orphan"
    )
    timeline_events: Mapped[list["TimelineEvent"]] = relationship(
        back_populates="memorial", cascade="all, delete-orphan"
    )
    family_members: Mapped[list["FamilyMember"]] = relationship(
        back_populates="memorial",
        cascade="all, delete-orphan",
        foreign_keys="FamilyMember.memorial_id",
    )
    condolences: Mapped[list["Condolence"]] = relationship(
        back_populates="memorial", cascade="all, delete-orphan"
    )
    candles: Mapped[list["VirtualCandle"]] = relationship(
        back_populates="memorial", cascade="all, delete-orphan"
    )
    qr_codes: Mapped[list["QRCode"]] = relationship(
        back_populates="memorial", cascade="all, delete-orphan"
    )


class MemorialMedia(BaseModel):
    """Foto, video o audio asociado a un memorial (almacenado en MinIO)."""

    __table_args__ = (
        Index("ix_media_memorial_type", "memorial_id", "media_type"),
    )

    memorial_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("memorial.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    media_type: Mapped[MediaType] = mapped_column(String(20), nullable=False)
    status: Mapped[MediaStatus] = mapped_column(
        String(20), default=MediaStatus.PENDING, nullable=False
    )

    # Claves en el bucket (no URLs firmadas, que se generan on-demand).
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    thumbnail_key: Mapped[str | None] = mapped_column(String(512), nullable=True)

    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    file_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    caption: Mapped[str | None] = mapped_column(String(500), nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)

    memorial: Mapped[Memorial] = relationship(back_populates="media")


class TimelineEvent(BaseModel):
    """Evento de la línea de tiempo del memorial."""

    __table_args__ = (
        Index("ix_timeline_memorial_order", "memorial_id", "event_date"),
    )

    memorial_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("memorial.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    event_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    memorial: Mapped[Memorial] = relationship(back_populates="timeline_events")


class FamilyMember(BaseModel):
    """Nodo del árbol genealógico vinculado al memorial."""

    memorial_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("memorial.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    # Auto-referencia para construir el árbol.
    parent_member_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("family_member.id", ondelete="SET NULL"),
        nullable=True,
    )
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    relationship_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    birth_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    death_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    photo_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    # Memorial enlazado si ese familiar también tiene su propio memorial.
    linked_memorial_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("memorial.id", ondelete="SET NULL"),
        nullable=True,
    )

    memorial: Mapped[Memorial] = relationship(
        back_populates="family_members", foreign_keys=[memorial_id]
    )
    children: Mapped[list["FamilyMember"]] = relationship(
        backref="parent", remote_side="FamilyMember.id",
        foreign_keys=[parent_member_id],
    )


class Condolence(BaseModel):
    """Mensaje del libro de condolencias (con moderación)."""

    __table_args__ = (
        Index("ix_condolence_memorial_status", "memorial_id", "moderation_status"),
    )

    memorial_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("memorial.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    author_name: Mapped[str] = mapped_column(String(150), nullable=False)
    author_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_user_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    photo_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    signature: Mapped[str | None] = mapped_column(String(200), nullable=True)

    moderation_status: Mapped[ModerationStatus] = mapped_column(
        String(20), default=ModerationStatus.PENDING, nullable=False
    )
    moderated_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    moderated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)

    memorial: Mapped[Memorial] = relationship(back_populates="condolences")


class VirtualCandle(BaseModel):
    """Vela virtual encendida en memoria (con geolocalización aproximada)."""

    __table_args__ = (
        Index("ix_candle_memorial_created", "memorial_id", "created_at"),
    )

    memorial_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("memorial.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    lit_by_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    lit_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    message: Mapped[str | None] = mapped_column(String(300), nullable=True)
    country: Mapped[str | None] = mapped_column(String(80), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    # Vela "permanente" (de pago) vs temporal (24-48h).
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    memorial: Mapped[Memorial] = relationship(back_populates="candles")


class QRCode(BaseModel):
    """Código QR generado para un memorial (lápida, nicho, mausoleo)."""

    __tablename__ = "qr_code"

    memorial_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("memorial.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    target_url: Mapped[str] = mapped_column(String(512), nullable=False)
    format: Mapped[QRFormat] = mapped_column(String(10), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    resolution: Mapped[int] = mapped_column(Integer, default=1024, nullable=False)
    scan_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    label: Mapped[str | None] = mapped_column(String(120), nullable=True)

    memorial: Mapped[Memorial] = relationship(back_populates="qr_codes")
