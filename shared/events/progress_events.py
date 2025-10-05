"""
Progress and certificate event schemas for Kafka messaging.
"""

import uuid
from typing import Optional

from pydantic import Field

from .base import BaseEvent


class ProgressUpdatedEvent(BaseEvent):
    """Event emitted when student progress is updated."""

    event_type: str = Field(default="progress.updated", frozen=True)
    service: str = Field(default="progress-service", frozen=True)

    student_id: uuid.UUID = Field(..., description="ID of student")
    course_id: uuid.UUID = Field(..., description="ID of course")
    completion_percentage: int = Field(..., description="Overall completion percentage")
    lessons_completed: int = Field(..., description="Number of lessons completed")
    total_lessons: int = Field(..., description="Total number of lessons")
    time_spent_seconds: int = Field(..., description="Total time spent on course")


class CourseCompletedEvent(BaseEvent):
    """Event emitted when a student completes a course."""

    event_type: str = Field(default="course.completed", frozen=True)
    service: str = Field(default="progress-service", frozen=True)

    student_id: uuid.UUID = Field(..., description="ID of student")
    course_id: uuid.UUID = Field(..., description="ID of completed course")
    completion_date: str = Field(..., description="Course completion date")
    final_score: Optional[float] = Field(default=None, description="Final course score")
    total_time_spent_seconds: int = Field(..., description="Total time spent on course")


class CertificateRequestedEvent(BaseEvent):
    """Event emitted when a certificate is requested."""

    event_type: str = Field(default="certificate.requested", frozen=True)
    service: str = Field(default="progress-service", frozen=True)

    student_id: uuid.UUID = Field(..., description="ID of student")
    course_id: uuid.UUID = Field(..., description="ID of course")
    completion_date: str = Field(..., description="Course completion date")


class CertificateIssuedEvent(BaseEvent):
    """Event emitted when a certificate is issued."""

    event_type: str = Field(default="certificate.issued", frozen=True)
    service: str = Field(default="certificate-service", frozen=True)

    certificate_id: uuid.UUID = Field(..., description="ID of issued certificate")
    student_id: uuid.UUID = Field(..., description="ID of student")
    course_id: uuid.UUID = Field(..., description="ID of course")
    certificate_url: str = Field(..., description="URL to download certificate")
    verification_code: str = Field(..., description="Certificate verification code")
    issue_date: str = Field(..., description="Certificate issue date")


class CertificateRevokedEvent(BaseEvent):
    """Event emitted when a certificate is revoked."""

    event_type: str = Field(default="certificate.revoked", frozen=True)
    service: str = Field(default="certificate-service", frozen=True)

    certificate_id: uuid.UUID = Field(..., description="ID of revoked certificate")
    student_id: uuid.UUID = Field(..., description="ID of student")
    course_id: uuid.UUID = Field(..., description="ID of course")
    revocation_reason: str = Field(..., description="Reason for revocation")
    revoked_by: uuid.UUID = Field(..., description="ID of user who revoked certificate")
