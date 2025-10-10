"""
Event handlers for user events.
"""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_db_session

from ..models.notification import NotificationType
from ..repositories.notification_repository import NotificationRepository


class UserEventHandler:
    """Handler for user-related events."""

    async def handle_user_registered(self, event: dict[str, Any]):
        """
        Handle user.registered event.

        Args:
            event: Event data from Kafka
        """
        user_id = event.get("user_id")
        email = event.get("email")
        username = event.get("username")
        event_id = event.get("event_id")

        print(f"🎉 New user registered!")
        print(f"   User ID: {user_id}")
        print(f"   Email: {email}")
        print(f"   Username: {username}")

        # Save notification to database
        try:
            async for session in get_db_session():
                repo = NotificationRepository(session)

                notification_data = {
                    "user_id": uuid.UUID(user_id),
                    "type": NotificationType.IN_APP,
                    "title": "Welcome to EduPlatform! 🎓",
                    "message": f"Hi {username}! Thank you for joining EduPlatform. Start exploring our courses and begin your learning journey today!",
                    "event_type": "user.registered",
                    "event_id": uuid.UUID(event_id) if event_id else None,
                }

                notification = await repo.create(notification_data)
                await repo.mark_as_sent(notification.id)
                await session.commit()

                print(f"✅ Notification saved to database: {notification.id}")

        except Exception as e:
            print(f"❌ Error saving notification: {e}")

        print(f"✅ Welcome notification sent to {email}")

    async def handle_user_login(self, event: dict[str, Any]):
        """
        Handle user.login event.

        Args:
            event: Event data from Kafka
        """
        user_id = event.get("user_id")
        login_method = event.get("login_method", "unknown")

        print(f"🔐 User logged in: {user_id} via {login_method}")

        # Could save security notification here if needed
        # For now, just log it

    async def route_event(self, event: dict[str, Any]):
        """
        Route event to appropriate handler based on event_type.

        Args:
            event: Event data from Kafka
        """
        event_type = event.get("event_type")

        handlers = {
            "user.registered": self.handle_user_registered,
            "user.login": self.handle_user_login,
        }

        handler = handlers.get(event_type)
        if handler:
            await handler(event)
        else:
            print(f"⚠️  No handler for event type: {event_type}")
