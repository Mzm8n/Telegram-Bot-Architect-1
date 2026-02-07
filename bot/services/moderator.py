import logging
from typing import Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.moderator_permission import ModeratorPermission
from bot.core.constants import LogMessages

logger = logging.getLogger("bot")


class ModeratorService:
    async def get_permissions(
        self, session: AsyncSession, user_id: int
    ) -> Optional[ModeratorPermission]:
        stmt = select(ModeratorPermission).where(
            ModeratorPermission.user_id == user_id
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_permissions(
        self, session: AsyncSession, user_id: int
    ) -> ModeratorPermission:
        perm = ModeratorPermission(user_id=user_id)
        session.add(perm)
        await session.flush()
        return perm

    async def update_permission(
        self,
        session: AsyncSession,
        user_id: int,
        field: str,
        value: bool,
    ) -> Optional[ModeratorPermission]:
        perm = await self.get_permissions(session, user_id)
        if perm is None:
            return None

        setattr(perm, field, value)
        await session.flush()
        return perm

    async def toggle_permission(
        self,
        session: AsyncSession,
        user_id: int,
        field: str,
    ) -> Optional[ModeratorPermission]:
        perm = await self.get_permissions(session, user_id)
        if perm is None:
            return None

        current = getattr(perm, field, False)
        setattr(perm, field, not current)
        await session.flush()
        return perm

    async def delete_permissions(
        self, session: AsyncSession, user_id: int
    ) -> None:
        stmt = delete(ModeratorPermission).where(
            ModeratorPermission.user_id == user_id
        )
        await session.execute(stmt)
        await session.flush()


moderator_service = ModeratorService()
