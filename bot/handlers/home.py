import logging
from typing import Any, Dict

from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from bot.core.constants import LogMessages, I18nKeys, CallbackPrefixes
from bot.services.i18n import get_i18n
from bot.services.state import get_state_service
from bot.services.permissions import has_permission, Permission
from bot.models.user import UserRole

logger = logging.getLogger("bot")


def build_home_keyboard(role: UserRole = UserRole.USER) -> InlineKeyboardMarkup:
    i18n = get_i18n()
    buttons = [
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.HOME_BTN_SECTIONS),
            callback_data=CallbackPrefixes.SECTIONS,
        )],
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.HOME_BTN_SEARCH),
            callback_data=CallbackPrefixes.SEARCH,
        )],
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.HOME_BTN_TOOLS),
            callback_data=CallbackPrefixes.TOOLS,
        )],
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.HOME_BTN_CONTRIBUTE),
            callback_data=CallbackPrefixes.CONTRIBUTE,
        )],
        [
            InlineKeyboardButton(
                text=i18n.get(I18nKeys.HOME_BTN_ABOUT),
                callback_data=CallbackPrefixes.ABOUT,
            ),
            InlineKeyboardButton(
                text=i18n.get(I18nKeys.HOME_BTN_CONTACT),
                callback_data=CallbackPrefixes.CONTACT,
            ),
        ],
    ]

    if has_permission(role, Permission.VIEW_ADMIN_PANEL):
        buttons.append([InlineKeyboardButton(
            text=i18n.get(I18nKeys.HOME_BTN_ADMIN_PANEL),
            callback_data=CallbackPrefixes.ADMIN_PANEL,
        )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_back_keyboard() -> InlineKeyboardMarkup:
    i18n = get_i18n()
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.HOME_BTN_BACK),
            callback_data=CallbackPrefixes.BACK,
        )],
    ])


async def _send_home(callback: CallbackQuery, role: UserRole = UserRole.USER) -> None:
    if not callback.from_user or not callback.message:
        return
    user_id = callback.from_user.id
    state_service = get_state_service()
    state_service.clear_state(user_id)

    i18n = get_i18n()
    name = callback.from_user.first_name or ""
    welcome_text = i18n.get(I18nKeys.HOME_WELCOME, name=name)

    await callback.message.edit_text(welcome_text, reply_markup=build_home_keyboard(role))  # type: ignore[union-attr]
    await callback.answer()
    logger.debug(LogMessages.HOME_DISPLAYED.format(user_id=user_id))


async def _send_placeholder(callback: CallbackQuery, button_name: str, state_name: str) -> None:
    if not callback.from_user or not callback.message:
        return
    user_id = callback.from_user.id
    logger.info(LogMessages.BUTTON_PRESSED.format(button=button_name, user_id=user_id))

    state_service = get_state_service()
    state_service.set_state(user_id, state_name)

    i18n = get_i18n()
    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.HOME_PLACEHOLDER),
        reply_markup=build_back_keyboard(),
    )
    await callback.answer()


async def _send_text_page(callback: CallbackQuery, button_name: str, state_name: str, text_key: str) -> None:
    if not callback.from_user or not callback.message:
        return
    user_id = callback.from_user.id
    logger.info(LogMessages.BUTTON_PRESSED.format(button=button_name, user_id=user_id))

    state_service = get_state_service()
    state_service.set_state(user_id, state_name)

    i18n = get_i18n()
    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(text_key),
        reply_markup=build_back_keyboard(),
    )
    await callback.answer()


def create_home_router() -> Router:
    router = Router(name="home")

    @router.message(Command("start"))
    async def start_command(message: Message, **kwargs: Any) -> None:
        if not message.from_user:
            return
        user_id = message.from_user.id
        logger.info(LogMessages.START_COMMAND.format(user_id=user_id))

        state_service = get_state_service()
        state_service.clear_state(user_id)

        role = kwargs.get("user_role", UserRole.USER)

        payload = message.text.split(maxsplit=1)[1] if message.text and len(message.text.split()) > 1 else ""

        if payload.startswith("file_"):
            try:
                file_id = int(payload.replace("file_", ""))
                from bot.handlers.files import handle_deep_link_file
                bot = message.bot
                if bot:
                    await handle_deep_link_file(bot, message, file_id)
                    return
            except (ValueError, IndexError):
                pass

        i18n = get_i18n()
        name = message.from_user.first_name or ""
        welcome_text = i18n.get(I18nKeys.HOME_WELCOME, name=name)

        await message.answer(welcome_text, reply_markup=build_home_keyboard(role))
        logger.debug(LogMessages.HOME_DISPLAYED.format(user_id=user_id))

    return router


async def handle_home_callback(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    role = kwargs.get("user_role", UserRole.USER)
    await _send_home(callback, role)


async def handle_contribute_callback(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    from bot.handlers.admin import handle_contribute_upload
    await handle_contribute_upload(callback, kwargs)


async def handle_about_callback(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    await _send_text_page(callback, "about", "about", I18nKeys.HOME_ABOUT_TEXT)


async def handle_contact_callback(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    await _send_text_page(callback, "contact", "contact", I18nKeys.HOME_CONTACT_TEXT)


async def handle_tools_callback(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    await _send_placeholder(callback, "tools", "tools")


def build_admin_panel_keyboard() -> InlineKeyboardMarkup:
    i18n = get_i18n()
    buttons = [
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.ADMIN_BTN_SECTIONS),
            callback_data=CallbackPrefixes.ADMIN_SECTIONS,
        )],
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.ADMIN_BTN_FILES),
            callback_data=CallbackPrefixes.ADMIN_FILES,
        )],
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.ADMIN_BTN_MODERATORS),
            callback_data=CallbackPrefixes.ADMIN_MODERATORS,
        )],
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.ADMIN_BTN_TEXTS),
            callback_data=CallbackPrefixes.ADMIN_TEXTS,
        )],
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.ADMIN_BTN_CONTRIBUTIONS),
            callback_data=CallbackPrefixes.ADMIN_CONTRIBUTIONS,
        )],
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.ADMIN_BTN_AUDIT),
            callback_data=CallbackPrefixes.ADMIN_AUDIT,
        )],
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTIONS_BTN_HOME),
            callback_data=CallbackPrefixes.HOME,
        )],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def handle_admin_panel_callback(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    from bot.services.permissions import check_permission_and_notify
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.VIEW_ADMIN_PANEL):
        return

    if not callback.from_user or not callback.message:
        return

    i18n = get_i18n()
    state_service = get_state_service()
    state_service.set_state(callback.from_user.id, "admin_panel")

    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.ADMIN_PANEL_TEXT),
        reply_markup=build_admin_panel_keyboard(),
    )
    await callback.answer()


async def handle_admin_sections_callback(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    from bot.services.permissions import check_permission_and_notify
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SECTIONS):
        return
    from bot.handlers.sections import handle_sections_callback
    await handle_sections_callback(callback, kwargs)


async def handle_back_callback(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user:
        return
    logger.info(LogMessages.BACK_PRESSED.format(user_id=callback.from_user.id))
    role = kwargs.get("user_role", UserRole.USER)
    await _send_home(callback, role)
