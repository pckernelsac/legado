"""
Servicio de facturación: plan vigente, límites y (des)alta de suscripción.

NOTA — pasarela de pago: la integración real con Stripe/MercadoPago (creación de
checkout sessions + webhooks) requiere claves de API configuradas. Mientras no
existan, `subscribe` realiza una activación directa (modo desarrollo) para poder
demostrar el cambio de plan y el enforcement de límites. El punto de extensión
está marcado en `subscribe`.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.application.schemas.billing import SubscribeRequest
from app.core.exceptions import NotFoundError, ValidationError
from app.infrastructure.models.billing import Plan, Subscription
from app.infrastructure.models.enums import PlanTier, SubscriptionStatus
from app.infrastructure.repositories.billing_repository import (
    PlanRepository,
    SubscriptionRepository,
)
from app.infrastructure.repositories.memorial_repository import (
    MediaRepository,
    MemorialRepository,
)

# Plan por defecto cuando el usuario no tiene suscripción activa.
_DEFAULT_TIER = PlanTier.BASIC


class BillingService:
    def __init__(
        self,
        plans: PlanRepository,
        subscriptions: SubscriptionRepository,
        memorials: MemorialRepository,
        media: MediaRepository,
    ) -> None:
        self.plans = plans
        self.subscriptions = subscriptions
        self.memorials = memorials
        self.media = media

    # --- Plan vigente -------------------------------------------------------
    async def effective_plan(self, user_id: uuid.UUID) -> Plan:
        sub = await self.subscriptions.get_active_for_user(user_id)
        if sub is not None:
            plan = await self.plans.get(sub.plan_id)
            if plan is not None:
                return plan
        plan = await self.plans.get_by_tier(_DEFAULT_TIER)
        if plan is None:
            raise NotFoundError("No hay planes configurados. Ejecute seed-plans.")
        return plan

    async def list_plans(self) -> list[Plan]:
        return await self.plans.list_active()

    async def overview(self, user_id: uuid.UUID):
        from app.application.schemas.billing import PlanOut, SubscriptionOverview

        sub = await self.subscriptions.get_active_for_user(user_id)
        plan = await self.effective_plan(user_id)
        used = await self.memorials.count_by_owner(user_id)
        return SubscriptionOverview(
            plan=PlanOut.model_validate(plan),
            status=sub.status if sub else SubscriptionStatus.ACTIVE,
            billing_cycle=sub.billing_cycle if sub else "monthly",
            current_period_end=sub.current_period_end if sub else None,
            memorials_used=used,
            memorials_limit=plan.max_memorials,
        )

    # --- Enforcement de límites --------------------------------------------
    async def assert_can_create_memorial(self, user_id: uuid.UUID) -> None:
        plan = await self.effective_plan(user_id)
        used = await self.memorials.count_by_owner(user_id)
        if used >= plan.max_memorials:
            raise ValidationError(
                f"Tu plan {plan.name} permite {plan.max_memorials} memorial(es). "
                "Mejora tu plan para crear más."
            )

    async def assert_can_add_media(
        self, user_id: uuid.UUID, memorial_id: uuid.UUID
    ) -> None:
        plan = await self.effective_plan(user_id)
        used = await self.media.count_by_memorial(memorial_id)
        if used >= plan.max_media_per_memorial:
            raise ValidationError(
                f"Tu plan {plan.name} permite {plan.max_media_per_memorial} archivos "
                "por memorial. Mejora tu plan para subir más."
            )

    # --- Alta / cambio de plan ---------------------------------------------
    async def subscribe(
        self, user_id: uuid.UUID, data: SubscribeRequest
    ) -> Subscription:
        plan = await self.plans.get_by_tier(data.tier)
        if plan is None or not plan.is_active:
            raise NotFoundError("Plan no disponible.")
        if data.billing_cycle not in ("monthly", "yearly"):
            raise ValidationError("Ciclo de facturación inválido.")

        # === PUNTO DE EXTENSIÓN PARA PAGOS REALES ==========================
        # Aquí se crearía la checkout session del proveedor (Stripe/MercadoPago)
        # y se devolvería la URL de pago. La suscripción pasaría a ACTIVE solo
        # tras confirmar el webhook. En desarrollo activamos directamente.
        # ===================================================================
        now = datetime.now(timezone.utc)
        period = timedelta(days=365 if data.billing_cycle == "yearly" else 30)

        sub = await self.subscriptions.get_active_for_user(user_id)
        if sub is None:
            sub = Subscription(user_id=user_id)
            self.subscriptions.session.add(sub)

        sub.plan_id = plan.id
        sub.status = SubscriptionStatus.ACTIVE
        sub.billing_cycle = data.billing_cycle
        sub.current_period_start = now
        sub.current_period_end = now + period
        await self.subscriptions.session.flush()
        return sub
