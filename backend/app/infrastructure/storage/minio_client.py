"""
Cliente de almacenamiento de objetos (MinIO / S3 compatible) vía boto3.

Genera URLs prefirmadas para subida/descarga directa, evitando que el archivo
pase por el backend (descarga la carga del servidor de aplicación).

IMPORTANTE — firma de URLs prefirmadas detrás de Docker:
Las URLs prefirmadas incluyen el host en la firma. El backend se conecta a MinIO
por la red interna (`minio:9000`), pero el navegador del usuario debe acceder por
el endpoint público (`localhost:9000` en dev, `cdn.legadoeterno.com` en prod).
Por eso usamos DOS clientes: uno interno para operaciones servidor-a-servidor
(put/get/delete) y otro que firma con el endpoint público para el navegador.
"""
from __future__ import annotations

import boto3
from botocore.client import Config

from app.core.config import settings

_S3_CONFIG = Config(signature_version="s3v4", s3={"addressing_style": "path"})


def _normalize_endpoint(endpoint: str, secure: bool) -> str:
    """Asegura que el endpoint tenga esquema http/https."""
    if endpoint.startswith(("http://", "https://")):
        return endpoint
    scheme = "https" if secure else "http"
    return f"{scheme}://{endpoint}"


def _build_client(endpoint: str):
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=settings.MINIO_ROOT_USER,
        aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
        region_name=settings.MINIO_REGION,
        config=_S3_CONFIG,
    )


class StorageService:
    def __init__(self) -> None:
        internal = _normalize_endpoint(settings.MINIO_ENDPOINT, settings.MINIO_SECURE)
        public = _normalize_endpoint(settings.MINIO_PUBLIC_ENDPOINT, settings.MINIO_SECURE)

        # Cliente interno: operaciones servidor-a-servidor.
        self.client = _build_client(internal)
        # Cliente público: firma de URLs prefirmadas accesibles desde el navegador.
        self._presign_client = _build_client(public)

        self.media_bucket = settings.MINIO_BUCKET_MEDIA
        self.qr_bucket = settings.MINIO_BUCKET_QR

    # --- URLs prefirmadas (consumidas por el navegador) --------------------
    def presigned_upload_url(
        self, key: str, content_type: str, *, bucket: str | None = None, expires: int = 900
    ) -> str:
        return self._presign_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket or self.media_bucket,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=expires,
        )

    def presigned_download_url(
        self, key: str, *, bucket: str | None = None, expires: int = 3600
    ) -> str:
        return self._presign_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket or self.media_bucket, "Key": key},
            ExpiresIn=expires,
        )

    # --- Operaciones servidor-a-servidor -----------------------------------
    def put_object(
        self, key: str, data: bytes, content_type: str, *, bucket: str | None = None
    ) -> None:
        self.client.put_object(
            Bucket=bucket or self.media_bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )

    def object_exists(self, key: str, *, bucket: str | None = None) -> bool:
        try:
            self.client.head_object(Bucket=bucket or self.media_bucket, Key=key)
            return True
        except Exception:  # noqa: BLE001
            return False

    def delete_object(self, key: str, *, bucket: str | None = None) -> None:
        self.client.delete_object(Bucket=bucket or self.media_bucket, Key=key)

    def public_url(self, key: str, *, bucket: str | None = None) -> str:
        b = bucket or self.qr_bucket
        base = _normalize_endpoint(settings.MINIO_PUBLIC_ENDPOINT, settings.MINIO_SECURE)
        return f"{base}/{b}/{key}"

    def public_media_url(self, key: str) -> str:
        """URL pública permanente de un objeto del bucket de media (lectura anónima)."""
        return self.public_url(key, bucket=self.media_bucket)


_storage: StorageService | None = None


def get_storage() -> StorageService:
    global _storage
    if _storage is None:
        _storage = StorageService()
    return _storage
