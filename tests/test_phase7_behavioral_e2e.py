import sys
import types

# Lightweight aiogram stub for offline behavioral tests
if "aiogram" not in sys.modules:
    aiogram = types.ModuleType("aiogram")
    class Router:
        def __init__(self, name=None):
            self.name=name
            self.message=types.SimpleNamespace(register=lambda *a, **k: None)
            self.callback_query=types.SimpleNamespace(register=lambda *a, **k: None)
    class BaseMiddleware:
        pass
    class Bot:
        pass
    aiogram.Router = Router
    aiogram.BaseMiddleware = BaseMiddleware
    aiogram.Bot = Bot
    sys.modules["aiogram"] = aiogram

    filters = types.ModuleType("aiogram.filters")
    filters.Command = lambda *_a, **_k: object()
    sys.modules["aiogram.filters"] = filters

    enums = types.ModuleType("aiogram.enums")
    class ChatMemberStatus:
        LEFT = "left"
        KICKED = "kicked"
    enums.ChatMemberStatus = ChatMemberStatus
    sys.modules["aiogram.enums"] = enums

    types_mod = types.ModuleType("aiogram.types")
    class _Obj:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    class InlineKeyboardButton(_Obj):
        pass
    class InlineKeyboardMarkup(_Obj):
        pass
    class Update(_Obj):
        pass
    class Message(_Obj):
        pass
    class CallbackQuery(_Obj):
        pass
    class FSInputFile(_Obj):
        pass
    class TelegramObject(_Obj):
        pass
    class ErrorEvent(_Obj):
        pass
    types_mod.InlineKeyboardButton = InlineKeyboardButton
    types_mod.InlineKeyboardMarkup = InlineKeyboardMarkup
    types_mod.Update = Update
    types_mod.Message = Message
    types_mod.CallbackQuery = CallbackQuery
    types_mod.FSInputFile = FSInputFile
    types_mod.TelegramObject = TelegramObject
    types_mod.ErrorEvent = ErrorEvent
    sys.modules["aiogram.types"] = types_mod

import asyncio
# Lightweight sqlalchemy stub for offline behavioral tests
if "sqlalchemy" not in sys.modules:
    sa = types.ModuleType("sqlalchemy")
    sa.select = lambda *a, **k: None
    sa.update = lambda *a, **k: None
    sa.delete = lambda *a, **k: None
    sa.func = types.SimpleNamespace(count=lambda *a, **k: 0, now=lambda: None)
    class _T:
        def __init__(self, *a, **k):
            pass
    for n in ["BigInteger","Integer","Boolean","String","DateTime","Enum","Text","UniqueConstraint","ForeignKey"]:
        setattr(sa, n, _T)
    sys.modules["sqlalchemy"] = sa

    exc = types.ModuleType("sqlalchemy.exc")
    class IntegrityError(Exception):
        pass
    exc.IntegrityError = IntegrityError
    sys.modules["sqlalchemy.exc"] = exc

    orm = types.ModuleType("sqlalchemy.orm")
    class DeclarativeBase:
        pass
    orm.DeclarativeBase = DeclarativeBase
    class _Mapped:
        def __class_getitem__(cls, item):
            return cls
    orm.Mapped = _Mapped
    orm.mapped_column = lambda *a, **k: None
    sys.modules["sqlalchemy.orm"] = orm

    ext = types.ModuleType("sqlalchemy.ext")
    async_mod = types.ModuleType("sqlalchemy.ext.asyncio")
    async_mod.create_async_engine = lambda *a, **k: None
    class AsyncSession:
        pass
    async_mod.AsyncSession = AsyncSession
    async_mod.async_sessionmaker = lambda *a, **k: (lambda: None)
    sys.modules["sqlalchemy.ext"] = ext
    sys.modules["sqlalchemy.ext.asyncio"] = async_mod

    sql = types.ModuleType("sqlalchemy.sql")
    sql.func = types.SimpleNamespace(now=lambda: None)
    sys.modules["sqlalchemy.sql"] = sql

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from bot.core.constants import CallbackPrefixes
from bot.handlers import home as home_handlers
from bot.handlers import admin as admin_handlers
from bot.middlewares.subscription_check import SubscriptionCheckMiddleware
from bot.middlewares.ban_check import BanCheckMiddleware
from bot.middlewares.maintenance_check import MaintenanceCheckMiddleware
from bot.models.user import UserRole
from bot.services.permissions import Permission, get_effective_permissions


