# ============================================================================
# Legado Eterno — Backend (FastAPI) — multi-stage build
# ============================================================================

# --- Base con dependencias ---------------------------------------------------
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Desarrollo --------------------------------------------------------------
FROM base AS development
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# --- Producción --------------------------------------------------------------
FROM base AS production

# Usuario sin privilegios
RUN groupadd -r legado && useradd -r -g legado legado

COPY . .
RUN chmod +x /app/scripts/start.sh && chown -R legado:legado /app

USER legado
EXPOSE 8000

# Gunicorn gestionando workers Uvicorn (async)
CMD ["/app/scripts/start.sh"]
