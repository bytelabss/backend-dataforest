import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, func, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class TermSection(Base):
    __tablename__ = "term_sections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    term_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("terms.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, default=False)

    term = relationship("Terms", back_populates="sections")

    def __repr__(self) -> str:
        return f"<TermSection(id='{self.id}', title='{self.title}', required={self.required})>"


class UserConsentSection(Base):
    __tablename__ = "user_consent_sections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    section_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("term_sections.id"), nullable=False)
    accepted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    accepted_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    section = relationship("TermSection")

    def __repr__(self) -> str:
        return f"<UserConsentSection(id='{self.id}', accepted={self.accepted}, section_id='{self.section_id}')>"

class Terms(Base):
    __tablename__ = "terms"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    sections = relationship("TermSection", back_populates="term")