"""Agregador del router principal de la API v1."""
from __future__ import annotations

from fastapi import APIRouter

from app.presentation.routers import (
    admin,
    auth,
    billing,
    health,
    media,
    memorials,
    public,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(memorials.router)
api_router.include_router(media.router)
api_router.include_router(public.router)
api_router.include_router(billing.plans_router)
api_router.include_router(billing.billing_router)
api_router.include_router(admin.router)
