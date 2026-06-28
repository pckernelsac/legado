"""Schemas de facturación: planes y suscripciones."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.application.schemas.common import ORMModel
from app.infrastructure.models.enums import PlanTier, SubscriptionStatus


class PlanOut(ORMModel):
    id: uuid.UUID
    tier: PlanTier
    name: str
    description: str | None
    price_monthly: float
    price_yearly: float
    currency: str
    max_memorials: int
    max_media_per_memorial: int
    max_storage_mb: int
    allow_video: bool
    allow_custom_qr: bool
    allow_ai_features: bool


class SubscribeRequest(BaseModel):
    tier: PlanTier
    billing_cycle: str = "monthly"  # "monthly" | "yearly"


class SubscriptionOverview(BaseModel):
    """Plan vigente del usuario y uso actual frente a los límites."""

    plan: PlanOut
    status: SubscriptionStatus
    billing_cycle: str
    current_period_end: datetime | None
    memorials_used: int
    memorials_limit: int
