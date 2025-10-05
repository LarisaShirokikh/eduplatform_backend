"""
Email verification service.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

from shared.config import config


class EmailVerificationService:
    """Service for handling email verification."""

    TOKEN_EXPIRE_HOURS = 24

    @staticmethod
    def generate_verification_token(user_id: uuid.UUID, email: str) -> str:
        """
        Generate email verification token.

        Args:
            user_id: User ID
            email: User email

        Returns:
            str: Verification token
        """
        expire = datetime.utcnow() + timedelta(
            hours=EmailVerificationService.TOKEN_EXPIRE_HOURS
        )

        payload = {
            "sub": str(user_id),
            "email": email,
            "type": "email_verification",
            "exp": expire,
        }

        token = jwt.encode(payload, config.secret_key, algorithm=config.jwt_algorithm)

        return token

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        Verify email verification token.

        Args:
            token: Verification token

        Returns:
            Optional[dict]: Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token, config.secret_key, algorithms=[config.jwt_algorithm]
            )

            if payload.get("type") != "email_verification":
                return None

            return payload

        except jwt.JWTError:
            return None
