import logging
from typing import List, Optional, Tuple

from aiogram import Bot
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core.constants import LogMessages
from bot.models.file import File, FileStatus
from bot.models.file_section import FileSection

logger = logging.getLogger("bot")

FILES_PER_PAGE = 5


class FileService:
    async def create_file(
        self,
        session: AsyncSession,
        file_id: str,
        file_unique_id: str,
        name: str,
        file_type: str,
        uploaded_by: int,
        size: Optional[int] = None,
        caption: Optional[str] = None,
        status: str = FileStatus.PUBLISHED.value,
    ) -> File:
        f = File(
            file_id=file_id,
            file_unique_id=file_unique_id,
            name=name,
            file_type=file_type,
            size=size,
            status=status,
            uploaded_by=uploaded_by,
            caption=caption,
        )
        session.add(f)
        await session.flush()
        logger.info(LogMessages.FILE_CREATED.format(
            file_id=f.id, name=name, user_id=uploaded_by
        ))
        return f

    async def get_file(
        self, session: AsyncSession, file_id: int
    ) -> Optional[File]:
        stmt = select(File).where(File.id == file_id, File.is_active == True)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_file_by_unique_id(
        self, session: AsyncSession, file_unique_id: str
    ) -> Optional[File]:
        stmt = select(File).where(
            File.file_unique_id == file_unique_id,
            File.is_active == True,
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_files_by_section(
        self, session: AsyncSession, section_id: int
    ) -> int:
        count_stmt = (
            select(func.count())
            .select_from(FileSection)
            .join(File, File.id == FileSection.file_id)
            .where(
                FileSection.section_id == section_id,
                File.is_active == True,
                File.status == FileStatus.PUBLISHED.value,
            )
        )
        result = await session.execute(count_stmt)
        return result.scalar() or 0

    async def check_duplicate(
        self, session: AsyncSession, file_unique_id: str
    ) -> Optional[File]:
        existing = await self.get_file_by_unique_id(session, file_unique_id)
        if existing:
            logger.info(LogMessages.FILE_DUPLICATE.format(
                file_unique_id=file_unique_id
            ))
        return existing

    async def list_files_by_section(
        self,
        session: AsyncSession,
        section_id: int,
        page: int = 1,
        per_page: int = FILES_PER_PAGE,
    ) -> Tuple[List[File], int]:
        count_stmt = (
            select(func.count())
            .select_from(FileSection)
            .join(File, File.id == FileSection.file_id)
            .where(
                FileSection.section_id == section_id,
                File.is_active == True,
                File.status == FileStatus.PUBLISHED.value,
            )
        )
        total_result = await session.execute(count_stmt)
        total = total_result.scalar() or 0

        offset = (page - 1) * per_page
        stmt = (
            select(File)
            .join(FileSection, File.id == FileSection.file_id)
            .where(
                FileSection.section_id == section_id,
                File.is_active == True,
                File.status == FileStatus.PUBLISHED.value,
            )
            .order_by(File.id.desc())
            .offset(offset)
            .limit(per_page)
        )
        result = await session.execute(stmt)
        files = list(result.scalars().all())
        total_pages = max(1, (total + per_page - 1) // per_page)
        return files, total_pages

    async def list_all_files_by_section(
        self,
        session: AsyncSession,
        section_id: int,
    ) -> List[File]:
        stmt = (
            select(File)
            .join(FileSection, File.id == FileSection.file_id)
            .where(
                FileSection.section_id == section_id,
                File.is_active == True,
                File.status == FileStatus.PUBLISHED.value,
            )
            .order_by(File.id.asc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def link_file_to_section(
        self, session: AsyncSession, file_id: int, section_id: int
    ) -> bool:
        existing = await session.execute(
            select(FileSection).where(
                FileSection.file_id == file_id,
                FileSection.section_id == section_id,
            )
        )
        if existing.scalar_one_or_none():
            return False

        fs = FileSection(file_id=file_id, section_id=section_id)
        session.add(fs)
        await session.flush()
        logger.info(LogMessages.FILE_LINKED.format(
            file_id=file_id, section_id=section_id
        ))
        return True

    async def unlink_file_from_section(
        self, session: AsyncSession, file_id: int, section_id: int
    ) -> bool:
        stmt = select(FileSection).where(
            FileSection.file_id == file_id,
            FileSection.section_id == section_id,
        )
        result = await session.execute(stmt)
        fs = result.scalar_one_or_none()
        if fs is None:
            return False

        await session.delete(fs)
        await session.flush()
        logger.info(LogMessages.FILE_UNLINKED.format(
            file_id=file_id, section_id=section_id
        ))
        return True

    async def soft_delete_file(
        self, session: AsyncSession, file_id: int
    ) -> Optional[File]:
        f = await self.get_file(session, file_id)
        if f is None:
            return None

        f.is_active = False
        await session.flush()
        logger.info(LogMessages.FILE_SOFT_DELETED.format(
            file_id=file_id, name=f.name
        ))
        return f

    async def get_file_sections(
        self, session: AsyncSession, file_id: int
    ) -> List[int]:
        stmt = select(FileSection.section_id).where(
            FileSection.file_id == file_id
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


file_service = FileService()


async def send_file_to_user(bot: Bot, chat_id: int, file: File) -> bool:
    try:
        if file.file_type == "photo":
            await bot.send_photo(chat_id=chat_id, photo=file.file_id, caption=file.caption)
        elif file.file_type == "video":
            await bot.send_video(chat_id=chat_id, video=file.file_id, caption=file.caption)
        elif file.file_type == "audio":
            await bot.send_audio(chat_id=chat_id, audio=file.file_id, caption=file.caption)
        elif file.file_type == "voice":
            await bot.send_voice(chat_id=chat_id, voice=file.file_id, caption=file.caption)
        elif file.file_type == "video_note":
            await bot.send_video_note(chat_id=chat_id, video_note=file.file_id)
        elif file.file_type == "animation":
            await bot.send_animation(chat_id=chat_id, animation=file.file_id, caption=file.caption)
        elif file.file_type == "sticker":
            await bot.send_sticker(chat_id=chat_id, sticker=file.file_id)
        else:
            await bot.send_document(chat_id=chat_id, document=file.file_id, caption=file.caption)
        return True
    except Exception as e:
        logger.error(LogMessages.FILE_SEND_FAILED.format(file_id=file.id, error=str(e)))
        return False
