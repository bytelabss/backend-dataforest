import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import MemoryBase


class TempUser(MemoryBase):
    __tablename__ = "user_temps"

    id: Mapped[str] = mapped_column(primary_key=True)
    full_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
