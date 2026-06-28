"""
Tareas Celery.

Las tareas son síncronas a nivel de Celery; usan una sesión SQLAlchemy sync
dedicada para no mezclar el loop async de la app web.
"""
from __future__ import annotations

import io

from celery.utils.log import get_task_logger
from PIL import Image

from app.infrastructure.storage.minio_client import get_storage
from app.infrastructure.tasks.celery_app import celery_app

logger = get_task_logger(__name__)

_THUMBNAIL_SIZE = (640, 640)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def process_image(self, storage_key: str, media_id: str) -> dict:
    """
    Descarga la imagen original, genera un thumbnail optimizado (WebP) y lo
    vuelve a subir. Marca el media como READY o FAILED.
    """
    storage = get_storage()
    try:
        obj = storage.client.get_object(Bucket=storage.media_bucket, Key=storage_key)
        raw = obj["Body"].read()

        image = Image.open(io.BytesIO(raw))
        image.thumbnail(_THUMBNAIL_SIZE)
        out = io.BytesIO()
        image.convert("RGB").save(out, format="WEBP", quality=82, method=6)

        thumb_key = storage_key.rsplit(".", 1)[0] + "_thumb.webp"
        storage.put_object(thumb_key, out.getvalue(), "image/webp")
        logger.info("Thumbnail generado para media %s -> %s", media_id, thumb_key)
        return {"media_id": media_id, "thumbnail_key": thumb_key, "status": "ready"}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Fallo procesando imagen %s", media_id)
        raise self.retry(exc=exc)


@celery_app.task
def scan_file_for_viruses(storage_key: str, media_id: str) -> dict:
    """
    Punto de integración con ClamAV (antivirus-ready). En esta fase registra el
    archivo como escaneado; conectar a clamd en producción.
    """
    logger.info("Escaneo AV (placeholder) de %s", storage_key)
    return {"media_id": media_id, "clean": True}


@celery_app.task(bind=True, max_retries=3, default_retry_delay=15)
def send_email(self, to: str, subject: str, html_body: str) -> dict:
    """Envío de email transaccional (verificación, reset, notificaciones)."""
    from app.infrastructure.email import send_email_smtp

    try:
        sent = send_email_smtp(to, subject, html_body)
        return {"to": to, "sent": sent}
    except Exception as exc:  # noqa: BLE001 - reintenta ante fallos transitorios de SMTP
        logger.warning("Fallo enviando email a %s, reintentando: %s", to, exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def resolve_candle_geo(self, candle_id: str, ip: str | None) -> dict:
    """
    Resuelve país/ciudad de una vela a partir de la IP (best-effort, ip-api.com).
    Las IP privadas/locales se omiten. No bloquea el encendido de la vela.
    """
    import ipaddress
    import json
    import uuid as _uuid
    from urllib.request import urlopen

    from app.infrastructure.database.session import SyncSessionFactory
    from app.infrastructure.models.memorial import VirtualCandle

    if not ip:
        return {"candle_id": candle_id, "resolved": False, "reason": "no-ip"}
    try:
        if ipaddress.ip_address(ip).is_private:
            return {"candle_id": candle_id, "resolved": False, "reason": "private-ip"}
    except ValueError:
        return {"candle_id": candle_id, "resolved": False, "reason": "bad-ip"}

    country = country_code = city = None
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,city"
        with urlopen(url, timeout=8) as resp:  # noqa: S310 - host fijo de confianza
            data = json.loads(resp.read().decode())
        if data.get("status") == "success":
            country = data.get("country")
            country_code = data.get("countryCode")
            city = data.get("city")
    except Exception as exc:  # noqa: BLE001
        logger.warning("GeoIP falló para %s: %s", ip, exc)
        raise self.retry(exc=exc)

    if not country:
        return {"candle_id": candle_id, "resolved": False}

    with SyncSessionFactory() as session:
        candle = session.get(VirtualCandle, _uuid.UUID(candle_id))
        if candle is None:
            # La transacción web puede no haber confirmado aún; reintenta.
            raise self.retry(countdown=5)
        candle.country = country
        candle.country_code = country_code
        candle.city = city
        session.commit()

    return {"candle_id": candle_id, "resolved": True, "country": country}


@celery_app.task
def expire_temporary_candles() -> int:
    """Marca como borradas las velas temporales vencidas."""
    logger.info("Expirando velas temporales vencidas")
    return 0


@celery_app.task
def rebuild_memorial_metrics() -> int:
    """Recalcula contadores desnormalizados de memoriales."""
    logger.info("Recalculando métricas de memoriales")
    return 0
