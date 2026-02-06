import logging
from typing import Any, Dict, List, Optional

from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.core.constants import LogMessages, I18nKeys, CallbackPrefixes, AuditActions
from bot.core.database import get_db
from bot.services.i18n import get_i18n
from bot.services.state import get_state_service
from bot.services.sections import section_service
from bot.services.audit import audit_service
from bot.services.permissions import has_permission, check_permission_and_notify, Permission
from bot.models.user import UserRole
from bot.models.section import Section

logger = logging.getLogger("bot")

STATES = {
    "ADD_NAME": "section_add_name",
    "ADD_DESC": "section_add_desc",
    "EDIT_NAME": "section_edit_name",
    "EDIT_ORDER": "section_edit_order",
}


def _build_sections_keyboard(
    sections: List[Section],
    parent_id: Optional[int],
    role: UserRole,
) -> InlineKeyboardMarkup:
    i18n = get_i18n()
    buttons: List[List[InlineKeyboardButton]] = []

    for sec in sections:
        buttons.append([InlineKeyboardButton(
            text=f"📁 {sec.name}",
            callback_data=f"{CallbackPrefixes.SECTION_VIEW}{sec.id}",
        )])

    if has_permission(role, Permission.MANAGE_SECTIONS):
        pid = parent_id if parent_id is not None else 0
        buttons.append([InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_ADD),
            callback_data=f"{CallbackPrefixes.SECTION_ADMIN_ADD}{pid}",
        )])

    if parent_id is not None:
        buttons.append([InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTIONS_BTN_BACK),
            callback_data=f"{CallbackPrefixes.SECTION_BACK}{parent_id}",
        )])
    else:
        buttons.append([InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTIONS_BTN_HOME),
            callback_data=CallbackPrefixes.HOME,
        )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def _build_section_detail_keyboard(
    section: Section,
    children: List[Section],
    role: UserRole,
    file_count: int = 0,
) -> InlineKeyboardMarkup:
    i18n = get_i18n()
    buttons: List[List[InlineKeyboardButton]] = []

    for child in children:
        buttons.append([InlineKeyboardButton(
            text=f"📁 {child.name}",
            callback_data=f"{CallbackPrefixes.SECTION_VIEW}{child.id}",
        )])

    files_label = i18n.get(I18nKeys.FILES_TITLE).rstrip(":")
    if file_count > 0:
        files_label = f"{files_label} ({file_count})"
    buttons.append([InlineKeyboardButton(
        text=files_label,
        callback_data=f"{CallbackPrefixes.FILE_PAGE}{section.id}:1",
    )])

    if has_permission(role, Permission.MANAGE_SECTIONS):
        pid = section.id
        admin_row = [
            InlineKeyboardButton(
                text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_ADD),
                callback_data=f"{CallbackPrefixes.SECTION_ADMIN_ADD}{pid}",
            ),
        ]
        buttons.append(admin_row)

        edit_row = [
            InlineKeyboardButton(
                text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_EDIT),
                callback_data=f"{CallbackPrefixes.SECTION_ADMIN_EDIT}{section.id}",
            ),
            InlineKeyboardButton(
                text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_ORDER),
                callback_data=f"{CallbackPrefixes.SECTION_ADMIN_SET_ORDER}{section.id}",
            ),
            InlineKeyboardButton(
                text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_DELETE),
                callback_data=f"{CallbackPrefixes.SECTION_ADMIN_DELETE}{section.id}",
            ),
        ]
        buttons.append(edit_row)

    back_target = section.parent_id if section.parent_id is not None else 0
    buttons.append([InlineKeyboardButton(
        text=i18n.get(I18nKeys.SECTIONS_BTN_BACK),
        callback_data=f"{CallbackPrefixes.SECTION_BACK}{back_target}",
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def _show_sections_list(
    callback: CallbackQuery,
    parent_id: Optional[int],
    role: UserRole,
) -> None:
    if not callback.message:
        return

    i18n = get_i18n()
    db = await get_db()
    sections: List[Section] = []

    async for session in db.get_session():
        sections = await section_service.list_sections(session, parent_id=parent_id)

    if not sections:
        title = i18n.get(I18nKeys.SECTIONS_EMPTY)
    else:
        title = i18n.get(I18nKeys.SECTIONS_TITLE)

    keyboard = _build_sections_keyboard(sections, parent_id, role)

    await callback.message.edit_text(title, reply_markup=keyboard)  # type: ignore[union-attr]
    await callback.answer()


async def _show_section_detail(
    callback: CallbackQuery,
    section_id: int,
    role: UserRole,
) -> None:
    if not callback.message or not callback.from_user:
        return

    i18n = get_i18n()
    db = await get_db()
    section: Optional[Section] = None
    children: List[Section] = []
    file_count = 0

    async for session in db.get_session():
        section = await section_service.get_section(session, section_id)
        if section is None or not section.is_active:
            await callback.answer(i18n.get(I18nKeys.SECTION_ADMIN_NOT_FOUND), show_alert=True)
            return
        children = await section_service.list_sections(session, parent_id=section_id)

        from bot.services.files import file_service as _fs
        file_count = await _fs.count_files_by_section(session, section_id)

    if section is None:
        return

    text = f"📂 <b>{section.name}</b>"
    if section.description:
        text += f"\n\n{section.description}"

    keyboard = _build_section_detail_keyboard(section, children, role, file_count=file_count)

    logger.debug(LogMessages.SECTION_VIEWED.format(
        section_id=section_id, user_id=callback.from_user.id
    ))

    await callback.message.edit_text(text, reply_markup=keyboard)  # type: ignore[union-attr]
    await callback.answer()


async def handle_sections_callback(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    role = kwargs.get("user_role", UserRole.USER)
    await _show_sections_list(callback, parent_id=None, role=role)


async def handle_section_view_callback(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data:
        return
    role = kwargs.get("user_role", UserRole.USER)
    try:
        section_id = int(callback.data.replace(CallbackPrefixes.SECTION_VIEW, ""))
    except (ValueError, IndexError):
        return
    await _show_section_detail(callback, section_id, role)


async def handle_section_back_callback(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data:
        return
    role = kwargs.get("user_role", UserRole.USER)
    try:
        target_id = int(callback.data.replace(CallbackPrefixes.SECTION_BACK, ""))
    except (ValueError, IndexError):
        return

    if target_id == 0:
        await _show_sections_list(callback, parent_id=None, role=role)
    else:
        await _show_section_detail(callback, target_id, role)


async def handle_section_admin_add(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SECTIONS):
        return

    try:
        parent_id = int(callback.data.replace(CallbackPrefixes.SECTION_ADMIN_ADD, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    state_service = get_state_service()
    state_service.set_state(callback.from_user.id, STATES["ADD_NAME"], data={
        "parent_id": parent_id if parent_id != 0 else None,
    })

    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_CANCEL),
            callback_data=CallbackPrefixes.SECTION_ADMIN_CANCEL,
        ),
    ]])

    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.SECTION_ADMIN_ENTER_NAME),
        reply_markup=cancel_kb,
    )
    await callback.answer()


async def handle_section_admin_edit(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SECTIONS):
        return

    try:
        section_id = int(callback.data.replace(CallbackPrefixes.SECTION_ADMIN_EDIT, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    state_service = get_state_service()
    state_service.set_state(callback.from_user.id, STATES["EDIT_NAME"], data={
        "section_id": section_id,
    })

    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_CANCEL),
            callback_data=CallbackPrefixes.SECTION_ADMIN_CANCEL,
        ),
    ]])

    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.SECTION_ADMIN_ENTER_NEW_NAME),
        reply_markup=cancel_kb,
    )
    await callback.answer()


