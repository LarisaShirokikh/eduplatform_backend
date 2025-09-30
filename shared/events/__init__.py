"""
Event schemas for Kafka messaging in EduPlatform.
"""

from .base import BaseEvent, EventMetadata
from .course_events import (
    CourseCreatedEvent,
    CourseDeletedEvent,
    CourseEnrolledEvent,
    CoursePublishedEvent,
    CourseUnenrolledEvent,
    CourseUpdatedEvent,
    LessonCompletedEvent,
    LessonCreatedEvent,
    LessonStartedEvent,
    LessonUpdatedEvent,
)
from .file_notification_events import (
    EmailSendEvent,
    FileUploadedEvent,
    NotificationSendEvent,
    PushSendEvent,
    SMSSendEvent,
    VideoProcessingCompletedEvent,
    VideoProcessingFailedEvent,
    VideoProcessingStartedEvent,
)
from .progress_events import (
    CertificateIssuedEvent,
    CertificateRequestedEvent,
    CertificateRevokedEvent,
    CourseCompletedEvent,
    ProgressUpdatedEvent,
)
from .user_events import (
    UserDeletedEvent,
    UserEmailVerifiedEvent,
    UserLoginEvent,
    UserLogoutEvent,
    UserPasswordChangedEvent,
    UserRegisteredEvent,
    UserUpdatedEvent,
)

__all__ = [
    # Base
    "BaseEvent",
    "EventMetadata",
    # User events
    "UserRegisteredEvent",
    "UserUpdatedEvent",
    "UserDeletedEvent",
    "UserLoginEvent",
    "UserLogoutEvent",
    "UserEmailVerifiedEvent",
    "UserPasswordChangedEvent",
    # Course events
    "CourseCreatedEvent",
    "CourseUpdatedEvent",
    "CoursePublishedEvent",
    "CourseDeletedEvent",
    "CourseEnrolledEvent",
    "CourseUnenrolledEvent",
    "LessonCreatedEvent",
    "LessonUpdatedEvent",
    "LessonCompletedEvent",
    "LessonStartedEvent",
    # Progress events
    "ProgressUpdatedEvent",
    "CourseCompletedEvent",
    "CertificateRequestedEvent",
    "CertificateIssuedEvent",
    "CertificateRevokedEvent",
    # File events
    "FileUploadedEvent",
    "VideoProcessingStartedEvent",
    "VideoProcessingCompletedEvent",
    "VideoProcessingFailedEvent",
    # Notification events
    "NotificationSendEvent",
    "EmailSendEvent",
    "SMSSendEvent",
    "PushSendEvent",
]
