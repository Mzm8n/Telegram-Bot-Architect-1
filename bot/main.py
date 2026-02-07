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
from bot.handlers.home import (
    create_home_router,
    handle_home_callback,
    handle_contribute_callback,
    handle_about_callback,
    handle_contact_callback,
    handle_tools_callback,
    handle_admin_panel_callback,
    handle_admin_sections_callback,
    handle_back_callback,
)
from bot.handlers.search import (
    create_search_router,
    handle_search_callback,
    handle_search_back_callback,
    handle_search_result_section,
    handle_search_result_file,
)
from bot.handlers.sections import (
    create_sections_router,
    handle_sections_callback,
    handle_section_view_callback,
    handle_section_back_callback,
    handle_section_admin_add,
    handle_section_admin_edit,
    handle_section_admin_set_order,
    handle_section_admin_delete,
    handle_section_admin_confirm_delete,
    handle_section_admin_cancel,
    handle_section_skip_desc,
)
from bot.handlers.files import (
    create_files_router,
    set_storage_channel_id,
    handle_file_upload_start,
    handle_file_done,
    handle_file_cancel,
    handle_file_view,
    handle_file_delete,
    handle_file_confirm_delete,
    handle_file_page,
)
from bot.handlers.fallback import create_fallback_router
from bot.core.constants import CallbackPrefixes


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

    if config.bot.storage_channel_id != 0:
        set_storage_channel_id(config.bot.storage_channel_id)
    else:
        logger.warning(LogMessages.STORAGE_CHANNEL_NOT_SET)

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

    central_router.register(CallbackPrefixes.HOME, handle_home_callback)
    central_router.register(CallbackPrefixes.SECTIONS, handle_sections_callback)
    central_router.register(CallbackPrefixes.SECTION_VIEW, handle_section_view_callback)
    central_router.register(CallbackPrefixes.SECTION_BACK, handle_section_back_callback)
    central_router.register(CallbackPrefixes.SECTION_ADMIN_ADD, handle_section_admin_add)
    central_router.register(CallbackPrefixes.SECTION_ADMIN_EDIT, handle_section_admin_edit)
    central_router.register(CallbackPrefixes.SECTION_ADMIN_SET_ORDER, handle_section_admin_set_order)
    central_router.register(CallbackPrefixes.SECTION_ADMIN_DELETE, handle_section_admin_delete)
    central_router.register(CallbackPrefixes.SECTION_ADMIN_CONFIRM_DELETE, handle_section_admin_confirm_delete)
    central_router.register(CallbackPrefixes.SECTION_ADMIN_CANCEL, handle_section_admin_cancel)
    central_router.register(CallbackPrefixes.SECTION_ADMIN_SKIP_DESC, handle_section_skip_desc)
    central_router.register(CallbackPrefixes.FILE_VIEW, handle_file_view)
    central_router.register(CallbackPrefixes.FILE_PAGE, handle_file_page)
    central_router.register(CallbackPrefixes.FILE_UPLOAD, handle_file_upload_start)
    central_router.register(CallbackPrefixes.FILE_DELETE, handle_file_delete)
    central_router.register(CallbackPrefixes.FILE_CONFIRM_DELETE, handle_file_confirm_delete)
    central_router.register(CallbackPrefixes.FILE_DONE, handle_file_done)
    central_router.register(CallbackPrefixes.FILE_CANCEL, handle_file_cancel)
    central_router.register(CallbackPrefixes.SEARCH_RESULT_SECTION, handle_search_result_section)
    central_router.register(CallbackPrefixes.SEARCH_RESULT_FILE, handle_search_result_file)
    central_router.register(CallbackPrefixes.SEARCH_BACK, handle_search_back_callback)
    central_router.register(CallbackPrefixes.SEARCH, handle_search_callback)
    central_router.register(CallbackPrefixes.CONTRIBUTE, handle_contribute_callback)
    central_router.register(CallbackPrefixes.ABOUT, handle_about_callback)
    central_router.register(CallbackPrefixes.CONTACT, handle_contact_callback)
    central_router.register(CallbackPrefixes.TOOLS, handle_tools_callback)
    central_router.register(CallbackPrefixes.ADMIN_PANEL, handle_admin_panel_callback)
    central_router.register(CallbackPrefixes.ADMIN_SECTIONS, handle_admin_sections_callback)
    central_router.register(CallbackPrefixes.BACK, handle_back_callback)

    dp.include_router(create_error_handler())
    dp.include_router(create_home_router())
    dp.include_router(create_files_router())
    dp.include_router(create_search_router())
    dp.include_router(create_sections_router())
    dp.include_router(central_router.router)
    dp.include_router(create_fallback_router())
    logger.info(LogMessages.HANDLERS_REGISTERED)

    logger.info(LogMessages.BOT_READY)

    try:
        await dp.start_polling(bot)
    finally:
        logger.info(LogMessages.BOT_STOPPED)
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
