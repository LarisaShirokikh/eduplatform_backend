"""
Notification repository for database operations.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import BaseRepository

from ..models.notification import Notification, NotificationStatus


class NotificationRepository(BaseRepository[Notification]):
    """Repository for Notification model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Notification, session)

    async def get_by_user(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[Notification]:
        """
        Get notifications for a specific user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            list[Notification]: List of notifications
        """
        result = await self.session.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_unread(
        self, user_id: uuid.UUID, limit: int = 50
    ) -> list[Notification]:
        """
        Get unread notifications for a user.

        Args:
            user_id: User ID
            limit: Maximum number of records

        Returns:
            list[Notification]: List of unread notifications
        """
        result = await self.session.execute(
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_as_read(self, notification_id: uuid.UUID) -> Notification | None:
        """
        Mark notification as read.

        Args:
            notification_id: Notification ID

        Returns:
            Notification | None: Updated notification or None
        """
        from datetime import datetime

        return await self.update(
            notification_id,
            {"is_read": True, "read_at": datetime.utcnow()},
        )

    async def mark_as_sent(self, notification_id: uuid.UUID) -> Notification | None:
        """
        Mark notification as sent.

        Args:
            notification_id: Notification ID

        Returns:
            Notification | None: Updated notification or None
        """
        from datetime import datetime

        return await self.update(
            notification_id,
            {
                "status": NotificationStatus.SENT,
                "sent_at": datetime.utcnow(),
            },
        )
