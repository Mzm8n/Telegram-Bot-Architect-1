import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Integer, String, Text, Boolean, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from bot.core.database import Base


class FileStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    file_id: Mapped[str] = mapped_column(String(255), index=True)
    file_unique_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(50))
    size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default=FileStatus.PUBLISHED.value,
    )
    uploaded_by: Mapped[int] = mapped_column(BigInteger, index=True)
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
