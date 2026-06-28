"""Endpoints de autenticación."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.schemas.auth import (
    EmailVerificationRequest,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from app.application.schemas.common import MessageResponse
from app.core.config import settings
from app.infrastructure.email import render_email
from app.infrastructure.tasks.jobs import send_email
from app.presentation.dependencies import (
    AuthServiceDep,
    CurrentUser,
    get_client_ip,
    get_user_agent,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, service: AuthServiceDep):
    user, verification_token = await service.register(data)
    verify_url = f"{settings.PUBLIC_BASE_URL}/verify-email?token={verification_token}"
    send_email.delay(
        user.email,
        "Verifica tu cuenta en Legado Eterno",
        render_email(
            title="Te damos la bienvenida 🕊️",
            intro=(
                f"Hola {user.full_name}, gracias por unirte a Legado Eterno. "
                "Confirma tu correo para activar tu cuenta y empezar a crear memoriales."
            ),
            cta_label="Verificar mi correo",
            cta_url=verify_url,
            outro="Este enlace es personal; no lo compartas.",
        ),
    )
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    service: AuthServiceDep,
    ip: Annotated[str | None, Depends(get_client_ip)],
    user_agent: Annotated[str | None, Depends(get_user_agent)],
):
    _, access, refresh = await service.authenticate(data, ip=ip, user_agent=user_agent)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(data: RefreshRequest, service: AuthServiceDep):
    access, refresh = await service.refresh(data.refresh_token)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(data: RefreshRequest, service: AuthServiceDep):
    await service.logout(data.refresh_token)
    return MessageResponse(message="Sesión cerrada correctamente.")


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(data: EmailVerificationRequest, service: AuthServiceDep):
    await service.verify_email(data.token)
    return MessageResponse(message="Correo verificado correctamente.")


@router.post("/password-reset", response_model=MessageResponse)
async def request_password_reset(data: PasswordResetRequest, service: AuthServiceDep):
    token = await service.request_password_reset(data.email)
    if token:
        reset_url = f"{settings.PUBLIC_BASE_URL}/reset-password?token={token}"
        send_email.delay(
            data.email,
            "Recupera tu contraseña — Legado Eterno",
            render_email(
                title="Restablece tu contraseña",
                intro=(
                    "Recibimos una solicitud para restablecer tu contraseña. "
                    "Haz clic en el botón para elegir una nueva. El enlace expira en 1 hora."
                ),
                cta_label="Restablecer contraseña",
                cta_url=reset_url,
                outro="Si no solicitaste esto, puedes ignorar este correo.",
            ),
        )
    # Respuesta idéntica exista o no el correo (anti enumeración).
    return MessageResponse(
        message="Si el correo existe, recibirás instrucciones para restablecer tu contraseña."
    )


@router.post("/password-reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(data: PasswordResetConfirm, service: AuthServiceDep):
    await service.confirm_password_reset(data.token, data.new_password)
    return MessageResponse(message="Contraseña actualizada. Inicia sesión de nuevo.")


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser):
    return user
