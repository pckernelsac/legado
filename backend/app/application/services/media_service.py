"""
Servicio de multimedia: subida directa a MinIO mediante URLs prefirmadas.

Flujo:
  1. `init_upload`  → crea el registro (status=pending) y devuelve una URL PUT
                      prefirmada. El navegador sube el archivo directo a MinIO.
  2. `confirm_upload` → verifica que el objeto exista, marca READY y encola el
                      procesamiento (thumbnail / escaneo AV) en Celery.
  3. `list_media`   → devuelve los items con URLs GET prefirmadas.
"""
from __future__ import annotations

import uuid

from app.application.schemas.memorial import (
    MediaOut,
    MediaUpdate,
    MediaUploadInit,
    MediaUploadResponse,
)
from app.core.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from app.infrastructure.models.enums import MediaStatus, MediaType
from app.infrastructure.models.memorial import Memorial, MemorialMedia
from app.infrastructure.repositories.memorial_repository import (
    MediaRepository,
    MemorialRepository,
)
from app.infrastructure.storage.minio_client import StorageService

_PRESIGN_EXPIRES = 900  # 15 min (solo para la subida)

# Tipos permitidos por categoría y tamaños máximos.
_ALLOWED = {
    MediaType.PHOTO: ({"image/jpeg", "image/png", "image/webp", "image/avif"}, 25 * 1024 * 1024),
    MediaType.VIDEO: ({"video/mp4", "video/webm", "video/quicktime"}, 200 * 1024 * 1024),
    MediaType.AUDIO: ({"audio/mpeg", "audio/mp4", "audio/wav", "audio/ogg"}, 50 * 1024 * 1024),
}

_EXT = {
    "image/jpeg": "jpg", "image/png": "png", "image/webp": "webp", "image/avif": "avif",
    "video/mp4": "mp4", "video/webm": "webm", "video/quicktime": "mov",
    "audio/mpeg": "mp3", "audio/mp4": "m4a", "audio/wav": "wav", "audio/ogg": "ogg",
}


