import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from bot.core.constants import LogMessages, I18nKeys, CallbackPrefixes, AuditActions
from bot.core.database import get_db
from bot.services.i18n import get_i18n
from bot.services.state import get_state_service
from bot.services.files import file_service
from bot.services.sections import section_service
from bot.services.user import user_service
from bot.services.audit import audit_service
from bot.services.moderator import moderator_service
from bot.services.permissions import has_permission, check_permission_and_notify, Permission
from bot.services.settings_manager import settings_manager
from bot.services.stats import stats_service
from bot.services.backup import backup_service
from bot.models.user import UserRole
from bot.models.file import File, FileStatus
from bot.models.section import Section

logger = logging.getLogger("bot")

ADMIN_FILES_PER_PAGE = 5
ADMIN_AUDIT_PER_PAGE = 8
ADMIN_CONTRIB_PER_PAGE = 5

STATES = {
    "MOD_ADD": "admin_mod_add",
    "TEXT_EDIT": "admin_text_edit",
    "CONTRIBUTE_UPLOAD": "contribute_upload",
    "SUB_ADD_CHANNEL": "admin_sub_add_channel",
    "BROADCAST_TEXT": "admin_broadcast_text",
    "BROADCAST_FILE": "admin_broadcast_file",
    "BAN_BLOCK": "admin_ban_block",
    "BAN_UNBLOCK": "admin_ban_unblock",
    "MAINT_MESSAGE": "admin_maintenance_message",
    "BACKUP_RESTORE": "admin_backup_restore",
}


def _admin_back_button() -> InlineKeyboardButton:
    i18n = get_i18n()
    return InlineKeyboardButton(
        text=i18n.get(I18nKeys.ADMIN_BTN_BACK),
        callback_data=CallbackPrefixes.ADMIN_PANEL,
    )


async def handle_admin_files(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_FILES):
        return
    await _show_admin_files(callback, page=1)


async def _show_admin_files(callback: CallbackQuery, page: int = 1) -> None:
    if not callback.message:
        return

    i18n = get_i18n()
    db = await get_db()
    files: List[File] = []
    total = 0

    async for session in db.get_session():
        files, total = await file_service.list_all_files(
            session, page=page, per_page=ADMIN_FILES_PER_PAGE
        )

    if not files:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[_admin_back_button()]])
        await callback.message.edit_text(  # type: ignore[union-attr]
            i18n.get(I18nKeys.ADMIN_FILES_EMPTY),
            reply_markup=keyboard,
        )  # type: ignore[union-attr]
        await callback.answer()
        return

    buttons: List[List[InlineKeyboardButton]] = []
    file_type_emoji = {
        "document": "📄", "photo": "🖼", "video": "🎬",
        "audio": "🎵", "voice": "🎤", "video_note": "📹",
        "animation": "🎞", "sticker": "🏷",
    }

    for f in files:
        emoji = file_type_emoji.get(f.file_type, "📄")
        status_icon = "✅" if f.status == FileStatus.PUBLISHED.value else "📝"
        display_name = f.name
        if len(display_name) > 35:
            display_name = display_name[:32] + "..."
        buttons.append([InlineKeyboardButton(
            text=f"{emoji}{status_icon} {display_name}",
            callback_data=f"{CallbackPrefixes.ADMIN_FILE_DETAIL}{f.id}",
        )])

    total_pages = max(1, (total + ADMIN_FILES_PER_PAGE - 1) // ADMIN_FILES_PER_PAGE)
    nav_row: List[InlineKeyboardButton] = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(
            text=i18n.get(I18nKeys.FILES_PAGE_PREV),
            callback_data=f"{CallbackPrefixes.ADMIN_FILES_PAGE}{page - 1}",
        ))
    if total_pages > 1:
        nav_row.append(InlineKeyboardButton(
            text=i18n.get(I18nKeys.FILES_PAGE_INFO, page=page, total=total_pages),
            callback_data="noop",
        ))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(
            text=i18n.get(I18nKeys.FILES_PAGE_NEXT),
            callback_data=f"{CallbackPrefixes.ADMIN_FILES_PAGE}{page + 1}",
        ))
    if nav_row:
        buttons.append(nav_row)

    buttons.append([_admin_back_button()])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.ADMIN_FILES_TITLE, count=total),
        reply_markup=keyboard,
    )  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_files_page(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_FILES):
        return
    try:
        page = int(callback.data.replace(CallbackPrefixes.ADMIN_FILES_PAGE, ""))
    except (ValueError, IndexError):
        return
    await _show_admin_files(callback, page=page)


