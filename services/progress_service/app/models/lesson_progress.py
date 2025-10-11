"""
Lesson Progress model.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class LessonProgress(Base):
    """Lesson progress model."""

    __tablename__ = "lesson_progress"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # References
    course_progress_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("course_progress.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    lesson_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)

    # Progress
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completion_percentage: Mapped[int] = mapped_column(Integer, default=0)
    time_spent: Mapped[int] = mapped_column(
        Integer, default=0, comment="Time in minutes"
    )

    # Tracking
    watch_count: Mapped[int] = mapped_column(Integer, default=0)
    last_position: Mapped[int] = mapped_column(
        Integer, default=0, comment="Last position in seconds"
    )

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_accessed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<LessonProgress lesson={self.lesson_id} user={self.user_id}>"
