import logging
from typing import Optional

from aiogram.types import CallbackQuery

from bot.models.user import UserRole
from bot.core.constants import I18nKeys
from bot.services.i18n import get_i18n

logger = logging.getLogger("bot")


class Permission:
    BROWSE = "browse"
    UPLOAD_FILE = "upload_file"
    MANAGE_SECTIONS = "manage_sections"
    MANAGE_FILES = "manage_files"
    MANAGE_USERS = "manage_users"
    MANAGE_SETTINGS = "manage_settings"
    VIEW_AUDIT_LOG = "view_audit_log"
    VIEW_ADMIN_PANEL = "view_admin_panel"


ROLE_PERMISSIONS = {
    UserRole.USER: {
        Permission.BROWSE,
    },
    UserRole.MODERATOR: {
        Permission.BROWSE,
        Permission.UPLOAD_FILE,
    },
    UserRole.ADMIN: {
        Permission.BROWSE,
        Permission.UPLOAD_FILE,
        Permission.MANAGE_SECTIONS,
        Permission.MANAGE_FILES,
        Permission.MANAGE_USERS,
        Permission.MANAGE_SETTINGS,
        Permission.VIEW_AUDIT_LOG,
        Permission.VIEW_ADMIN_PANEL,
    },
}


def has_permission(role: UserRole, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())


def is_admin(role: UserRole) -> bool:
    return role == UserRole.ADMIN


def is_moderator_or_above(role: UserRole) -> bool:
    return role in (UserRole.MODERATOR, UserRole.ADMIN)


async def check_permission_and_notify(
    callback: CallbackQuery,
    role: UserRole,
    permission: str,
) -> bool:
    if has_permission(role, permission):
        return True

    from bot.core.constants import LogMessages
    user_id = callback.from_user.id if callback.from_user else 0
    logger.warning(LogMessages.PERMISSION_DENIED.format(user_id=user_id, permission=permission))

    i18n = get_i18n()
    text = i18n.get(I18nKeys.ERROR_PERMISSION_DENIED)
    await callback.answer(text, show_alert=True)
    return False
