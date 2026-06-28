"""Schemas comunes: respuestas paginadas y envoltorios."""
from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Page(BaseModel, Generic[T]):
    """Paginación clásica por offset."""

    items: list[T]
    total: int
    limit: int
    offset: int


class CursorPage(BaseModel, Generic[T]):
    """Paginación por cursor (keyset)."""

    items: list[T]
    next_cursor: str | None = None
    has_more: bool = False


class MessageResponse(BaseModel):
    message: str
