import logging
from typing import Optional
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


audit_service = AuditService()
