import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from bot.core.constants import LogMessages, I18nKeys
from bot.services.i18n import get_i18n
from bot.services.user import user_service
from bot.core.database import get_db

logger = logging.getLogger("bot")


class BanCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        is_blocked = False
        db = await get_db()
        async for session in db.get_session():
            is_blocked = await user_service.is_blocked(session, user.id)

        if is_blocked:
            logger.info(LogMessages.USER_BLOCKED.format(user_id=user.id))
            i18n = get_i18n()
            text = i18n.get(I18nKeys.ERROR_BLOCKED)

            if isinstance(event, Update):
                if event.message:
                    await event.message.answer(text)
                elif event.callback_query:
                    await event.callback_query.answer(text, show_alert=True)
            return None

        return await handler(event, data)
