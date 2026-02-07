import logging
from typing import Any, Dict, List, Optional

from aiogram import Bot, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.core.constants import LogMessages, I18nKeys, CallbackPrefixes, AuditActions
from bot.core.database import get_db
from bot.services.i18n import get_i18n
from bot.services.state import get_state_service
from bot.services.files import file_service, send_file_to_user, FILES_PER_PAGE
from bot.services.audit import audit_service
from bot.services.permissions import has_permission, check_permission_and_notify, Permission
from bot.models.user import UserRole
from bot.models.file import File, FileStatus

logger = logging.getLogger("bot")

STATES = {
    "UPLOAD": "file_upload",
}

_storage_channel_id: int = 0


def set_storage_channel_id(channel_id: int) -> None:
    global _storage_channel_id
    _storage_channel_id = channel_id


def get_storage_channel_id() -> int:
    return _storage_channel_id


def _extract_file_info(message: Message) -> Optional[Dict[str, Any]]:
    if message.document:
        return {
            "file_id": message.document.file_id,
            "file_unique_id": message.document.file_unique_id,
            "name": message.document.file_name or f"doc_{message.document.file_unique_id}",
            "file_type": "document",
            "size": message.document.file_size,
        }
    elif message.photo:
        photo = message.photo[-1]
        return {
            "file_id": photo.file_id,
            "file_unique_id": photo.file_unique_id,
            "name": f"photo_{photo.file_unique_id}.jpg",
            "file_type": "photo",
            "size": photo.file_size,
        }
    elif message.video:
        return {
            "file_id": message.video.file_id,
            "file_unique_id": message.video.file_unique_id,
            "name": message.video.file_name or f"video_{message.video.file_unique_id}.mp4",
            "file_type": "video",
            "size": message.video.file_size,
        }
    elif message.audio:
        return {
            "file_id": message.audio.file_id,
            "file_unique_id": message.audio.file_unique_id,
            "name": message.audio.file_name or f"audio_{message.audio.file_unique_id}.mp3",
            "file_type": "audio",
            "size": message.audio.file_size,
        }
    elif message.voice:
        return {
            "file_id": message.voice.file_id,
            "file_unique_id": message.voice.file_unique_id,
            "name": f"voice_{message.voice.file_unique_id}.ogg",
            "file_type": "voice",
            "size": message.voice.file_size,
        }
    elif message.video_note:
        return {
            "file_id": message.video_note.file_id,
            "file_unique_id": message.video_note.file_unique_id,
            "name": f"videonote_{message.video_note.file_unique_id}.mp4",
            "file_type": "video_note",
            "size": message.video_note.file_size,
        }
    elif message.animation:
        return {
            "file_id": message.animation.file_id,
            "file_unique_id": message.animation.file_unique_id,
            "name": message.animation.file_name or f"animation_{message.animation.file_unique_id}.gif",
            "file_type": "animation",
            "size": message.animation.file_size,
        }
    elif message.sticker:
        return {
            "file_id": message.sticker.file_id,
            "file_unique_id": message.sticker.file_unique_id,
            "name": f"sticker_{message.sticker.file_unique_id}",
            "file_type": "sticker",
            "size": message.sticker.file_size,
        }
    return None


async def _forward_to_storage(bot: Bot, message: Message) -> Optional[str]:
    channel_id = get_storage_channel_id()
    if channel_id == 0:
        logger.warning(LogMessages.STORAGE_CHANNEL_NOT_SET)
        return None

    try:
        forwarded = await message.forward(chat_id=channel_id)
        logger.debug(LogMessages.FILE_FORWARDED.format(file_id=message.message_id))
        return str(forwarded.message_id)
    except Exception as e:
        logger.error(f"Failed to forward to storage: {e}")
        return None


async def _send_file_to_user(bot: Bot, chat_id: int, file: File) -> bool:
    return await send_file_to_user(bot, chat_id, file)


