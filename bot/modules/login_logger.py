import logging
from datetime import datetime
from typing import Optional

from aiogram import Bot

from bot.core.constants import LogMessages, I18nKeys
from bot.services.i18n import get_i18n

logger = logging.getLogger("bot")


class LoginLogger:
    def __init__(self, bot: Bot, log_channel_id: int):
        self._bot = bot
        self._log_channel_id = log_channel_id

    async def log_login(
        self,
        user_id: int,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> None:
        logger.info(LogMessages.USER_LOGIN.format(user_id=user_id))

        if self._log_channel_id == 0:
            return

        name = first_name
        if last_name:
            name = f"{first_name} {last_name}"

        username_display = f"@{username}" if username else "-"
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        i18n = get_i18n()
        text = i18n.get(
            I18nKeys.LOGIN_NOTIFICATION,
            user_id=user_id,
            name=name,
            time=time_str,
            username=username_display,
        )

        try:
            await self._bot.send_message(self._log_channel_id, text)
        except Exception as e:
            logger.error(LogMessages.ERROR_HANDLER_TRIGGERED.format(error=str(e)))
