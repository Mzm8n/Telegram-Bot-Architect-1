import logging
from typing import List, Optional

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.section import Section
from bot.models.file_section import FileSection
from bot.core.constants import LogMessages

logger = logging.getLogger("bot")


class SectionService:
    async def list_sections(
        self,
        session: AsyncSession,
        parent_id: Optional[int] = None,
        include_inactive: bool = False,
    ) -> List[Section]:
        stmt = select(Section).where(Section.parent_id == parent_id)
        if not include_inactive:
            stmt = stmt.where(Section.is_active == True)
        stmt = stmt.order_by(Section.order.asc(), Section.id.asc())
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_section(
        self, session: AsyncSession, section_id: int
    ) -> Optional[Section]:
        stmt = select(Section).where(Section.id == section_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_section(
        self,
        session: AsyncSession,
        name: str,
        parent_id: Optional[int] = None,
        description: Optional[str] = None,
        order: int = 0,
    ) -> Section:
        section = Section(
            name=name,
            description=description,
            parent_id=parent_id,
            order=order,
        )
        session.add(section)
        await session.flush()
        logger.info(LogMessages.SECTION_CREATED.format(
            section_id=section.id, name=name
        ))
        return section

    async def update_section(
        self,
        session: AsyncSession,
        section_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        order: Optional[int] = None,
    ) -> Optional[Section]:
        section = await self.get_section(session, section_id)
        if section is None:
            return None

        if name is not None:
            section.name = name
        if description is not None:
            section.description = description
        if order is not None:
            section.order = order

        await session.flush()
        logger.info(LogMessages.SECTION_UPDATED.format(
            section_id=section_id, name=section.name
        ))
        return section

    async def soft_delete_section(
        self, session: AsyncSession, section_id: int
    ) -> Optional[Section]:
        section = await self.get_section(session, section_id)
        if section is None:
            return None

        section.is_active = False
        await session.flush()
        logger.info(LogMessages.SECTION_SOFT_DELETED.format(
            section_id=section_id, name=section.name
        ))
        return section

    async def get_next_order(
        self, session: AsyncSession, parent_id: Optional[int] = None
    ) -> int:
        stmt = (
            select(Section.order)
            .where(Section.parent_id == parent_id)
            .order_by(Section.order.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        max_order = result.scalar_one_or_none()
        return (max_order or 0) + 1

    async def has_children(
        self, session: AsyncSession, section_id: int
    ) -> bool:
        stmt = (
            select(Section.id)
            .where(Section.parent_id == section_id, Section.is_active == True)
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_breadcrumb(
        self, session: AsyncSession, section_id: int
    ) -> List[Section]:
        breadcrumb = []
        current_id: Optional[int] = section_id
        while current_id is not None:
            section = await self.get_section(session, current_id)
            if section is None:
                break
            breadcrumb.insert(0, section)
            current_id = section.parent_id
        return breadcrumb


    async def search_sections(
        self,
        session: AsyncSession,
        query: str,
        limit: int = 20,
    ) -> List[Section]:
        stmt = (
            select(Section)
            .where(
                Section.is_active == True,
                func.lower(Section.name).contains(query.lower()),
            )
            .order_by(Section.order.asc(), Section.id.asc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


    async def toggle_active(
        self, session: AsyncSession, section_id: int
    ) -> Optional[Section]:
        section = await self.get_section(session, section_id)
        if section is None:
            return None

        section.is_active = not section.is_active
        await session.flush()
        logger.info(LogMessages.SECTION_TOGGLED.format(
            section_id=section_id, is_active=section.is_active
        ))
        return section

    async def copy_section_tree(
        self,
        session: AsyncSession,
        source_id: int,
        target_parent_id: Optional[int] = None,
    ) -> Optional[Section]:
        source = await self.get_section(session, source_id)
        if source is None:
            return None

        new_section = Section(
            name=f"{source.name} (نسخة)",
            description=source.description,
            parent_id=target_parent_id,
            order=source.order,
            is_active=source.is_active,
        )
        session.add(new_section)
        await session.flush()

        stmt = select(FileSection).where(FileSection.section_id == source_id)
        result = await session.execute(stmt)
        file_sections = list(result.scalars().all())
        for fs in file_sections:
            new_fs = FileSection(
                file_id=fs.file_id,
                section_id=new_section.id,
            )
            session.add(new_fs)
        await session.flush()

        children_stmt = select(Section).where(Section.parent_id == source_id)
        children_result = await session.execute(children_stmt)
        children = list(children_result.scalars().all())
        for child in children:
            await self.copy_section_tree(session, child.id, new_section.id)

        return new_section


section_service = SectionService()