async def handle_admin_file_detail(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_FILES):
        return

    try:
        file_id = int(callback.data.replace(CallbackPrefixes.ADMIN_FILE_DETAIL, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()
    file: Optional[File] = None
    sections: List[Section] = []
    uploader_name = ""

    async for session in db.get_session():
        file = await file_service.get_file(session, file_id)
        if file is None:
            await callback.answer(i18n.get(I18nKeys.FILES_NOT_FOUND), show_alert=True)
            return
        sections = await file_service.get_file_sections(session, file_id)
        uploader = await user_service.get_by_id(session, file.uploaded_by)
        uploader_name = uploader.first_name if uploader else str(file.uploaded_by)

    if file is None:
        return

    section_names = ", ".join(s.name for s in sections) if sections else "-"
    status_text = "✅" if file.status == FileStatus.PUBLISHED.value else "📝"

    text = i18n.get(
        I18nKeys.ADMIN_FILE_DETAIL_TEXT,
        name=file.name,
        file_type=file.file_type,
        status=status_text,
        uploaded_by=uploader_name,
        sections=section_names,
    )

    buttons: List[List[InlineKeyboardButton]] = []

    if file.status == FileStatus.PUBLISHED.value:
        buttons.append([InlineKeyboardButton(
            text=i18n.get(I18nKeys.ADMIN_FILE_BTN_DRAFT),
            callback_data=f"{CallbackPrefixes.ADMIN_FILE_TOGGLE_STATUS}{file_id}",
        )])
    else:
        buttons.append([InlineKeyboardButton(
            text=i18n.get(I18nKeys.ADMIN_FILE_BTN_PUBLISH),
            callback_data=f"{CallbackPrefixes.ADMIN_FILE_TOGGLE_STATUS}{file_id}",
        )])

    buttons.append([
        InlineKeyboardButton(
            text=i18n.get(I18nKeys.ADMIN_FILE_BTN_LINK),
            callback_data=f"{CallbackPrefixes.ADMIN_FILE_LINK_PICK}{file_id}",
        ),
        InlineKeyboardButton(
            text=i18n.get(I18nKeys.ADMIN_FILE_BTN_UNLINK),
            callback_data=f"{CallbackPrefixes.ADMIN_FILE_UNLINK_PICK}{file_id}",
        ),
    ])

    buttons.append([_admin_back_button()])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_file_toggle_status(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_FILES):
        return

    try:
        file_id = int(callback.data.replace(CallbackPrefixes.ADMIN_FILE_TOGGLE_STATUS, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()
    new_status = ""

    async for session in db.get_session():
        file = await file_service.get_file(session, file_id)
        if file is None:
            await callback.answer(i18n.get(I18nKeys.FILES_NOT_FOUND), show_alert=True)
            return

        if file.status == FileStatus.PUBLISHED.value:
            new_status = FileStatus.DRAFT.value
        else:
            new_status = FileStatus.PUBLISHED.value

        await file_service.set_file_status(session, file_id, new_status)
        await audit_service.log_action(
            session, callback.from_user.id,
            AuditActions.FILE_STATUS_CHANGED,
            f"file_id={file_id} status={new_status}",
        )
        logger.info(LogMessages.FILE_STATUS_CHANGED.format(
            file_id=file_id, status=new_status, user_id=callback.from_user.id
        ))

    status_text = "✅" if new_status == FileStatus.PUBLISHED.value else "📝"
    await callback.answer(
        i18n.get(I18nKeys.ADMIN_FILE_STATUS_CHANGED, status=status_text),
        show_alert=True,
    )

    cb_data = callback.data
    object.__setattr__(callback, 'data', f"{CallbackPrefixes.ADMIN_FILE_DETAIL}{file_id}")
    await handle_admin_file_detail(callback, kwargs)
    object.__setattr__(callback, 'data', cb_data)


async def handle_admin_file_link_pick(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_FILES):
        return

    try:
        file_id = int(callback.data.replace(CallbackPrefixes.ADMIN_FILE_LINK_PICK, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()
    all_sections: List[Section] = []

    async for session in db.get_session():
        all_sections = await section_service.list_sections(session, parent_id=None, include_inactive=False)

    if not all_sections:
        await callback.answer(i18n.get(I18nKeys.ADMIN_FILE_NO_SECTIONS), show_alert=True)
        return

    buttons: List[List[InlineKeyboardButton]] = []
    for sec in all_sections:
        buttons.append([InlineKeyboardButton(
            text=f"📁 {sec.name}",
            callback_data=f"{CallbackPrefixes.ADMIN_FILE_LINK_SEC}{file_id}:{sec.id}",
        )])
    buttons.append([InlineKeyboardButton(
        text=i18n.get(I18nKeys.ADMIN_BTN_BACK),
        callback_data=f"{CallbackPrefixes.ADMIN_FILE_DETAIL}{file_id}",
    )])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.ADMIN_FILE_SELECT_SECTION_LINK),
        reply_markup=keyboard,
    )  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_file_link_sec(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_FILES):
        return

    try:
        parts = callback.data.replace(CallbackPrefixes.ADMIN_FILE_LINK_SEC, "").split(":")
        file_id = int(parts[0])
        section_id = int(parts[1])
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()

    async for session in db.get_session():
        linked = await file_service.link_file_to_section(session, file_id, section_id)
        if linked:
            await audit_service.log_action(
                session, callback.from_user.id,
                AuditActions.FILE_LINKED,
                f"file_id={file_id} section_id={section_id}",
            )
            await callback.answer(i18n.get(I18nKeys.ADMIN_FILE_LINKED), show_alert=True)
        else:
            await callback.answer(i18n.get(I18nKeys.FILES_ALREADY_LINKED), show_alert=True)

    cb_data = callback.data
    object.__setattr__(callback, 'data', f"{CallbackPrefixes.ADMIN_FILE_DETAIL}{file_id}")
    await handle_admin_file_detail(callback, kwargs)
    object.__setattr__(callback, 'data', cb_data)


async def handle_admin_file_unlink_pick(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_FILES):
        return

    try:
        file_id = int(callback.data.replace(CallbackPrefixes.ADMIN_FILE_UNLINK_PICK, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()
    sections: List[Section] = []

    async for session in db.get_session():
        sections = await file_service.get_file_sections(session, file_id)

    if not sections:
        await callback.answer(i18n.get(I18nKeys.ADMIN_FILE_NO_SECTIONS), show_alert=True)
        return

    buttons: List[List[InlineKeyboardButton]] = []
    for sec in sections:
        buttons.append([InlineKeyboardButton(
            text=f"📁 {sec.name}",
            callback_data=f"{CallbackPrefixes.ADMIN_FILE_UNLINK_SEC}{file_id}:{sec.id}",
        )])
    buttons.append([InlineKeyboardButton(
        text=i18n.get(I18nKeys.ADMIN_BTN_BACK),
        callback_data=f"{CallbackPrefixes.ADMIN_FILE_DETAIL}{file_id}",
    )])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.ADMIN_FILE_SELECT_SECTION_UNLINK),
        reply_markup=keyboard,
    )  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_file_unlink_sec(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_FILES):
        return

    try:
        parts = callback.data.replace(CallbackPrefixes.ADMIN_FILE_UNLINK_SEC, "").split(":")
        file_id = int(parts[0])
        section_id = int(parts[1])
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()

    async for session in db.get_session():
        unlinked = await file_service.unlink_file_from_section(session, file_id, section_id)
        if unlinked:
            await audit_service.log_action(
                session, callback.from_user.id,
                AuditActions.FILE_UNLINKED,
                f"file_id={file_id} section_id={section_id}",
            )
            await callback.answer(i18n.get(I18nKeys.ADMIN_FILE_UNLINKED), show_alert=True)
        else:
            await callback.answer(i18n.get(I18nKeys.ADMIN_FILE_NO_SECTIONS), show_alert=True)

    cb_data = callback.data
    object.__setattr__(callback, 'data', f"{CallbackPrefixes.ADMIN_FILE_DETAIL}{file_id}")
    await handle_admin_file_detail(callback, kwargs)
    object.__setattr__(callback, 'data', cb_data)


async def handle_admin_moderators(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_USERS):
        return
    await _show_moderators_list(callback)


async def _show_moderators_list(callback: CallbackQuery) -> None:
    if not callback.message:
        return

    i18n = get_i18n()
    db = await get_db()
    moderators: List = []

    async for session in db.get_session():
        moderators = await user_service.list_moderators(session)

    buttons: List[List[InlineKeyboardButton]] = []

    if not moderators:
        title = i18n.get(I18nKeys.ADMIN_MODS_EMPTY)
    else:
        title = i18n.get(I18nKeys.ADMIN_MODS_TITLE)
        for mod in moderators:
            display = mod.first_name or str(mod.id)
            buttons.append([InlineKeyboardButton(
                text=f"👤 {display}",
                callback_data=f"{CallbackPrefixes.ADMIN_MOD_VIEW}{mod.id}",
            )])

    buttons.append([InlineKeyboardButton(
        text=i18n.get(I18nKeys.ADMIN_MOD_BTN_ADD),
        callback_data=CallbackPrefixes.ADMIN_MOD_ADD,
    )])
    buttons.append([_admin_back_button()])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(title, reply_markup=keyboard)  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_mod_view(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_USERS):
        return

    try:
        target_id = int(callback.data.replace(CallbackPrefixes.ADMIN_MOD_VIEW, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()

    async for session in db.get_session():
        user = await user_service.get_by_id(session, target_id)
        if user is None:
            await callback.answer(i18n.get(I18nKeys.ADMIN_MOD_NOT_FOUND), show_alert=True)
            return

        perms = await moderator_service.get_permissions(session, target_id)
        perm_lines = []
        if perms:
            perm_lines.append(f"{'✅' if perms.can_upload else '❌'} {i18n.get(I18nKeys.ADMIN_MOD_PERM_UPLOAD)}")
            perm_lines.append(f"{'✅' if perms.can_link else '❌'} {i18n.get(I18nKeys.ADMIN_MOD_PERM_LINK)}")
            perm_lines.append(f"{'✅' if perms.can_publish else '❌'} {i18n.get(I18nKeys.ADMIN_MOD_PERM_PUBLISH)}")
            perm_lines.append(f"{'✅' if perms.own_files_only else '❌'} {i18n.get(I18nKeys.ADMIN_MOD_PERM_OWN_ONLY)}")

        text = i18n.get(
            I18nKeys.ADMIN_MOD_DETAIL,
            name=user.first_name or "-",
            user_id=user.id,
            username=f"@{user.username}" if user.username else "-",
            permissions="\n".join(perm_lines) if perm_lines else "-",
        )

    buttons = [
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.ADMIN_MOD_BTN_PERMS),
            callback_data=f"{CallbackPrefixes.ADMIN_MOD_PERMS}{target_id}",
        )],
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.ADMIN_MOD_BTN_REMOVE),
            callback_data=f"{CallbackPrefixes.ADMIN_MOD_REMOVE}{target_id}",
        )],
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.ADMIN_BTN_BACK),
            callback_data=CallbackPrefixes.ADMIN_MODERATORS,
        )],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_mod_add(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_USERS):
        return

    i18n = get_i18n()
    state_service = get_state_service()
    state_service.set_state(callback.from_user.id, STATES["MOD_ADD"])

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_CANCEL),
            callback_data=CallbackPrefixes.ADMIN_MODERATORS,
        ),
    ]])

    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.ADMIN_MOD_ENTER_ID),
        reply_markup=keyboard,
    )  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_mod_remove(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_USERS):
        return

    try:
        target_id = int(callback.data.replace(CallbackPrefixes.ADMIN_MOD_REMOVE, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()
    target_user: Optional[Any] = None

    async for session in db.get_session():
        target_user = await user_service.get_by_id(session, target_id)
        if target_user is None:
            await callback.answer(i18n.get(I18nKeys.ADMIN_MOD_NOT_FOUND), show_alert=True)
            return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_CONFIRM),
            callback_data=f"{CallbackPrefixes.ADMIN_MOD_CONFIRM_REMOVE}{target_id}",
        )],
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_CANCEL),
            callback_data=f"{CallbackPrefixes.ADMIN_MOD_VIEW}{target_id}",
        )],
    ])

    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.ADMIN_MOD_CONFIRM_REMOVE, name=target_user.first_name if target_user else "-"),
        reply_markup=keyboard,
    )
    await callback.answer()


