import logging
from typing import Any

from aiogram import Router
from aiogram.types import Message

from bot.core.constants import LogMessages, I18nKeys
from bot.services.i18n import get_i18n
from bot.services.state import get_state_service
from bot.handlers.home import build_home_keyboard
from bot.models.user import UserRole

logger = logging.getLogger("bot")


def create_fallback_router() -> Router:
    router = Router(name="fallback")

    @router.message()
    async def unknown_text_handler(message: Message, **kwargs: Any) -> None:
        if not message.from_user:
            return
        user_id = message.from_user.id
        logger.debug(LogMessages.UNKNOWN_TEXT.format(user_id=user_id))

        state_service = get_state_service()
        state_service.clear_state(user_id)

        role = kwargs.get("user_role", UserRole.USER)

        i18n = get_i18n()
        name = message.from_user.first_name or ""
        unknown_text = i18n.get(I18nKeys.HOME_UNKNOWN_TEXT)
        welcome_text = i18n.get(I18nKeys.HOME_WELCOME, name=name)

        await message.answer(
            f"{unknown_text}\n\n{welcome_text}",
            reply_markup=build_home_keyboard(role),
        )

    return router
