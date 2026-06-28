"""Endpoints de multimedia de un memorial (subida directa a MinIO)."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, status

from app.application.schemas.common import MessageResponse
from app.application.schemas.memorial import (
    MediaOut,
    MediaUpdate,
    MediaUploadInit,
    MediaUploadResponse,
)
from app.presentation.dependencies import (
    BillingServiceDep,
    CurrentUser,
    MediaServiceDep,
)

router = APIRouter(prefix="/memorials/{memorial_id}/media", tags=["media"])


@router.post("/upload-url", response_model=MediaUploadResponse, status_code=status.HTTP_201_CREATED)
async def init_upload(
    memorial_id: uuid.UUID,
    data: MediaUploadInit,
    user: CurrentUser,
    service: MediaServiceDep,
    billing: BillingServiceDep,
):
    """Paso 1: obtener una URL prefirmada para subir el archivo directo a MinIO."""
    await billing.assert_can_add_media(user.id, memorial_id)
    return await service.init_upload(user.id, memorial_id, data)


@router.post("/{media_id}/confirm", response_model=MediaOut)
async def confirm_upload(
    memorial_id: uuid.UUID,
    media_id: uuid.UUID,
    user: CurrentUser,
    service: MediaServiceDep,
):
    """Paso 2: confirmar la subida; marca READY y encola el procesamiento."""
    return await service.confirm_upload(user.id, memorial_id, media_id)


@router.get("", response_model=list[MediaOut])
async def list_media(
    memorial_id: uuid.UUID, user: CurrentUser, service: MediaServiceDep
):
    return await service.list_media(user.id, memorial_id)


@router.patch("/{media_id}", response_model=MediaOut)
async def update_media(
    memorial_id: uuid.UUID,
    media_id: uuid.UUID,
    data: MediaUpdate,
    user: CurrentUser,
    service: MediaServiceDep,
):
    return await service.update_media(user.id, memorial_id, media_id, data)


@router.post("/{media_id}/set-main", response_model=MessageResponse)
async def set_main_photo(
    memorial_id: uuid.UUID,
    media_id: uuid.UUID,
    user: CurrentUser,
    service: MediaServiceDep,
):
    await service.set_main_photo(user.id, memorial_id, media_id)
    return MessageResponse(message="Foto principal actualizada.")


@router.post("/{media_id}/set-cover", response_model=MessageResponse)
async def set_cover_photo(
    memorial_id: uuid.UUID,
    media_id: uuid.UUID,
    user: CurrentUser,
    service: MediaServiceDep,
):
    await service.set_cover_photo(user.id, memorial_id, media_id)
    return MessageResponse(message="Foto de portada actualizada.")


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    memorial_id: uuid.UUID,
    media_id: uuid.UUID,
    user: CurrentUser,
    service: MediaServiceDep,
):
    await service.delete_media(user.id, memorial_id, media_id)
