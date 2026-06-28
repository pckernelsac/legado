"""Modelos de identidad: usuarios, roles, permisos, sesiones y dispositivos."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, BaseModel, UUIDPrimaryKeyMixin
from app.infrastructure.models.enums import RoleName

# Tabla de asociación many-to-many rol <-> permiso.
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        PG_UUID(as_uuid=True),
        ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        PG_UUID(as_uuid=True),
        ForeignKey("permission.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Permission(BaseModel):
    """Permiso granular, ej. `memorial:create`, `user:delete`."""

    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    roles: Mapped[list["Role"]] = relationship(
        secondary=role_permissions, back_populates="permissions"
    )


class Role(BaseModel):
    """Rol del sistema (RBAC)."""

    name: Mapped[RoleName] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    permissions: Mapped[list[Permission]] = relationship(
        secondary=role_permissions, back_populates="roles", lazy="selectin"
    )
    users: Mapped[list["User"]] = relationship(back_populates="role")


class User(BaseModel):
    """Usuario de la plataforma."""

    __table_args__ = (
        Index("ix_user_email_active", "email", "is_deleted"),
        UniqueConstraint("email", name="uq_user_email"),
    )

    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    locale: Mapped[str] = mapped_column(String(10), default="es", nullable=False)

    # Estado de la cuenta
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # MFA (preparado)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Bloqueo de cuenta / intentos fallidos
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Verificación de email / reset de contraseña (tokens hasheados)
    email_verification_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_reset_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_reset_expires: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Multi-tenant ready: agrupación lógica (org/funeraria). Nullable por defecto.
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True, index=True
    )

    role_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("role.id"), nullable=False, index=True
    )
    role: Mapped[Role] = relationship(back_populates="users", lazy="joined")

    memorials: Mapped[list["Memorial"]] = relationship(  # noqa: F821
        back_populates="owner", cascade="all, delete-orphan"
    )
    sessions: Mapped[list["Session"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    devices: Mapped[list["Device"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Device(BaseModel):
    """Dispositivo conocido de un usuario (device tracking)."""

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    device_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    device_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    os: Mapped[str | None] = mapped_column(String(80), nullable=True)
    browser: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_trusted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped[User] = relationship(back_populates="devices")


class Session(UUIDPrimaryKeyMixin, Base):
    """
    Sesión de refresh token (session tracking).

    Permite revocación: cuando `revoked_at` está poblado el refresh token deja
    de ser válido. `jti` es el id del refresh token JWT emitido.
    """

    __tablename__ = "session"
    __table_args__ = (
        Index("ix_session_user_active", "user_id", "revoked_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    device_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("device.id", ondelete="SET NULL"), nullable=True
    )
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped[User] = relationship(back_populates="sessions")
