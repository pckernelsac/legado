"""Schemas del panel de administración."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.infrastructure.models.enums import MemorialStatus


class AdminStats(BaseModel):
    total_users: int
    total_memorials: int
    published_memorials: int
    total_candles: int
    total_condolences: int
    pending_condolences: int


class AdminUserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    is_email_verified: bool
    memorials_count: int
    created_at: datetime
    last_login_at: datetime | None


class AdminMemorialOut(BaseModel):
    id: uuid.UUID
    public_slug: str
    full_name: str
    owner_email: str
    status: MemorialStatus
    view_count: int
    candle_count: int
    condolence_count: int
    created_at: datetime


class UserActiveUpdate(BaseModel):
    is_active: bool


class MemorialStatusUpdate(BaseModel):
    status: MemorialStatus
