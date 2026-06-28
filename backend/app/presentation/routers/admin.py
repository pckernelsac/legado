"""Panel de administración (solo super_admin / admin)."""
from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.application.schemas.admin import (
    AdminMemorialOut,
    AdminStats,
    AdminUserOut,
    MemorialStatusUpdate,
    UserActiveUpdate,
)
from app.application.schemas.common import MessageResponse
from app.application.schemas.memorial import QRGenerateRequest, QROut
from app.infrastructure.models.enums import RoleName
from app.infrastructure.models.memorial import QRCode
from app.infrastructure.repositories.memorial_repository import QRRepository
from app.infrastructure.services.qr_service import get_qr_service
from app.infrastructure.storage.minio_client import get_storage
from app.presentation.dependencies import AdminServiceDep, DbSession, require_roles

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_roles(RoleName.SUPER_ADMIN, RoleName.ADMIN))],
)


@router.get("/stats", response_model=AdminStats)
async def stats(service: AdminServiceDep):
    return await service.stats()


@router.get("/users", response_model=list[AdminUserOut])
async def list_users(
    service: AdminServiceDep,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return await service.list_users(limit=limit, offset=offset)


@router.patch("/users/{user_id}", response_model=MessageResponse)
async def set_user_active(
    user_id: uuid.UUID, data: UserActiveUpdate, service: AdminServiceDep
):
    await service.set_user_active(user_id, data.is_active)
    return MessageResponse(
        message="Usuario activado." if data.is_active else "Usuario desactivado."
    )


@router.get("/memorials", response_model=list[AdminMemorialOut])
async def list_memorials(
    service: AdminServiceDep,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return await service.list_memorials(limit=limit, offset=offset)


@router.patch("/memorials/{memorial_id}/status", response_model=MessageResponse)
async def set_memorial_status(
    memorial_id: uuid.UUID, data: MemorialStatusUpdate, service: AdminServiceDep
):
    await service.set_memorial_status(memorial_id, data.status)
    return MessageResponse(message="Estado del memorial actualizado.")


# --- QR de cualquier memorial (para imprimir) ------------------------------
def _qr_out(qr) -> QROut:
    storage = get_storage()
    return QROut(
        id=qr.id,
        format=qr.format,
        target_url=qr.target_url,
        storage_key=qr.storage_key,
        resolution=qr.resolution,
        label=qr.label,
        qr_url=storage.public_url(qr.storage_key),
    )


@router.get("/memorials/{memorial_id}/qr", response_model=list[QROut])
async def list_memorial_qr(
    memorial_id: uuid.UUID, service: AdminServiceDep, db: DbSession
):
    await service.get_memorial(memorial_id)
    qrs = await QRRepository(db).list_by_memorial(memorial_id)
    return [_qr_out(qr) for qr in qrs]


@router.post(
    "/memorials/{memorial_id}/qr",
    response_model=QROut,
    status_code=status.HTTP_201_CREATED,
)
async def generate_memorial_qr(
    memorial_id: uuid.UUID,
    data: QRGenerateRequest,
    service: AdminServiceDep,
    db: DbSession,
):
    from app.core.config import settings

    memorial = await service.get_memorial(memorial_id)
    target_url = f"{settings.PUBLIC_BASE_URL}/m/{memorial.public_slug}"
    storage_key, _ = get_qr_service().generate_and_store(
        memorial_slug=memorial.public_slug, url=target_url, fmt=data.format.value
    )
    qr = QRCode(
        memorial_id=memorial.id,
        target_url=target_url,
        format=data.format,
        storage_key=storage_key,
        label=data.label,
    )
    db.add(qr)
    await db.flush()
    return _qr_out(qr)
