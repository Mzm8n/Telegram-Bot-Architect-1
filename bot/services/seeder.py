import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.text_entry import TextEntry
from bot.core.constants import LogMessages, DefaultTexts

logger = logging.getLogger("bot")


async def seed_default_texts(session: AsyncSession, language: str = "ar") -> None:
    for key, text in DefaultTexts.TEXTS.items():
        stmt = select(TextEntry).where(
            TextEntry.key == key,
            TextEntry.language == language,
        )
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is None:
            entry = TextEntry(key=key, language=language, text=text)
            session.add(entry)

    await session.commit()
    logger.info(LogMessages.I18N_SEEDED)
