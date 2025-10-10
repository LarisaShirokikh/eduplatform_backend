"""
Notification model.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class NotificationType(str, Enum):
    """Notification type."""

    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"


class NotificationStatus(str, Enum):
    """Notification status."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"


class Notification(Base):
    """Notification model."""

    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Recipient
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)

    # Notification details
    type: Mapped[str] = mapped_column(String(20), default=NotificationType.IN_APP)
    status: Mapped[str] = mapped_column(
        String(20), default=NotificationStatus.PENDING, index=True
    )

    # Content
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Metadata
    event_type: Mapped[str] = mapped_column(String(100), nullable=True)
    event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=True)

    # Flags
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    read_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Notification {self.title}>"
