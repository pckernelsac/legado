"""Enumeraciones compartidas por los modelos."""
from __future__ import annotations

import enum


class RoleName(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    CLIENT = "client"
    FAMILY_GUEST = "family_guest"


class MemorialStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"


class MemorialVisibility(str, enum.Enum):
    PUBLIC = "public"
    UNLISTED = "unlisted"      # accesible solo con el slug
    PRIVATE = "private"        # requiere autenticación


class MediaType(str, enum.Enum):
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"


class MediaStatus(str, enum.Enum):
    PENDING = "pending"        # subido, pendiente de procesar
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    QUARANTINED = "quarantined"  # marcado por el escaneo antivirus


class ModerationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"


class QRFormat(str, enum.Enum):
    PNG = "png"
    SVG = "svg"
    PDF = "pdf"


class PlanTier(str, enum.Enum):
    BASIC = "basic"
    FAMILY = "family"
    PREMIUM = "premium"
    CORPORATE = "corporate"


class SubscriptionStatus(str, enum.Enum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    EXPIRED = "expired"


class PaymentProvider(str, enum.Enum):
    STRIPE = "stripe"
    MERCADOPAGO = "mercadopago"
    YAPE = "yape"
    PLIN = "plin"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class NotificationType(str, enum.Enum):
    CONDOLENCE = "condolence"
    CANDLE = "candle"
    SYSTEM = "system"
    PAYMENT = "payment"
    MODERATION = "moderation"
