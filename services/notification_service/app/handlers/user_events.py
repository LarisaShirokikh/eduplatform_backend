"""
Event handlers for user events.
"""

from typing import Any


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

        print(f"🎉 New user registered!")
        print(f"   User ID: {user_id}")
        print(f"   Email: {email}")
        print(f"   Username: {username}")

        # TODO: Send welcome email
        # TODO: Create notification in database
        # TODO: Send push notification

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

        # TODO: Log login attempt
        # TODO: Check for suspicious activity

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
