import asyncio
import logging

from bot.core.config import load_config
from bot.core.logging_config import setup_logging
from bot.core.database import init_database


async def main() -> None:
    logger = setup_logging()
    logger.info("جاري تشغيل البوت...")
    
    config = load_config()
    
    if not config.database.url:
        logger.error("DATABASE_URL غير محدد")
        return
    
    logger.info("جاري الاتصال بقاعدة البيانات...")
    db = await init_database(config.database.url)
    logger.info("تم الاتصال بقاعدة البيانات بنجاح")
    
    if not config.bot.token:
        logger.warning("BOT_TOKEN غير محدد - تشغيل في وضع الاختبار")
        logger.info("البنية جاهزة للعمل")
        await db.close()
        return
    
    logger.info("البوت جاهز للعمل")
    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
