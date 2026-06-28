"""
CLI de administración: seed de roles/permisos/planes y creación de super admin.

Uso:
    python -m app.cli seed-roles
    python -m app.cli seed-plans
    python -m app.cli sync-plans
    python -m app.cli create-superadmin <email> <password> <full_name>
    python -m app.cli reset-password <email> <new_password>
"""
from __future__ import annotations

import asyncio
import sys

from sqlalchemy import select, update

from app.core.security import hash_password
from app.infrastructure.database.session import AsyncSessionFactory
from app.infrastructure.models.billing import Plan
from app.infrastructure.models.enums import PlanTier, RoleName
from app.infrastructure.models.user import Permission, Role, User
from app.infrastructure.repositories.user_repository import RoleRepository, UserRepository

_ROLE_DEFS = {
    RoleName.SUPER_ADMIN: "Super Administrador",
    RoleName.ADMIN: "Administrador",
    RoleName.CLIENT: "Cliente",
    RoleName.FAMILY_GUEST: "Familiar Invitado",
}

_PERMISSIONS = [
    "memorial:create", "memorial:read", "memorial:update", "memorial:delete",
    "media:upload", "media:delete", "condolence:moderate",
    "user:read", "user:update", "user:delete",
    "plan:manage", "payment:read", "audit:read",
]

_PLAN_DEFS = [
    dict(tier=PlanTier.BASIC, name="Básico", price_monthly=20, price_yearly=200,
         max_memorials=1, max_media_per_memorial=20, max_storage_mb=500,
         allow_video=False, allow_custom_qr=False, allow_ai_features=False),
    dict(tier=PlanTier.FAMILY, name="Familiar", price_monthly=50, price_yearly=500,
         max_memorials=5, max_media_per_memorial=100, max_storage_mb=5000,
         allow_video=True, allow_custom_qr=True, allow_ai_features=False),
    dict(tier=PlanTier.PREMIUM, name="Premium", price_monthly=80, price_yearly=800,
         max_memorials=20, max_media_per_memorial=500, max_storage_mb=20000,
         allow_video=True, allow_custom_qr=True, allow_ai_features=True),
]


async def seed_roles() -> None:
    async with AsyncSessionFactory() as session:
        roles = RoleRepository(session)
        perms_by_code: dict[str, Permission] = {}
        for code in _PERMISSIONS:
            perm = Permission(code=code, description=code)
            session.add(perm)
            perms_by_code[code] = perm
        await session.flush()

        for name, display in _ROLE_DEFS.items():
            if await roles.get_by_name(name):
                continue
            role = Role(name=name.value, display_name=display)
            if name in (RoleName.SUPER_ADMIN, RoleName.ADMIN):
                role.permissions = list(perms_by_code.values())
            elif name == RoleName.CLIENT:
                role.permissions = [
                    perms_by_code[c] for c in _PERMISSIONS if c.startswith(("memorial", "media", "condolence"))
                ]
            session.add(role)
        await session.commit()
    print("✓ Roles y permisos creados.")


async def seed_plans() -> None:
    async with AsyncSessionFactory() as session:
        for definition in _PLAN_DEFS:
            session.add(Plan(currency="PEN", **definition))
        await session.commit()
    print("✓ Planes creados.")


async def sync_plans() -> None:
    """Idempotente: actualiza precios/moneda de los planes vigentes, crea los
    que falten y desactiva tiers que ya no se ofrecen (p. ej. Corporativo).
    Se desactivan (is_active=False), NO se borran, para no romper la FK de
    suscripciones existentes. Seguro de correr varias veces."""
    keep_tiers = {d["tier"] for d in _PLAN_DEFS}
    async with AsyncSessionFactory() as session:
        for definition in _PLAN_DEFS:
            existing = (
                await session.execute(
                    select(Plan).where(Plan.tier == definition["tier"])
                )
            ).scalar_one_or_none()
            if existing is None:
                session.add(Plan(currency="PEN", is_active=True, **definition))
                print(f"  + creado: {definition['name']}")
            else:
                for field, value in definition.items():
                    setattr(existing, field, value)
                existing.currency = "PEN"
                existing.is_active = True
                print(f"  ~ actualizado: {definition['name']}")

        deactivated = await session.execute(
            update(Plan)
            .where(Plan.tier.notin_(keep_tiers), Plan.is_active.is_(True))
            .values(is_active=False)
        )
        if deactivated.rowcount:
            print(f"  - desactivados {deactivated.rowcount} plan(es) obsoletos")
        await session.commit()
    print("✓ Planes sincronizados.")


async def create_superadmin(email: str, password: str, full_name: str) -> None:
    async with AsyncSessionFactory() as session:
        roles = RoleRepository(session)
        users = UserRepository(session)
        role = await roles.get_by_name(RoleName.SUPER_ADMIN)
        if role is None:
            print("✗ Ejecute primero: python -m app.cli seed-roles")
            return
        if await users.get_by_email(email):
            print("✗ El usuario ya existe.")
            return
        user = User(
            email=email.lower(),
            hashed_password=hash_password(password),
            full_name=full_name,
            role_id=role.id,
            is_active=True,
            is_email_verified=True,
        )
        session.add(user)
        await session.commit()
    print(f"✓ Super admin creado: {email}")


async def reset_password(email: str, new_password: str) -> None:
    async with AsyncSessionFactory() as session:
        users = UserRepository(session)
        user = await users.get_by_email(email)
        if user is None:
            print(f"✗ No existe un usuario con email: {email}")
            return
        await session.execute(
            update(User)
            .where(User.id == user.id)
            .values(hashed_password=hash_password(new_password))
        )
        await session.commit()
    print(f"✓ Contraseña actualizada para: {email}")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    cmd = args[0]
    if cmd == "seed-roles":
        asyncio.run(seed_roles())
    elif cmd == "seed-plans":
        asyncio.run(seed_plans())
    elif cmd == "sync-plans":
        asyncio.run(sync_plans())
    elif cmd == "create-superadmin" and len(args) == 4:
        asyncio.run(create_superadmin(args[1], args[2], args[3]))
    elif cmd == "reset-password" and len(args) == 3:
        asyncio.run(reset_password(args[1], args[2]))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
