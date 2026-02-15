import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.audit_log import AuditLog
from bot.models.file import File
from bot.models.file_section import FileSection
from bot.models.moderator_permission import ModeratorPermission
from bot.models.section import Section
from bot.models.setting import Setting
from bot.models.text_entry import TextEntry
from bot.models.user import User


class BackupService:
    TABLES_ORDER = [
        User,
        TextEntry,
        Setting,
        Section,
        File,
        FileSection,
        ModeratorPermission,
        AuditLog,
    ]

    async def export_backup(self, session: AsyncSession, dir_path: str = "backups") -> str:
        data: Dict[str, List[Dict[str, Any]]] = {}
        for model in self.TABLES_ORDER:
            result = await session.execute(select(model))
            rows = result.scalars().all()
            table_rows: List[Dict[str, Any]] = []
            for row in rows:
                row_data: Dict[str, Any] = {}
                for column in model.__table__.columns:
                    value = getattr(row, column.name)
                    if hasattr(value, "value"):
                        value = value.value
                    if hasattr(value, "isoformat"):
                        value = value.isoformat()
                    row_data[column.name] = value
                table_rows.append(row_data)
            data[model.__tablename__] = table_rows

        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        filename = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = path / filename
        backup_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(backup_path)

    async def restore_backup(self, session: AsyncSession, backup_data: Dict[str, Any]) -> None:
        for model in reversed(self.TABLES_ORDER):
            await session.execute(delete(model))

        for model in self.TABLES_ORDER:
            rows = backup_data.get(model.__tablename__, [])
            for row_data in rows if isinstance(rows, list) else []:
                payload = {k: v for k, v in row_data.items() if k in model.__table__.columns.keys()}
                session.add(model(**payload))

        await session.flush()


backup_service = BackupService()
