"""
User repository for database operations.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import BaseRepository

from ..models.user import User


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User email address

        Returns:
            Optional[User]: Found user or None
        """
        result = await self.session.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            username: Username

        Returns:
            Optional[User]: Found user or None
        """
        result = await self.session.execute(
            select(User).where(User.username == username.lower())
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """
        Check if email already exists.

        Args:
            email: Email address to check

        Returns:
            bool: True if email exists
        """
        user = await self.get_by_email(email)
        return user is not None

    async def username_exists(self, username: str) -> bool:
        """
        Check if username already exists.

        Args:
            username: Username to check

        Returns:
            bool: True if username exists
        """
        user = await self.get_by_username(username)
        return user is not None

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Get all active users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            list[User]: List of active users
        """
        result = await self.session.execute(
            select(User).where(User.is_active == True).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_role(
        self, role: str, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """
        Get users by role with pagination.

        Args:
            role: User role to filter by
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            list[User]: List of users with specified role
        """
        result = await self.session.execute(
            select(User).where(User.role == role).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update_last_login(self, user_id: uuid.UUID) -> None:
        """
        Update user's last login timestamp.

        Args:
            user_id: User ID
        """
        from datetime import datetime

        await self.update(user_id, {"last_login_at": datetime.utcnow()})

    async def verify_email(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Mark user email as verified.

        Args:
            user_id: User ID

        Returns:
            Optional[User]: Updated user or None
        """
        from datetime import datetime

        return await self.update(
            user_id, {"is_verified": True, "email_verified_at": datetime.utcnow()}
        )

    async def deactivate_user(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Deactivate user account.

        Args:
            user_id: User ID

        Returns:
            Optional[User]: Updated user or None
        """
        return await self.update(user_id, {"is_active": False})

    async def activate_user(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Activate user account.

        Args:
            user_id: User ID

        Returns:
            Optional[User]: Updated user or None
        """
        return await self.update(user_id, {"is_active": True})
