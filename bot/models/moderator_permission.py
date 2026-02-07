from sqlalchemy import BigInteger, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from bot.core.database import Base


class ModeratorPermission(Base):
    __tablename__ = "moderator_permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    can_upload: Mapped[bool] = mapped_column(Boolean, default=True)
    can_link: Mapped[bool] = mapped_column(Boolean, default=True)
    can_publish: Mapped[bool] = mapped_column(Boolean, default=False)
    own_files_only: Mapped[bool] = mapped_column(Boolean, default=False)
