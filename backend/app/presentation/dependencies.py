"""
Inyección de dependencias de FastAPI: sesión DB, cache, servicios, usuario
autenticado y guards de roles/permisos.
"""
from __future__ import annotations

import time
import uuid
from typing import Annotated

import jwt
from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.admin_service import AdminService
from app.application.services.auth_service import AuthService
from app.application.services.billing_service import BillingService
from app.application.services.media_service import MediaService
from app.application.services.memorial_service import MemorialService
from app.core.exceptions import (
    AuthenticationError,
    PermissionDeniedError,
    RateLimitError,
)
from app.core.security import ACCESS_TOKEN, decode_token
from app.infrastructure.cache.redis_client import CacheService, get_redis
from app.infrastructure.database.session import get_db_session
from app.infrastructure.models.enums import RoleName
from app.infrastructure.models.user import User
from app.infrastructure.repositories.billing_repository import (
    PlanRepository,
    SubscriptionRepository,
)
from app.infrastructure.repositories.memorial_repository import (
    CandleRepository,
    CondolenceRepository,
    FamilyRepository,
    MediaRepository,
    MemorialRepository,
    TimelineRepository,
)
from app.infrastructure.storage.minio_client import get_storage
from app.infrastructure.repositories.user_repository import (
    RoleRepository,
    SessionRepository,
    UserRepository,
)

_bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_cache() -> CacheService:
    return CacheService(get_redis())


Cache = Annotated[CacheService, Depends(get_cache)]


# --- Factories de servicios -------------------------------------------------
def get_auth_service(db: DbSession, cache: Cache) -> AuthService:
    return AuthService(
        users=UserRepository(db),
        roles=RoleRepository(db),
        sessions=SessionRepository(db),
        cache=cache,
    )


def get_memorial_service(db: DbSession, cache: Cache) -> MemorialService:
    return MemorialService(
        memorials=MemorialRepository(db),
        condolences=CondolenceRepository(db),
        candles=CandleRepository(db),
        cache=cache,
        storage=get_storage(),
        timeline=TimelineRepository(db),
        family=FamilyRepository(db),
    )


def get_media_service(db: DbSession) -> MediaService:
    return MediaService(
        memorials=MemorialRepository(db),
        media=MediaRepository(db),
        storage=get_storage(),
    )


def get_billing_service(db: DbSession) -> BillingService:
    return BillingService(
        plans=PlanRepository(db),
        subscriptions=SubscriptionRepository(db),
        memorials=MemorialRepository(db),
        media=MediaRepository(db),
    )


def get_admin_service(db: DbSession) -> AdminService:
    return AdminService(db)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
MemorialServiceDep = Annotated[MemorialService, Depends(get_memorial_service)]
MediaServiceDep = Annotated[MediaService, Depends(get_media_service)]
BillingServiceDep = Annotated[BillingService, Depends(get_billing_service)]
AdminServiceDep = Annotated[AdminService, Depends(get_admin_service)]


# --- Usuario autenticado ----------------------------------------------------
async def get_current_user(
    db: DbSession,
    cache: Cache,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    if credentials is None:
        raise AuthenticationError("No autenticado.")
    try:
        payload = decode_token(credentials.credentials, expected_type=ACCESS_TOKEN)
    except jwt.PyJWTError as exc:
        raise AuthenticationError("Token inválido o expirado.") from exc

    if await cache.is_jti_revoked(payload["jti"]):
        raise AuthenticationError("Token revocado.")

    users = UserRepository(db)
    user = await users.get_with_role(uuid.UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise AuthenticationError("Usuario no disponible.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: RoleName):
    """Guard de autorización por rol."""

    allowed = {r.value for r in roles}

    async def _guard(user: CurrentUser) -> User:
        if user.role.name not in allowed:
            raise PermissionDeniedError()
        return user

    return _guard


RequireAdmin = Annotated[
    User, Depends(require_roles(RoleName.SUPER_ADMIN, RoleName.ADMIN))
]


# --- Metadatos de la request ------------------------------------------------
def get_client_ip(request: Request) -> str | None:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else None


def get_user_agent(user_agent: Annotated[str | None, Header()] = None) -> str | None:
    return user_agent


# --- Rate limiting de escrituras anónimas -----------------------------------
async def enforce_rate_limit(
    *, ip: str | None, scope: str, limit: int, window: int, cache: CacheService
) -> None:
    """
    Límite por IP con ventana fija en Redis, independiente del rate-limit global
    del middleware. Si Redis no responde, deja pasar (fail-open) para no convertir
    una caída del cache en una caída del servicio.
    """
    bucket = ip or "unknown"
    key = f"ratelimit:{scope}:{bucket}:{int(time.time()) // window}"
    try:
        count = await cache.incr_with_ttl(key, window)
    except Exception:  # noqa: BLE001
        return
    if count > limit:
        raise RateLimitError(retry_after=window)
