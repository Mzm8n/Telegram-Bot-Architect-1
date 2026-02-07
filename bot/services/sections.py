import logging
from typing import List, Optional

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.section import Section
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


section_service = SectionService()
