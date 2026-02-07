import logging
from typing import Dict, Callable, Awaitable, Any

from aiogram import Router
from aiogram.types import CallbackQuery

from bot.core.constants import LogMessages

logger = logging.getLogger("bot")


RouteHandler = Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]]


class CentralRouter:
    def __init__(self):
        self._router = Router(name="central")
        self._routes: Dict[str, RouteHandler] = {}
        self._router.callback_query.register(self._handle_callback)

    @property
    def router(self) -> Router:
        return self._router

    def register(self, prefix: str, handler: RouteHandler) -> None:
        self._routes[prefix] = handler

    async def _handle_callback(self, callback: CallbackQuery, **kwargs: Any) -> None:
        if callback.data is None:
            return

        if callback.data == "noop":
            await callback.answer()
            return

        logger.info(LogMessages.CENTRAL_ROUTER_CALLBACK.format(callback_data=callback.data))

        for prefix, handler in self._routes.items():
            if callback.data.startswith(prefix):
                logger.info(f"Matched prefix '{prefix}' -> {handler.__name__}")
                await handler(callback, kwargs)
                return

        logger.info(LogMessages.CENTRAL_ROUTER_NO_HANDLER.format(callback_data=callback.data))


central_router = CentralRouter()
