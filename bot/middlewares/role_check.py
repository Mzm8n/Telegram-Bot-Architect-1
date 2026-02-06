import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.core.constants import LogMessages
from bot.services.user import user_service
from bot.core.database import get_db
from bot.models.user import UserRole

logger = logging.getLogger("bot")


class RoleMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        role = None
        db = await get_db()
        async for session in db.get_session():
            role = await user_service.get_role(session, user.id)

        user_role = role if role else UserRole.USER
        data["user_role"] = user_role
        logger.debug(LogMessages.MIDDLEWARE_ROLE_LOADED.format(user_id=user.id, role=user_role.value))

        return await handler(event, data)
