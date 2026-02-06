import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.core.config import load_config
from bot.core.logging_config import setup_logging
from bot.core.database import init_database
from bot.core.constants import LogMessages
from bot.services.i18n import init_i18n
from bot.services.state import init_state_service
from bot.services.seeder import seed_default_texts
from bot.middlewares.ban_check import BanCheckMiddleware
from bot.middlewares.subscription_check import SubscriptionCheckMiddleware
from bot.middlewares.role_check import RoleMiddleware
from bot.middlewares.i18n_middleware import I18nMiddleware
from bot.middlewares.user_tracking import UserTrackingMiddleware
from bot.modules.central_router import central_router
from bot.modules.error_handler import create_error_handler
from bot.modules.health_check import check_health


async def main() -> None:
    logger = setup_logging()
    logger.info(LogMessages.STARTING_BOT)

    config = load_config()

    if not config.database.url:
        logger.error(LogMessages.DATABASE_URL_NOT_SET)
        return

    logger.info(LogMessages.CONNECTING_TO_DATABASE)
    db = await init_database(config.database.url)
    logger.info(LogMessages.DATABASE_CONNECTED)

    i18n = init_i18n(default_language=config.default_language)
    async for session in db.get_session():
        await seed_default_texts(session, language=config.default_language)
    async for session in db.get_session():
        await i18n.load_texts(session)

    init_state_service(timeout_seconds=config.state.timeout_seconds)
    logger.info(LogMessages.SERVICES_INITIALIZED)

    if not config.bot.token:
        logger.warning(LogMessages.BOT_TOKEN_NOT_SET)
        health = await check_health()
        logger.info(LogMessages.INFRASTRUCTURE_READY)
        await db.close()
        return

    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    dp.update.outer_middleware(BanCheckMiddleware())
    dp.update.outer_middleware(SubscriptionCheckMiddleware(
        enabled=config.subscription.enabled,
        channel_ids=config.subscription.channel_ids,
    ))
    dp.update.outer_middleware(UserTrackingMiddleware(
        log_channel_id=config.bot.log_channel_id,
    ))
    dp.update.outer_middleware(RoleMiddleware())
    dp.update.outer_middleware(I18nMiddleware())
    logger.info(LogMessages.MIDDLEWARES_REGISTERED)

    dp.include_router(create_error_handler())
    dp.include_router(central_router.router)
    logger.info(LogMessages.CENTRAL_ROUTER_REGISTERED)

    logger.info(LogMessages.BOT_READY)

    try:
        await dp.start_polling(bot)
    finally:
        logger.info(LogMessages.BOT_STOPPED)
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
