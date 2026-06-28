"""Schemas de autenticación y usuarios (Pydantic v2)."""
from __future__ import annotations

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.application.schemas.common import ORMModel
from app.core.config import settings

_PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).+$")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=settings.PASSWORD_MIN_LENGTH, max_length=128)
    full_name: str = Field(min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=30)

    @field_validator("password")
    @classmethod
    def _strong_password(cls, v: str) -> str:
        if not _PASSWORD_RE.match(v):
            raise ValueError(
                "La contraseña debe incluir mayúsculas, minúsculas, número y símbolo."
            )
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    mfa_code: str | None = Field(default=None, max_length=10)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=settings.PASSWORD_MIN_LENGTH, max_length=128)

    @field_validator("new_password")
    @classmethod
    def _strong_password(cls, v: str) -> str:
        if not _PASSWORD_RE.match(v):
            raise ValueError(
                "La contraseña debe incluir mayúsculas, minúsculas, número y símbolo."
            )
        return v


class EmailVerificationRequest(BaseModel):
    token: str


class RoleOut(ORMModel):
    name: str
    display_name: str


class UserOut(ORMModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    phone: str | None
    avatar_url: str | None
    is_active: bool
    is_email_verified: bool
    mfa_enabled: bool
    role: RoleOut
    last_login_at: datetime | None
    created_at: datetime
