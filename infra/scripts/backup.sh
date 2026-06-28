#!/usr/bin/env bash
# ============================================================================
# Backup automático: PostgreSQL (dump comprimido) + MinIO (mirror).
# Programar vía cron:  0 3 * * *  /opt/legadoeterno/infra/scripts/backup.sh
# ============================================================================
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/opt/legadoeterno/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
STAMP="$(date +%Y%m%d_%H%M%S)"

source /opt/legadoeterno/.env

mkdir -p "${BACKUP_DIR}/postgres" "${BACKUP_DIR}/minio"

echo "==> Backup de PostgreSQL..."
docker compose -f /opt/legadoeterno/docker-compose.yml exec -T postgres \
    pg_dump -U "${POSTGRES_USER}" "${POSTGRES_DB}" \
    | gzip > "${BACKUP_DIR}/postgres/db_${STAMP}.sql.gz"

echo "==> Backup de MinIO (mirror)..."
docker compose -f /opt/legadoeterno/docker-compose.yml run --rm minio-init \
    sh -c "mc alias set local http://minio:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD} && \
           mc mirror --overwrite local/${MINIO_BUCKET_MEDIA} /backup/${MINIO_BUCKET_MEDIA}" \
    2>/dev/null || echo "   (mirror de MinIO opcional, requiere volumen montado)"

echo "==> Limpiando backups con más de ${RETENTION_DAYS} días..."
find "${BACKUP_DIR}/postgres" -name "db_*.sql.gz" -mtime "+${RETENTION_DAYS}" -delete

echo "==> Backup completado: ${STAMP}"
