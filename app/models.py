import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Status(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class Category(str, enum.Enum):
    ROAD = "road"
    WATER = "water"
    ELECTRICITY = "electricity"
    WASTE = "waste"
    OTHER = "other"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[Category] = mapped_column(Enum(Category), index=True)
    citizen_name: Mapped[str] = mapped_column(String(80))
    phone: Mapped[str | None] = mapped_column(String(15), nullable=True)
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.PENDING, index=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )
