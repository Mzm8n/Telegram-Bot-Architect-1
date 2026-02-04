import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.core.config import load_config
from bot.core.logging_config import setup_logging
from bot.core.database import init_database
from bot.core.constants import LogMessages


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
    
    if not config.bot.token:
        logger.warning(LogMessages.BOT_TOKEN_NOT_SET)
        logger.info(LogMessages.INFRASTRUCTURE_READY)
        await db.close()
        return
    
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    
    logger.info(LogMessages.BOT_READY)
    
    try:
        await dp.start_polling(bot)
    finally:
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