async def handle_section_admin_set_order(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SECTIONS):
        return

    try:
        section_id = int(callback.data.replace(CallbackPrefixes.SECTION_ADMIN_SET_ORDER, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    state_service = get_state_service()
    state_service.set_state(callback.from_user.id, STATES["EDIT_ORDER"], data={
        "section_id": section_id,
    })

    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_CANCEL),
            callback_data=CallbackPrefixes.SECTION_ADMIN_CANCEL,
        ),
    ]])

    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.SECTION_ADMIN_ENTER_ORDER),
        reply_markup=cancel_kb,
    )
    await callback.answer()


async def handle_section_admin_delete(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SECTIONS):
        return

    try:
        section_id = int(callback.data.replace(CallbackPrefixes.SECTION_ADMIN_DELETE, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()
    section_name = ""

    async for session in db.get_session():
        section = await section_service.get_section(session, section_id)
        if section is None:
            await callback.answer(i18n.get(I18nKeys.SECTION_ADMIN_NOT_FOUND), show_alert=True)
            return

        children_exist = await section_service.has_children(session, section_id)
        if children_exist:
            await callback.answer(i18n.get(I18nKeys.SECTION_ADMIN_HAS_CHILDREN), show_alert=True)
            return

        section_name = section.name

    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_CONFIRM),
            callback_data=f"{CallbackPrefixes.SECTION_ADMIN_CONFIRM_DELETE}{section_id}",
        )],
        [InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_CANCEL),
            callback_data=CallbackPrefixes.SECTION_ADMIN_CANCEL,
        )],
    ])

    await callback.message.edit_text(  # type: ignore[union-attr]
        i18n.get(I18nKeys.SECTION_ADMIN_CONFIRM_DELETE, name=section_name),
        reply_markup=confirm_kb,
    )
    await callback.answer()


