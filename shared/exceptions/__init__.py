"""
Exception classes for EduPlatform.
"""

from .auth import (
    AccountDisabledError,
    AuthenticationError,
    AuthorizationError,
    EmailNotVerifiedError,
    InsufficientPermissionsError,
    InvalidCredentialsError,
    InvalidTokenError,
    RefreshTokenExpiredError,
    RoleRequiredError,
    TokenExpiredError,
    TokenNotFoundError,
)
from .base import (
    AlreadyExistsError,
    ConfigurationError,
    DatabaseError,
    EduPlatformException,
    ExternalServiceError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ValidationError,
)

__all__ = [
    # Base exceptions
    "EduPlatformException",
    "ValidationError",
    "NotFoundError",
    "AlreadyExistsError",
    "PermissionDeniedError",
    "DatabaseError",
    "ExternalServiceError",
    "RateLimitError",
    "ConfigurationError",
    # Authentication exceptions
    "AuthenticationError",
    "InvalidCredentialsError",
    "TokenExpiredError",
    "InvalidTokenError",
    "TokenNotFoundError",
    "RefreshTokenExpiredError",
    # Authorization exceptions
    "AuthorizationError",
    "InsufficientPermissionsError",
    "RoleRequiredError",
    "AccountDisabledError",
    "EmailNotVerifiedError",
]
