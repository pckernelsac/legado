"""Repositorios de facturación: planes y suscripciones."""
from __future__ import annotations

import uuid

from sqlalchemy import select

from app.infrastructure.models.billing import Plan, Subscription
from app.infrastructure.models.enums import PlanTier, SubscriptionStatus
from app.infrastructure.repositories.base import SQLAlchemyRepository

# Estados que otorgan acceso a los límites del plan.
_ACTIVE_STATUSES = (SubscriptionStatus.TRIALING, SubscriptionStatus.ACTIVE)


class PlanRepository(SQLAlchemyRepository[Plan]):
    model = Plan

    async def list_active(self) -> list[Plan]:
        stmt = (
            select(Plan)
            .where(Plan.is_active.is_(True), Plan.is_deleted.is_(False))
            .order_by(Plan.price_monthly.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_tier(self, tier: PlanTier) -> Plan | None:
        stmt = select(Plan).where(Plan.tier == tier, Plan.is_deleted.is_(False))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class SubscriptionRepository(SQLAlchemyRepository[Subscription]):
    model = Subscription

    async def get_active_for_user(self, user_id: uuid.UUID) -> Subscription | None:
        stmt = (
            select(Subscription)
            .where(
                Subscription.user_id == user_id,
                Subscription.is_deleted.is_(False),
                Subscription.status.in_(_ACTIVE_STATUSES),
            )
            .order_by(Subscription.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
