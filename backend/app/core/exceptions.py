"""Excepciones de dominio/aplicación con mapeo a códigos HTTP."""
from __future__ import annotations


class AppError(Exception):
    """Excepción base de la aplicación."""

    status_code: int = 500
    error_code: str = "internal_error"
    message: str = "Ha ocurrido un error interno."

    def __init__(self, message: str | None = None, *, error_code: str | None = None):
        if message:
            self.message = message
        if error_code:
            self.error_code = error_code
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"
    message = "Recurso no encontrado."


class ConflictError(AppError):
    status_code = 409
    error_code = "conflict"
    message = "El recurso ya existe o está en conflicto."


class ValidationError(AppError):
    status_code = 422
    error_code = "validation_error"
    message = "Datos de entrada inválidos."


class AuthenticationError(AppError):
    status_code = 401
    error_code = "authentication_error"
    message = "Credenciales inválidas."


class PermissionDeniedError(AppError):
    status_code = 403
    error_code = "permission_denied"
    message = "No tiene permisos para realizar esta acción."


class RateLimitError(AppError):
    status_code = 429
    error_code = "rate_limited"
    message = "Demasiadas solicitudes. Intente más tarde."

    def __init__(
        self,
        message: str | None = None,
        *,
        error_code: str | None = None,
        retry_after: int | None = None,
    ):
        super().__init__(message, error_code=error_code)
        self.retry_after = retry_after


class AccountLockedError(AuthenticationError):
    error_code = "account_locked"
    message = "Cuenta bloqueada temporalmente por intentos fallidos."
