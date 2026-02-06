import logging
from typing import Optional, Tuple
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.user import User, UserRole
from bot.core.constants import LogMessages

logger = logging.getLogger("bot")


class UserService:
    async def get_or_create(
        self,
        session: AsyncSession,
        user_id: int,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> Tuple[User, bool]:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is not None:
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            await session.flush()
            return user, False

        user = User(
            id=user_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
        )
        session.add(user)
        await session.flush()
        logger.info(LogMessages.USER_CREATED.format(user_id=user_id))
        return user, True

    async def get_by_id(self, session: AsyncSession, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def is_blocked(self, session: AsyncSession, user_id: int) -> bool:
        stmt = select(User.is_blocked).where(User.id == user_id)
        result = await session.execute(stmt)
        blocked = result.scalar_one_or_none()
        return blocked is True

    async def get_role(self, session: AsyncSession, user_id: int) -> Optional[UserRole]:
        stmt = select(User.role).where(User.id == user_id)
        result = await session.execute(stmt)
        role = result.scalar_one_or_none()
        if role is None:
            return None
        return UserRole(role) if isinstance(role, str) else role

    async def set_role(self, session: AsyncSession, user_id: int, role: UserRole) -> None:
        stmt = update(User).where(User.id == user_id).values(role=role)
        await session.execute(stmt)
        await session.flush()

    async def set_blocked(self, session: AsyncSession, user_id: int, blocked: bool) -> None:
        stmt = update(User).where(User.id == user_id).values(is_blocked=blocked)
        await session.execute(stmt)
        await session.flush()


user_service = UserService()
