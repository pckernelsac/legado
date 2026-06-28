# Legado Eterno

Plataforma SaaS empresarial de memoriales digitales premium con códigos QR inteligentes.

> Preparada para 100.000 usuarios registrados, 10.000 memoriales, 1M de fotografías y 1.000 usuarios concurrentes.

## Arquitectura

Monorepo con dos servicios principales y stack de infraestructura completo vía Docker Compose.

```
legadoeterno/
├── backend/            # FastAPI + SQLAlchemy 2.0 + Clean Architecture / DDD
├── frontend/           # React 19 + Vite + TypeScript + Tailwind + shadcn/ui
├── infra/              # Nginx, Postgres, Redis, MinIO, scripts de backup
├── docker-compose.yml  # Orquestación de producción
├── docker-compose.dev.yml
└── .env.example
```

### Backend — Clean Architecture / DDD

```
backend/app/
├── domain/          # Entidades, value objects, interfaces de repositorio (sin dependencias externas)
├── application/     # Casos de uso, DTOs, servicios de aplicación (orquestación)
├── infrastructure/  # SQLAlchemy, Redis, MinIO, implementaciones concretas
└── presentation/    # FastAPI routers, schemas, dependencias HTTP
```

Patrones: Repository, Service Layer, Unit of Work, CQRS-ready, Event-Driven-ready, Multi-tenant-ready.

## Stack

| Capa            | Tecnología                                                        |
|-----------------|-------------------------------------------------------------------|
| Frontend        | React 19, TypeScript, Vite, TailwindCSS, shadcn/ui, React Query, React Router, RHF, Zod, Axios, Framer Motion |
| Backend         | FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, JWT, Redis, Celery, Uvicorn, Gunicorn |
| Base de datos   | PostgreSQL 16 (UUIDv7 PK)                                          |
| Cache / Broker  | Redis 7                                                            |
| Almacenamiento  | MinIO (S3 compatible)                                              |
| Infra           | Docker, Docker Compose, Nginx, Ubuntu 24.04 (Contabo VPS)         |

## Arranque rápido (desarrollo)

```bash
cp .env.example .env
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

- Frontend: http://localhost:5173
- API:      http://localhost:8000/docs
- MinIO:    http://localhost:9001
- MailHog:  http://localhost:8025 (captura todos los emails en desarrollo)
- Postgres: localhost:5432

> **Nota dev:** en desarrollo el backend expone sus rutas en la raíz (`/auth`, `/memorials`, …), no bajo `/api`. Por eso `frontend/.env` usa `VITE_API_BASE_URL=http://localhost:8000` (sin `/api`). En producción Nginx enruta `/api/*` → backend, así que ahí sí se usa `.../api`.

## Credenciales de prueba (desarrollo)

Login en http://localhost:5173. Cuentas **super administrador** (acceso al panel `/admin`):

| Email                      | Contraseña            |
|----------------------------|-----------------------|
| `admin@legadoeterno.com`   | `Admin2026!Legado`    |
| `revisor@legadoeterno.com` | `Revisor2026!Legado`  |

> ⚠️ Solo para entorno local. **No** usar en staging/producción.

Si la base de datos está vacía (primer arranque), crea los datos base y el usuario antes de entrar:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend alembic upgrade head
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend python -m app.cli seed-roles
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend python -m app.cli seed-plans
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend \
  python -m app.cli create-superadmin revisor@legadoeterno.com 'Revisor2026!Legado' 'Revisor Demo'
```

La consola de MinIO (http://localhost:9001) usa las credenciales `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` de tu `.env`.

## Producción (VPS Contabo / Ubuntu 24.04)

```bash
cp .env.example .env       # editar secretos reales
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.cli seed-roles
```

Consulta [`infra/DEPLOY.md`](infra/DEPLOY.md) para el procedimiento completo de despliegue, TLS y backups.

### Producción (Dokploy)

Despliegue gestionado con Postgres administrado por Dokploy y el resto del stack en un Compose dedicado:

- Compose: [`docker-compose.dokploy.yml`](docker-compose.dokploy.yml)
- Variables: [`.env.dokploy.example`](.env.dokploy.example)
- Guía paso a paso: [`infra/DOKPLOY.md`](infra/DOKPLOY.md)

## Seguridad

UUIDv7 en todas las PK · slugs públicos opacos · Argon2id · JWT access/refresh con rotación · rate limiting · security headers · audit & activity logs · CSRF · device/session tracking · MFA-ready · account lockout. Detalle en [`backend/SECURITY.md`](backend/SECURITY.md).