async def handle_admin_mod_confirm_remove(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_USERS):
        return

    try:
        target_id = int(callback.data.replace(CallbackPrefixes.ADMIN_MOD_CONFIRM_REMOVE, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()

    async for session in db.get_session():
        await user_service.set_role(session, target_id, UserRole.USER)
        await moderator_service.delete_permissions(session, target_id)
        await audit_service.log_action(
            session, callback.from_user.id,
            AuditActions.MODERATOR_REMOVED,
            f"target_id={target_id}",
        )
        logger.info(LogMessages.MODERATOR_REMOVED.format(
            target_id=target_id, admin_id=callback.from_user.id
        ))

    await callback.answer(i18n.get(I18nKeys.ADMIN_MOD_REMOVED), show_alert=True)
    await _show_moderators_list(callback)


async def handle_admin_mod_perms(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_USERS):
        return

    try:
        target_id = int(callback.data.replace(CallbackPrefixes.ADMIN_MOD_PERMS, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()
    perms: Optional[Any] = None

    async for session in db.get_session():
        perms = await moderator_service.get_permissions(session, target_id)
        if perms is None:
            perms = await moderator_service.create_permissions(session, target_id)

    if perms is None:
        return

    perm_fields = [
        ("can_upload", I18nKeys.ADMIN_MOD_PERM_UPLOAD),
        ("can_link", I18nKeys.ADMIN_MOD_PERM_LINK),
        ("can_publish", I18nKeys.ADMIN_MOD_PERM_PUBLISH),
        ("own_files_only", I18nKeys.ADMIN_MOD_PERM_OWN_ONLY),
    ]

    buttons: List[List[InlineKeyboardButton]] = []
    for field, label_key in perm_fields:
        val = getattr(perms, field, False)
        icon = "✅" if val else "❌"
        buttons.append([InlineKeyboardButton(
            text=f"{icon} {i18n.get(label_key)}",
            callback_data=f"{CallbackPrefixes.ADMIN_MOD_TOGGLE_PERM}{target_id}:{field}",
        )])

    buttons.append([InlineKeyboardButton(
        text=i18n.get(I18nKeys.ADMIN_BTN_BACK),
        callback_data=f"{CallbackPrefixes.ADMIN_MOD_VIEW}{target_id}",
    )])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.ADMIN_MOD_PERMS_TITLE),
        reply_markup=keyboard,
    )  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_mod_toggle_perm(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_USERS):
        return

    try:
        data = callback.data.replace(CallbackPrefixes.ADMIN_MOD_TOGGLE_PERM, "")
        parts = data.split(":")
        target_id = int(parts[0])
        field = parts[1]
    except (ValueError, IndexError):
        return

    valid_fields = {"can_upload", "can_link", "can_publish", "own_files_only"}
    if field not in valid_fields:
        return

    i18n = get_i18n()
    db = await get_db()

    async for session in db.get_session():
        updated = await moderator_service.toggle_permission(session, target_id, field)
        if updated is None:
            return
        new_val = getattr(updated, field, False)
        await audit_service.log_action(
            session, callback.from_user.id,
            AuditActions.MODERATOR_PERMS_UPDATED,
            f"target_id={target_id} field={field} value={new_val}",
        )
        logger.info(LogMessages.MODERATOR_PERMS_UPDATED.format(
            target_id=target_id, admin_id=callback.from_user.id
        ))

    await callback.answer(i18n.get(I18nKeys.ADMIN_MOD_PERMS_UPDATED), show_alert=True)

    cb_data = callback.data
    object.__setattr__(callback, 'data', f"{CallbackPrefixes.ADMIN_MOD_PERMS}{target_id}")
    await handle_admin_mod_perms(callback, kwargs)
    object.__setattr__(callback, 'data', cb_data)


async def handle_admin_texts(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SETTINGS):
        return

    i18n = get_i18n()
    editable_keys = [
        I18nKeys.HOME_WELCOME,
        I18nKeys.HOME_ABOUT_TEXT,
        I18nKeys.HOME_CONTACT_TEXT,
        I18nKeys.SECTIONS_TITLE,
        I18nKeys.FILES_UPLOAD_PROMPT,
        I18nKeys.CONTRIBUTE_PROMPT,
    ]

    buttons: List[List[InlineKeyboardButton]] = []
    for key in editable_keys:
        short_label = key.split(".")[-1]
        buttons.append([InlineKeyboardButton(
            text=f"📝 {short_label}",
            callback_data=f"{CallbackPrefixes.ADMIN_TEXT_EDIT}{key}",
        )])

    buttons.append([_admin_back_button()])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.ADMIN_TEXTS_TITLE),
        reply_markup=keyboard,
    )  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_text_edit(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SETTINGS):
        return

    key = callback.data.replace(CallbackPrefixes.ADMIN_TEXT_EDIT, "")

    i18n = get_i18n()
    current_text = i18n.get(key)

    state_service = get_state_service()
    state_service.set_state(callback.from_user.id, STATES["TEXT_EDIT"], data={"key": key})

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_CANCEL),
            callback_data=CallbackPrefixes.ADMIN_TEXTS,
        ),
    ]])

    display_text = i18n.get(I18nKeys.ADMIN_TEXT_CURRENT, label=key, text=current_text)
    await callback.message.edit_text(  # type: ignore[union-attr]
        display_text + "\n\n" + i18n.get(I18nKeys.ADMIN_TEXT_ENTER_NEW),
        reply_markup=keyboard,
    )
    await callback.answer()


