"""
Base exception classes for EduPlatform.
All custom exceptions should inherit from these base classes.
"""

from typing import Any, Dict, Optional


class EduPlatformException(Exception):
    """Base exception for all EduPlatform errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize base exception.

        Args:
            message: Human-readable error message
            status_code: HTTP status code
            error_code: Machine-readable error code
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }

    def __str__(self) -> str:
        return f"{self.error_code}: {self.message}"


class ValidationError(EduPlatformException):
    """Raised when data validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class NotFoundError(EduPlatformException):
    """Raised when requested resource is not found."""

    def __init__(self, resource: str, identifier: Any):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, status_code=404)
        self.details = {"resource": resource, "identifier": str(identifier)}


class AlreadyExistsError(EduPlatformException):
    """Raised when trying to create a resource that already exists."""

    def __init__(self, resource: str, field: str, value: Any):
        message = f"{resource} with {field}='{value}' already exists"
        super().__init__(message, status_code=409)
        self.details = {"resource": resource, "field": field, "value": str(value)}


class PermissionDeniedError(EduPlatformException):
    """Raised when user doesn't have permission for action."""

    def __init__(self, action: str, resource: Optional[str] = None):
        message = f"Permission denied for action '{action}'"
        if resource:
            message += f" on resource '{resource}'"
        super().__init__(message, status_code=403)
        self.details = {"action": action, "resource": resource}


class DatabaseError(EduPlatformException):
    """Raised when database operation fails."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, status_code=500)
        if original_error:
            self.details = {"original_error": str(original_error)}


class ExternalServiceError(EduPlatformException):
    """Raised when external service call fails."""

    def __init__(
        self, service: str, message: str, original_error: Optional[Exception] = None
    ):
        super().__init__(f"{service} error: {message}", status_code=502)
        self.details = {"service": service}
        if original_error:
            self.details["original_error"] = str(original_error)


class RateLimitError(EduPlatformException):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: Optional[int] = None):
        message = "Rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message, status_code=429)
        if retry_after:
            self.details = {"retry_after": retry_after}


class ConfigurationError(EduPlatformException):
    """Raised when configuration is invalid or missing."""

    def __init__(self, parameter: str, message: str):
        super().__init__(f"Configuration error for '{parameter}': {message}")
        self.details = {"parameter": parameter}
