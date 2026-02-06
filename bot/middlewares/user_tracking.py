import logging
from typing import Callable, Dict, Any, Awaitable, Optional

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject

from bot.core.constants import LogMessages
from bot.services.user import user_service
from bot.core.database import get_db
from bot.modules.login_logger import LoginLogger

logger = logging.getLogger("bot")


class UserTrackingMiddleware(BaseMiddleware):
    def __init__(self, log_channel_id: int = 0):
        self._log_channel_id = log_channel_id
        self._login_logger: Optional[LoginLogger] = None

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        db = await get_db()
        is_new = False
        async for session in db.get_session():
            db_user, is_new = await user_service.get_or_create(
                session,
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
            )

        if is_new and self._log_channel_id != 0:
            bot: Bot = data["bot"]
            if self._login_logger is None:
                self._login_logger = LoginLogger(bot, self._log_channel_id)
            await self._login_logger.log_login(
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
            )

        return await handler(event, data)
