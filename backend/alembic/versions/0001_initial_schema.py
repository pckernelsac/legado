"""Esquema inicial completo de Legado Eterno.

Esta migración de arranque materializa el esquema completo a partir de los
metadatos de los modelos SQLAlchemy, garantizando consistencia 1:1 con el código.
Las extensiones (pg_trgm, pgcrypto, etc.) las provee el init de Postgres.

A partir de aquí, los cambios de esquema se generan con:
    alembic revision --autogenerate -m "descripcion"

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-23
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op

from app.infrastructure.database.base import Base
import app.infrastructure.models  # noqa: F401  (puebla Base.metadata)

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