class FakeSessionCtx:
    def __init__(self, session):
        self._session = session

    async def get_session(self):
        yield self._session


class FakeMessage:
    def __init__(self, text="", from_user=None, bot=None):
        self.text = text
        self.caption = None
        self.document = None
        self.from_user = from_user
        self.bot = bot
        self.edits = []
        self.answers = []

    async def edit_text(self, text, reply_markup=None):
        self.edits.append((text, reply_markup))

    async def answer(self, text, reply_markup=None):
        self.answers.append((text, reply_markup))

    async def reply(self, text, reply_markup=None):
        self.answers.append((text, reply_markup))


class FakeCallback:
    def __init__(self, user_id=1, role=UserRole.USER, data="", message=None, bot=None):
        self.from_user = SimpleNamespace(id=user_id, first_name="U")
        self.data = data
        self.message = message or FakeMessage(from_user=self.from_user)
        self.bot = bot
        self.answers = []
        self.role = role

    async def answer(self, text="", show_alert=False):
        self.answers.append((text, show_alert))




class FakeI18n:
    default_language = "ar"

    def get(self, key, **kwargs):
        if kwargs:
            return f"{key}:{kwargs}"
        return str(key)


class FakeStateService:
    def __init__(self):
        self.cleared = []
        self.states = {}

    def clear_state(self, uid):
        self.cleared.append(uid)
        self.states.pop(uid, None)

    def set_state(self, uid, name, data=None):
        self.states[uid] = SimpleNamespace(name=name, data=data or {})

    def get_state(self, uid):
        return self.states.get(uid)


