import logging
from typing import Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.text_entry import TextEntry
from bot.core.constants import LogMessages

logger = logging.getLogger("bot")


class I18nService:
    def __init__(self, default_language: str = "ar"):
        self._default_language = default_language
        self._cache: Dict[str, Dict[str, str]] = {}
        self._loaded = False

    @property
    def default_language(self) -> str:
        return self._default_language

    async def load_texts(self, session: AsyncSession) -> None:
        stmt = select(TextEntry).where(TextEntry.is_active == True)
        result = await session.execute(stmt)
        entries = result.scalars().all()

        self._cache.clear()
        for entry in entries:
            if entry.language not in self._cache:
                self._cache[entry.language] = {}
            self._cache[entry.language][entry.key] = entry.text

        self._loaded = True
        logger.info(LogMessages.I18N_LOADED)

    async def reload(self, session: AsyncSession) -> None:
        await self.load_texts(session)

    def get(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        lang = language or self._default_language

        text = self._cache.get(lang, {}).get(key)

        if text is None and lang != self._default_language:
            text = self._cache.get(self._default_language, {}).get(key)

        if text is None:
            return key

        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, IndexError):
                pass

        return text

    def has_key(self, key: str, language: Optional[str] = None) -> bool:
        lang = language or self._default_language
        return key in self._cache.get(lang, {})

    @property
    def is_loaded(self) -> bool:
        return self._loaded


i18n_service: Optional[I18nService] = None


def get_i18n() -> I18nService:
    from bot.core.constants import ErrorMessages
    if i18n_service is None:
        raise RuntimeError(ErrorMessages.I18N_NOT_INITIALIZED)
    return i18n_service


def init_i18n(default_language: str = "ar") -> I18nService:
    global i18n_service
    i18n_service = I18nService(default_language=default_language)
    return i18n_service
