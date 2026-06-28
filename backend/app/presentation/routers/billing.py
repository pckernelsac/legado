"""Endpoints de facturación: planes públicos y suscripción del usuario."""
from __future__ import annotations

from fastapi import APIRouter, status

from app.application.schemas.billing import (
    PlanOut,
    SubscribeRequest,
    SubscriptionOverview,
)
from app.presentation.dependencies import BillingServiceDep, CurrentUser

# Planes públicos (para la landing / pricing).
plans_router = APIRouter(prefix="/plans", tags=["billing"])


@plans_router.get("", response_model=list[PlanOut])
async def list_plans(service: BillingServiceDep):
    return await service.list_plans()


# Suscripción del usuario autenticado.
billing_router = APIRouter(prefix="/billing", tags=["billing"])


@billing_router.get("/subscription", response_model=SubscriptionOverview)
async def my_subscription(user: CurrentUser, service: BillingServiceDep):
    return await service.overview(user.id)


@billing_router.post(
    "/subscribe", response_model=SubscriptionOverview, status_code=status.HTTP_201_CREATED
)
async def subscribe(
    data: SubscribeRequest, user: CurrentUser, service: BillingServiceDep
):
    await service.subscribe(user.id, data)
    return await service.overview(user.id)