class MediaService:
    def __init__(
        self,
        memorials: MemorialRepository,
        media: MediaRepository,
        storage: StorageService,
    ) -> None:
        self.memorials = memorials
        self.media = media
        self.storage = storage

    async def _owned_memorial(self, owner_id: uuid.UUID, memorial_id: uuid.UUID) -> Memorial:
        memorial = await self.memorials.get(memorial_id)
        if memorial is None:
            raise NotFoundError("Memorial no encontrado.")
        if memorial.owner_id != owner_id:
            raise PermissionDeniedError("Este memorial no le pertenece.")
        return memorial

    # --- Paso 1: iniciar subida --------------------------------------------
    async def init_upload(
        self, owner_id: uuid.UUID, memorial_id: uuid.UUID, data: MediaUploadInit
    ) -> MediaUploadResponse:
        memorial = await self._owned_memorial(owner_id, memorial_id)

        allowed_types, max_size = _ALLOWED[data.media_type]
        if data.content_type not in allowed_types:
            raise ValidationError(
                f"Tipo de archivo no permitido para {data.media_type.value}: {data.content_type}"
            )
        if data.file_size > max_size:
            raise ValidationError(
                f"El archivo supera el tamaño máximo ({max_size // (1024 * 1024)} MB)."
            )

        media_id = uuid.uuid4()
        ext = _EXT.get(data.content_type, "bin")
        storage_key = f"{memorial.public_slug}/media/{media_id}.{ext}"

        record = MemorialMedia(
            id=media_id,
            memorial_id=memorial.id,
            media_type=data.media_type,
            status=MediaStatus.PENDING,
            storage_key=storage_key,
            original_filename=data.original_filename,
            content_type=data.content_type,
            file_size=data.file_size,
        )
        await self.media.add(record)

        upload_url = self.storage.presigned_upload_url(
            storage_key, data.content_type, expires=_PRESIGN_EXPIRES
        )
        return MediaUploadResponse(
            media_id=media_id,
            upload_url=upload_url,
            storage_key=storage_key,
            expires_in=_PRESIGN_EXPIRES,
        )

    # --- Paso 2: confirmar subida ------------------------------------------
    async def confirm_upload(
        self, owner_id: uuid.UUID, memorial_id: uuid.UUID, media_id: uuid.UUID
    ) -> MediaOut:
        memorial = await self._owned_memorial(owner_id, memorial_id)
        record = await self.media.get(media_id)
        if record is None or record.memorial_id != memorial_id:
            raise NotFoundError("Archivo no encontrado.")

        if not self.storage.object_exists(record.storage_key):
            raise ValidationError("El archivo no se encuentra en el almacenamiento.")

        # Las imágenes son utilizables de inmediato; el thumbnail se genera async.
        record.status = MediaStatus.READY

        # UX: la primera foto subida se usa como principal y portada por defecto.
        if record.media_type == MediaType.PHOTO:
            public_url = self.storage.public_media_url(record.storage_key)
            if not memorial.main_photo_url:
                memorial.main_photo_url = public_url
            if not memorial.cover_photo_url:
                memorial.cover_photo_url = public_url
            self._enqueue_processing(record)

        await self.media.session.flush()
        return self._to_out(record)

    def _enqueue_processing(self, record: MemorialMedia) -> None:
        """Encola thumbnail + escaneo AV en Celery (best-effort)."""
        try:
            from app.infrastructure.tasks.jobs import process_image, scan_file_for_viruses

            process_image.delay(record.storage_key, str(record.id))
            scan_file_for_viruses.delay(record.storage_key, str(record.id))
        except Exception:  # noqa: BLE001 - si el broker no está, no bloquea la subida
            pass

    # --- Listado ------------------------------------------------------------
    async def list_media(
        self, owner_id: uuid.UUID, memorial_id: uuid.UUID
    ) -> list[MediaOut]:
        await self._owned_memorial(owner_id, memorial_id)
        items = await self.media.list_by_memorial(memorial_id)
        return [self._to_out(m) for m in items]

    async def update_media(
        self, owner_id: uuid.UUID, memorial_id: uuid.UUID, media_id: uuid.UUID,
        data: MediaUpdate,
    ) -> MediaOut:
        await self._owned_memorial(owner_id, memorial_id)
        record = await self.media.get(media_id)
        if record is None or record.memorial_id != memorial_id:
            raise NotFoundError("Archivo no encontrado.")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(record, field, value)
        await self.media.session.flush()
        return self._to_out(record)

    async def delete_media(
        self, owner_id: uuid.UUID, memorial_id: uuid.UUID, media_id: uuid.UUID
    ) -> None:
        memorial = await self._owned_memorial(owner_id, memorial_id)
        record = await self.media.get(media_id)
        if record is None or record.memorial_id != memorial_id:
            raise NotFoundError("Archivo no encontrado.")

        deleted_url = self.storage.public_media_url(record.storage_key)
        await self.media.soft_delete(record)

        # Si la foto borrada era la principal o la portada, el memorial quedaría
        # apuntando a un objeto eliminado y la imagen "desaparecería". Limpiamos
        # la referencia y caemos a otra foto restante si existe.
        if deleted_url in (memorial.main_photo_url, memorial.cover_photo_url):
            remaining = [
                m
                for m in await self.media.list_by_memorial(memorial_id)
                if m.media_type == MediaType.PHOTO
            ]
            fallback = (
                self.storage.public_media_url(remaining[0].storage_key)
                if remaining
                else None
            )
            if memorial.main_photo_url == deleted_url:
                memorial.main_photo_url = fallback
            if memorial.cover_photo_url == deleted_url:
                memorial.cover_photo_url = fallback
            await self.media.session.flush()

        try:
            self.storage.delete_object(record.storage_key)
            if record.thumbnail_key:
                self.storage.delete_object(record.thumbnail_key)
        except Exception:  # noqa: BLE001
            pass

    # --- Foto principal / portada ------------------------------------------
    async def _photo_record(
        self, owner_id: uuid.UUID, memorial_id: uuid.UUID, media_id: uuid.UUID
    ) -> tuple[MemorialMedia, "Memorial"]:
        memorial = await self._owned_memorial(owner_id, memorial_id)
        record = await self.media.get(media_id)
        if record is None or record.memorial_id != memorial_id:
            raise NotFoundError("Archivo no encontrado.")
        if record.media_type != MediaType.PHOTO:
            raise ValidationError("Solo una foto puede usarse como imagen destacada.")
        return record, memorial

    async def set_main_photo(
        self, owner_id: uuid.UUID, memorial_id: uuid.UUID, media_id: uuid.UUID
    ) -> None:
        record, memorial = await self._photo_record(owner_id, memorial_id, media_id)
        memorial.main_photo_url = self.storage.public_media_url(record.storage_key)
        await self.media.session.flush()

    async def set_cover_photo(
        self, owner_id: uuid.UUID, memorial_id: uuid.UUID, media_id: uuid.UUID
    ) -> None:
        record, memorial = await self._photo_record(owner_id, memorial_id, media_id)
        memorial.cover_photo_url = self.storage.public_media_url(record.storage_key)
        await self.media.session.flush()

    # --- Mapeo a DTO con URLs públicas permanentes -------------------------
    def _to_out(self, record: MemorialMedia) -> MediaOut:
        url = self.storage.public_media_url(record.storage_key)
        thumb = (
            self.storage.public_media_url(record.thumbnail_key)
            if record.thumbnail_key
            else None
        )
        return MediaOut(
            id=record.id,
            media_type=record.media_type,
            status=record.status,
            url=url,
            thumbnail_url=thumb,
            caption=record.caption,
            position=record.position,
            content_type=record.content_type,
            original_filename=record.original_filename,
        )
