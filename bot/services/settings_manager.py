import json
from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.setting import Setting


class SettingsManager:
    async def get_raw(self, session: AsyncSession, key: str, default: Optional[str] = None) -> Optional[str]:
        stmt = select(Setting).where(Setting.key == key)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return default
        return row.value

    async def set_raw(self, session: AsyncSession, key: str, value: str) -> None:
        stmt = select(Setting).where(Setting.key == key)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            row = Setting(key=key, value=value)
            session.add(row)
        else:
            row.value = value
        await session.flush()

    async def get_bool(self, session: AsyncSession, key: str, default: bool = False) -> bool:
        value = await self.get_raw(session, key)
        if value is None:
            return default
        return value.lower() in {"1", "true", "yes", "on"}

    async def set_bool(self, session: AsyncSession, key: str, value: bool) -> None:
        await self.set_raw(session, key, "true" if value else "false")

    async def get_json(self, session: AsyncSession, key: str, default: Any) -> Any:
        value = await self.get_raw(session, key)
        if value is None:
            return default
        try:
            return json.loads(value)
        except Exception:
            return default

    async def set_json(self, session: AsyncSession, key: str, value: Any) -> None:
        await self.set_raw(session, key, json.dumps(value, ensure_ascii=False))

    async def get_subscription_enabled(self, session: AsyncSession) -> bool:
        return await self.get_bool(session, "subscription.enabled", default=False)

    async def set_subscription_enabled(self, session: AsyncSession, enabled: bool) -> None:
        await self.set_bool(session, "subscription.enabled", enabled)

    async def get_subscription_channels(self, session: AsyncSession) -> List[str]:
        channels = await self.get_json(session, "subscription.channels", default=[])
        cleaned: List[str] = []
        for ch in channels if isinstance(channels, list) else []:
            chs = str(ch).strip()
            if chs:
                cleaned.append(chs)
        return cleaned

    async def set_subscription_channels(self, session: AsyncSession, channels: List[str]) -> None:
        unique = []
        seen = set()
        for ch in channels:
            value = str(ch).strip()
            if not value or value in seen:
                continue
            seen.add(value)
            unique.append(value)
        await self.set_json(session, "subscription.channels", unique)

    async def add_subscription_channel(self, session: AsyncSession, channel: str) -> List[str]:
        channels = await self.get_subscription_channels(session)
        channel = channel.strip()
        if channel and channel not in channels:
            channels.append(channel)
            await self.set_subscription_channels(session, channels)
        return channels

    async def remove_subscription_channel(self, session: AsyncSession, index: int) -> List[str]:
        channels = await self.get_subscription_channels(session)
        if 0 <= index < len(channels):
            channels.pop(index)
            await self.set_subscription_channels(session, channels)
        return channels

    async def get_maintenance_enabled(self, session: AsyncSession) -> bool:
        return await self.get_bool(session, "maintenance.enabled", default=False)

    async def set_maintenance_enabled(self, session: AsyncSession, enabled: bool) -> None:
        await self.set_bool(session, "maintenance.enabled", enabled)

    async def get_maintenance_message(self, session: AsyncSession, default: str) -> str:
        value = await self.get_raw(session, "maintenance.message")
        return value if value else default

    async def set_maintenance_message(self, session: AsyncSession, message: str) -> None:
        await self.set_raw(session, "maintenance.message", message)


settings_manager = SettingsManager()
