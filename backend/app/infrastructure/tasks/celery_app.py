"""
Aplicación Celery para trabajos en segundo plano.

Tareas previstas: procesamiento de imágenes (thumbnails/optimización), escaneo
antivirus de archivos subidos, envío de emails, generación de QR pesados,
expiración de velas temporales y materialización de métricas.
"""
from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "legadoeterno",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_url,
    include=["app.infrastructure.tasks.jobs"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=200,
    task_acks_late=True,
)

# Tareas periódicas (celery beat).
celery_app.conf.beat_schedule = {
    "expire-temporary-candles": {
        "task": "app.infrastructure.tasks.jobs.expire_temporary_candles",
        "schedule": crontab(minute="*/30"),
    },
    "rebuild-memorial-metrics": {
        "task": "app.infrastructure.tasks.jobs.rebuild_memorial_metrics",
        "schedule": crontab(minute=0),  # cada hora
    },
}

# Importa las tareas para registrarlas.
celery_app.autodiscover_tasks(["app.infrastructure.tasks"])
