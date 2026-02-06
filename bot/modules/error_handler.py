import logging
from typing import Any

from aiogram import Router
from aiogram.types import ErrorEvent

from bot.core.constants import LogMessages, I18nKeys
from bot.services.i18n import get_i18n

logger = logging.getLogger("bot")


def create_error_handler() -> Router:
    router = Router(name="error_handler")

    @router.errors()
    async def global_error_handler(event: ErrorEvent, **kwargs: Any) -> bool:
        logger.error(LogMessages.ERROR_HANDLER_TRIGGERED.format(error=event.exception), exc_info=event.exception)

        i18n = get_i18n()
        error_text = i18n.get(I18nKeys.ERROR_GENERAL)

        update = event.update
        if update:
            try:
                if update.message:
                    await update.message.answer(error_text)
                elif update.callback_query:
                    await update.callback_query.answer(error_text, show_alert=True)
            except Exception:
                pass

        return True

    return router
