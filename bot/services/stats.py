from typing import Dict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.file import File, FileStatus
from bot.models.section import Section
from bot.models.user import User, UserRole


class StatsService:
    async def collect_basic(self, session: AsyncSession) -> Dict[str, int]:
        users = (await session.execute(select(func.count()).select_from(User))).scalar() or 0
        sections = (await session.execute(select(func.count()).select_from(Section))).scalar() or 0
        files = (await session.execute(select(func.count()).select_from(File))).scalar() or 0
        moderators = (
            await session.execute(select(func.count()).select_from(User).where(User.role == UserRole.MODERATOR))
        ).scalar() or 0
        contributions = (
            await session.execute(select(func.count()).select_from(File).where(File.status == FileStatus.PENDING.value))
        ).scalar() or 0
        return {
            "users": int(users),
            "sections": int(sections),
            "files": int(files),
            "moderators": int(moderators),
            "contributions": int(contributions),
        }


stats_service = StatsService()
