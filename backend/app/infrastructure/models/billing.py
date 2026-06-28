"""Modelos de facturación: planes, suscripciones y pagos."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import BaseModel
from app.infrastructure.models.enums import (
    PaymentProvider,
    PaymentStatus,
    PlanTier,
    SubscriptionStatus,
)


class Plan(BaseModel):
    """Plan de suscripción comercializable."""

    tier: Mapped[PlanTier] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_monthly: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    price_yearly: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    # Límites del plan
    max_memorials: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_media_per_memorial: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    max_storage_mb: Mapped[int] = mapped_column(Integer, default=500, nullable=False)
    allow_video: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allow_custom_qr: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allow_ai_features: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    features: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="plan")


class Subscription(BaseModel):
    """Suscripción de un usuario a un plan."""

    __table_args__ = (
        Index("ix_subscription_user_status", "user_id", "status"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("plan.id"), nullable=False, index=True
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        String(20), default=SubscriptionStatus.TRIALING, nullable=False, index=True
    )
    billing_cycle: Mapped[str] = mapped_column(String(10), default="monthly", nullable=False)

    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    trial_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    canceled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Referencia al proveedor externo (Stripe/MercadoPago).
    provider: Mapped[PaymentProvider | None] = mapped_column(String(20), nullable=True)
    provider_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    plan: Mapped[Plan] = relationship(back_populates="subscriptions")
    payments: Mapped[list["Payment"]] = relationship(back_populates="subscription")


class Payment(BaseModel):
    """Pago individual asociado a una suscripción."""

    __table_args__ = (
        Index("ix_payment_subscription_status", "subscription_id", "status"),
    )

    subscription_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("subscription.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    provider: Mapped[PaymentProvider] = mapped_column(String(20), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        String(20), default=PaymentStatus.PENDING, nullable=False
    )
    provider_payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    subscription: Mapped[Subscription | None] = relationship(back_populates="payments")