class BehavioralE2ETest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        fake_i18n = FakeI18n()
        self._patchers = [
            patch("bot.handlers.home.get_i18n", return_value=fake_i18n),
            patch("bot.handlers.admin.get_i18n", return_value=fake_i18n),
            patch("bot.services.permissions.get_i18n", return_value=fake_i18n),
            patch("bot.middlewares.subscription_check.get_i18n", return_value=fake_i18n),
            patch("bot.middlewares.ban_check.get_i18n", return_value=fake_i18n),
            patch("bot.middlewares.maintenance_check.get_i18n", return_value=fake_i18n),
        ]
        for p in self._patchers:
            p.start()

    async def asyncTearDown(self):
        for p in reversed(self._patchers):
            p.stop()

    async def test_01_main_buttons_and_admin_visibility(self):
        kb_user = home_handlers.build_home_keyboard(UserRole.USER)
        kb_mod = home_handlers.build_home_keyboard(UserRole.MODERATOR)
        kb_admin = home_handlers.build_home_keyboard(UserRole.ADMIN)

        def callback_set(kb):
            return {b.callback_data for row in kb.inline_keyboard for b in row if b.callback_data}

        required = {
            CallbackPrefixes.SECTIONS,
            CallbackPrefixes.SEARCH,
            CallbackPrefixes.CONTRIBUTE,
            CallbackPrefixes.TOOLS,
            CallbackPrefixes.ABOUT,
            CallbackPrefixes.CONTACT,
        }
        self.assertTrue(required.issubset(callback_set(kb_user)))
        self.assertNotIn(CallbackPrefixes.ADMIN_PANEL, callback_set(kb_user))
        self.assertIn(CallbackPrefixes.ADMIN_PANEL, callback_set(kb_mod))
        self.assertIn(CallbackPrefixes.ADMIN_PANEL, callback_set(kb_admin))

    async def test_02_admin_panel_dynamic_permissions(self):
        async def fake_effective(user_id, role):
            return {Permission.VIEW_ADMIN_PANEL, Permission.MANAGE_FILES}

        with patch("bot.handlers.home.get_effective_permissions", fake_effective):
            kb = await home_handlers.build_admin_panel_keyboard(10, UserRole.MODERATOR)

        callbacks = {b.callback_data for row in kb.inline_keyboard for b in row if b.callback_data}
        self.assertIn(CallbackPrefixes.ADMIN_FILES, callbacks)
        self.assertIn(CallbackPrefixes.ADMIN_CONTRIBUTIONS, callbacks)
        self.assertNotIn(CallbackPrefixes.ADMIN_MODERATORS, callbacks)
        self.assertNotIn(CallbackPrefixes.ADMIN_SECTIONS, callbacks)

    async def test_03_forged_callback_blocked_when_permission_removed(self):
        async def fake_effective(user_id, role):
            return {Permission.BROWSE, Permission.VIEW_ADMIN_PANEL}

        cb = FakeCallback(user_id=77, role=UserRole.MODERATOR, data=CallbackPrefixes.ADMIN_FILES)
        with patch("bot.services.permissions.get_effective_permissions", fake_effective):
            await admin_handlers.handle_admin_files(cb, {"user_role": UserRole.MODERATOR})
        self.assertTrue(cb.answers)
        self.assertTrue(cb.answers[-1][1])

    async def test_04_moderator_assignment_updates_db_and_notification_non_blocking(self):
        fake_state = FakeStateService()
        fake_state.set_state(1, admin_handlers.STATES["MOD_ADD"])
        sent = []

        class FakeBot:
            async def send_message(self, uid, text):
                sent.append((uid, text))
                raise RuntimeError("blocked")

        msg = FakeMessage(text="99", from_user=SimpleNamespace(id=1, first_name="Admin"), bot=FakeBot())

        async def fake_get_by_id(_s, uid):
            return SimpleNamespace(id=uid, role=UserRole.USER, first_name="Mod99")

        with patch("bot.handlers.admin.get_state_service", return_value=fake_state), \
             patch("bot.handlers.admin.get_db", AsyncMock(return_value=FakeSessionCtx(object()))), \
             patch("bot.handlers.admin.user_service.get_by_id", AsyncMock(side_effect=fake_get_by_id)), \
             patch("bot.handlers.admin.user_service.set_role", AsyncMock()) as set_role, \
             patch("bot.handlers.admin.moderator_service.create_permissions", AsyncMock()) as create_perm, \
             patch("bot.handlers.admin.audit_service.log_action", AsyncMock()):
            await admin_handlers._handle_mod_add_input(msg, fake_state.get_state(1), {"user_role": UserRole.ADMIN})

        set_role.assert_awaited()
        create_perm.assert_awaited()
        self.assertIn(1, fake_state.cleared)
        self.assertEqual(sent[0][0], 99)

    async def test_05_subscription_ban_maintenance_middlewares(self):
        called = {"ok": 0}

        async def handler(event, data):
            called["ok"] += 1
            return "ok"

        fake_update = SimpleNamespace(message=FakeMessage(from_user=SimpleNamespace(id=5)), callback_query=None)
        data = {"event_from_user": SimpleNamespace(id=5), "bot": SimpleNamespace(get_chat_member=AsyncMock(return_value=SimpleNamespace(status="left"))), "user_role": UserRole.USER}

        with patch("bot.middlewares.subscription_check.get_db", AsyncMock(return_value=FakeSessionCtx(object()))), \
             patch("bot.middlewares.subscription_check.settings_manager.get_subscription_enabled", AsyncMock(return_value=True)), \
             patch("bot.middlewares.subscription_check.settings_manager.get_subscription_channels", AsyncMock(return_value=["@chan"])):
            mw = SubscriptionCheckMiddleware()
            result = await mw(handler, fake_update, data)
            self.assertIsNone(result)

        with patch("bot.middlewares.ban_check.get_db", AsyncMock(return_value=FakeSessionCtx(object()))), \
             patch("bot.middlewares.ban_check.user_service.is_blocked", AsyncMock(return_value=True)):
            mw = BanCheckMiddleware()
            result = await mw(handler, fake_update, {"event_from_user": SimpleNamespace(id=5)})
            self.assertIsNone(result)

        with patch("bot.middlewares.maintenance_check.get_db", AsyncMock(return_value=FakeSessionCtx(object()))), \
             patch("bot.middlewares.maintenance_check.settings_manager.get_maintenance_enabled", AsyncMock(return_value=True)), \
             patch("bot.middlewares.maintenance_check.settings_manager.get_maintenance_message", AsyncMock(return_value="صيانة")):
            mw = MaintenanceCheckMiddleware()
            result = await mw(handler, fake_update, {"event_from_user": SimpleNamespace(id=5), "user_role": UserRole.USER})
            self.assertIsNone(result)

        self.assertEqual(called["ok"], 0)

    async def test_06_effective_permissions_for_moderator(self):
        with patch("bot.services.permissions.get_db", AsyncMock(return_value=FakeSessionCtx(object()))), \
             patch("bot.services.permissions.moderator_service.get_permissions", AsyncMock(return_value=SimpleNamespace(can_upload=False, can_link=False, can_publish=False))):
            perms = await get_effective_permissions(50, UserRole.MODERATOR)
        self.assertIn(Permission.VIEW_ADMIN_PANEL, perms)
        self.assertNotIn(Permission.MANAGE_FILES, perms)


if __name__ == "__main__":
    unittest.main()
