"""Endpoints de gestión de memoriales del propietario (panel cliente)."""
from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.application.schemas.common import MessageResponse, Page
from app.application.schemas.memorial import (
    CondolenceAdminOut,
    CondolenceModerateRequest,
    FamilyMemberCreate,
    FamilyMemberOut,
    FamilyMemberUpdate,
    MemorialCreate,
    MemorialOut,
    MemorialUpdate,
    QRGenerateRequest,
    QROut,
    TimelineEventCreate,
    TimelineEventOut,
    TimelineEventUpdate,
)
from app.infrastructure.services.qr_service import get_qr_service
from app.infrastructure.storage.minio_client import get_storage
from app.presentation.dependencies import (
    BillingServiceDep,
    CurrentUser,
    MemorialServiceDep,
)

router = APIRouter(prefix="/memorials", tags=["memorials"])


@router.post("", response_model=MemorialOut, status_code=status.HTTP_201_CREATED)
async def create_memorial(
    data: MemorialCreate,
    user: CurrentUser,
    service: MemorialServiceDep,
    billing: BillingServiceDep,
):
    await billing.assert_can_create_memorial(user.id)
    return await service.create(user.id, data)


@router.get("", response_model=Page[MemorialOut])
async def list_my_memorials(
    user: CurrentUser,
    service: MemorialServiceDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    items, total = await service.list_owned(user.id, limit=limit, offset=offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.get("/{memorial_id}", response_model=MemorialOut)
async def get_memorial(
    memorial_id: uuid.UUID, user: CurrentUser, service: MemorialServiceDep
):
    return await service.get_owned(user.id, memorial_id)


@router.patch("/{memorial_id}", response_model=MemorialOut)
async def update_memorial(
    memorial_id: uuid.UUID,
    data: MemorialUpdate,
    user: CurrentUser,
    service: MemorialServiceDep,
):
    return await service.update(user.id, memorial_id, data)


@router.delete("/{memorial_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memorial(
    memorial_id: uuid.UUID, user: CurrentUser, service: MemorialServiceDep
):
    await service.delete(user.id, memorial_id)


# --- Línea de tiempo --------------------------------------------------------
@router.get("/{memorial_id}/timeline", response_model=list[TimelineEventOut])
async def list_timeline(
    memorial_id: uuid.UUID, user: CurrentUser, service: MemorialServiceDep
):
    return await service.list_timeline_owned(user.id, memorial_id)


@router.post(
    "/{memorial_id}/timeline",
    response_model=TimelineEventOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_timeline_event(
    memorial_id: uuid.UUID,
    data: TimelineEventCreate,
    user: CurrentUser,
    service: MemorialServiceDep,
):
    return await service.create_timeline_event(user.id, memorial_id, data)


@router.patch("/{memorial_id}/timeline/{event_id}", response_model=TimelineEventOut)
async def update_timeline_event(
    memorial_id: uuid.UUID,
    event_id: uuid.UUID,
    data: TimelineEventUpdate,
    user: CurrentUser,
    service: MemorialServiceDep,
):
    return await service.update_timeline_event(user.id, memorial_id, event_id, data)


@router.delete(
    "/{memorial_id}/timeline/{event_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_timeline_event(
    memorial_id: uuid.UUID,
    event_id: uuid.UUID,
    user: CurrentUser,
    service: MemorialServiceDep,
):
    await service.delete_timeline_event(user.id, memorial_id, event_id)


# --- Árbol genealógico ------------------------------------------------------
@router.get("/{memorial_id}/family", response_model=list[FamilyMemberOut])
async def list_family(
    memorial_id: uuid.UUID, user: CurrentUser, service: MemorialServiceDep
):
    return await service.list_family_owned(user.id, memorial_id)


@router.post(
    "/{memorial_id}/family",
    response_model=FamilyMemberOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_family_member(
    memorial_id: uuid.UUID,
    data: FamilyMemberCreate,
    user: CurrentUser,
    service: MemorialServiceDep,
):
    return await service.create_family_member(user.id, memorial_id, data)


@router.patch("/{memorial_id}/family/{member_id}", response_model=FamilyMemberOut)
async def update_family_member(
    memorial_id: uuid.UUID,
    member_id: uuid.UUID,
    data: FamilyMemberUpdate,
    user: CurrentUser,
    service: MemorialServiceDep,
):
    return await service.update_family_member(user.id, memorial_id, member_id, data)


@router.delete(
    "/{memorial_id}/family/{member_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_family_member(
    memorial_id: uuid.UUID,
    member_id: uuid.UUID,
    user: CurrentUser,
    service: MemorialServiceDep,
):
    await service.delete_family_member(user.id, memorial_id, member_id)


# --- Moderación de condolencias --------------------------------------------
@router.get("/{memorial_id}/condolences", response_model=list[CondolenceAdminOut])
async def list_condolences_for_moderation(
    memorial_id: uuid.UUID,
    user: CurrentUser,
    service: MemorialServiceDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return await service.list_condolences_owned(
        user.id, memorial_id, limit=limit, offset=offset
    )


@router.post(
    "/{memorial_id}/condolences/{condolence_id}/moderate",
    response_model=MessageResponse,
)
async def moderate_condolence(
    memorial_id: uuid.UUID,
    condolence_id: uuid.UUID,
    data: CondolenceModerateRequest,
    user: CurrentUser,
    service: MemorialServiceDep,
):
    await service.moderate_condolence(
        user.id, memorial_id, condolence_id, approve=data.approve
    )
    return MessageResponse(
        message="Condolencia aprobada." if data.approve else "Condolencia rechazada."
    )


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


@router.get("/{memorial_id}/qr", response_model=list[QROut])
async def list_qr(
    memorial_id: uuid.UUID, user: CurrentUser, service: MemorialServiceDep
):
    from app.infrastructure.repositories.memorial_repository import QRRepository

    await service.get_owned(user.id, memorial_id)
    qrs = await QRRepository(service.memorials.session).list_by_memorial(memorial_id)
    return [_qr_out(qr) for qr in qrs]


@router.post("/{memorial_id}/qr", response_model=QROut, status_code=status.HTTP_201_CREATED)
async def generate_qr(
    memorial_id: uuid.UUID,
    data: QRGenerateRequest,
    user: CurrentUser,
    service: MemorialServiceDep,
):
    from app.core.config import settings
    from app.infrastructure.models.memorial import QRCode

    memorial = await service.get_owned(user.id, memorial_id)
    target_url = f"{settings.PUBLIC_BASE_URL}/m/{memorial.public_slug}"

    qr_service = get_qr_service()
    storage_key, _ = qr_service.generate_and_store(
        memorial_slug=memorial.public_slug, url=target_url, fmt=data.format.value
    )
    qr = QRCode(
        memorial_id=memorial.id,
        target_url=target_url,
        format=data.format,
        storage_key=storage_key,
        label=data.label,
    )
    service.memorials.session.add(qr)
    await service.memorials.session.flush()
    return _qr_out(qr)
