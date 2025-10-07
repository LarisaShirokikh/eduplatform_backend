"""
Course model.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Boolean, DateTime, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.database import Base


class CourseLevel(str, Enum):
    """Course difficulty level."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CourseStatus(str, Enum):
    """Course publication status."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Course(Base):
    """Course model."""

    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(
        String(200), unique=True, nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    short_description: Mapped[str] = mapped_column(String(500), nullable=True)

    # Instructor
    instructor_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)

    # Course details
    level: Mapped[str] = mapped_column(String(20), default=CourseLevel.BEGINNER)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(10), default="en")

    # Pricing
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=True)
    is_free: Mapped[bool] = mapped_column(Boolean, default=False)

    # Media
    thumbnail_url: Mapped[str] = mapped_column(String(500), nullable=True)
    preview_video_url: Mapped[str] = mapped_column(String(500), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(20), default=CourseStatus.DRAFT)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Stats
    student_count: Mapped[int] = mapped_column(default=0)
    rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=0.0)
    review_count: Mapped[int] = mapped_column(default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    # lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Course {self.title}>"
