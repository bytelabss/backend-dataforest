import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    encrypted_password: Mapped[str]

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    reforested_areas = relationship("ReforestedArea", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, plaintext_password: str) -> None:
        from .services import PasswordService

        self.encrypted_password = PasswordService.hash_password(plaintext_password)

    def check_password(self, plaintext_password: str) -> bool:
        from .services import PasswordService

        return PasswordService.verify_password(
            self.encrypted_password, plaintext_password
        )

    def __repr__(self) -> str:
        return f"User(id='{self.id}', email='{self.email}', name='{self.full_name}')"
