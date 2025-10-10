"""
Authentication service for user registration, login, and token management.
"""

import uuid
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from services.user_service.app.services.email_service import EmailVerificationService
from shared.config import config
from shared.events import UserLoginEvent, UserRegisteredEvent
from shared.exceptions import (
    AccountDisabledError,
    AlreadyExistsError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from shared.messaging.kafka_producer import get_kafka_producer
from shared.utils import password_hasher, token_manager

from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..schemas.user import (
    LoginResponse,
    TokenResponse,
    UserRegisterRequest,
    UserResponse,
)


class AuthService:
    """Service for handling authentication operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(
        self, register_data: UserRegisterRequest
    ) -> tuple[UserResponse, TokenResponse]:
        """
        Register a new user.

        Args:
            register_data: User registration data

        Returns:
            tuple[UserResponse, TokenResponse]: Created user and auth tokens

        Raises:
            AlreadyExistsError: If email or username already exists
        """
        # Check if email already exists
        if await self.user_repo.email_exists(register_data.email):
            raise AlreadyExistsError("User", "email", register_data.email)

        # Check if username already exists
        if await self.user_repo.username_exists(register_data.username):
            raise AlreadyExistsError("User", "username", register_data.username)

        # Hash password
        hashed_password = password_hasher.hash_password(register_data.password)

        # Create user
        user_data = {
            "email": register_data.email.lower(),
            "username": register_data.username.lower(),
            "hashed_password": hashed_password,
            "first_name": register_data.first_name,
            "last_name": register_data.last_name,
        }

        user = await self.user_repo.create(user_data)
        await self.session.commit()

        # Generate verification token

        verification_token = EmailVerificationService.generate_verification_token(
            user.id, user.email
        )

        kafka_producer = await get_kafka_producer()

        # Emit user registered event
        event = UserRegisteredEvent(
            user_id=user.id,
            email=user.email,
            username=user.username,
            role=user.role,
            is_verified=user.is_verified,
        )
        # Send to Kafka
        await kafka_producer.send_event(
            topic="user.registered",
            event_data=event.model_dump(mode="json"),
            key=str(user.id),
        )
        print(f"Event sent to Kafka: user.registered")
        print(f"Verification token for {user.email}: {verification_token}")
        print(
            f"Verification URL: http://localhost:8001/api/v1/auth/verify-email?token={verification_token}"
        )

        # Generate tokens
        tokens = self._generate_tokens(user)

        return UserResponse.model_validate(user), tokens

    async def login(self, email: str, password: str) -> LoginResponse:
        """
        Authenticate user and return tokens.

        Args:
            email: User email
            password: User password

        Returns:
            LoginResponse: User data and auth tokens

        Raises:
            InvalidCredentialsError: If credentials are invalid
            AccountDisabledError: If account is disabled
        """
        # Get user by email
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsError()

        # Verify password
        if not password_hasher.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        # Check if account is active
        if not user.is_active:
            raise AccountDisabledError()

        # Update last login
        await self.user_repo.update_last_login(user.id)
        await self.session.commit()

        # Emit login event
        event = UserLoginEvent(
            user_id=user.id,
            login_method="password",
        )
        # TODO: Publish event to Kafka

        # Generate tokens
        tokens = self._generate_tokens(user)

        return LoginResponse(
            user=UserResponse.model_validate(user),
            tokens=tokens,
        )

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            TokenResponse: New access and refresh tokens

        Raises:
            InvalidTokenError: If refresh token is invalid
        """
        # Decode and validate refresh token
        payload = token_manager.decode_token(refresh_token)
        token_manager.verify_token_type(payload, "refresh")

        # Get user
        user_id = token_manager.extract_user_id(payload)
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise InvalidTokenError("User not found")

        if not user.is_active:
            raise AccountDisabledError()

        # Generate new tokens
        return self._generate_tokens(user)

    async def verify_email(self, user_id: uuid.UUID) -> UserResponse:
        """
        Verify user email.

        Args:
            user_id: User ID

        Returns:
            UserResponse: Updated user

        Raises:
            NotFoundError: If user not found
        """
        user = await self.user_repo.verify_email(user_id)
        await self.session.commit()

        if not user:
            raise InvalidTokenError("User not found")

        return UserResponse.model_validate(user)

    def _generate_tokens(self, user: User) -> TokenResponse:
        """
        Generate access and refresh tokens for user.

        Args:
            user: User object

        Returns:
            TokenResponse: Access and refresh tokens
        """
        # Token payload
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }

        # Generate access token
        access_token = token_manager.create_access_token(token_data)

        # Generate refresh token
        refresh_token = token_manager.create_refresh_token({"sub": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=config.jwt_expire_minutes * 60,
        )
