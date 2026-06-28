# Seguridad — Legado Eterno (Backend)

## Identificadores
- **UUIDv7** como PK en todas las tablas (`app/core/identifiers.py`). Ordenable temporalmente, sin secuencias correlativas enumerables.
- **`public_slug`** opaco (20 chars, ~10³⁵ combinaciones) para URLs públicas (`/m/{slug}`). El UUID real nunca se expone en la API ni en las URLs.

## Autenticación
- **Argon2id** (OWASP params: time_cost=3, 64 MiB, parallelism=4) con re-hash automático al iniciar sesión.
- **JWT** access (15 min) + refresh (30 días) con `jti`, `iss`, `aud`, `nbf`, `exp` obligatorios.
- **Rotación de refresh tokens**: cada refresh revoca el anterior (`Session.revoked_at`).
- **Denylist de access tokens** en Redis para logout inmediato.
- **MFA-ready** (`User.mfa_enabled` / `mfa_secret`, integrar TOTP con pyotp).

## Protección de cuentas
- **Account lockout** tras `ACCOUNT_LOCKOUT_THRESHOLD` intentos (configurable).
- **Política de contraseñas**: mínimo 12 chars, mayúscula + minúscula + número + símbolo.
- **Verificación de email** y **reset de contraseña** con tokens de un solo uso y expiración.
- **Anti-enumeración**: mensajes genéricos en login y password-reset.

## Capa HTTP
- **Security headers** (`SecurityHeadersMiddleware`) + CSP en Nginx.
- **Rate limiting** doble: Nginx (borde) + Redis (aplicación).
- **CORS** restringido a orígenes configurados.
- **CSRF**: tokens firmados (itsdangerous) para flujos con cookies; la API usa Bearer tokens.
- **SQL injection**: SQLAlchemy parametrizado, sin SQL crudo con interpolación.
- **XSS**: validación Pydantic + escape en frontend + CSP.

## Datos y auditoría
- **Soft delete** universal (`is_deleted`, `deleted_at`).
- **Audit logs** (acciones sensibles, inmutables) y **activity logs** (negocio).
- **Device & session tracking** con IP y user-agent.

## Archivos
- **Validación** de tipo/tamaño en `MediaUploadInit` (máx. 200 MB).
- **Checksums SHA-256** y **antivirus-ready** (tarea Celery `scan_file_for_viruses`, conectar a ClamAV).
- **URLs prefirmadas** de MinIO: el archivo no atraviesa el backend.

## Checklist de producción
- [ ] Rotar `SECRET_KEY`, contraseñas de DB/Redis/MinIO.
- [ ] `COOKIE_SECURE=true`, TLS con certificados válidos.
- [ ] Conectar ClamAV al worker de Celery.
- [ ] Activar `pg_stat_statements` y revisar queries lentas.
- [ ] Configurar backups automáticos (`infra/scripts/backup.sh`).