async def handle_admin_contributions(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_FILES):
        return
    await _show_contributions(callback, page=1)


async def _show_contributions(callback: CallbackQuery, page: int = 1) -> None:
    if not callback.message:
        return

    i18n = get_i18n()
    db = await get_db()
    files: List[File] = []
    total = 0

    async for session in db.get_session():
        files, total = await file_service.get_pending_files(
            session, page=page, per_page=ADMIN_CONTRIB_PER_PAGE
        )

    if not files:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[_admin_back_button()]])
        await callback.message.edit_text(  # type: ignore[union-attr]
            i18n.get(I18nKeys.ADMIN_CONTRIB_EMPTY),
            reply_markup=keyboard,
        )  # type: ignore[union-attr]
        await callback.answer()
        return

    buttons: List[List[InlineKeyboardButton]] = []
    for f in files:
        display_name = f.name
        if len(display_name) > 35:
            display_name = display_name[:32] + "..."
        buttons.append([InlineKeyboardButton(
            text=f"📄 {display_name}",
            callback_data=f"{CallbackPrefixes.ADMIN_CONTRIB_VIEW}{f.id}",
        )])

    total_pages = max(1, (total + ADMIN_CONTRIB_PER_PAGE - 1) // ADMIN_CONTRIB_PER_PAGE)
    nav_row: List[InlineKeyboardButton] = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(
            text=i18n.get(I18nKeys.FILES_PAGE_PREV),
            callback_data=f"{CallbackPrefixes.ADMIN_CONTRIB_PAGE}{page - 1}",
        ))
    if total_pages > 1:
        nav_row.append(InlineKeyboardButton(
            text=i18n.get(I18nKeys.FILES_PAGE_INFO, page=page, total=total_pages),
            callback_data="noop",
        ))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(
            text=i18n.get(I18nKeys.FILES_PAGE_NEXT),
            callback_data=f"{CallbackPrefixes.ADMIN_CONTRIB_PAGE}{page + 1}",
        ))
    if nav_row:
        buttons.append(nav_row)

    buttons.append([_admin_back_button()])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.ADMIN_CONTRIB_TITLE, count=total),
        reply_markup=keyboard,
    )  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_contrib_page(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_FILES):
        return
    try:
        page = int(callback.data.replace(CallbackPrefixes.ADMIN_CONTRIB_PAGE, ""))
    except (ValueError, IndexError):
        return
    await _show_contributions(callback, page=page)


async def handle_admin_contrib_view(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_FILES):
        return

    try:
        file_id = int(callback.data.replace(CallbackPrefixes.ADMIN_CONTRIB_VIEW, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()
    file: Optional[Any] = None
    uploader_name: str = ""

    async for session in db.get_session():
        file = await file_service.get_file(session, file_id)
        if file is None:
            await callback.answer(i18n.get(I18nKeys.FILES_NOT_FOUND), show_alert=True)
            return

        uploader = await user_service.get_by_id(session, file.uploaded_by)
        uploader_name = uploader.first_name if uploader else str(file.uploaded_by)

    if file is None:
        return

    text = i18n.get(
        I18nKeys.ADMIN_CONTRIB_DETAIL,
        name=file.name,
        file_type=file.file_type,
        uploaded_by=uploader_name,
    )

    buttons = [
        [
            InlineKeyboardButton(
                text=i18n.get(I18nKeys.ADMIN_CONTRIB_BTN_APPROVE),
                callback_data=f"{CallbackPrefixes.ADMIN_CONTRIB_APPROVE}{file_id}",
            ),
            InlineKeyboardButton(
                text=i18n.get(I18nKeys.ADMIN_CONTRIB_BTN_REJECT),
                callback_data=f"{CallbackPrefixes.ADMIN_CONTRIB_REJECT}{file_id}",
            ),
        ],
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.ADMIN_BTN_BACK),
            callback_data=CallbackPrefixes.ADMIN_CONTRIBUTIONS,
        )],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_contrib_approve(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_FILES):
        return

    try:
        file_id = int(callback.data.replace(CallbackPrefixes.ADMIN_CONTRIB_APPROVE, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()
    uploader_id = 0
    file_name: str = ""

    async for session in db.get_session():
        file = await file_service.get_file(session, file_id)
        if file is None:
            await callback.answer(i18n.get(I18nKeys.FILES_NOT_FOUND), show_alert=True)
            return
        uploader_id = file.uploaded_by
        file_name = file.name
        await file_service.set_file_status(session, file_id, FileStatus.PUBLISHED.value)
        await audit_service.log_action(
            session, callback.from_user.id,
            AuditActions.CONTRIBUTION_APPROVED,
            f"file_id={file_id}",
        )
        logger.info(LogMessages.CONTRIBUTION_APPROVED.format(
            file_id=file_id, admin_id=callback.from_user.id
        ))

    await callback.answer(i18n.get(I18nKeys.ADMIN_CONTRIB_APPROVED), show_alert=True)

    bot = callback.bot
    if bot and uploader_id:
        try:
            await bot.send_message(
                uploader_id,
                i18n.get(I18nKeys.ADMIN_CONTRIB_USER_APPROVED, name=file_name),
            )
        except Exception:
            pass

    await _show_contributions(callback, page=1)


async def handle_admin_contrib_reject(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_FILES):
        return

    try:
        file_id = int(callback.data.replace(CallbackPrefixes.ADMIN_CONTRIB_REJECT, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()
    uploader_id = 0
    file_name: str = ""

    async for session in db.get_session():
        file = await file_service.get_file(session, file_id)
        if file is None:
            await callback.answer(i18n.get(I18nKeys.FILES_NOT_FOUND), show_alert=True)
            return
        uploader_id = file.uploaded_by
        file_name = file.name
        await file_service.soft_delete_file(session, file_id)
        await audit_service.log_action(
            session, callback.from_user.id,
            AuditActions.CONTRIBUTION_REJECTED,
            f"file_id={file_id}",
        )
        logger.info(LogMessages.CONTRIBUTION_REJECTED.format(
            file_id=file_id, admin_id=callback.from_user.id
        ))

    await callback.answer(i18n.get(I18nKeys.ADMIN_CONTRIB_REJECTED), show_alert=True)

    bot = callback.bot
    if bot and uploader_id:
        try:
            await bot.send_message(
                uploader_id,
                i18n.get(I18nKeys.ADMIN_CONTRIB_USER_REJECTED, name=file_name),
            )
        except Exception:
            pass

    await _show_contributions(callback, page=1)


async def handle_admin_audit(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.VIEW_AUDIT_LOG):
        return
    await _show_audit_log(callback, page=1)


async def _show_audit_log(callback: CallbackQuery, page: int = 1) -> None:
    if not callback.message:
        return

    i18n = get_i18n()
    db = await get_db()
    logs: List = []
    total = 0

    async for session in db.get_session():
        logs, total = await audit_service.list_logs(
            session, page=page, per_page=ADMIN_AUDIT_PER_PAGE
        )

    if not logs:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[_admin_back_button()]])
        await callback.message.edit_text(  # type: ignore[union-attr]
            i18n.get(I18nKeys.ADMIN_AUDIT_EMPTY),
            reply_markup=keyboard,
        )  # type: ignore[union-attr]
        await callback.answer()
        return

    entries: List[str] = []
    for log in logs:
        created = log.created_at.strftime("%Y-%m-%d %H:%M") if log.created_at else "-"
        entry_text = i18n.get(
            I18nKeys.ADMIN_AUDIT_ENTRY,
            user_id=log.user_id,
            action=log.action,
            details=log.details or "-",
            time=created,
        )
        entries.append(entry_text)

    text = i18n.get(I18nKeys.ADMIN_AUDIT_TITLE) + "\n\n" + "\n\n".join(entries)

    total_pages = max(1, (total + ADMIN_AUDIT_PER_PAGE - 1) // ADMIN_AUDIT_PER_PAGE)
    buttons: List[List[InlineKeyboardButton]] = []

    nav_row: List[InlineKeyboardButton] = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(
            text=i18n.get(I18nKeys.FILES_PAGE_PREV),
            callback_data=f"{CallbackPrefixes.ADMIN_AUDIT_PAGE}{page - 1}",
        ))
    if total_pages > 1:
        nav_row.append(InlineKeyboardButton(
            text=i18n.get(I18nKeys.FILES_PAGE_INFO, page=page, total=total_pages),
            callback_data="noop",
        ))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(
            text=i18n.get(I18nKeys.FILES_PAGE_NEXT),
            callback_data=f"{CallbackPrefixes.ADMIN_AUDIT_PAGE}{page + 1}",
        ))
    if nav_row:
        buttons.append(nav_row)

    buttons.append([_admin_back_button()])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    if len(text) > 4000:
        text = text[:4000] + "..."

    await callback.message.edit_text(text, reply_markup=keyboard)  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_audit_page(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.VIEW_AUDIT_LOG):
        return
    try:
        page = int(callback.data.replace(CallbackPrefixes.ADMIN_AUDIT_PAGE, ""))
    except (ValueError, IndexError):
        return
    await _show_audit_log(callback, page=page)


async def handle_section_toggle(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SECTIONS):
        return

    try:
        section_id = int(callback.data.replace(CallbackPrefixes.SECTION_ADMIN_TOGGLE, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()
    msg: str = ""

    async for session in db.get_session():
        section = await section_service.toggle_active(session, section_id)
        if section is None:
            await callback.answer(i18n.get(I18nKeys.SECTION_ADMIN_NOT_FOUND), show_alert=True)
            return

        await audit_service.log_action(
            session, callback.from_user.id,
            AuditActions.SECTION_TOGGLED,
            f"section_id={section_id} is_active={section.is_active}",
        )

        if section.is_active:
            msg = i18n.get(I18nKeys.SECTION_ADMIN_TOGGLED_SHOWN, name=section.name)
        else:
            msg = i18n.get(I18nKeys.SECTION_ADMIN_TOGGLED_HIDDEN, name=section.name)

    await callback.answer(msg, show_alert=True)

    from bot.handlers.sections import _show_section_detail
    await _show_section_detail(callback, section_id, role)


async def handle_section_copy(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SECTIONS):
        return

    try:
        section_id = int(callback.data.replace(CallbackPrefixes.SECTION_ADMIN_COPY, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()
    section: Optional[Any] = None

    async for session in db.get_session():
        section = await section_service.get_section(session, section_id)
        if section is None:
            await callback.answer(i18n.get(I18nKeys.SECTION_ADMIN_NOT_FOUND), show_alert=True)
            return

    if section is None:
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_CONFIRM),
            callback_data=f"{CallbackPrefixes.SECTION_ADMIN_CONFIRM_COPY}{section_id}",
        )],
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_CANCEL),
            callback_data=f"{CallbackPrefixes.SECTION_VIEW}{section_id}",
        )],
    ])

    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.SECTION_ADMIN_CONFIRM_COPY, name=section.name),
        reply_markup=keyboard,
    )  # type: ignore[union-attr]
    await callback.answer()


