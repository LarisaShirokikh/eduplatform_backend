"""
Lesson model.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.database import Base


class LessonType(str, Enum):
    """Lesson content type."""

    VIDEO = "video"
    TEXT = "text"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"


class Lesson(Base):
    """Lesson model."""

    __tablename__ = "lessons"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Content
    content_type: Mapped[str] = mapped_column(String(20), default=LessonType.VIDEO)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    video_url: Mapped[str] = mapped_column(String(500), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)

    # Order
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Status
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    is_preview: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    # course = relationship("Course", back_populates="lessons")

    def __repr__(self) -> str:
        return f"<Lesson {self.title}>"
