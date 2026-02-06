from sqlalchemy import Integer, String, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from bot.core.database import Base


class TextEntry(Base):
    __tablename__ = "text_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(255), index=True)
    language: Mapped[str] = mapped_column(String(10), default="ar")
    text: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("key", "language", name="uq_text_key_language"),
    )