async def handle_section_confirm_copy(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SECTIONS):
        return

    try:
        section_id = int(callback.data.replace(CallbackPrefixes.SECTION_ADMIN_CONFIRM_COPY, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()
    new_section = None
    section: Optional[Any] = None

    async for session in db.get_session():
        section = await section_service.get_section(session, section_id)
        if section is None:
            await callback.answer(i18n.get(I18nKeys.SECTION_ADMIN_NOT_FOUND), show_alert=True)
            return

        new_section = await section_service.copy_section_tree(
            session, section_id, target_parent_id=section.parent_id
        )
        if new_section:
            await audit_service.log_action(
                session, callback.from_user.id,
                AuditActions.SECTION_COPIED,
                f"source_id={section_id} new_id={new_section.id}",
            )
            logger.info(LogMessages.SECTION_COPIED.format(
                source_id=section_id, new_id=new_section.id, user_id=callback.from_user.id
            ))

    if new_section:
        await callback.answer(
            i18n.get(I18nKeys.SECTION_ADMIN_COPIED, name=new_section.name),
            show_alert=True,
        )

    from bot.handlers.sections import _show_sections_list
    parent_id = section.parent_id if section else None
    await _show_sections_list(callback, parent_id=parent_id, role=role)


async def handle_admin_back(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    from bot.handlers.home import handle_admin_panel_callback
    await handle_admin_panel_callback(callback, kwargs)


async def handle_contribute_upload(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message:
        return

    i18n = get_i18n()
    state_service = get_state_service()
    state_service.set_state(callback.from_user.id, STATES["CONTRIBUTE_UPLOAD"], data={
        "uploaded_count": 0,
    })

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.FILES_BTN_DONE),
            callback_data=CallbackPrefixes.BACK,
        )],
    ])

    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.CONTRIBUTE_PROMPT),
        reply_markup=keyboard,
    )  # type: ignore[union-attr]
    await callback.answer()



async def handle_subscription_verify(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    i18n = get_i18n()
    await callback.answer(i18n.get(I18nKeys.SUBSCRIPTION_BTN_VERIFY), show_alert=True)


async def _show_admin_subscription(callback: CallbackQuery) -> None:
    if not callback.message:
        return
    i18n = get_i18n()
    db = await get_db()
    enabled = False
    channels: List[str] = []
    async for session in db.get_session():
        enabled = await settings_manager.get_subscription_enabled(session)
        channels = await settings_manager.get_subscription_channels(session)

    status = i18n.get(I18nKeys.ADMIN_SUB_STATUS_ON) if enabled else i18n.get(I18nKeys.ADMIN_SUB_STATUS_OFF)
    channels_text = "\n".join(f"{idx + 1}. {ch}" for idx, ch in enumerate(channels)) if channels else "-"
    text = i18n.get(I18nKeys.ADMIN_SUB_TITLE, status=status, channels=channels_text)

    buttons: List[List[InlineKeyboardButton]] = [
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.ADMIN_SUB_BTN_TOGGLE_OFF if enabled else I18nKeys.ADMIN_SUB_BTN_TOGGLE_ON),
            callback_data=CallbackPrefixes.ADMIN_SUB_TOGGLE,
        )],
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.ADMIN_SUB_BTN_ADD),
            callback_data=CallbackPrefixes.ADMIN_SUB_ADD,
        )],
    ]
    for idx, ch in enumerate(channels):
        buttons.append([InlineKeyboardButton(
            text=f"{i18n.get(I18nKeys.ADMIN_SUB_BTN_REMOVE)}: {ch}",
            callback_data=f"{CallbackPrefixes.ADMIN_SUB_REMOVE}{idx}",
        )])
    buttons.append([_admin_back_button()])

    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_subscription(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SETTINGS):
        return
    await _show_admin_subscription(callback)


