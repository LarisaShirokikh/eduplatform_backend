"""
User-related event schemas for Kafka messaging.
"""

import uuid
from typing import Optional

from pydantic import EmailStr, Field

from .base import BaseEvent


class UserRegisteredEvent(BaseEvent):
    """Event emitted when a new user registers."""

    event_type: str = Field(default="user.registered", frozen=True)
    service: str = Field(default="user-service", frozen=True)

    user_id: uuid.UUID = Field(..., description="ID of newly registered user")
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="User's username")
    role: str = Field(default="student", description="User's role")
    is_verified: bool = Field(default=False, description="Email verification status")


class UserUpdatedEvent(BaseEvent):
    """Event emitted when user data is updated."""

    event_type: str = Field(default="user.updated", frozen=True)
    service: str = Field(default="user-service", frozen=True)

    user_id: uuid.UUID = Field(..., description="ID of updated user")
    fields_updated: list[str] = Field(..., description="List of updated fields")
    previous_values: Optional[dict] = Field(
        default=None, description="Previous values of updated fields"
    )


class UserDeletedEvent(BaseEvent):
    """Event emitted when a user is deleted."""

    event_type: str = Field(default="user.deleted", frozen=True)
    service: str = Field(default="user-service", frozen=True)

    user_id: uuid.UUID = Field(..., description="ID of deleted user")
    deletion_reason: Optional[str] = Field(
        default=None, description="Reason for deletion"
    )
    soft_delete: bool = Field(
        default=True, description="Whether this is a soft or hard delete"
    )


class UserLoginEvent(BaseEvent):
    """Event emitted when a user logs in."""

    event_type: str = Field(default="user.login", frozen=True)
    service: str = Field(default="user-service", frozen=True)

    user_id: uuid.UUID = Field(..., description="ID of logged in user")
    ip_address: Optional[str] = Field(default=None, description="Login IP address")
    user_agent: Optional[str] = Field(default=None, description="User agent string")
    login_method: str = Field(default="password", description="Login method used")


class UserLogoutEvent(BaseEvent):
    """Event emitted when a user logs out."""

    event_type: str = Field(default="user.logout", frozen=True)
    service: str = Field(default="user-service", frozen=True)

    user_id: uuid.UUID = Field(..., description="ID of logged out user")
    session_duration: Optional[int] = Field(
        default=None, description="Session duration in seconds"
    )


class UserEmailVerifiedEvent(BaseEvent):
    """Event emitted when user verifies their email."""

    event_type: str = Field(default="user.email_verified", frozen=True)
    service: str = Field(default="user-service", frozen=True)

    user_id: uuid.UUID = Field(..., description="ID of user who verified email")
    email: EmailStr = Field(..., description="Verified email address")


class UserPasswordChangedEvent(BaseEvent):
    """Event emitted when user changes password."""

    event_type: str = Field(default="user.password_changed", frozen=True)
    service: str = Field(default="user-service", frozen=True)

    user_id: uuid.UUID = Field(..., description="ID of user who changed password")
    ip_address: Optional[str] = Field(
        default=None, description="IP address from which password was changed"
    )
