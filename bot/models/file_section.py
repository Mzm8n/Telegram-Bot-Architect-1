from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from bot.core.database import Base


class FileSection(Base):
    __tablename__ = "file_sections"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    file_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("files.id", ondelete="CASCADE"),
        index=True,
    )
    section_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("sections.id", ondelete="CASCADE"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("file_id", "section_id", name="uq_file_section"),
    )