async def handle_admin_sub_toggle(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SETTINGS):
        return
    db = await get_db()
    async for session in db.get_session():
        current = await settings_manager.get_subscription_enabled(session)
        await settings_manager.set_subscription_enabled(session, not current)
        await audit_service.log_action(session, callback.from_user.id, AuditActions.SUBSCRIPTION_UPDATED, f"enabled={not current}")
    await _show_admin_subscription(callback)


async def handle_admin_sub_add(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SETTINGS):
        return
    i18n = get_i18n()
    get_state_service().set_state(callback.from_user.id, STATES["SUB_ADD_CHANNEL"])
    await callback.message.edit_text(i18n.get(I18nKeys.ADMIN_SUB_ENTER_CHANNEL), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[_admin_back_button()]]))  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_sub_remove(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SETTINGS):
        return
    try:
        idx = int(callback.data.replace(CallbackPrefixes.ADMIN_SUB_REMOVE, ""))
    except Exception:
        return
    db = await get_db()
    async for session in db.get_session():
        channels_before = await settings_manager.get_subscription_channels(session)
        await settings_manager.remove_subscription_channel(session, idx)
        await audit_service.log_action(session, callback.from_user.id, AuditActions.SUBSCRIPTION_UPDATED, f"remove_index={idx} from={channels_before}")
    await callback.answer(get_i18n().get(I18nKeys.ADMIN_SUB_REMOVED), show_alert=True)
    await _show_admin_subscription(callback)


async def handle_admin_stats(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SETTINGS):
        return
    if not callback.message:
        return
    i18n = get_i18n()
    db = await get_db()
    stats: Dict[str, int] = {}
    async for session in db.get_session():
        stats = await stats_service.collect_basic(session)
    await callback.message.edit_text(i18n.get(I18nKeys.ADMIN_STATS_TITLE, **stats), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[_admin_back_button()]]))  # type: ignore[union-attr]
    await callback.answer()


async def _show_admin_broadcast(callback: CallbackQuery) -> None:
    if not callback.message:
        return
    i18n = get_i18n()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=i18n.get(I18nKeys.ADMIN_BROADCAST_BTN_TEXT), callback_data=CallbackPrefixes.ADMIN_BROADCAST_TEXT)],
        [InlineKeyboardButton(text=i18n.get(I18nKeys.ADMIN_BROADCAST_BTN_FILE), callback_data=CallbackPrefixes.ADMIN_BROADCAST_FILE)],
        [_admin_back_button()],
    ])
    await callback.message.edit_text(i18n.get(I18nKeys.ADMIN_BROADCAST_TITLE), reply_markup=kb)  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_broadcast(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SETTINGS):
        return
    await _show_admin_broadcast(callback)


async def handle_admin_broadcast_text(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SETTINGS):
        return
    get_state_service().set_state(callback.from_user.id, STATES["BROADCAST_TEXT"])
    await callback.message.edit_text(get_i18n().get(I18nKeys.ADMIN_BROADCAST_ENTER_TEXT), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[_admin_back_button()]]))  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_broadcast_file(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SETTINGS):
        return
    get_state_service().set_state(callback.from_user.id, STATES["BROADCAST_FILE"])
    await callback.message.edit_text(get_i18n().get(I18nKeys.ADMIN_BROADCAST_ENTER_FILE), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[_admin_back_button()]]))  # type: ignore[union-attr]
    await callback.answer()


async def _run_broadcast(callback: CallbackQuery, payload: Dict[str, Any]) -> None:
    if not callback.from_user:
        return
    i18n = get_i18n()
    bot = callback.bot
    if bot is None:
        return

    db = await get_db()
    user_ids: List[int] = []
    async for session in db.get_session():
        user_ids = await user_service.list_user_ids(session)

    success = 0
    failed = 0
    for uid in user_ids:
        try:
            if payload.get("type") == "text":
                await bot.send_message(uid, payload.get("text", ""))
            else:
                await bot.send_document(uid, document=payload.get("file_id", ""), caption=payload.get("caption"))
            success += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    async for session in db.get_session():
        await audit_service.log_action(session, callback.from_user.id, AuditActions.BROADCAST_SENT, f"type={payload.get('type')} success={success} failed={failed}")

    await callback.answer(i18n.get(I18nKeys.ADMIN_BROADCAST_DONE, success=success, failed=failed), show_alert=True)
    await _show_admin_broadcast(callback)


async def handle_admin_broadcast_confirm(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SETTINGS):
        return
    state = get_state_service().get_state(callback.from_user.id)
    if state is None or state.name not in ("admin_broadcast_confirm_text", "admin_broadcast_confirm_file"):
        return
    payload = state.data.get("payload", {})
    get_state_service().clear_state(callback.from_user.id)
    await _run_broadcast(callback, payload)


async def handle_admin_broadcast_cancel(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if callback.from_user:
        get_state_service().clear_state(callback.from_user.id)
    await callback.answer(get_i18n().get(I18nKeys.ADMIN_BROADCAST_CANCELLED), show_alert=True)
    await _show_admin_broadcast(callback)


async def _show_admin_ban(callback: CallbackQuery) -> None:
    if not callback.message:
        return
    i18n = get_i18n()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=i18n.get(I18nKeys.ADMIN_BAN_BTN_BLOCK), callback_data=CallbackPrefixes.ADMIN_BAN_BLOCK)],
        [InlineKeyboardButton(text=i18n.get(I18nKeys.ADMIN_BAN_BTN_UNBLOCK), callback_data=CallbackPrefixes.ADMIN_BAN_UNBLOCK)],
        [_admin_back_button()],
    ])
    await callback.message.edit_text(i18n.get(I18nKeys.ADMIN_BAN_TITLE), reply_markup=kb)  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_ban(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_USERS):
        return
    await _show_admin_ban(callback)


async def handle_admin_ban_block(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_USERS):
        return
    get_state_service().set_state(callback.from_user.id, STATES["BAN_BLOCK"])
    await callback.message.edit_text(get_i18n().get(I18nKeys.ADMIN_BAN_ENTER_ID_BLOCK), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[_admin_back_button()]]))  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_ban_unblock(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_USERS):
        return
    get_state_service().set_state(callback.from_user.id, STATES["BAN_UNBLOCK"])
    await callback.message.edit_text(get_i18n().get(I18nKeys.ADMIN_BAN_ENTER_ID_UNBLOCK), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[_admin_back_button()]]))  # type: ignore[union-attr]
    await callback.answer()


