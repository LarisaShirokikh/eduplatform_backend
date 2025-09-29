"""
Authentication and authorization exceptions.
"""

from typing import Optional

from .base import EduPlatformException


class AuthenticationError(EduPlatformException):
    """Base class for authentication errors."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid."""

    def __init__(self):
        super().__init__("Invalid username or password")


class TokenExpiredError(AuthenticationError):
    """Raised when JWT token has expired."""

    def __init__(self):
        super().__init__("Token has expired")


class InvalidTokenError(AuthenticationError):
    """Raised when JWT token is invalid."""

    def __init__(self, reason: Optional[str] = None):
        message = "Invalid token"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class TokenNotFoundError(AuthenticationError):
    """Raised when token is missing from request."""

    def __init__(self):
        super().__init__("Authentication token not found")


class RefreshTokenExpiredError(AuthenticationError):
    """Raised when refresh token has expired."""

    def __init__(self):
        super().__init__("Refresh token has expired")


class AuthorizationError(EduPlatformException):
    """Base class for authorization errors."""

    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status_code=403)


class InsufficientPermissionsError(AuthorizationError):
    """Raised when user lacks required permissions."""

    def __init__(self, required_permission: str):
        super().__init__(f"Insufficient permissions. Required: {required_permission}")
        self.details = {"required_permission": required_permission}


class RoleRequiredError(AuthorizationError):
    """Raised when specific role is required."""

    def __init__(self, required_role: str):
        super().__init__(f"Role '{required_role}' is required")
        self.details = {"required_role": required_role}


class AccountDisabledError(AuthenticationError):
    """Raised when user account is disabled."""

    def __init__(self):
        super().__init__("Account is disabled")


class EmailNotVerifiedError(AuthenticationError):
    """Raised when email verification is required."""

    def __init__(self):
        super().__init__("Email verification required")
