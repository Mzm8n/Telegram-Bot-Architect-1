import logging
from typing import Any, Dict, List

from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.core.constants import LogMessages, I18nKeys, CallbackPrefixes
from bot.core.database import get_db
from bot.services.i18n import get_i18n
from bot.services.state import get_state_service
from bot.services.sections import section_service
from bot.services.files import file_service, send_file_to_user
from bot.models.user import UserRole

logger = logging.getLogger("bot")

SEARCH_STATE = "search_input"
MAX_RESULTS = 20


def _is_search_state(message: Message) -> bool:
    if not message.from_user or not message.text:
        return False
    state_service = get_state_service()
    state = state_service.get_state(message.from_user.id)
    if state is None:
        return False
    return state.name == SEARCH_STATE


def _build_search_back_keyboard() -> InlineKeyboardMarkup:
    i18n = get_i18n()
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.SEARCH_BTN_BACK),
            callback_data=CallbackPrefixes.SEARCH_BACK,
        )],
    ])


def _build_results_keyboard(
    sections: list,
    files: list,
) -> InlineKeyboardMarkup:
    i18n = get_i18n()
    buttons: List[List[InlineKeyboardButton]] = []

    for sec in sections:
        buttons.append([InlineKeyboardButton(
            text=i18n.get(I18nKeys.SEARCH_RESULT_SECTION_LABEL, name=sec.name),
            callback_data=f"{CallbackPrefixes.SEARCH_RESULT_SECTION}{sec.id}",
        )])

    for f in files:
        buttons.append([InlineKeyboardButton(
            text=i18n.get(I18nKeys.SEARCH_RESULT_FILE_LABEL, name=f.name),
            callback_data=f"{CallbackPrefixes.SEARCH_RESULT_FILE}{f.id}",
        )])

    buttons.append([InlineKeyboardButton(
        text=i18n.get(I18nKeys.SEARCH_BTN_BACK),
        callback_data=CallbackPrefixes.SEARCH_BACK,
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def handle_search_callback(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message:
        return
    user_id = callback.from_user.id
    logger.info(LogMessages.SEARCH_STARTED.format(user_id=user_id))

    state_service = get_state_service()
    state_service.set_state(user_id, SEARCH_STATE)

    i18n = get_i18n()
    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.SEARCH_PROMPT),
        reply_markup=_build_search_back_keyboard(),
    )
    await callback.answer()


async def handle_search_back_callback(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message:
        return

    state_service = get_state_service()
    state_service.clear_state(callback.from_user.id)

    from bot.handlers.home import build_home_keyboard
    role = kwargs.get("user_role", UserRole.USER)
    i18n = get_i18n()
    name = callback.from_user.first_name or ""
    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.HOME_WELCOME, name=name),
        reply_markup=build_home_keyboard(role),
    )
    await callback.answer()


async def handle_search_result_section(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message or not callback.data:
        return

    section_id_str = callback.data.replace(CallbackPrefixes.SEARCH_RESULT_SECTION, "")
    try:
        section_id = int(section_id_str)
    except ValueError:
        await callback.answer()
        return

    logger.info(LogMessages.SEARCH_RESULT_SELECTED.format(
        user_id=callback.from_user.id, type="section", id=section_id
    ))

    state_service = get_state_service()
    state_service.clear_state(callback.from_user.id)

    from bot.handlers.sections import _show_section_detail
    role = kwargs.get("user_role", UserRole.USER)
    await _show_section_detail(callback, section_id, role)


async def handle_search_result_file(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message or not callback.data:
        return

    file_id_str = callback.data.replace(CallbackPrefixes.SEARCH_RESULT_FILE, "")
    try:
        file_id = int(file_id_str)
    except ValueError:
        await callback.answer()
        return

    logger.info(LogMessages.SEARCH_RESULT_SELECTED.format(
        user_id=callback.from_user.id, type="file", id=file_id
    ))

    state_service = get_state_service()
    state_service.clear_state(callback.from_user.id)

    bot = callback.message.bot
    if not bot:
        await callback.answer()
        return

    from bot.models.file import FileStatus
    db = await get_db()
    i18n = get_i18n()
    async for session in db.get_session():
        file = await file_service.get_file(session, file_id)
        if file and file.status == FileStatus.PUBLISHED.value:
            await send_file_to_user(bot, callback.from_user.id, file)
        else:
            await callback.message.answer(i18n.get(I18nKeys.FILES_NOT_FOUND))

    await callback.answer()


def create_search_router() -> Router:
    router = Router(name="search")

    @router.message(_is_search_state)
    async def search_text_handler(message: Message, **kwargs: Any) -> None:
        if not message.from_user or not message.text:
            return

        user_id = message.from_user.id
        query = message.text.strip()
        i18n = get_i18n()

        if len(query) < 2:
            await message.answer(
                i18n.get(I18nKeys.SEARCH_QUERY_TOO_SHORT),
                reply_markup=_build_search_back_keyboard(),
            )
            return

        logger.info(LogMessages.SEARCH_QUERY.format(user_id=user_id, query=query))

        sections = []
        files = []
        db = await get_db()
        async for session in db.get_session():
            sections = await section_service.search_sections(session, query, limit=MAX_RESULTS)
            files = await file_service.search_files(session, query, limit=MAX_RESULTS)

        total = len(sections) + len(files)
        logger.info(LogMessages.SEARCH_RESULTS.format(
            user_id=user_id, sections=len(sections), files=len(files)
        ))

        if total == 0:
            await message.answer(
                i18n.get(I18nKeys.SEARCH_NO_RESULTS),
                reply_markup=_build_search_back_keyboard(),
            )
            return

        title = i18n.get(I18nKeys.SEARCH_RESULTS_TITLE, query=query, count=total)
        keyboard = _build_results_keyboard(sections, files)
        await message.answer(title, reply_markup=keyboard)

    return router