async def _show_admin_maintenance(callback: CallbackQuery) -> None:
    if not callback.message:
        return
    i18n = get_i18n()
    db = await get_db()
    enabled = False
    message = i18n.get(I18nKeys.MAINTENANCE_DEFAULT_MESSAGE)
    async for session in db.get_session():
        enabled = await settings_manager.get_maintenance_enabled(session)
        message = await settings_manager.get_maintenance_message(session, default=message)

    status = i18n.get(I18nKeys.ADMIN_SUB_STATUS_ON) if enabled else i18n.get(I18nKeys.ADMIN_SUB_STATUS_OFF)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=i18n.get(I18nKeys.ADMIN_MAINT_BTN_TOGGLE_OFF if enabled else I18nKeys.ADMIN_MAINT_BTN_TOGGLE_ON), callback_data=CallbackPrefixes.ADMIN_MAINT_TOGGLE)],
        [InlineKeyboardButton(text=i18n.get(I18nKeys.ADMIN_MAINT_BTN_SET_MESSAGE), callback_data=CallbackPrefixes.ADMIN_MAINT_SET_MESSAGE)],
        [InlineKeyboardButton(text=i18n.get(I18nKeys.ADMIN_MAINT_BTN_BACKUP_EXPORT), callback_data=CallbackPrefixes.ADMIN_BACKUP_EXPORT)],
        [InlineKeyboardButton(text=i18n.get(I18nKeys.ADMIN_MAINT_BTN_BACKUP_RESTORE), callback_data=CallbackPrefixes.ADMIN_BACKUP_RESTORE)],
        [_admin_back_button()],
    ])
    await callback.message.edit_text(i18n.get(I18nKeys.ADMIN_MAINT_TITLE, status=status, message=message), reply_markup=kb)  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_maintenance(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SETTINGS):
        return
    await _show_admin_maintenance(callback)


async def handle_admin_maint_toggle(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SETTINGS):
        return
    db = await get_db()
    async for session in db.get_session():
        current = await settings_manager.get_maintenance_enabled(session)
        await settings_manager.set_maintenance_enabled(session, not current)
        await audit_service.log_action(session, callback.from_user.id, AuditActions.MAINTENANCE_TOGGLED, f"enabled={not current}")
    await _show_admin_maintenance(callback)


async def handle_admin_maint_set_message(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SETTINGS):
        return
    get_state_service().set_state(callback.from_user.id, STATES["MAINT_MESSAGE"])
    await callback.message.edit_text(get_i18n().get(I18nKeys.ADMIN_MAINT_ENTER_MESSAGE), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[_admin_back_button()]]))  # type: ignore[union-attr]
    await callback.answer()


async def handle_admin_backup_export(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SETTINGS):
        return
    db = await get_db()
    backup_path = ""
    async for session in db.get_session():
        backup_path = await backup_service.export_backup(session)
        await audit_service.log_action(session, callback.from_user.id, AuditActions.BACKUP_EXPORTED, backup_path)
    if callback.message and backup_path:
        await callback.message.answer_document(FSInputFile(backup_path), caption=Path(backup_path).name)
    await callback.answer(get_i18n().get(I18nKeys.ADMIN_BACKUP_EXPORTED), show_alert=True)


async def handle_admin_backup_restore(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SETTINGS):
        return
    get_state_service().set_state(callback.from_user.id, STATES["BACKUP_RESTORE"])
    await callback.message.edit_text(get_i18n().get(I18nKeys.ADMIN_BACKUP_RESTORE_PROMPT), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[_admin_back_button()]]))  # type: ignore[union-attr]
    await callback.answer()


def _is_admin_text_state(message: Message) -> bool:
    if not message.from_user:
        return False
    state_service = get_state_service()
    state = state_service.get_state(message.from_user.id)
    if state is None:
        return False
    return state.name in (
        STATES["MOD_ADD"],
        STATES["TEXT_EDIT"],
        STATES["CONTRIBUTE_UPLOAD"],
        STATES["SUB_ADD_CHANNEL"],
        STATES["BROADCAST_TEXT"],
        STATES["BROADCAST_FILE"],
        STATES["BAN_BLOCK"],
        STATES["BAN_UNBLOCK"],
        STATES["MAINT_MESSAGE"],
        STATES["BACKUP_RESTORE"],
        "admin_broadcast_confirm_text",
        "admin_broadcast_confirm_file",
    )


def create_admin_router() -> Router:
    router = Router(name="admin")

    @router.message(_is_admin_text_state)
    async def admin_text_handler(message: Message, **kwargs: Any) -> None:
        if not message.from_user:
            return

        user_id = message.from_user.id
        state_service = get_state_service()
        state = state_service.get_state(user_id)
        if state is None:
            return

        if state.name == STATES["MOD_ADD"]:
            await _handle_mod_add_input(message, state, kwargs)
        elif state.name == STATES["TEXT_EDIT"]:
            await _handle_text_edit_input(message, state, kwargs)
        elif state.name == STATES["CONTRIBUTE_UPLOAD"]:
            await _handle_contribute_upload(message, state)
        elif state.name == STATES["SUB_ADD_CHANNEL"]:
            await _handle_sub_add_channel_input(message, kwargs)
        elif state.name == STATES["BROADCAST_TEXT"]:
            await _handle_broadcast_text_input(message, kwargs)
        elif state.name == STATES["BROADCAST_FILE"]:
            await _handle_broadcast_file_input(message, kwargs)
        elif state.name in (STATES["BAN_BLOCK"], STATES["BAN_UNBLOCK"]):
            await _handle_ban_input(message, state, kwargs)
        elif state.name == STATES["MAINT_MESSAGE"]:
            await _handle_maintenance_message_input(message, kwargs)
        elif state.name == STATES["BACKUP_RESTORE"]:
            await _handle_backup_restore_input(message, kwargs)

    return router


async def _handle_sub_add_channel_input(message: Message, kwargs: Dict[str, Any]) -> None:
    if not message.from_user or not message.text:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not has_permission(role, Permission.MANAGE_SETTINGS):
        return
    channel = message.text.strip()
    db = await get_db()
    async for session in db.get_session():
        await settings_manager.add_subscription_channel(session, channel)
        await audit_service.log_action(session, message.from_user.id, AuditActions.SUBSCRIPTION_UPDATED, f"add_channel={channel}")
    get_state_service().clear_state(message.from_user.id)
    await message.answer(get_i18n().get(I18nKeys.ADMIN_SUB_ADDED))


async def _handle_broadcast_text_input(message: Message, kwargs: Dict[str, Any]) -> None:
    if not message.from_user or not message.text:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not has_permission(role, Permission.MANAGE_SETTINGS):
        return
    i18n = get_i18n()
    get_state_service().set_state(message.from_user.id, "admin_broadcast_confirm_text", data={
        "payload": {"type": "text", "text": message.text},
    })
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=i18n.get(I18nKeys.ADMIN_BROADCAST_BTN_CONFIRM), callback_data=CallbackPrefixes.ADMIN_BROADCAST_CONFIRM)],
        [InlineKeyboardButton(text=i18n.get(I18nKeys.ADMIN_BROADCAST_BTN_CANCEL), callback_data=CallbackPrefixes.ADMIN_BROADCAST_CANCEL)],
    ])
    await message.answer(i18n.get(I18nKeys.ADMIN_BROADCAST_CONFIRM_TEXT, text=message.text), reply_markup=kb)


async def _handle_broadcast_file_input(message: Message, kwargs: Dict[str, Any]) -> None:
    if not message.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not has_permission(role, Permission.MANAGE_SETTINGS):
        return
    from bot.handlers.files import _extract_file_info
    info = _extract_file_info(message)
    if info is None:
        return
    i18n = get_i18n()
    get_state_service().set_state(message.from_user.id, "admin_broadcast_confirm_file", data={
        "payload": {
            "type": "file",
            "file_id": info["file_id"],
            "caption": message.caption,
            "name": info.get("name", "file"),
        }
    })
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=i18n.get(I18nKeys.ADMIN_BROADCAST_BTN_CONFIRM), callback_data=CallbackPrefixes.ADMIN_BROADCAST_CONFIRM)],
        [InlineKeyboardButton(text=i18n.get(I18nKeys.ADMIN_BROADCAST_BTN_CANCEL), callback_data=CallbackPrefixes.ADMIN_BROADCAST_CANCEL)],
    ])
    await message.answer(i18n.get(I18nKeys.ADMIN_BROADCAST_CONFIRM_FILE, name=info.get("name", "file")), reply_markup=kb)


