"""
Notification schemas for API validation.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from ..models.notification import NotificationStatus, NotificationType


class NotificationResponse(BaseModel):
    """Schema for notification response."""

    id: uuid.UUID
    user_id: uuid.UUID
    type: NotificationType
    status: NotificationStatus
    title: str
    message: str
    event_type: Optional[str]
    event_id: Optional[uuid.UUID]
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list."""

    notifications: list[NotificationResponse]
    total: int
    unread_count: int
