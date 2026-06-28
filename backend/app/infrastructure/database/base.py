"""
Base declarativa de SQLAlchemy 2.0 y mixins reutilizables.

Todos los modelos heredan UUIDv7 como PK, timestamps automáticos y soft-delete.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from app.core.identifiers import uuid7


class Base(DeclarativeBase):
    """Base declarativa común a todos los modelos."""

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        # Convención: CamelCase -> snake_case en plural simple.
        name = cls.__name__
        snake = "".join(
            f"_{c.lower()}" if c.isupper() else c for c in name
        ).lstrip("_")
        return snake


class UUIDPrimaryKeyMixin:
    """Clave primaria UUIDv7 generada en la aplicación."""

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
        index=True,
    )


class TimestampMixin:
    """created_at / updated_at gestionados por la base de datos."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Borrado lógico: nunca se eliminan filas físicamente."""

    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class BaseModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Modelo base completo: PK UUIDv7 + timestamps + soft delete."""

    __abstract__ = True
