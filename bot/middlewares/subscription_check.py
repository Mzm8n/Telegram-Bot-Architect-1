import logging
from typing import Callable, Dict, Any, Awaitable, List, Optional

from aiogram import BaseMiddleware, Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import TelegramObject, Update, InlineKeyboardMarkup, InlineKeyboardButton

from bot.core.constants import LogMessages, I18nKeys, CallbackPrefixes
from bot.core.database import get_db
from bot.services.i18n import get_i18n
from bot.services.settings_manager import settings_manager

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
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        logger.debug(LogMessages.MIDDLEWARE_SUBSCRIPTION_CHECK.format(user_id=user.id))

        db = await get_db()
        dynamic_enabled = self._enabled
        dynamic_channels: List[str] = [str(c) for c in self._channel_ids]
        async for session in db.get_session():
            dynamic_enabled = await settings_manager.get_subscription_enabled(session)
            db_channels = await settings_manager.get_subscription_channels(session)
            if db_channels:
                dynamic_channels = db_channels

        if not dynamic_enabled or not dynamic_channels:
            return await handler(event, data)

        bot: Bot = data["bot"]
        missing: List[str] = []
        for channel_id in dynamic_channels:
            try:
                member = await bot.get_chat_member(channel_id, user.id)
                if member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED):
                    missing.append(channel_id)
            except Exception:
                missing.append(channel_id)

        if not missing:
            return await handler(event, data)

        i18n = get_i18n()
        text = i18n.get(I18nKeys.ERROR_SUBSCRIPTION_REQUIRED)
        buttons: List[List[InlineKeyboardButton]] = []
        for ch in missing[:3]:
            if str(ch).startswith("@"):
                buttons.append([InlineKeyboardButton(text=f"📢 {ch}", url=f"https://t.me/{str(ch).lstrip('@')}")])
        buttons.append([InlineKeyboardButton(
            text=i18n.get(I18nKeys.SUBSCRIPTION_BTN_VERIFY),
            callback_data=CallbackPrefixes.SUB_VERIFY,
        )])
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        if isinstance(event, Update):
            if event.message:
                await event.message.answer(text, reply_markup=keyboard)
            elif event.callback_query:
                if event.callback_query.message:
                    await event.callback_query.message.answer(text, reply_markup=keyboard)
                await event.callback_query.answer(text, show_alert=True)
        return None
