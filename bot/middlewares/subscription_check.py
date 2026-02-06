import logging
from typing import Callable, Dict, Any, Awaitable, List, Optional

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Update
from aiogram.enums import ChatMemberStatus

from bot.core.constants import LogMessages, I18nKeys
from bot.services.i18n import get_i18n

logger = logging.getLogger("bot")


class SubscriptionCheckMiddleware(BaseMiddleware):
    def __init__(self, enabled: bool = False, channel_ids: Optional[List[int]] = None):
        self._enabled = enabled
        self._channel_ids = channel_ids or []

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not self._enabled or not self._channel_ids:
            return await handler(event, data)

        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        logger.debug(LogMessages.MIDDLEWARE_SUBSCRIPTION_CHECK.format(user_id=user.id))

        bot: Bot = data["bot"]
        for channel_id in self._channel_ids:
            try:
                member = await bot.get_chat_member(channel_id, user.id)
                if member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED):
                    i18n = get_i18n()
                    text = i18n.get(I18nKeys.ERROR_SUBSCRIPTION_REQUIRED)

                    if isinstance(event, Update):
                        if event.message:
                            await event.message.answer(text)
                        elif event.callback_query:
                            await event.callback_query.answer(text, show_alert=True)
                    return None
            except Exception:
                pass

        return await handler(event, data)
