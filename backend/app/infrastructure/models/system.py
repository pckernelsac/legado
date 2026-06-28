"""Modelos transversales: auditoría, actividad y notificaciones."""
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.infrastructure.models.enums import NotificationType


class AuditLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Registro de auditoría de seguridad: acciones sensibles e inmutables.
    (login, cambios de rol, eliminación de datos, accesos administrativos...)
    """

    __tablename__ = "audit_log"
    __table_args__ = (
        Index("ix_audit_actor_created", "actor_id", "created_at"),
        Index("ix_audit_action_created", "action", "created_at"),
    )

    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True, index=True
    )
    actor_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)  # success/failure
    detail: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class ActivityLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Registro de actividad de negocio (para métricas y feed del dashboard)."""

    __tablename__ = "activity_log"
    __table_args__ = (
        Index("ix_activity_user_created", "user_id", "created_at"),
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True, index=True
    )
    memorial_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True, index=True
    )
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class Notification(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Notificación dirigida a un usuario."""

    __tablename__ = "notification"
    __table_args__ = (
        Index("ix_notification_user_read", "user_id", "is_read"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    type: Mapped[NotificationType] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    link: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
