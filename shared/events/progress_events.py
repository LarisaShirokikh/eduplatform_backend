"""
Course-related event schemas for Kafka messaging.
"""

import uuid
from decimal import Decimal
from typing import Optional

from pydantic import Field

from .base import BaseEvent


class CourseCreatedEvent(BaseEvent):
    """Event emitted when a new course is created."""

    event_type: str = Field(default="course.created", frozen=True)
    service: str = Field(default="course-service", frozen=True)

    course_id: uuid.UUID = Field(..., description="ID of newly created course")
    title: str = Field(..., description="Course title")
    instructor_id: uuid.UUID = Field(..., description="ID of course instructor")
    category: str = Field(..., description="Course category")
    price: Optional[Decimal] = Field(default=None, description="Course price")
    is_published: bool = Field(default=False, description="Publication status")


class CourseUpdatedEvent(BaseEvent):
    """Event emitted when a course is updated."""

    event_type: str = Field(default="course.updated", frozen=True)
    service: str = Field(default="course-service", frozen=True)

    course_id: uuid.UUID = Field(..., description="ID of updated course")
    fields_updated: list[str] = Field(..., description="List of updated fields")


class CoursePublishedEvent(BaseEvent):
    """Event emitted when a course is published."""

    event_type: str = Field(default="course.published", frozen=True)
    service: str = Field(default="course-service", frozen=True)

    course_id: uuid.UUID = Field(..., description="ID of published course")
    title: str = Field(..., description="Course title")
    instructor_id: uuid.UUID = Field(..., description="ID of course instructor")
    lesson_count: int = Field(..., description="Number of lessons in course")


class CourseDeletedEvent(BaseEvent):
    """Event emitted when a course is deleted."""

    event_type: str = Field(default="course.deleted", frozen=True)
    service: str = Field(default="course-service", frozen=True)

    course_id: uuid.UUID = Field(..., description="ID of deleted course")
    deletion_reason: Optional[str] = Field(
        default=None, description="Reason for deletion"
    )


class CourseEnrolledEvent(BaseEvent):
    """Event emitted when a user enrolls in a course."""

    event_type: str = Field(default="course.enrolled", frozen=True)
    service: str = Field(default="course-service", frozen=True)

    course_id: uuid.UUID = Field(..., description="ID of course")
    student_id: uuid.UUID = Field(..., description="ID of enrolled student")
    enrollment_type: str = Field(
        default="paid", description="Enrollment type (paid/free/trial)"
    )
    price_paid: Optional[Decimal] = Field(
        default=None, description="Amount paid for enrollment"
    )


class CourseUnenrolledEvent(BaseEvent):
    """Event emitted when a user unenrolls from a course."""

    event_type: str = Field(default="course.unenrolled", frozen=True)
    service: str = Field(default="course-service", frozen=True)

    course_id: uuid.UUID = Field(..., description="ID of course")
    student_id: uuid.UUID = Field(..., description="ID of unenrolled student")
    reason: Optional[str] = Field(default=None, description="Reason for unenrollment")


class LessonCreatedEvent(BaseEvent):
    """Event emitted when a new lesson is created."""

    event_type: str = Field(default="lesson.created", frozen=True)
    service: str = Field(default="course-service", frozen=True)

    lesson_id: uuid.UUID = Field(..., description="ID of newly created lesson")
    course_id: uuid.UUID = Field(..., description="ID of parent course")
    title: str = Field(..., description="Lesson title")
    order: int = Field(..., description="Lesson order in course")
    content_type: str = Field(..., description="Type of content (video/text/quiz)")


class LessonUpdatedEvent(BaseEvent):
    """Event emitted when a lesson is updated."""

    event_type: str = Field(default="lesson.updated", frozen=True)
    service: str = Field(default="course-service", frozen=True)

    lesson_id: uuid.UUID = Field(..., description="ID of updated lesson")
    course_id: uuid.UUID = Field(..., description="ID of parent course")
    fields_updated: list[str] = Field(..., description="List of updated fields")


class LessonCompletedEvent(BaseEvent):
    """Event emitted when a student completes a lesson."""

    event_type: str = Field(default="lesson.completed", frozen=True)
    service: str = Field(default="progress-service", frozen=True)

    lesson_id: uuid.UUID = Field(..., description="ID of completed lesson")
    course_id: uuid.UUID = Field(..., description="ID of parent course")
    student_id: uuid.UUID = Field(..., description="ID of student")
    completion_percentage: int = Field(default=100, description="Completion percentage")
    time_spent_seconds: Optional[int] = Field(
        default=None, description="Time spent on lesson"
    )


class LessonStartedEvent(BaseEvent):
    """Event emitted when a student starts a lesson."""

    event_type: str = Field(default="lesson.started", frozen=True)
    service: str = Field(default="progress-service", frozen=True)

    lesson_id: uuid.UUID = Field(..., description="ID of started lesson")
    course_id: uuid.UUID = Field(..., description="ID of parent course")
    student_id: uuid.UUID = Field(..., description="ID of student")