async def handle_section_admin_confirm_delete(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.data or not callback.from_user or not callback.message:
        return
    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SECTIONS):
        return

    try:
        section_id = int(callback.data.replace(CallbackPrefixes.SECTION_ADMIN_CONFIRM_DELETE, ""))
    except (ValueError, IndexError):
        return

    i18n = get_i18n()
    db = await get_db()
    parent_id = None

    async for session in db.get_session():
        section = await section_service.get_section(session, section_id)
        if section is None:
            await callback.answer(i18n.get(I18nKeys.SECTION_ADMIN_NOT_FOUND), show_alert=True)
            return

        parent_id = section.parent_id
        await section_service.soft_delete_section(session, section_id)
        await audit_service.log_action(
            session, callback.from_user.id,
            AuditActions.SECTION_DELETED,
            f"section_id={section_id} name={section.name}",
        )

    await callback.answer(i18n.get(I18nKeys.SECTION_ADMIN_DELETED), show_alert=True)
    await _show_sections_list(callback, parent_id=parent_id, role=role)


async def handle_section_admin_cancel(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user:
        return

    state_service = get_state_service()
    state_service.clear_state(callback.from_user.id)

    i18n = get_i18n()
    await callback.answer(i18n.get(I18nKeys.SECTION_ADMIN_CANCELLED))

    role = kwargs.get("user_role", UserRole.USER)
    await _show_sections_list(callback, parent_id=None, role=role)


async def handle_section_skip_desc(callback: CallbackQuery, kwargs: Dict[str, Any]) -> None:
    if not callback.from_user or not callback.message:
        return

    role = kwargs.get("user_role", UserRole.USER)
    if not await check_permission_and_notify(callback, role, Permission.MANAGE_SECTIONS):
        return

    state_service = get_state_service()
    state = state_service.get_state(callback.from_user.id)
    if state is None or state.name != STATES["ADD_DESC"]:
        return

    i18n = get_i18n()
    db = await get_db()

    parent_id = state.data.get("parent_id")
    name = state.data.get("name", "")

    async for session in db.get_session():
        next_order = await section_service.get_next_order(session, parent_id)
        section = await section_service.create_section(
            session, name=name, parent_id=parent_id, order=next_order,
        )
        await audit_service.log_action(
            session, callback.from_user.id,
            AuditActions.SECTION_CREATED,
            f"section_id={section.id} name={name} parent_id={parent_id}",
        )

    state_service.clear_state(callback.from_user.id)
    await callback.answer(i18n.get(I18nKeys.SECTION_ADMIN_SAVED), show_alert=True)
    await _show_sections_list(callback, parent_id=parent_id, role=role)


def _is_section_state(message: Message) -> bool:
    if not message.from_user or not message.text:
        return False
    state_service = get_state_service()
    state = state_service.get_state(message.from_user.id)
    if state is None:
        return False
    return state.name in STATES.values()


def create_sections_router() -> Router:
    router = Router(name="sections")

    @router.message(_is_section_state)
    async def sections_text_handler(message: Message, **kwargs: Any) -> None:
        if not message.from_user or not message.text:
            return

        user_id = message.from_user.id
        state_service = get_state_service()
        state = state_service.get_state(user_id)

        if state is None:
            return

        role = kwargs.get("user_role", UserRole.USER)

        if not has_permission(role, Permission.MANAGE_SECTIONS):
            state_service.clear_state(user_id)
            i18n = get_i18n()
            await message.answer(i18n.get(I18nKeys.ERROR_PERMISSION_DENIED))
            return

        i18n = get_i18n()

        if state.name == STATES["ADD_NAME"]:
            await _handle_add_name(message, state, role, i18n)
        elif state.name == STATES["ADD_DESC"]:
            await _handle_add_desc(message, state, role, i18n)
        elif state.name == STATES["EDIT_NAME"]:
            await _handle_edit_name(message, state, role, i18n)
        elif state.name == STATES["EDIT_ORDER"]:
            await _handle_edit_order(message, state, role, i18n)

    return router


async def _handle_add_name(message: Message, state: Any, role: UserRole, i18n: Any) -> None:
    user_id = message.from_user.id
    name = message.text.strip()
    state_service = get_state_service()

    state_service.set_state(user_id, STATES["ADD_DESC"], data={
        "parent_id": state.data.get("parent_id"),
        "name": name,
    })

    skip_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_SKIP_DESC),
            callback_data=CallbackPrefixes.SECTION_ADMIN_SKIP_DESC,
        ),
        InlineKeyboardButton(
            text=i18n.get(I18nKeys.SECTION_ADMIN_BTN_CANCEL),
            callback_data=CallbackPrefixes.SECTION_ADMIN_CANCEL,
        ),
    ]])

    await message.answer(
        i18n.get(I18nKeys.SECTION_ADMIN_ENTER_DESC),
        reply_markup=skip_kb,
    )


