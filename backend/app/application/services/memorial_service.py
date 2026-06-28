"""Servicio de memoriales: creación, gestión, contenido público y métricas."""
from __future__ import annotations

import io
import uuid
from datetime import date, datetime, timezone

from PIL import Image

from app.application.schemas.memorial import (
    CandleCreate,
    CondolenceAdminOut,
    CondolenceCreate,
    CondolenceOut,
    FamilyMemberCreate,
    FamilyMemberUpdate,
    MemorialCreate,
    MemorialUpdate,
    TimelineEventCreate,
    TimelineEventUpdate,
)
from app.application.schemas.memorial import MediaOut, TimelinePublicOut
from app.core.config import settings
from app.core.identifiers import uuid7
from app.core.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from app.infrastructure.cache.redis_client import CacheService
from app.infrastructure.models.enums import (
    MediaStatus,
    MediaType,
    MemorialStatus,
    ModerationStatus,
)
from app.infrastructure.models.memorial import (
    Condolence,
    FamilyMember,
    Memorial,
    TimelineEvent,
    VirtualCandle,
)
from app.infrastructure.repositories.memorial_repository import (
    CandleRepository,
    CondolenceRepository,
    FamilyRepository,
    MemorialRepository,
    TimelineRepository,
)
from app.infrastructure.storage.minio_client import StorageService

_PUBLIC_CACHE_TTL = 300

# Foto opcional que un visitante adjunta a su condolencia. La entrada es de un
# usuario anónimo y NO confiable: limitamos tipo y tamaño, y verificamos los
# bytes reales con Pillow (no se confía en el Content-Type declarado).
_CONDOLENCE_PHOTO_TYPES = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
_CONDOLENCE_PHOTO_MAX = 8 * 1024 * 1024  # 8 MB


