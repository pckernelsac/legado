"""Repositorio de usuarios, roles y sesiones."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.infrastructure.models.enums import RoleName
from app.infrastructure.models.user import Role, Session, User
from app.infrastructure.repositories.base import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        stmt = (
            select(User)
            .where(User.email == email.lower(), User.is_deleted.is_(False))
            .options(selectinload(User.role).selectinload(Role.permissions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_role(self, user_id: uuid.UUID) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id, User.is_deleted.is_(False))
            .options(selectinload(User.role).selectinload(Role.permissions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_verification_token(self, token: str) -> User | None:
        stmt = select(User).where(
            User.email_verification_token == token, User.is_deleted.is_(False)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_reset_token(self, token: str) -> User | None:
        stmt = select(User).where(
            User.password_reset_token == token, User.is_deleted.is_(False)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class RoleRepository(SQLAlchemyRepository[Role]):
    model = Role

    async def get_by_name(self, name: RoleName) -> Role | None:
        stmt = select(Role).where(Role.name == name.value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class SessionRepository:
    """Sesiones de refresh token (no usa soft-delete; tiene revoked_at)."""

    def __init__(self, session) -> None:
        self.session = session

    async def add(self, entity: Session) -> Session:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get_by_jti(self, jti: str) -> Session | None:
        stmt = select(Session).where(Session.jti == jti)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        from datetime import datetime, timezone

        stmt = select(Session).where(
            Session.user_id == user_id, Session.revoked_at.is_(None)
        )
        result = await self.session.execute(stmt)
        for s in result.scalars().all():
            s.revoked_at = datetime.now(timezone.utc)
        await self.session.flush()
