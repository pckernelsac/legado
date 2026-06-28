# Despliegue en Dokploy

Guía para desplegar Legado Eterno en [Dokploy](https://dokploy.com) usando la
base de datos PostgreSQL **gestionada** por Dokploy y el resto del stack
(backend, frontend, Redis, MinIO, Celery, nginx) auto-alojado en un Compose.

## Arquitectura en Dokploy

```
Internet ── Traefik (TLS) ──┬─ nginx:80  ── /api/* ─► backend:8000 (FastAPI)
                            │              ── /     ─► frontend:80 (SPA React)
                            └─ minio:9000  (medios / presigned URLs)

backend / celery ─► postgres GESTIONADA (app-legado-db-8h5dty:5432)  [dokploy-network]
backend / celery ─► redis, minio                                     [legado-internal]
```

- **TLS**: lo termina Traefik (Dokploy). El nginx interno solo habla HTTP en :80
  y conserva el ruteo `/api/* → backend` (quitando el prefijo `/api`).
- **Postgres**: NO está en el Compose; se usa la BD gestionada de Dokploy.
- **Redis y MinIO**: auto-alojados con volúmenes persistentes.

## Pasos

### 1. Base de datos (ya creada)
Tu BD gestionada: `app-legado-db-8h5dty:5432`, base `legado`, usuario `legado_user`.
No necesitas crear nada más; el backend aplica las migraciones Alembic al arrancar.

### 2. Crear el servicio Compose
En Dokploy: **Create → Compose**.
- **Provider**: GitHub → repo `pckernelsac/legado`, rama `main`.
- **Compose Path**: `docker-compose.dokploy.yml`.

### 3. Variables de entorno
Pestaña **Environment** → pega el contenido de `.env.dokploy.example` y rellena
los valores `<<< CAMBIAR >>>` (Postgres password, secretos `openssl rand -hex`,
dominio, SMTP). Localmente tienes `.env.dokploy.local` con todo listo (no se sube
a Git).

> Los secretos deben generarse con `openssl rand -hex 32`. La plantilla del repo
> NO contiene secretos reales.

### 4. Dominios
Pestaña **Domains**:
- Servicio `legado-proxy`, puerto `80` → dominio principal (p.ej. el sslip.io
  generado por Dokploy o tu dominio real). HTTPS/Let's Encrypt activado.
- Servicio `legado-minio`, puerto `9000` → subdominio para medios.
  Este host debe coincidir con `MINIO_PUBLIC_ENDPOINT`.

> ⚠️ Los servicios expuestos usan nombres ÚNICOS (`legado-proxy`, `legado-minio`)
> a propósito: si se llamaran `nginx`/`minio` colisionarían en Traefik con otros
> proyectos del mismo servidor Dokploy y el dominio acabaría sirviendo otra app.

Tras fijar los dominios, actualiza en Environment:
`DOMAIN`, `PUBLIC_BASE_URL`, `API_BASE_URL`, `BACKEND_CORS_ORIGINS`,
`VITE_API_BASE_URL`, `VITE_PUBLIC_BASE_URL` y `MINIO_PUBLIC_ENDPOINT`.

> Importante: `VITE_*` se hornea en el build del frontend. Si cambias el dominio,
> hay que **redeploy** (rebuild) para que el frontend apunte a la URL correcta.

### 5. Deploy
Pulsa **Deploy**. Orden esperado: redis/minio sanos → backend (migra Alembic y
arranca Gunicorn) → frontend (build) → nginx.

### 6. Datos iniciales (automático en cada deploy)
`scripts/start.sh` ejecuta, tras migrar Alembic, `python -m app.cli bootstrap`,
que es **idempotente** y deja todo listo sin intervención manual:
- crea roles/permisos solo si faltan,
- sincroniza los planes (`sync-plans`),
- crea el super admin desde `ADMIN_EMAIL`/`ADMIN_PASSWORD` **solo si no existe**
  (nunca pisa la contraseña de un usuario ya creado).

Por eso basta con definir `ADMIN_EMAIL` y `ADMIN_PASSWORD` en el Environment de
Dokploy (ver `.env.dokploy.example`). Si dejas `ADMIN_PASSWORD` vacío, el paso del
super admin se omite y puedes crearlo a mano:

```bash
python -m app.cli create-superadmin admin@legadoeterno.com 'TU_PASSWORD_FUERTE' 'Admin'
```

Las migraciones (`alembic upgrade head`) y el `bootstrap` corren solos en
`scripts/start.sh`.

### Restablecer contraseña de un usuario (p. ej. super admin)
```bash
python -m app.cli reset-password admin@legadoeterno.com 'NUEVO_PASSWORD'
```

## Verificación
- `https://<dominio>/`            → carga la SPA.
- `https://<dominio>/api/health`  → responde el backend (vía nginx, prefijo strip).
- Subir una foto en un memorial   → confirma MinIO + `MINIO_PUBLIC_ENDPOINT`.

## Notas
- La red `dokploy-network` es **externa**: la crea Dokploy. El backend la usa
  para llegar a la BD gestionada; nginx y minio, para ser publicados por Traefik.
- Si el frontend da 404 contra la API, revisa que `VITE_API_BASE_URL` termine en
  `/api` (en prod el prefijo lo enruta nginx; en dev NO se usa `/api`).
