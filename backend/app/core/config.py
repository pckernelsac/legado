"""
Configuración central de la aplicación.

Carga y valida todas las variables de entorno con Pydantic v2 Settings.
Es la única fuente de verdad para la configuración del backend.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- General ------------------------------------------------------------
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    PROJECT_NAME: str = "Legado Eterno"
    DOMAIN: str = "legadoeterno.com"
    PUBLIC_BASE_URL: str = "http://localhost:5173"
    API_BASE_URL: str = "http://localhost:8000/api"
    TZ: str = "UTC"
    LOG_LEVEL: str = "INFO"
    WORKERS: int = 4

    # --- Seguridad / JWT ----------------------------------------------------
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    JWT_ISSUER: str = "legadoeterno"
    JWT_AUDIENCE: str = "legadoeterno-app"
    CSRF_SECRET: str = "change-me-csrf-secret"

    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"

    # --- Políticas de seguridad --------------------------------------------
    RATE_LIMIT_LOGIN: str = "5/minute"
    RATE_LIMIT_DEFAULT: str = "120/minute"
    # Escrituras anónimas del público (anti-spam / anti-abuso de almacenamiento).
    # Por IP. El sublímite de foto es más estricto porque cada subida persiste
    # un objeto en MinIO.
    RATE_LIMIT_CONDOLENCE: int = 5
    RATE_LIMIT_CONDOLENCE_WINDOW: int = 600  # 10 min
    RATE_LIMIT_CONDOLENCE_PHOTO: int = 3
    RATE_LIMIT_CONDOLENCE_PHOTO_WINDOW: int = 3600  # 1 hora
    RATE_LIMIT_CANDLE: int = 10
    RATE_LIMIT_CANDLE_WINDOW: int = 600  # 10 min
    ACCOUNT_LOCKOUT_THRESHOLD: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 15
    PASSWORD_MIN_LENGTH: int = 12
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    # --- PostgreSQL ---------------------------------------------------------
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "legadoeterno"
    POSTGRES_USER: str = "legado"
    POSTGRES_PASSWORD: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # --- Redis --------------------------------------------------------------
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    CELERY_BROKER_DB: int = 1
    CELERY_RESULT_DB: int = 2

    # --- MinIO --------------------------------------------------------------
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_PUBLIC_ENDPOINT: str = "http://localhost:9000"
    MINIO_ROOT_USER: str = "legado-minio-admin"
    MINIO_ROOT_PASSWORD: str = ""
    MINIO_BUCKET_MEDIA: str = "memorial-media"
    MINIO_BUCKET_QR: str = "qr-codes"
    MINIO_SECURE: bool = False
    MINIO_REGION: str = "us-east-1"

    # --- Email --------------------------------------------------------------
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "no-reply@legadoeterno.com"
    SMTP_FROM_NAME: str = "Legado Eterno"
    SMTP_TLS: bool = True

    # --- Integraciones futuras ---------------------------------------------
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    MERCADOPAGO_ACCESS_TOKEN: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # ------------------------------------------------------------------------
    @field_validator("SECRET_KEY")
    @classmethod
    def _validate_secret(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY debe tener al menos 32 caracteres.")
        return v

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        """DSN async (asyncpg) para la aplicación."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url_sync(self) -> str:
        """DSN sync (psycopg2) para Alembic."""
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def redis_url(self) -> str:
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def celery_broker_url(self) -> str:
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.CELERY_BROKER_DB}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def celery_result_url(self) -> str:
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.CELERY_RESULT_DB}"


@lru_cache
def get_settings() -> Settings:
    """Singleton de configuración (cacheado)."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
