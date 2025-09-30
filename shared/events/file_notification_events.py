"""
File processing and notification event schemas.
"""

import uuid
from typing import Dict, Optional

from pydantic import Field

from .base import BaseEvent


# File Events
class FileUploadedEvent(BaseEvent):
    """Event emitted when a file is uploaded."""

    event_type: str = Field(default="file.uploaded", frozen=True)
    service: str = Field(default="file-service", frozen=True)

    file_id: uuid.UUID = Field(..., description="ID of uploaded file")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File MIME type")
    file_size: int = Field(..., description="File size in bytes")
    storage_path: str = Field(..., description="File storage path")
    uploaded_by: uuid.UUID = Field(..., description="ID of user who uploaded file")


class VideoProcessingStartedEvent(BaseEvent):
    """Event emitted when video processing starts."""

    event_type: str = Field(default="video.processing.started", frozen=True)
    service: str = Field(default="file-service", frozen=True)

    file_id: uuid.UUID = Field(..., description="ID of video file")
    lesson_id: Optional[uuid.UUID] = Field(
        default=None, description="ID of associated lesson"
    )
    original_filename: str = Field(..., description="Original video filename")
    quality_levels: list[str] = Field(..., description="Quality levels to generate")


class VideoProcessingCompletedEvent(BaseEvent):
    """Event emitted when video processing completes successfully."""

    event_type: str = Field(default="video.processing.completed", frozen=True)
    service: str = Field(default="file-service", frozen=True)

    file_id: uuid.UUID = Field(..., description="ID of video file")
    lesson_id: Optional[uuid.UUID] = Field(
        default=None, description="ID of associated lesson"
    )
    output_files: Dict[str, str] = Field(
        ..., description="Dict of quality -> file path"
    )
    thumbnail_url: Optional[str] = Field(default=None, description="Thumbnail URL")
    duration_seconds: int = Field(..., description="Video duration in seconds")
    processing_time_seconds: int = Field(..., description="Time taken to process")


class VideoProcessingFailedEvent(BaseEvent):
    """Event emitted when video processing fails."""

    event_type: str = Field(default="video.processing.failed", frozen=True)
    service: str = Field(default="file-service", frozen=True)

    file_id: uuid.UUID = Field(..., description="ID of video file")
    lesson_id: Optional[uuid.UUID] = Field(
        default=None, description="ID of associated lesson"
    )
    error_message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(default=None, description="Error code")


# Notification Events
class NotificationSendEvent(BaseEvent):
    """Generic notification send event."""

    event_type: str = Field(default="notification.send", frozen=True)
    service: str = Field(default="notification-service", frozen=True)

    notification_type: str = Field(
        ..., description="Type of notification (email/sms/push)"
    )
    recipient_id: uuid.UUID = Field(..., description="ID of recipient user")
    template_id: str = Field(..., description="Notification template ID")
    template_data: Dict[str, str] = Field(
        default_factory=dict, description="Data for template rendering"
    )
    priority: str = Field(default="normal", description="Priority (low/normal/high)")


class EmailSendEvent(BaseEvent):
    """Event for sending email notifications."""

    event_type: str = Field(default="email.send", frozen=True)
    service: str = Field(default="notification-service", frozen=True)

    recipient_email: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    template_id: str = Field(..., description="Email template ID")
    template_data: Dict[str, str] = Field(
        default_factory=dict, description="Data for template rendering"
    )
    priority: str = Field(default="normal", description="Priority (low/normal/high)")


class SMSSendEvent(BaseEvent):
    """Event for sending SMS notifications."""

    event_type: str = Field(default="sms.send", frozen=True)
    service: str = Field(default="notification-service", frozen=True)

    recipient_phone: str = Field(..., description="Recipient phone number")
    message: str = Field(..., description="SMS message content")
    template_id: Optional[str] = Field(default=None, description="SMS template ID")
    priority: str = Field(default="normal", description="Priority (low/normal/high)")


class PushSendEvent(BaseEvent):
    """Event for sending push notifications."""

    event_type: str = Field(default="push.send", frozen=True)
    service: str = Field(default="notification-service", frozen=True)

    recipient_id: uuid.UUID = Field(..., description="Recipient user ID")
    title: str = Field(..., description="Notification title")
    body: str = Field(..., description="Notification body")
    data: Dict[str, str] = Field(
        default_factory=dict, description="Additional notification data"
    )
    priority: str = Field(default="normal", description="Priority (low/normal/high)")