class MemorialService:
    def __init__(
        self,
        memorials: MemorialRepository,
        condolences: CondolenceRepository,
        candles: CandleRepository,
        cache: CacheService,
        storage: StorageService,
        timeline: TimelineRepository,
        family: FamilyRepository,
    ) -> None:
        self.memorials = memorials
        self.condolences = condolences
        self.candles = candles
        self.cache = cache
        self.storage = storage
        self.timeline = timeline
        self.family = family

    # --- CRUD propietario ---------------------------------------------------
    async def create(self, owner_id: uuid.UUID, data: MemorialCreate) -> Memorial:
        memorial = Memorial(owner_id=owner_id, **data.model_dump(exclude_unset=True))
        await self.memorials.add(memorial)
        return memorial

    async def get_owned(self, owner_id: uuid.UUID, memorial_id: uuid.UUID) -> Memorial:
        memorial = await self.memorials.get(memorial_id)
        if memorial is None:
            raise NotFoundError("Memorial no encontrado.")
        if memorial.owner_id != owner_id:
            raise PermissionDeniedError("Este memorial no le pertenece.")
        return memorial

    async def list_owned(
        self, owner_id: uuid.UUID, *, limit: int, offset: int
    ) -> tuple[list[Memorial], int]:
        items = await self.memorials.list_by_owner(owner_id, limit=limit, offset=offset)
        total = await self.memorials.count_by_owner(owner_id)
        return items, total

    async def update(
        self, owner_id: uuid.UUID, memorial_id: uuid.UUID, data: MemorialUpdate
    ) -> Memorial:
        memorial = await self.get_owned(owner_id, memorial_id)
        changes = data.model_dump(exclude_unset=True)

        if changes.get("status") == MemorialStatus.PUBLISHED and memorial.published_at is None:
            memorial.published_at = datetime.now(timezone.utc)

        for field, value in changes.items():
            setattr(memorial, field, value)

        await self.cache.delete(self._public_key(memorial.public_slug))
        return memorial

    async def delete(self, owner_id: uuid.UUID, memorial_id: uuid.UUID) -> None:
        memorial = await self.get_owned(owner_id, memorial_id)
        await self.memorials.soft_delete(memorial)
        await self.cache.delete(self._public_key(memorial.public_slug))

    # --- Vista pública (cacheada) ------------------------------------------
    def _public_key(self, slug: str) -> str:
        return f"memorial:public:{slug}"

    async def get_public(self, slug: str) -> Memorial:
        memorial = await self.memorials.get_by_slug(slug, with_content=True)
        if memorial is None or memorial.status != MemorialStatus.PUBLISHED:
            raise NotFoundError("Memorial no disponible.")
        # Incremento de visitas asíncrono (no bloquea la respuesta de lectura).
        await self.memorials.increment_views(memorial.id)
        return memorial

    async def _published_with_content(self, slug: str) -> Memorial:
        memorial = await self.memorials.get_by_slug(slug, with_content=True)
        if memorial is None or memorial.status != MemorialStatus.PUBLISHED:
            raise NotFoundError("Memorial no disponible.")
        return memorial

    async def list_public_media(self, slug: str) -> list[MediaOut]:
        """Recuerdos públicos: fotos listas, ordenadas por posición."""
        memorial = await self._published_with_content(slug)
        photos = [
            m
            for m in memorial.media
            if not m.is_deleted
            and m.media_type == MediaType.PHOTO
            and m.status != MediaStatus.PENDING
        ]
        photos.sort(key=lambda m: (m.position, m.created_at))
        return [
            MediaOut(
                id=m.id,
                media_type=m.media_type,
                status=m.status,
                url=self.storage.public_media_url(m.storage_key),
                thumbnail_url=(
                    self.storage.public_media_url(m.thumbnail_key)
                    if m.thumbnail_key
                    else None
                ),
                caption=m.caption,
                position=m.position,
                content_type=m.content_type,
                original_filename=m.original_filename,
            )
            for m in photos
        ]

    async def list_public_timeline(self, slug: str) -> list[TimelinePublicOut]:
        """Momentos importantes de la vida, ordenados cronológicamente."""
        memorial = await self._published_with_content(slug)
        events = [e for e in memorial.timeline_events if not e.is_deleted]
        events.sort(
            key=lambda e: (e.position, e.event_date or date.max, e.year or 0)
        )
        return [
            TimelinePublicOut(
                id=e.id,
                year=e.year,
                event_date=e.event_date,
                title=e.title,
                description=e.description,
                image_url=(
                    self.storage.public_media_url(e.image_key) if e.image_key else None
                ),
                position=e.position,
            )
            for e in events
        ]

    async def candles_by_country(self, slug: str) -> list[dict]:
        memorial = await self.memorials.get_by_slug(slug)
        if memorial is None:
            raise NotFoundError("Memorial no encontrado.")
        rows = await self.candles.count_by_country(memorial.id)
        return [
            {"country": c, "country_code": cc, "count": n} for c, cc, n in rows
        ]

    # --- Condolencias -------------------------------------------------------
    def _store_condolence_photo(
        self, slug: str, condolence_id: uuid.UUID, data: bytes, content_type: str | None
    ) -> str:
        """Valida la imagen de un visitante y la sube a MinIO; devuelve su key."""
        ext = _CONDOLENCE_PHOTO_TYPES.get(content_type or "")
        if ext is None:
            raise ValidationError(
                "Formato de imagen no permitido. Usa JPG, PNG o WebP."
            )
        if len(data) > _CONDOLENCE_PHOTO_MAX:
            raise ValidationError("La imagen supera el tamaño máximo (8 MB).")
        try:
            # verify() comprueba la integridad/firma del archivo sin decodificarlo
            # entero; descarta ejecutables o cargas disfrazadas de imagen.
            Image.open(io.BytesIO(data)).verify()
        except Exception as exc:  # noqa: BLE001
            raise ValidationError("El archivo no es una imagen válida.") from exc

        key = f"{slug}/condolences/{condolence_id}.{ext}"
        self.storage.put_object(key, data, content_type)
        return key

    def _condolence_out(self, c: Condolence) -> CondolenceOut:
        return CondolenceOut(
            id=c.id,
            author_name=c.author_name,
            message=c.message,
            signature=c.signature,
            photo_url=self.storage.public_media_url(c.photo_key) if c.photo_key else None,
            created_at=c.created_at,
        )

    def _condolence_admin_out(self, c: Condolence) -> CondolenceAdminOut:
        return CondolenceAdminOut(
            id=c.id,
            author_name=c.author_name,
            author_email=c.author_email,
            message=c.message,
            signature=c.signature,
            photo_url=self.storage.public_media_url(c.photo_key) if c.photo_key else None,
            moderation_status=c.moderation_status,
            created_at=c.created_at,
        )

    async def add_condolence(
        self,
        slug: str,
        data: CondolenceCreate,
        *,
        ip: str | None,
        photo_bytes: bytes | None = None,
        photo_content_type: str | None = None,
    ) -> CondolenceOut:
        memorial = await self.memorials.get_by_slug(slug)
        if memorial is None or not memorial.allow_condolences:
            raise NotFoundError("No se admiten condolencias en este memorial.")

        status = (
            ModerationStatus.AUTO_APPROVED
            if memorial.auto_moderate
            else ModerationStatus.PENDING
        )
        # Generamos el id por adelantado para nombrar el objeto en MinIO. La foto
        # se sube antes de insertar la fila; si el insert fallara, sólo quedaría un
        # objeto huérfano (sin referencia ni visibilidad), nunca un estado roto.
        condolence_id = uuid7()
        photo_key = (
            self._store_condolence_photo(
                memorial.public_slug, condolence_id, photo_bytes, photo_content_type
            )
            if photo_bytes
            else None
        )
        condolence = Condolence(
            id=condolence_id,
            memorial_id=memorial.id,
            author_name=data.author_name,
            author_email=data.author_email,
            message=data.message,
            signature=data.signature,
            photo_key=photo_key,
            moderation_status=status,
            ip_address=ip,
        )
        await self.condolences.add(condolence)
        if status != ModerationStatus.PENDING:
            memorial.condolence_count += 1
        await self.cache.delete(self._public_key(slug))
        return self._condolence_out(condolence)

    async def list_condolences(
        self, slug: str, *, limit: int, offset: int
    ) -> list[CondolenceOut]:
        memorial = await self.memorials.get_by_slug(slug)
        if memorial is None:
            raise NotFoundError("Memorial no encontrado.")
        rows = await self.condolences.list_approved(
            memorial.id, limit=limit, offset=offset
        )
        return [self._condolence_out(c) for c in rows]

    # --- Línea de tiempo (gestión del propietario) -------------------------
    async def list_timeline_owned(
        self, owner_id: uuid.UUID, memorial_id: uuid.UUID
    ) -> list[TimelineEvent]:
        await self.get_owned(owner_id, memorial_id)
        return await self.timeline.list_by_memorial(memorial_id)

    async def create_timeline_event(
        self, owner_id: uuid.UUID, memorial_id: uuid.UUID, data: TimelineEventCreate
    ) -> TimelineEvent:
        await self.get_owned(owner_id, memorial_id)
        event = TimelineEvent(memorial_id=memorial_id, **data.model_dump())
        await self.timeline.add(event)
        await self._invalidate_public(memorial_id)
        return event

    async def update_timeline_event(
        self,
        owner_id: uuid.UUID,
        memorial_id: uuid.UUID,
        event_id: uuid.UUID,
        data: TimelineEventUpdate,
    ) -> TimelineEvent:
        await self.get_owned(owner_id, memorial_id)
        event = await self.timeline.get(event_id)
        if event is None or event.memorial_id != memorial_id:
            raise NotFoundError("Evento no encontrado.")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(event, field, value)
        await self.timeline.session.flush()
        await self._invalidate_public(memorial_id)
        return event

    async def delete_timeline_event(
        self, owner_id: uuid.UUID, memorial_id: uuid.UUID, event_id: uuid.UUID
    ) -> None:
        await self.get_owned(owner_id, memorial_id)
        event = await self.timeline.get(event_id)
        if event is None or event.memorial_id != memorial_id:
            raise NotFoundError("Evento no encontrado.")
        await self.timeline.soft_delete(event)
        await self._invalidate_public(memorial_id)

    # --- Árbol genealógico --------------------------------------------------
    async def list_family_owned(
        self, owner_id: uuid.UUID, memorial_id: uuid.UUID
    ) -> list[FamilyMember]:
        await self.get_owned(owner_id, memorial_id)
        return await self.family.list_by_memorial(memorial_id)

    async def list_family_public(self, slug: str) -> list[FamilyMember]:
        memorial = await self._published_with_content(slug)
        return await self.family.list_by_memorial(memorial.id)

    async def create_family_member(
        self, owner_id: uuid.UUID, memorial_id: uuid.UUID, data: FamilyMemberCreate
    ) -> FamilyMember:
        await self.get_owned(owner_id, memorial_id)
        await self._assert_valid_parent(memorial_id, data.parent_member_id)
        member = FamilyMember(memorial_id=memorial_id, **data.model_dump())
        await self.family.add(member)
        await self._invalidate_public(memorial_id)
        return member

    async def update_family_member(
        self,
        owner_id: uuid.UUID,
        memorial_id: uuid.UUID,
        member_id: uuid.UUID,
        data: FamilyMemberUpdate,
    ) -> FamilyMember:
        await self.get_owned(owner_id, memorial_id)
        member = await self.family.get(member_id)
        if member is None or member.memorial_id != memorial_id:
            raise NotFoundError("Familiar no encontrado.")
        changes = data.model_dump(exclude_unset=True)
        if "parent_member_id" in changes:
            if changes["parent_member_id"] == member_id:
                raise ValidationError("Un familiar no puede ser su propio padre.")
            await self._assert_valid_parent(memorial_id, changes["parent_member_id"])
        for field, value in changes.items():
            setattr(member, field, value)
        await self.family.session.flush()
        await self._invalidate_public(memorial_id)
        return member

    async def delete_family_member(
        self, owner_id: uuid.UUID, memorial_id: uuid.UUID, member_id: uuid.UUID
    ) -> None:
        await self.get_owned(owner_id, memorial_id)
        member = await self.family.get(member_id)
        if member is None or member.memorial_id != memorial_id:
            raise NotFoundError("Familiar no encontrado.")
        await self.family.soft_delete(member)
        await self._invalidate_public(memorial_id)

    async def _assert_valid_parent(
        self, memorial_id: uuid.UUID, parent_id: uuid.UUID | None
    ) -> None:
        if parent_id is None:
            return
        parent = await self.family.get(parent_id)
        if parent is None or parent.memorial_id != memorial_id:
            raise ValidationError("El familiar padre no pertenece a este memorial.")

    # --- Moderación de condolencias (propietario) --------------------------
    async def list_condolences_owned(
        self, owner_id: uuid.UUID, memorial_id: uuid.UUID, *, limit: int, offset: int
    ) -> list[CondolenceAdminOut]:
        await self.get_owned(owner_id, memorial_id)
        rows = await self.condolences.list_all(memorial_id, limit=limit, offset=offset)
        return [self._condolence_admin_out(c) for c in rows]

    async def moderate_condolence(
        self,
        owner_id: uuid.UUID,
        memorial_id: uuid.UUID,
        condolence_id: uuid.UUID,
        *,
        approve: bool,
    ) -> Condolence:
        memorial = await self.get_owned(owner_id, memorial_id)
        condolence = await self.condolences.get(condolence_id)
        if condolence is None or condolence.memorial_id != memorial_id:
            raise NotFoundError("Condolencia no encontrada.")

        was_visible = condolence.moderation_status in (
            ModerationStatus.APPROVED,
            ModerationStatus.AUTO_APPROVED,
        )
        new_status = ModerationStatus.APPROVED if approve else ModerationStatus.REJECTED
        condolence.moderation_status = new_status
        condolence.moderated_by = owner_id
        condolence.moderated_at = datetime.now(timezone.utc)

        # No se retiene contenido rechazado: borramos la foto del visitante de MinIO
        # y soltamos la referencia (best-effort; un fallo de borrado no bloquea).
        if new_status == ModerationStatus.REJECTED and condolence.photo_key:
            try:
                self.storage.delete_object(condolence.photo_key)
            except Exception:  # noqa: BLE001
                pass
            condolence.photo_key = None

        # Mantiene el contador desnormalizado de mensajes visibles.
        now_visible = new_status == ModerationStatus.APPROVED
        if now_visible and not was_visible:
            memorial.condolence_count += 1
        elif not now_visible and was_visible:
            memorial.condolence_count = max(0, memorial.condolence_count - 1)

        await self.condolences.session.flush()
        await self._invalidate_public(memorial.public_slug)
        return condolence

    async def _invalidate_public(self, memorial_or_slug: uuid.UUID | str) -> None:
        slug = memorial_or_slug
        if isinstance(memorial_or_slug, uuid.UUID):
            memorial = await self.memorials.get(memorial_or_slug)
            if memorial is None:
                return
            slug = memorial.public_slug
        await self.cache.delete(self._public_key(slug))

    # --- Velas virtuales ----------------------------------------------------
    async def light_candle(
        self, slug: str, data: CandleCreate, *, ip: str | None, country: str | None,
        city: str | None,
    ) -> VirtualCandle:
        memorial = await self.memorials.get_by_slug(slug)
        if memorial is None:
            raise NotFoundError("Memorial no encontrado.")
        candle = VirtualCandle(
            memorial_id=memorial.id,
            lit_by_name=data.lit_by_name,
            message=data.message,
            ip_address=ip,
            country=country,
            city=city,
        )
        await self.candles.add(candle)
        memorial.candle_count += 1
        await self.cache.delete(self._public_key(slug))

        # Geolocaliza la vela en segundo plano (no bloquea la respuesta).
        if country is None and ip:
            try:
                from app.infrastructure.tasks.jobs import resolve_candle_geo

                resolve_candle_geo.delay(str(candle.id), ip)
            except Exception:  # noqa: BLE001 - si el broker no está, no bloquea
                pass

        return candle
