"""
Course Progress model.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Integer, Numeric, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class EnrollmentStatus(str, Enum):
    """Enrollment status."""

    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"


class CourseProgress(Base):
    """Course progress model."""

    __tablename__ = "course_progress"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # References
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)

    # Progress tracking
    status: Mapped[str] = mapped_column(default=EnrollmentStatus.ACTIVE, index=True)
    completion_percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)
    completed_lessons: Mapped[int] = mapped_column(Integer, default=0)
    total_lessons: Mapped[int] = mapped_column(Integer, default=0)

    # Time tracking
    total_time_spent: Mapped[int] = mapped_column(
        Integer, default=0, comment="Time in minutes"
    )

    # Flags
    is_certificate_issued: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_accessed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<CourseProgress user={self.user_id} course={self.course_id}>"
