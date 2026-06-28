"""
Servicio de autenticación.

Orquesta registro, login (con lockout), emisión/rotación de tokens, verificación
de email y reset de contraseña. No conoce FastAPI ni HTTP (testeable de forma
aislada). Depende de repositorios y del cache (Redis).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.application.schemas.auth import LoginRequest, RegisterRequest
from app.core.config import settings
from app.core.exceptions import (
    AccountLockedError,
    AuthenticationError,
    ConflictError,
    ValidationError,
)
from app.core.identifiers import generate_token
from app.core.security import (
    REFRESH_TOKEN,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    password_needs_rehash,
    verify_password,
)
from app.infrastructure.cache.redis_client import CacheService
from app.infrastructure.models.enums import RoleName
from app.infrastructure.models.user import Session, User
from app.infrastructure.repositories.user_repository import (
    RoleRepository,
    SessionRepository,
    UserRepository,
)


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        roles: RoleRepository,
        sessions: SessionRepository,
        cache: CacheService,
    ) -> None:
        self.users = users
        self.roles = roles
        self.sessions = sessions
        self.cache = cache

    # --- Registro -----------------------------------------------------------
    async def register(self, data: RegisterRequest) -> tuple[User, str]:
        existing = await self.users.get_by_email(data.email)
        if existing:
            raise ConflictError("Ya existe una cuenta con este correo.")

        role = await self.roles.get_by_name(RoleName.CLIENT)
        if role is None:
            raise ValidationError("Rol por defecto no configurado. Ejecute seed-roles.")

        verification_token = generate_token()
        user = User(
            email=data.email.lower(),
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
            role=role,  # pobla la relación para evitar lazy-load en la serialización
            is_active=True,
            is_email_verified=False,
            email_verification_token=verification_token,
        )
        await self.users.add(user)
        return user, verification_token

    # --- Login --------------------------------------------------------------
    async def authenticate(
        self, data: LoginRequest, *, ip: str | None, user_agent: str | None
    ) -> tuple[User, str, str]:
        user = await self.users.get_by_email(data.email)
        if user is None:
            # Mensaje genérico anti enumeración de usuarios.
            raise AuthenticationError("Credenciales inválidas.")

        self._assert_not_locked(user)

        if not verify_password(data.password, user.hashed_password):
            await self._register_failed_attempt(user)
            raise AuthenticationError("Credenciales inválidas.")

        if not user.is_active:
            raise AuthenticationError("La cuenta está desactivada.")

        if user.mfa_enabled and not self._verify_mfa(user, data.mfa_code):
            raise AuthenticationError("Código MFA inválido.")

        # Login correcto: re-hash si los parámetros Argon2 cambiaron.
        if password_needs_rehash(user.hashed_password):
            user.hashed_password = hash_password(data.password)

        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(timezone.utc)

        access, refresh = await self._issue_tokens(user, ip=ip, user_agent=user_agent)
        return user, access, refresh

    def _assert_not_locked(self, user: User) -> None:
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise AccountLockedError()

    async def _register_failed_attempt(self, user: User) -> None:
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.ACCOUNT_LOCKOUT_THRESHOLD:
            user.locked_until = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCOUNT_LOCKOUT_MINUTES
            )

    def _verify_mfa(self, user: User, code: str | None) -> bool:
        # Punto de integración TOTP (pyotp). MFA-ready.
        return bool(code)

    # --- Tokens -------------------------------------------------------------
    async def _issue_tokens(
        self, user: User, *, ip: str | None, user_agent: str | None
    ) -> tuple[str, str]:
        claims = {"role": user.role.name, "email": user.email}
        access, _, _ = create_access_token(str(user.id), extra_claims=claims)
        refresh, refresh_jti, refresh_exp = create_refresh_token(str(user.id))

        session = Session(
            user_id=user.id,
            jti=refresh_jti,
            ip_address=ip,
            user_agent=user_agent,
            created_at=datetime.now(timezone.utc),
            expires_at=refresh_exp,
        )
        await self.sessions.add(session)
        return access, refresh

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        try:
            payload = decode_token(refresh_token, expected_type=REFRESH_TOKEN)
        except Exception as exc:  # noqa: BLE001
            raise AuthenticationError("Refresh token inválido.") from exc

        jti = payload["jti"]
        session = await self.sessions.get_by_jti(jti)
        if session is None or session.revoked_at is not None:
            raise AuthenticationError("Sesión revocada o inexistente.")
        if session.expires_at < datetime.now(timezone.utc):
            raise AuthenticationError("Sesión expirada.")

        user = await self.users.get_with_role(session.user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("Usuario no disponible.")

        # Rotación de refresh token: revoca el anterior y emite uno nuevo.
        session.revoked_at = datetime.now(timezone.utc)
        access, new_refresh = await self._issue_tokens(
            user, ip=session.ip_address, user_agent=session.user_agent
        )
        return access, new_refresh

    async def logout(self, refresh_token: str) -> None:
        try:
            payload = decode_token(refresh_token, expected_type=REFRESH_TOKEN)
        except Exception:  # noqa: BLE001
            return
        session = await self.sessions.get_by_jti(payload["jti"])
        if session and session.revoked_at is None:
            session.revoked_at = datetime.now(timezone.utc)
        # Revoca también el access token vía denylist hasta su expiración.
        await self.cache.revoke_jti(payload["jti"], settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    # --- Verificación de email ---------------------------------------------
    async def verify_email(self, token: str) -> User:
        user = await self.users.get_by_verification_token(token)
        if user is None:
            raise ValidationError("Token de verificación inválido.")
        user.is_email_verified = True
        user.email_verification_token = None
        return user

    # --- Reset de contraseña -----------------------------------------------
    async def request_password_reset(self, email: str) -> str | None:
        user = await self.users.get_by_email(email)
        if user is None:
            return None  # no revelar si existe el email
        token = generate_token()
        user.password_reset_token = token
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        return token

    async def confirm_password_reset(self, token: str, new_password: str) -> None:
        user = await self.users.get_by_reset_token(token)
        if user is None or (
            user.password_reset_expires
            and user.password_reset_expires < datetime.now(timezone.utc)
        ):
            raise ValidationError("Token de recuperación inválido o expirado.")
        user.hashed_password = hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.failed_login_attempts = 0
        user.locked_until = None
        await self.sessions.revoke_all_for_user(user.id)
