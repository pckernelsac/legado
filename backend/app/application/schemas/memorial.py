"""Schemas de memoriales, multimedia, línea de tiempo, condolencias y velas."""
from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.application.schemas.common import ORMModel
from app.infrastructure.models.enums import (
    MediaStatus,
    MediaType,
    MemorialStatus,
    MemorialVisibility,
    ModerationStatus,
    QRFormat,
)


# --- Memorial ---------------------------------------------------------------
class MemorialCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    birth_date: date | None = None
    death_date: date | None = None
    birth_place: str | None = Field(default=None, max_length=200)
    death_place: str | None = Field(default=None, max_length=200)
    profession: str | None = Field(default=None, max_length=200)
    biography: str | None = None
    epitaph: str | None = Field(default=None, max_length=500)
    memorable_quotes: list[str] | None = None
    visibility: MemorialVisibility = MemorialVisibility.PUBLIC


class MemorialUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=200)
    birth_date: date | None = None
    death_date: date | None = None
    birth_place: str | None = None
    death_place: str | None = None
    profession: str | None = None
    biography: str | None = None
    epitaph: str | None = None
    memorable_quotes: list[str] | None = None
    location_lat: float | None = None
    location_lng: float | None = None
    location_address: str | None = None
    cemetery_name: str | None = None
    visibility: MemorialVisibility | None = None
    status: MemorialStatus | None = None
    allow_condolences: bool | None = None
    auto_moderate: bool | None = None
    seo_title: str | None = Field(default=None, max_length=160)
    seo_description: str | None = Field(default=None, max_length=320)


class MemorialOut(ORMModel):
    id: uuid.UUID
    public_slug: str
    full_name: str
    birth_date: date | None
    death_date: date | None
    birth_place: str | None
    death_place: str | None
    profession: str | None
    biography: str | None
    epitaph: str | None
    main_photo_url: str | None
    cover_photo_url: str | None
    status: MemorialStatus
    visibility: MemorialVisibility
    view_count: int
    candle_count: int
    condolence_count: int
    created_at: datetime


class MemorialPublicOut(ORMModel):
    """Vista pública — nunca expone owner_id ni el UUID en URLs."""

    public_slug: str
    full_name: str
    birth_date: date | None
    death_date: date | None
    birth_place: str | None
    death_place: str | None
    profession: str | None
    biography: str | None
    epitaph: str | None
    memorable_quotes: list | None
    main_photo_url: str | None
    cover_photo_url: str | None
    location_lat: float | None
    location_lng: float | None
    location_address: str | None
    cemetery_name: str | None
    view_count: int
    candle_count: int
    condolence_count: int
    seo_title: str | None
    seo_description: str | None


# --- Media ------------------------------------------------------------------
class MediaUploadInit(BaseModel):
    media_type: MediaType
    original_filename: str = Field(max_length=255)
    content_type: str = Field(max_length=100)
    file_size: int = Field(gt=0, le=200 * 1024 * 1024)  # máx 200MB


class MediaUploadResponse(BaseModel):
    """Respuesta de inicio de subida: el navegador hace PUT directo a `upload_url`."""

    media_id: uuid.UUID
    upload_url: str
    storage_key: str
    expires_in: int = 900


class MediaUpdate(BaseModel):
    caption: str | None = Field(default=None, max_length=500)
    position: int | None = None


class MediaOut(BaseModel):
    """Item de multimedia con URLs prefirmadas listas para el navegador."""

    id: uuid.UUID
    media_type: MediaType
    status: MediaStatus
    url: str | None = None
    thumbnail_url: str | None = None
    caption: str | None = None
    position: int
    content_type: str | None = None
    original_filename: str | None = None


# --- Línea de tiempo --------------------------------------------------------
class TimelineEventCreate(BaseModel):
    year: int | None = Field(default=None, ge=0, le=3000)
    event_date: date | None = None
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    position: int = 0


class TimelineEventOut(ORMModel):
    id: uuid.UUID
    year: int | None
    event_date: date | None
    title: str
    description: str | None
    image_key: str | None
    position: int


class TimelineEventUpdate(BaseModel):
    year: int | None = Field(default=None, ge=0, le=3000)
    event_date: date | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    position: int | None = None


class TimelinePublicOut(BaseModel):
    """Evento de la línea de tiempo para la vista pública (con URL de imagen)."""

    id: uuid.UUID
    year: int | None = None
    event_date: date | None = None
    title: str
    description: str | None = None
    image_url: str | None = None
    position: int = 0


# --- Árbol genealógico ------------------------------------------------------
class FamilyMemberCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    relationship_type: str | None = Field(default=None, max_length=60)
    birth_year: int | None = Field(default=None, ge=0, le=3000)
    death_year: int | None = Field(default=None, ge=0, le=3000)
    parent_member_id: uuid.UUID | None = None


class FamilyMemberUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=200)
    relationship_type: str | None = Field(default=None, max_length=60)
    birth_year: int | None = Field(default=None, ge=0, le=3000)
    death_year: int | None = Field(default=None, ge=0, le=3000)
    parent_member_id: uuid.UUID | None = None


class FamilyMemberOut(ORMModel):
    id: uuid.UUID
    full_name: str
    relationship_type: str | None
    birth_year: int | None
    death_year: int | None
    parent_member_id: uuid.UUID | None


# --- Condolencias -----------------------------------------------------------
class CondolenceCreate(BaseModel):
    author_name: str = Field(min_length=2, max_length=150)
    author_email: str | None = None
    message: str = Field(min_length=2, max_length=2000)
    signature: str | None = Field(default=None, max_length=200)


class CondolenceOut(ORMModel):
    id: uuid.UUID
    author_name: str
    message: str
    signature: str | None
    photo_url: str | None = None
    created_at: datetime


class CondolenceAdminOut(ORMModel):
    """Condolencia con su estado de moderación (vista del propietario)."""

    id: uuid.UUID
    author_name: str
    author_email: str | None
    message: str
    signature: str | None
    photo_url: str | None = None
    moderation_status: ModerationStatus
    created_at: datetime


class CondolenceModerateRequest(BaseModel):
    approve: bool


# --- Velas ------------------------------------------------------------------
class CandleCreate(BaseModel):
    lit_by_name: str | None = Field(default=None, max_length=150)
    message: str | None = Field(default=None, max_length=300)


class CandleOut(ORMModel):
    id: uuid.UUID
    lit_by_name: str | None
    message: str | None
    country: str | None
    city: str | None
    created_at: datetime


class CandleCountryOut(BaseModel):
    """Agregado de velas por país para la vista pública."""

    country: str
    country_code: str | None
    count: int


# --- QR ---------------------------------------------------------------------
class QRGenerateRequest(BaseModel):
    format: QRFormat = QRFormat.PNG
    label: str | None = Field(default=None, max_length=120)


class QROut(ORMModel):
    id: uuid.UUID
    format: QRFormat
    target_url: str
    storage_key: str
    resolution: int
    label: str | None
    qr_url: str | None = None
