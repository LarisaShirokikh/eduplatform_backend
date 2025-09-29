"""
Data validation utilities for EduPlatform.
"""

import re
from typing import Any, List, Optional

from shared.exceptions.base import ValidationError


class Validators:
    """Collection of validation utilities."""

    # Regex patterns
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    PHONE_PATTERN = re.compile(r"^\+?1?\d{9,15}$")
    URL_PATTERN = re.compile(
        r"^https?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate email address.

        Args:
            email: Email address to validate

        Returns:
            str: Validated email (lowercase)

        Raises:
            ValidationError: If email is invalid
        """
        if not email:
            raise ValidationError("Email is required")

        email = email.strip().lower()

        if not Validators.EMAIL_PATTERN.match(email):
            raise ValidationError("Invalid email format")

        return email

    @staticmethod
    def validate_password(password: str, min_length: int = 8) -> str:
        """
        Validate password strength.

        Args:
            password: Password to validate
            min_length: Minimum password length

        Returns:
            str: Validated password

        Raises:
            ValidationError: If password doesn't meet requirements
        """
        if not password:
            raise ValidationError("Password is required")

        if len(password) < min_length:
            raise ValidationError(
                f"Password must be at least {min_length} characters long"
            )

        # Check for at least one uppercase letter
        if not any(c.isupper() for c in password):
            raise ValidationError("Password must contain at least one uppercase letter")

        # Check for at least one lowercase letter
        if not any(c.islower() for c in password):
            raise ValidationError("Password must contain at least one lowercase letter")

        # Check for at least one digit
        if not any(c.isdigit() for c in password):
            raise ValidationError("Password must contain at least one digit")

        # Check for at least one special character
        special_chars = set("!@#$%^&*()_+-=[]{}|;:,.<>?")
        if not any(c in special_chars for c in password):
            raise ValidationError(
                "Password must contain at least one special character"
            )

        return password

    @staticmethod
    def validate_phone(phone: str) -> str:
        """
        Validate phone number.

        Args:
            phone: Phone number to validate

        Returns:
            str: Validated phone number

        Raises:
            ValidationError: If phone is invalid
        """
        if not phone:
            raise ValidationError("Phone number is required")

        # Remove spaces and dashes
        phone = phone.replace(" ", "").replace("-", "")

        if not Validators.PHONE_PATTERN.match(phone):
            raise ValidationError("Invalid phone number format")

        return phone

    @staticmethod
    def validate_url(url: str) -> str:
        """
        Validate URL.

        Args:
            url: URL to validate

        Returns:
            str: Validated URL

        Raises:
            ValidationError: If URL is invalid
        """
        if not url:
            raise ValidationError("URL is required")

        url = url.strip()

        if not Validators.URL_PATTERN.match(url):
            raise ValidationError("Invalid URL format")

        return url

    @staticmethod
    def validate_string_length(
        value: str,
        field_name: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ) -> str:
        """
        Validate string length.

        Args:
            value: String to validate
            field_name: Name of the field (for error message)
            min_length: Minimum length
            max_length: Maximum length

        Returns:
            str: Validated string

        Raises:
            ValidationError: If string length is invalid
        """
        if value is None:
            raise ValidationError(f"{field_name} is required")

        value = value.strip()

        if min_length and len(value) < min_length:
            raise ValidationError(
                f"{field_name} must be at least {min_length} characters long"
            )

        if max_length and len(value) > max_length:
            raise ValidationError(
                f"{field_name} must be at most {max_length} characters long"
            )

        return value

    @staticmethod
    def validate_range(
        value: float | int,
        field_name: str,
        min_value: Optional[float | int] = None,
        max_value: Optional[float | int] = None,
    ) -> float | int:
        """
        Validate numeric range.

        Args:
            value: Number to validate
            field_name: Name of the field (for error message)
            min_value: Minimum value
            max_value: Maximum value

        Returns:
            float | int: Validated number

        Raises:
            ValidationError: If number is out of range
        """
        if value is None:
            raise ValidationError(f"{field_name} is required")

        if min_value is not None and value < min_value:
            raise ValidationError(f"{field_name} must be at least {min_value}")

        if max_value is not None and value > max_value:
            raise ValidationError(f"{field_name} must be at most {max_value}")

        return value

    @staticmethod
    def validate_enum(value: Any, field_name: str, allowed_values: List[Any]) -> Any:
        """
        Validate value is in allowed list.

        Args:
            value: Value to validate
            field_name: Name of the field (for error message)
            allowed_values: List of allowed values

        Returns:
            Any: Validated value

        Raises:
            ValidationError: If value not in allowed list
        """
        if value not in allowed_values:
            raise ValidationError(
                f"Invalid {field_name}. Allowed values: {', '.join(map(str, allowed_values))}"
            )

        return value

    @staticmethod
    def validate_slug(slug: str) -> str:
        """
        Validate URL slug format.

        Args:
            slug: Slug to validate

        Returns:
            str: Validated slug

        Raises:
            ValidationError: If slug is invalid
        """
        if not slug:
            raise ValidationError("Slug is required")

        slug = slug.strip().lower()

        # Slug should only contain lowercase letters, numbers, and hyphens
        if not re.match(r"^[a-z0-9-]+$", slug):
            raise ValidationError(
                "Slug can only contain lowercase letters, numbers, and hyphens"
            )

        # Slug shouldn't start or end with hyphen
        if slug.startswith("-") or slug.endswith("-"):
            raise ValidationError("Slug cannot start or end with a hyphen")

        return slug


# Global validator instance
validators = Validators()