async def _handle_ban_input(message: Message, state: Any, kwargs: Dict[str, Any]) -> None:
    if not message.from_user or not message.text:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not has_permission(role, Permission.MANAGE_USERS):
        return
    i18n = get_i18n()
    value = message.text.strip()
    if not value.isdigit():
        await message.answer(i18n.get(I18nKeys.ADMIN_BAN_INVALID_ID))
        return
    target_id = int(value)
    blocked = state.name == STATES["BAN_BLOCK"]
    db = await get_db()
    async for session in db.get_session():
        await user_service.set_blocked(session, target_id, blocked)
        await audit_service.log_action(
            session,
            message.from_user.id,
            AuditActions.USER_BLOCKED if blocked else AuditActions.USER_UNBLOCKED,
            f"target_id={target_id}",
        )
    get_state_service().clear_state(message.from_user.id)
    await message.answer(i18n.get(I18nKeys.ADMIN_BAN_BLOCKED if blocked else I18nKeys.ADMIN_BAN_UNBLOCKED, user_id=target_id))


async def _handle_maintenance_message_input(message: Message, kwargs: Dict[str, Any]) -> None:
    if not message.from_user or not message.text:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not has_permission(role, Permission.MANAGE_SETTINGS):
        return
    db = await get_db()
    async for session in db.get_session():
        await settings_manager.set_maintenance_message(session, message.text.strip())
        await audit_service.log_action(session, message.from_user.id, AuditActions.MAINTENANCE_TOGGLED, "maintenance_message_updated")
    get_state_service().clear_state(message.from_user.id)
    await message.answer(get_i18n().get(I18nKeys.ADMIN_MAINT_UPDATED))


async def _handle_backup_restore_input(message: Message, kwargs: Dict[str, Any]) -> None:
    if not message.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    i18n = get_i18n()
    if not has_permission(role, Permission.MANAGE_SETTINGS):
        return

    payload_text = ""
    if message.document:
        bot = message.bot
        if bot is None:
            return
        downloaded = await bot.download(message.document)
        if downloaded is None:
            await message.answer(i18n.get(I18nKeys.ADMIN_BACKUP_FAILED))
            return
        payload_text = downloaded.read().decode("utf-8")
    elif message.text:
        payload_text = message.text
    else:
        return

    try:
        data = json.loads(payload_text)
    except Exception:
        await message.answer(i18n.get(I18nKeys.ADMIN_BACKUP_FAILED))
        return

    db = await get_db()
    async for session in db.get_session():
        await backup_service.restore_backup(session, data)
        await audit_service.log_action(session, message.from_user.id, AuditActions.BACKUP_RESTORED, "backup_restored")

    get_state_service().clear_state(message.from_user.id)
    await message.answer(i18n.get(I18nKeys.ADMIN_BACKUP_RESTORED))


async def _handle_mod_add_input(message: Message, state: Any, kwargs: Dict[str, Any]) -> None:
    if not message.from_user or not message.text:
        return

    user_id = message.from_user.id
    i18n = get_i18n()
    state_service = get_state_service()
    query = message.text.strip()

    if not query.isdigit():
        await message.answer(i18n.get(I18nKeys.ADMIN_MOD_INVALID_ID))
        return

    target_id = int(query)

    if target_id == user_id:
        await message.answer(i18n.get(I18nKeys.ADMIN_MOD_CANNOT_ADD_SELF))
        return

    db = await get_db()
    target_user: Optional[Any] = None

    async for session in db.get_session():
        target_user = await user_service.get_by_id(session, target_id)
        if target_user is None:
            await message.answer(i18n.get(I18nKeys.ADMIN_MOD_NOT_FOUND))
            return

        if target_user.role == UserRole.MODERATOR:
            await message.answer(i18n.get(I18nKeys.ADMIN_MOD_ALREADY_MOD))
            state_service.clear_state(user_id)
            return

        await user_service.set_role(session, target_id, UserRole.MODERATOR)
        await moderator_service.create_permissions(session, target_id)
        await audit_service.log_action(
            session, user_id,
            AuditActions.MODERATOR_ADDED,
            f"target_id={target_id}",
        )
        logger.info(LogMessages.MODERATOR_ADDED.format(
            target_id=target_id, admin_id=user_id
        ))

    state_service.clear_state(user_id)
    await message.answer(i18n.get(I18nKeys.ADMIN_MOD_ADDED, name=target_user.first_name if target_user else ""))


async def _handle_text_edit_input(message: Message, state: Any, kwargs: Dict[str, Any]) -> None:
    if not message.from_user or not message.text:
        return

    user_id = message.from_user.id
    i18n = get_i18n()
    state_service = get_state_service()
    new_text = message.text.strip()
    key = state.data.get("key", "")

    if not key:
        state_service.clear_state(user_id)
        return

    db = await get_db()

    async for session in db.get_session():
        from bot.models.text_entry import TextEntry
        from sqlalchemy import select, update as sql_update

        stmt = select(TextEntry).where(
            TextEntry.key == key,
            TextEntry.language == i18n.default_language,
        )
        result = await session.execute(stmt)
        entry = result.scalar_one_or_none()

        if entry:
            entry.text = new_text
        else:
            entry = TextEntry(key=key, language=i18n.default_language, text=new_text)
            session.add(entry)

        await session.flush()
        await audit_service.log_action(
            session, user_id,
            AuditActions.TEXT_UPDATED,
            f"key={key}",
        )
        logger.info(LogMessages.TEXT_UPDATED.format(key=key, admin_id=user_id))

        await i18n.reload(session)

    state_service.clear_state(user_id)
    await message.answer(i18n.get(I18nKeys.ADMIN_TEXT_UPDATED))


async def _handle_contribute_upload(message: Message, state: Any) -> None:
    if not message.from_user:
        return

    user_id = message.from_user.id
    i18n = get_i18n()
    state_service = get_state_service()

    from bot.handlers.files import _extract_file_info, _forward_to_storage, get_storage_channel_id

    file_info = _extract_file_info(message)
    if file_info is None:
        return

    channel_id = get_storage_channel_id()
    if channel_id == 0:
        await message.reply(i18n.get(I18nKeys.FILES_STORAGE_NOT_SET))
        return

    bot = message.bot
    if bot is None:
        return

    db = await get_db()

    async for session in db.get_session():
        existing = await file_service.check_duplicate(session, file_info["file_unique_id"])
        if existing:
            await message.reply(i18n.get(I18nKeys.CONTRIBUTE_DUPLICATE))
            return

    await _forward_to_storage(bot, message)

    async for session in db.get_session():
        file = await file_service.create_file(
            session,
            file_id=file_info["file_id"],
            file_unique_id=file_info["file_unique_id"],
            name=file_info["name"],
            file_type=file_info["file_type"],
            uploaded_by=user_id,
            size=file_info.get("size"),
            status=FileStatus.PENDING.value,
        )

    uploaded_count = state.data.get("uploaded_count", 0) + 1
    state_service.set_state(user_id, STATES["CONTRIBUTE_UPLOAD"], data={
        "uploaded_count": uploaded_count,
    })

    await message.reply(i18n.get(I18nKeys.CONTRIBUTE_SUCCESS))
