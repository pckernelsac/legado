# Despliegue en VPS Contabo — Ubuntu 24.04

## 1. Preparación del servidor

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg ufw

# Docker + Compose
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Firewall
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 2. Código y variables

```bash
git clone <repo> /opt/legadoeterno && cd /opt/legadoeterno
cp .env.example .env
# Editar .env: SECRET_KEY, contraseñas de DB/Redis/MinIO, dominio, SMTP.
```

Genera secretos fuertes:

```bash
openssl rand -hex 32   # SECRET_KEY / CSRF_SECRET
openssl rand -base64 24 # contraseñas
```

## 3. TLS (Let's Encrypt)

```bash
sudo apt install -y certbot
sudo certbot certonly --standalone -d legadoeterno.com -d www.legadoeterno.com
sudo cp /etc/letsencrypt/live/legadoeterno.com/fullchain.pem infra/nginx/certs/
sudo cp /etc/letsencrypt/live/legadoeterno.com/privkey.pem   infra/nginx/certs/
```

Renovación automática (cron): `0 3 * * * certbot renew --quiet && docker compose restart nginx`.

## 4. Arranque

```bash
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.cli seed-roles
docker compose exec backend python -m app.cli seed-plans
docker compose exec backend python -m app.cli create-superadmin admin@legadoeterno.com 'Contrasena-Fuerte-12!' 'Administrador'
```

## 5. Verificación

```bash
curl -f https://legadoeterno.com/api/health/ready
docker compose ps
docker compose logs -f backend
```

## 6. Operación

- **Logs**: `docker compose logs -f <servicio>` (rotados a 20 MB × 5).
- **Backups**: programar `infra/scripts/backup.sh` vía cron diario.
- **Escalado**: aumentar `WORKERS` y réplicas de `backend`/`celery-worker`; añadir PgBouncer.
- **Actualización**: `git pull && docker compose up -d --build && docker compose exec backend alembic upgrade head`.