def _build_file_list_keyboard(
    files: List[File],
    section_id: int,
    page: int,
    total_pages: int,
    role: UserRole,
) -> InlineKeyboardMarkup:
    i18n = get_i18n()
    buttons: List[List[InlineKeyboardButton]] = []

    file_type_emoji = {
        "document": "📄", "photo": "🖼", "video": "🎬",
        "audio": "🎵", "voice": "🎤", "video_note": "📹",
        "animation": "🎞", "sticker": "🏷",
    }

    for f in files:
        emoji = file_type_emoji.get(f.file_type, "📄")
        display_name = f.name
        if len(display_name) > 40:
            display_name = display_name[:37] + "..."
        buttons.append([InlineKeyboardButton(
            text=f"{emoji} {display_name}",
            callback_data=f"{CallbackPrefixes.FILE_VIEW}{f.id}",
        )])

    nav_row: List[InlineKeyboardButton] = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(
            text=i18n.get(I18nKeys.FILES_PAGE_PREV),
            callback_data=f"{CallbackPrefixes.FILE_PAGE}{section_id}:{page - 1}",
        ))
    if total_pages > 1:
        nav_row.append(InlineKeyboardButton(
            text=i18n.get(I18nKeys.FILES_PAGE_INFO, page=page, total=total_pages),
            callback_data="noop",
        ))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(
            text=i18n.get(I18nKeys.FILES_PAGE_NEXT),
            callback_data=f"{CallbackPrefixes.FILE_PAGE}{section_id}:{page + 1}",
        ))
    if nav_row:
        buttons.append(nav_row)

    if has_permission(role, Permission.UPLOAD_FILE):
        buttons.append([InlineKeyboardButton(
            text=i18n.get(I18nKeys.FILES_BTN_UPLOAD),
            callback_data=f"{CallbackPrefixes.FILE_UPLOAD}{section_id}",
        )])

    buttons.append([InlineKeyboardButton(
        text=i18n.get(I18nKeys.SECTIONS_BTN_BACK),
        callback_data=f"{CallbackPrefixes.SECTION_VIEW}{section_id}",
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def handle_file_upload_start(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message or not callback.data:
        return

    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.UPLOAD_FILE):
        return

    i18n = get_i18n()
    channel_id = get_storage_channel_id()
    if channel_id == 0:
        await callback.answer(i18n.get(I18nKeys.FILES_STORAGE_NOT_SET), show_alert=True)
        return

    try:
        section_id = int(callback.data.replace(CallbackPrefixes.FILE_UPLOAD, ""))
    except (ValueError, IndexError):
        return

    state_service = get_state_service()
    state_service.set_state(callback.from_user.id, STATES["UPLOAD"], {
        "section_id": section_id,
        "uploaded_count": 0,
    })

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.FILES_BTN_DONE),
            callback_data=CallbackPrefixes.FILE_DONE,
        )],
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.FILES_BTN_CANCEL),
            callback_data=CallbackPrefixes.FILE_CANCEL,
        )],
    ])

    await callback.message.edit_text(
        i18n.get(I18nKeys.FILES_UPLOAD_PROMPT),
        reply_markup=keyboard,
    )  # type: ignore[union-attr]
    await callback.answer()


