import logging
from typing import Optional, Set

from aiogram.types import CallbackQuery

from bot.models.user import UserRole
from bot.core.constants import I18nKeys
from bot.services.i18n import get_i18n
from bot.core.database import get_db
from bot.services.moderator import moderator_service

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
        Permission.VIEW_ADMIN_PANEL,
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


async def get_effective_permissions(user_id: int, role: UserRole) -> Set[str]:
    permissions = set(ROLE_PERMISSIONS.get(role, set()))

    if role != UserRole.MODERATOR:
        return permissions

    db = await get_db()
    async for session in db.get_session():
        moderator_permissions = await moderator_service.get_permissions(session, user_id)

    if moderator_permissions is None:
        return permissions

    if moderator_permissions.can_upload or moderator_permissions.can_link or moderator_permissions.can_publish:
        permissions.add(Permission.MANAGE_FILES)
    else:
        permissions.discard(Permission.MANAGE_FILES)

    return permissions


def is_admin(role: UserRole) -> bool:
    return role == UserRole.ADMIN


def is_moderator_or_above(role: UserRole) -> bool:
    return role in (UserRole.MODERATOR, UserRole.ADMIN)


async def check_permission_and_notify(
    callback: CallbackQuery,
    role: UserRole,
    permission: str,
) -> bool:
    user_id = callback.from_user.id if callback.from_user else 0
    if user_id:
        permissions = await get_effective_permissions(user_id, role)
        if permission in permissions:
            return True
    elif has_permission(role, permission):
        return True

    from bot.core.constants import LogMessages
    logger.warning(LogMessages.PERMISSION_DENIED.format(user_id=user_id, permission=permission))

    i18n = get_i18n()
    text = i18n.get(I18nKeys.ERROR_PERMISSION_DENIED)
    await callback.answer(text, show_alert=True)
    return False
