"""
Registro central de modelos SQLAlchemy.

Importar todos los modelos aquí garantiza que Alembic (autogenerate) y los
metadatos de la Base conozcan el esquema completo.
"""
from app.infrastructure.models.billing import (  # noqa: F401
    Payment,
    Plan,
    Subscription,
)
from app.infrastructure.models.memorial import (  # noqa: F401
    Condolence,
    FamilyMember,
    Memorial,
    MemorialMedia,
    QRCode,
    TimelineEvent,
    VirtualCandle,
)
from app.infrastructure.models.system import (  # noqa: F401
    ActivityLog,
    AuditLog,
    Notification,
)
from app.infrastructure.models.user import (  # noqa: F401
    Device,
    Permission,
    Role,
    Session,
    User,
    role_permissions,
)

__all__ = [
    "User",
    "Role",
    "Permission",
    "Session",
    "Device",
    "role_permissions",
    "Memorial",
    "MemorialMedia",
    "TimelineEvent",
    "FamilyMember",
    "Condolence",
    "VirtualCandle",
    "QRCode",
    "Plan",
    "Subscription",
    "Payment",
    "AuditLog",
    "ActivityLog",
    "Notification",
]
