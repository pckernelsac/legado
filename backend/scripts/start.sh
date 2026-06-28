#!/usr/bin/env sh
# ============================================================================
# Arranque de producción: migra la base de datos y lanza Gunicorn + Uvicorn.
# ============================================================================
set -e

echo "==> Aplicando migraciones Alembic..."
alembic upgrade head

echo "==> Bootstrap idempotente (roles, planes, super admin)..."
python -m app.cli bootstrap || echo "WARN: bootstrap falló; continúo el arranque."

echo "==> Lanzando Gunicorn (${WORKERS:-4} workers Uvicorn)..."
exec gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers "${WORKERS:-4}" \
    --bind 0.0.0.0:8000 \
    --timeout 60 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --max-requests 2000 \
    --max-requests-jitter 200 \
    --access-logfile - \
    --error-logfile -
