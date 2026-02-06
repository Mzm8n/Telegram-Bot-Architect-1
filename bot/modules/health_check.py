import logging
from typing import Dict, Any

from bot.core.constants import LogMessages
from bot.core.database import get_db
from bot.services.i18n import get_i18n

logger = logging.getLogger("bot")


async def check_health() -> Dict[str, Any]:
    status: Dict[str, Any] = {
        "healthy": True,
        "checks": {},
    }

    try:
        db = await get_db()
        async for session in db.get_session():
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
        status["checks"]["database"] = True
    except Exception as e:
        status["healthy"] = False
        status["checks"]["database"] = False
        logger.error(LogMessages.HEALTH_CHECK_FAIL.format(reason=str(e)))

    try:
        i18n = get_i18n()
        status["checks"]["i18n"] = i18n.is_loaded
        if not i18n.is_loaded:
            status["healthy"] = False
    except Exception:
        status["healthy"] = False
        status["checks"]["i18n"] = False

    if status["healthy"]:
        logger.info(LogMessages.HEALTH_CHECK_OK)
    
    return status