async def _handle_add_desc(message: Message, state: Any, role: UserRole, i18n: Any) -> None:
    user_id = message.from_user.id
    description = message.text.strip()
    state_service = get_state_service()

    parent_id = state.data.get("parent_id")
    name = state.data.get("name", "")

    db = await get_db()
    async for session in db.get_session():
        next_order = await section_service.get_next_order(session, parent_id)
        section = await section_service.create_section(
            session, name=name, parent_id=parent_id,
            description=description, order=next_order,
        )
        await audit_service.log_action(
            session, user_id,
            AuditActions.SECTION_CREATED,
            f"section_id={section.id} name={name} parent_id={parent_id}",
        )

    state_service.clear_state(user_id)
    await message.answer(i18n.get(I18nKeys.SECTION_ADMIN_SAVED))


async def _handle_edit_name(message: Message, state: Any, role: UserRole, i18n: Any) -> None:
    user_id = message.from_user.id
    new_name = message.text.strip()
    state_service = get_state_service()

    section_id = state.data.get("section_id")
    if section_id is None:
        state_service.clear_state(user_id)
        return

    db = await get_db()
    async for session in db.get_session():
        section = await section_service.update_section(session, section_id, name=new_name)
        if section is None:
            await message.answer(i18n.get(I18nKeys.SECTION_ADMIN_NOT_FOUND))
            state_service.clear_state(user_id)
            return

        await audit_service.log_action(
            session, user_id,
            AuditActions.SECTION_UPDATED,
            f"section_id={section_id} new_name={new_name}",
        )

    state_service.clear_state(user_id)
    await message.answer(i18n.get(I18nKeys.SECTION_ADMIN_UPDATED))


async def _handle_edit_order(message: Message, state: Any, role: UserRole, i18n: Any) -> None:
    user_id = message.from_user.id
    state_service = get_state_service()

    try:
        new_order = int(message.text.strip())
    except ValueError:
        await message.answer(i18n.get(I18nKeys.SECTION_ADMIN_INVALID_ORDER))
        return

    section_id = state.data.get("section_id")
    if section_id is None:
        state_service.clear_state(user_id)
        return

    db = await get_db()
    async for session in db.get_session():
        section = await section_service.update_section(session, section_id, order=new_order)
        if section is None:
            await message.answer(i18n.get(I18nKeys.SECTION_ADMIN_NOT_FOUND))
            state_service.clear_state(user_id)
            return

        await audit_service.log_action(
            session, user_id,
            AuditActions.SECTION_UPDATED,
            f"section_id={section_id} new_order={new_order}",
        )

    state_service.clear_state(user_id)
    await message.answer(i18n.get(I18nKeys.SECTION_ADMIN_UPDATED))
