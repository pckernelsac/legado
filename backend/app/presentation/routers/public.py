"""Endpoints públicos del memorial: vista, condolencias y velas (sin auth)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

from app.application.schemas.memorial import (
    CandleCountryOut,
    CandleCreate,
    CandleOut,
    CondolenceCreate,
    CondolenceOut,
    FamilyMemberOut,
    MediaOut,
    MemorialPublicOut,
    TimelinePublicOut,
)
from app.core.config import settings
from app.presentation.dependencies import (
    Cache,
    MemorialServiceDep,
    enforce_rate_limit,
    get_client_ip,
)

router = APIRouter(prefix="/public/memorials", tags=["public"])


@router.get("/{slug}", response_model=MemorialPublicOut)
async def view_memorial(slug: str, service: MemorialServiceDep):
    return await service.get_public(slug)


@router.get("/{slug}/media", response_model=list[MediaOut])
async def list_public_media(slug: str, service: MemorialServiceDep):
    return await service.list_public_media(slug)


@router.get("/{slug}/timeline", response_model=list[TimelinePublicOut])
async def list_public_timeline(slug: str, service: MemorialServiceDep):
    return await service.list_public_timeline(slug)


@router.get("/{slug}/candles/by-country", response_model=list[CandleCountryOut])
async def candles_by_country(slug: str, service: MemorialServiceDep):
    return await service.candles_by_country(slug)


@router.get("/{slug}/family", response_model=list[FamilyMemberOut])
async def list_public_family(slug: str, service: MemorialServiceDep):
    return await service.list_family_public(slug)


@router.get("/{slug}/condolences", response_model=list[CondolenceOut])
async def list_condolences(
    slug: str,
    service: MemorialServiceDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return await service.list_condolences(slug, limit=limit, offset=offset)


@router.post(
    "/{slug}/condolences",
    response_model=CondolenceOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_condolence(
    slug: str,
    service: MemorialServiceDep,
    cache: Cache,
    ip: Annotated[str | None, Depends(get_client_ip)],
    author_name: Annotated[str, Form(min_length=2, max_length=150)],
    message: Annotated[str, Form(min_length=2, max_length=2000)],
    author_email: Annotated[str | None, Form(max_length=255)] = None,
    signature: Annotated[str | None, Form(max_length=200)] = None,
    photo: Annotated[UploadFile | None, File()] = None,
):
    """Multipart: campos de texto + foto opcional que el visitante adjunta."""
    # Anti-spam de escrituras anónimas (por IP). Se evalúa antes de leer/validar
    # la foto, de modo que un abusador no llegue a escribir en MinIO.
    await enforce_rate_limit(
        ip=ip,
        scope="condolence",
        limit=settings.RATE_LIMIT_CONDOLENCE,
        window=settings.RATE_LIMIT_CONDOLENCE_WINDOW,
        cache=cache,
    )

    photo_bytes: bytes | None = None
    photo_content_type: str | None = None
    if photo is not None and photo.filename:
        # Sublímite más estricto para subidas: cada foto persiste un objeto.
        await enforce_rate_limit(
            ip=ip,
            scope="condolence_photo",
            limit=settings.RATE_LIMIT_CONDOLENCE_PHOTO,
            window=settings.RATE_LIMIT_CONDOLENCE_PHOTO_WINDOW,
            cache=cache,
        )
        photo_bytes = await photo.read() or None
        photo_content_type = photo.content_type

    data = CondolenceCreate(
        author_name=author_name,
        message=message,
        author_email=author_email or None,
        signature=signature or None,
    )
    return await service.add_condolence(
        slug,
        data,
        ip=ip,
        photo_bytes=photo_bytes,
        photo_content_type=photo_content_type,
    )


@router.post("/{slug}/candles", response_model=CandleOut, status_code=status.HTTP_201_CREATED)
async def light_candle(
    slug: str,
    data: CandleCreate,
    service: MemorialServiceDep,
    cache: Cache,
    ip: Annotated[str | None, Depends(get_client_ip)],
):
    # Anti-spam de escrituras anónimas (por IP).
    await enforce_rate_limit(
        ip=ip,
        scope="candle",
        limit=settings.RATE_LIMIT_CANDLE,
        window=settings.RATE_LIMIT_CANDLE_WINDOW,
        cache=cache,
    )
    # País/ciudad se resolverían vía GeoIP a partir de la IP (integración futura).
    return await service.light_candle(slug, data, ip=ip, country=None, city=None)
