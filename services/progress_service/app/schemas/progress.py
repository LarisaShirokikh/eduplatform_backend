"""
Progress schemas for API validation.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..models.progress import EnrollmentStatus


class EnrollmentRequest(BaseModel):
    """Schema for enrolling in a course."""

    course_id: uuid.UUID


class CourseProgressResponse(BaseModel):
    """Schema for course progress response."""

    id: uuid.UUID
    user_id: uuid.UUID
    course_id: uuid.UUID
    status: EnrollmentStatus
    completion_percentage: float
    completed_lessons: int
    total_lessons: int
    total_time_spent: int
    is_certificate_issued: bool
    enrolled_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    last_accessed_at: Optional[datetime]

    class Config:
        from_attributes = True


class LessonProgressResponse(BaseModel):
    """Schema for lesson progress response."""

    id: uuid.UUID
    user_id: uuid.UUID
    lesson_id: uuid.UUID
    is_completed: bool
    completion_percentage: int
    time_spent: int
    watch_count: int
    last_position: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    last_accessed_at: datetime

    class Config:
        from_attributes = True


class MarkLessonCompleteRequest(BaseModel):
    """Schema for marking lesson as complete."""

    lesson_id: uuid.UUID
    time_spent: int = Field(default=0, ge=0, description="Time spent in minutes")
