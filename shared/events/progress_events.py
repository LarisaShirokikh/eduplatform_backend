"""
Progress and certificate event schemas for Kafka messaging.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import Field

from .base import BaseEvent


class EnrollmentCreatedEvent(BaseEvent):
    """Event emitted when user enrolls in a course."""

    event_type: str = Field(default="enrollment.created", frozen=True)
    service: str = Field(default="progress-service", frozen=True)

    user_id: uuid.UUID = Field(..., description="ID of user")
    course_id: uuid.UUID = Field(..., description="ID of course")
    total_lessons: int = Field(..., description="Total lessons in course")
    enrolled_at: datetime = Field(..., description="Enrollment timestamp")


class LessonCompletedEvent(BaseEvent):
    """Event emitted when user completes a lesson."""

    event_type: str = Field(default="lesson.completed", frozen=True)
    service: str = Field(default="progress-service", frozen=True)

    user_id: uuid.UUID = Field(..., description="ID of user")
    course_id: uuid.UUID = Field(..., description="ID of course")
    lesson_id: uuid.UUID = Field(..., description="ID of lesson")
    time_spent: int = Field(..., description="Time spent in minutes")
    completed_at: datetime = Field(..., description="Completion timestamp")


class ProgressUpdatedEvent(BaseEvent):
    """Event emitted when course progress is updated."""

    event_type: str = Field(default="progress.updated", frozen=True)
    service: str = Field(default="progress-service", frozen=True)

    user_id: uuid.UUID = Field(..., description="ID of user")
    course_id: uuid.UUID = Field(..., description="ID of course")
    completion_percentage: float = Field(..., description="Completion percentage")
    completed_lessons: int = Field(..., description="Number of completed lessons")
    total_lessons: int = Field(..., description="Total number of lessons")
    time_spent_seconds: int = Field(default=0, description="Total time spent")


class CourseCompletedEvent(BaseEvent):
    """Event emitted when user completes a course."""

    event_type: str = Field(default="course.completed", frozen=True)
    service: str = Field(default="progress-service", frozen=True)

    user_id: uuid.UUID = Field(..., description="ID of user")
    course_id: uuid.UUID = Field(..., description="ID of course")
    completion_percentage: float = Field(
        default=100.0, description="Completion percentage"
    )
    total_time_spent: int = Field(..., description="Total time spent in minutes")
    completed_at: datetime = Field(..., description="Completion timestamp")
    total_lessons: int = Field(..., description="Total lessons completed")
    final_score: Optional[float] = Field(
        default=None, description="Final score if applicable"
    )


class CertificateRequestedEvent(BaseEvent):
    """Event emitted when a certificate is requested."""

    event_type: str = Field(default="certificate.requested", frozen=True)
    service: str = Field(default="progress-service", frozen=True)

    student_id: uuid.UUID = Field(..., description="ID of student")
    course_id: uuid.UUID = Field(..., description="ID of course")
    completion_date: datetime = Field(..., description="Course completion date")


class CertificateIssuedEvent(BaseEvent):
    """Event emitted when a certificate is issued."""

    event_type: str = Field(default="certificate.issued", frozen=True)
    service: str = Field(default="certificate-service", frozen=True)

    certificate_id: uuid.UUID = Field(..., description="ID of issued certificate")
    student_id: uuid.UUID = Field(..., description="ID of student")
    course_id: uuid.UUID = Field(..., description="ID of course")
    certificate_url: str = Field(..., description="URL to download certificate")
    verification_code: str = Field(..., description="Certificate verification code")
    issue_date: datetime = Field(..., description="Certificate issue date")


class CertificateRevokedEvent(BaseEvent):
    """Event emitted when a certificate is revoked."""

    event_type: str = Field(default="certificate.revoked", frozen=True)
    service: str = Field(default="certificate-service", frozen=True)

    certificate_id: uuid.UUID = Field(..., description="ID of revoked certificate")
    student_id: uuid.UUID = Field(..., description="ID of student")
    course_id: uuid.UUID = Field(..., description="ID of course")
    revocation_reason: str = Field(..., description="Reason for revocation")
    revoked_by: uuid.UUID = Field(..., description="ID of user who revoked certificate")