async def handle_file_done(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message:
        return

    state_service = get_state_service()
    state = state_service.get_state(callback.from_user.id)

    section_id = None
    uploaded_count = 0
    if state and state.name == STATES["UPLOAD"]:
        section_id = state.data.get("section_id")
        uploaded_count = state.data.get("uploaded_count", 0)
        state_service.clear_state(callback.from_user.id)

    i18n = get_i18n()
    if uploaded_count > 0:
        await callback.answer(
            i18n.get(I18nKeys.FILES_UPLOAD_COUNT, count=uploaded_count),
            show_alert=True,
        )
    else:
        await callback.answer(i18n.get(I18nKeys.FILES_CANCELLED))

    if section_id is not None:
        role = kwargs.get("user_role", UserRole.USER)
        await _show_section_files(callback, section_id, role=role)
    else:
        await callback.answer()


async def handle_file_cancel(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message:
        return

    state_service = get_state_service()
    state = state_service.get_state(callback.from_user.id)

    section_id = None
    if state and state.name == STATES["UPLOAD"]:
        section_id = state.data.get("section_id")

    state_service.clear_state(callback.from_user.id)

    i18n = get_i18n()
    await callback.answer(i18n.get(I18nKeys.FILES_CANCELLED))

    if section_id is not None:
        role = kwargs.get("user_role", UserRole.USER)
        await _show_section_files(callback, section_id, role=role)


async def handle_file_view(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message or not callback.data:
        return

    try:
        file_id = int(callback.data.replace(CallbackPrefixes.FILE_VIEW, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()
    file: Optional[File] = None
    section_ids: List[int] = []

    async for session in db.get_session():
        file = await file_service.get_file(session, file_id)
        if file:
            section_ids = await file_service.get_file_section_ids(session, file_id)

    if file is None:
        await callback.answer(i18n.get(I18nKeys.FILES_NOT_FOUND), show_alert=True)
        return

    bot = callback.bot
    if bot is None:
        return

    success = await _send_file_to_user(bot, callback.from_user.id, file)
    if success:
        logger.debug(LogMessages.FILE_SENT.format(
            file_id=file_id, user_id=callback.from_user.id
        ))

    role = kwargs.get("user_role", UserRole.USER)
    admin_buttons: List[List[InlineKeyboardButton]] = []

    if has_permission(role, Permission.MANAGE_FILES):
        admin_buttons.append([
            InlineKeyboardButton(
                text=i18n.get(I18nKeys.FILES_BTN_DELETE),
                callback_data=f"{CallbackPrefixes.FILE_DELETE}{file_id}",
            ),
        ])

    if section_ids:
        back_section = section_ids[0]
        admin_buttons.append([InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTIONS_BTN_BACK),
            callback_data=f"{CallbackPrefixes.SECTION_VIEW}{back_section}",
        )])

    if admin_buttons:
        keyboard = InlineKeyboardMarkup(inline_keyboard=admin_buttons)
        await callback.message.edit_reply_markup(reply_markup=keyboard)  # type: ignore[union-attr]

    await callback.answer()


async def handle_file_delete(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message or not callback.data:
        return

    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_FILES):
        return

    try:
        file_id = int(callback.data.replace(CallbackPrefixes.FILE_DELETE, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()
    section_ids: List[int] = []

    async for session in db.get_session():
        file = await file_service.get_file(session, file_id)
        if file is None:
            await callback.answer(i18n.get(I18nKeys.FILES_NOT_FOUND), show_alert=True)
            return
        section_ids = await file_service.get_file_section_ids(session, file_id)

        back_section = section_ids[0] if section_ids else 0
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=i18n.get(I18nKeys.FILES_BTN_CONFIRM_DELETE),
                callback_data=f"{CallbackPrefixes.FILE_CONFIRM_DELETE}{file_id}",
            )],
            [InlineKeyboardButton(
                text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_CANCEL),
                callback_data=f"{CallbackPrefixes.SECTION_VIEW}{back_section}" if back_section else CallbackPrefixes.HOME,
            )],
        ])

        await callback.message.edit_text(
            i18n.get(I18nKeys.FILES_DELETE_CONFIRM, name=file.name),
            reply_markup=keyboard,
        )  # type: ignore[union-attr]
        await callback.answer()


