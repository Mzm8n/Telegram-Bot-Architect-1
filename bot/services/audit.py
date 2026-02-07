import logging
from typing import List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.audit_log import AuditLog
from bot.core.constants import LogMessages

logger = logging.getLogger("bot")


class AuditService:
    async def log_action(
        self,
        session: AsyncSession,
        user_id: int,
        action: str,
        details: Optional[str] = None,
    ) -> None:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
        )
        session.add(entry)
        await session.flush()
        logger.info(LogMessages.AUDIT_LOG_CREATED.format(user_id=user_id, action=action))


    async def list_logs(
        self,
        session: AsyncSession,
        page: int = 1,
        per_page: int = 10,
    ) -> Tuple[List[AuditLog], int]:
        count_stmt = select(func.count()).select_from(AuditLog)
        total_result = await session.execute(count_stmt)
        total = total_result.scalar() or 0

        offset = (page - 1) * per_page
        stmt = (
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        result = await session.execute(stmt)
        logs = list(result.scalars().all())
        return logs, total


audit_service = AuditService()
