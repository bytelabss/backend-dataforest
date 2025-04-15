import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import SecondaryBase


class UsersKeys(SecondaryBase):
    __tablename__ = "user_keys"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str]
    encryption_key: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