async def handle_file_confirm_delete(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message or not callback.data:
        return

    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_FILES):
        return

    try:
        file_id = int(callback.data.replace(CallbackPrefixes.FILE_CONFIRM_DELETE, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()
    section_ids: List[int] = []

    async for session in db.get_session():
        section_ids = await file_service.get_file_section_ids(session, file_id)
        deleted = await file_service.soft_delete_file(session, file_id)
        if deleted is None:
            await callback.answer(i18n.get(I18nKeys.FILES_NOT_FOUND), show_alert=True)
            return

        await audit_service.log_action(
            session, callback.from_user.id,
            AuditActions.FILE_DELETED,
            f"file_id={file_id} name={deleted.name}",
        )

    await callback.answer(i18n.get(I18nKeys.FILES_DELETED), show_alert=True)

    if section_ids:
        await _show_section_files(callback, section_ids[0], role=role)


async def handle_file_page(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.message:
        return

    try:
        data = callback.data.replace(CallbackPrefixes.FILE_PAGE, "")
        parts = data.split(":")
        section_id = int(parts[0])
        page = int(parts[1])
    except (ValueError, IndexError):
        return

    role = kwargs.get("user_role", UserRole.USER)
    await _show_section_files(callback, section_id, page=page, role=role)


async def _show_section_files(
    callback: CallbackQuery,
    section_id: int,
    page: int = 1,
    role: UserRole = UserRole.USER,
) -> None:
    if not callback.message:
        return

    i18n = get_i18n()
    db = await get_db()
    files: List[File] = []
    total_pages = 1

    async for session in db.get_session():
        files, total_pages = await file_service.list_files_by_section(
            session, section_id, page=page,
        )

    from bot.services.sections import section_service
    section_name = ""
    async for session in db.get_session():
        section = await section_service.get_section(session, section_id)
        if section:
            section_name = section.name

    if files:
        title = f"<b>{section_name}</b>\n{i18n.get(I18nKeys.FILES_TITLE)}"
    else:
        title = f"<b>{section_name}</b>\n{i18n.get(I18nKeys.FILES_EMPTY)}"

    keyboard = _build_file_list_keyboard(files, section_id, page, total_pages, role)

    await callback.message.edit_text(title, reply_markup=keyboard)  # type: ignore[union-attr]
    await callback.answer()


def _is_file_upload_state(message: Message) -> bool:
    if not message.from_user:
        return False
    state_service = get_state_service()
    state = state_service.get_state(message.from_user.id)
    if state is None:
        return False
    return state.name == STATES["UPLOAD"]


async def _process_single_file(
    message: Message,
    bot: Bot,
    section_id: int,
    user_id: int,
) -> Optional[str]:
    file_info = _extract_file_info(message)
    if file_info is None:
        return None

    i18n = get_i18n()
    db = await get_db()

    async for session in db.get_session():
        existing = await file_service.check_duplicate(session, file_info["file_unique_id"])
        if existing:
            linked = await file_service.link_file_to_section(session, existing.id, section_id)
            if linked:
                await audit_service.log_action(
                    session, user_id,
                    AuditActions.FILE_LINKED,
                    f"file_id={existing.id} section_id={section_id}",
                )
            return "duplicate"

    await _forward_to_storage(bot, message)

    caption = message.caption if message.caption else None

    async for session in db.get_session():
        file = await file_service.create_file(
            session,
            file_id=file_info["file_id"],
            file_unique_id=file_info["file_unique_id"],
            name=file_info["name"],
            file_type=file_info["file_type"],
            uploaded_by=user_id,
            size=file_info.get("size"),
            caption=caption,
        )
        await file_service.link_file_to_section(session, file.id, section_id)
        await audit_service.log_action(
            session, user_id,
            AuditActions.FILE_UPLOADED,
            f"file_id={file.id} name={file_info['name']} section_id={section_id}",
        )

    return file_info["name"]


def create_files_router() -> Router:
    router = Router(name="files")

    @router.message(_is_file_upload_state)
    async def files_upload_handler(message: Message, **kwargs: Any) -> None:
        if not message.from_user:
            return

        user_id = message.from_user.id
        role = kwargs.get("user_role", UserRole.USER)

        if not has_permission(role, Permission.UPLOAD_FILE):
            state_service = get_state_service()
            state_service.clear_state(user_id)
            i18n = get_i18n()
            await message.answer(i18n.get(I18nKeys.ERROR_PERMISSION_DENIED))
            return

        state_service = get_state_service()
        state = state_service.get_state(user_id)
        if state is None:
            return

        section_id = state.data.get("section_id")
        if section_id is None:
            return

        file_info = _extract_file_info(message)
        if file_info is None:
            return

        bot = message.bot
        if bot is None:
            return

        i18n = get_i18n()

        result = await _process_single_file(message, bot, section_id, user_id)

        if result == "duplicate":
            await message.reply(i18n.get(I18nKeys.FILES_UPLOAD_DUPLICATE))
        elif result:
            await message.reply(i18n.get(I18nKeys.FILES_UPLOAD_SUCCESS, name=result))
            uploaded_count = state.data.get("uploaded_count", 0) + 1
            state_service.set_state(user_id, STATES["UPLOAD"], {
                "section_id": section_id,
                "uploaded_count": uploaded_count,
            })
        else:
            await message.reply(i18n.get(I18nKeys.FILES_UPLOAD_ERROR))

    return router


async def handle_deep_link_file(bot: Bot, message: Message, file_id: int) -> bool:
    i18n = get_i18n()
    db = await get_db()
    file: Optional[File] = None

    async for session in db.get_session():
        file = await file_service.get_file(session, file_id)
        if file is None or file.status != FileStatus.PUBLISHED.value:
            await message.answer(i18n.get(I18nKeys.FILES_DEEP_LINK_NOT_FOUND))
            return False

    if file is None:
        await message.answer(i18n.get(I18nKeys.FILES_DEEP_LINK_NOT_FOUND))
        return False

    if message.from_user:
        logger.info(LogMessages.DEEP_LINK.format(
            user_id=message.from_user.id, file_id=file_id
        ))

    success = await _send_file_to_user(bot, message.chat.id, file)
    if not success:
        await message.answer(i18n.get(I18nKeys.FILES_UPLOAD_ERROR))
    return success
