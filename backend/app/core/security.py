"""
Primitivas de seguridad: hashing de contraseñas (Argon2id) y JWT (access/refresh).

- Argon2id es el ganador del Password Hashing Competition y la recomendación
  OWASP para almacenamiento de contraseñas.
- Los JWT incluyen `jti` (id único) para permitir revocación vía Redis y `type`
  para distinguir access de refresh.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from app.core.config import settings

# Parámetros Argon2id alineados con las recomendaciones OWASP (2024).
_password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=64 * 1024,  # 64 MiB
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


# ---------------------------------------------------------------------------
# Contraseñas
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return _password_hasher.verify(hashed, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def password_needs_rehash(hashed: str) -> bool:
    """True si el hash usa parámetros antiguos y conviene re-hashear al loguear."""
    return _password_hasher.check_needs_rehash(hashed)


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------
ACCESS_TOKEN = "access"
REFRESH_TOKEN = "refresh"


def _create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> tuple[str, str, datetime]:
    """Devuelve (token, jti, expiración)."""
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    jti = str(uuid.uuid4())

    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "jti": jti,
        "iat": now,
        "nbf": now,
        "exp": expire,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }
    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti, expire


def create_access_token(
    subject: str, extra_claims: dict[str, Any] | None = None
) -> tuple[str, str, datetime]:
    return _create_token(
        subject,
        ACCESS_TOKEN,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_claims,
    )


def create_refresh_token(subject: str) -> tuple[str, str, datetime]:
    return _create_token(
        subject,
        REFRESH_TOKEN,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    """
    Decodifica y valida un JWT. Lanza jwt.PyJWTError si es inválido/expirado.
    """
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        audience=settings.JWT_AUDIENCE,
        issuer=settings.JWT_ISSUER,
        options={"require": ["exp", "iat", "sub", "jti"]},
    )
    if expected_type and payload.get("type") != expected_type:
        raise jwt.InvalidTokenError(
            f"Tipo de token inesperado: {payload.get('type')} != {expected_type}"
        )
    return payload
