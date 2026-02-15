from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from bot.core.database import get_db
from bot.core.constants import I18nKeys
from bot.models.user import UserRole
from bot.services.i18n import get_i18n
from bot.services.settings_manager import settings_manager


class MaintenanceCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        role = data.get("user_role", UserRole.USER)
        if role == UserRole.ADMIN:
            return await handler(event, data)

        db = await get_db()
        i18n = get_i18n()
        enabled = False
        message = i18n.get(I18nKeys.MAINTENANCE_DEFAULT_MESSAGE)

        async for session in db.get_session():
            enabled = await settings_manager.get_maintenance_enabled(session)
            if enabled:
                message = await settings_manager.get_maintenance_message(
                    session,
                    default=i18n.get(I18nKeys.MAINTENANCE_DEFAULT_MESSAGE),
                )

        if not enabled:
            return await handler(event, data)

        if isinstance(event, Update):
            if event.message:
                await event.message.answer(message)
            elif event.callback_query:
                await event.callback_query.answer(message, show_alert=True)
        return None
