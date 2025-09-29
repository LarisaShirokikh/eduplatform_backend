"""
Security utilities for EduPlatform.
Handles password hashing, JWT tokens, and other security operations.
"""

import secrets
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from shared.config import config
from shared.exceptions.auth import InvalidTokenError, TokenExpiredError

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHasher:
    """Handles password hashing and verification."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            str: Hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            bool: True if password matches
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def needs_rehash(hashed_password: str) -> bool:
        """
        Check if password hash needs to be updated.

        Args:
            hashed_password: Hashed password

        Returns:
            bool: True if needs rehash
        """
        return pwd_context.needs_update(hashed_password)


class TokenManager:
    """Manages JWT token creation and validation."""

    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create a new access token.

        Args:
            data: Data to encode in token
            expires_delta: Token expiration time

        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=config.jwt_expire_minutes)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode, config.secret_key, algorithm=config.jwt_algorithm
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create a new refresh token.

        Args:
            data: Data to encode in token
            expires_delta: Token expiration time

        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            # Refresh tokens typically last longer (7 days)
            expire = datetime.utcnow() + timedelta(days=7)

        to_encode.update({"exp": expire, "type": "refresh", "jti": str(uuid.uuid4())})
        encoded_jwt = jwt.encode(
            to_encode, config.secret_key, algorithm=config.jwt_algorithm
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.

        Args:
            token: JWT token to decode

        Returns:
            Dict: Decoded token data

        Raises:
            TokenExpiredError: If token has expired
            InvalidTokenError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token, config.secret_key, algorithms=[config.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except JWTError as e:
            raise InvalidTokenError(str(e))

    @staticmethod
    def verify_token_type(payload: Dict[str, Any], expected_type: str) -> None:
        """
        Verify token type matches expected type.

        Args:
            payload: Decoded token payload
            expected_type: Expected token type (access/refresh)

        Raises:
            InvalidTokenError: If token type doesn't match
        """
        token_type = payload.get("type")
        if token_type != expected_type:
            raise InvalidTokenError(
                f"Invalid token type. Expected: {expected_type}, Got: {token_type}"
            )

    @staticmethod
    def extract_user_id(payload: Dict[str, Any]) -> uuid.UUID:
        """
        Extract user ID from token payload.

        Args:
            payload: Decoded token payload

        Returns:
            uuid.UUID: User ID

        Raises:
            InvalidTokenError: If user_id not found in token
        """
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError("User ID not found in token")

        try:
            return uuid.UUID(user_id)
        except (ValueError, AttributeError):
            raise InvalidTokenError("Invalid user ID format in token")


class SecurityUtils:
    """General security utilities."""

    @staticmethod
    def generate_verification_token() -> str:
        """
        Generate a secure random token for email verification.

        Returns:
            str: Random token
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a secure API key.

        Returns:
            str: Random API key
        """
        return secrets.token_urlsafe(48)

    @staticmethod
    def constant_time_compare(val1: str, val2: str) -> bool:
        """
        Compare two strings in constant time to prevent timing attacks.

        Args:
            val1: First string
            val2: Second string

        Returns:
            bool: True if strings match
        """
        return secrets.compare_digest(val1, val2)

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename to prevent directory traversal attacks.

        Args:
            filename: Original filename

        Returns:
            str: Sanitized filename
        """
        # Remove path components
        filename = filename.split("/")[-1].split("\\")[-1]

        # Remove dangerous characters
        dangerous_chars = ["<", ">", ":", '"', "|", "?", "*", "\x00"]
        for char in dangerous_chars:
            filename = filename.replace(char, "_")

        # Limit length
        max_length = 255
        if len(filename) > max_length:
            name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
            name = name[: max_length - len(ext) - 1]
            filename = f"{name}.{ext}" if ext else name

        return filename


# Global instances
password_hasher = PasswordHasher()
token_manager = TokenManager()
security_utils = SecurityUtils()
