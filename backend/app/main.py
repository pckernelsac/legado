"""
Punto de entrada de la API FastAPI de Legado Eterno.

Configura middleware de seguridad, CORS, manejadores de excepciones de dominio
y registra el router principal.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging import configure_logging, get_logger
from app.presentation.middleware import RateLimitMiddleware, SecurityHeadersMiddleware
from app.presentation.routers.api import api_router

configure_logging()
logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting", environment=settings.ENVIRONMENT, project=settings.PROJECT_NAME)
    yield
    logger.info("shutting_down")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API de la plataforma de memoriales digitales Legado Eterno.",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
    lifespan=lifespan,
)

# --- Middleware (orden importa: el último añadido se ejecuta primero) --------
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=600, window_seconds=60)
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-CSRF-Token"],
    expose_headers=["X-Request-ID", "X-Response-Time"],
    max_age=600,
)


# --- Manejadores de excepciones --------------------------------------------
@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError):
    retry_after = getattr(exc, "retry_after", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "message": exc.message},
        headers={"Retry-After": str(retry_after)} if retry_after else None,
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "validation_error",
            "message": "Datos de entrada inválidos.",
            "detail": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def handle_unexpected(request: Request, exc: Exception):
    logger.exception("unhandled_error", path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error_code": "internal_error", "message": "Error interno del servidor."},
    )


app.include_router(api_router)
