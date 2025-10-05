"""
Authentication API routes.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from services.user_service.app.repositories.user_repository import UserRepository
from services.user_service.app.services.email_service import EmailVerificationService
from shared.database import get_db_session

from ..schemas.user import (
    EmailVerificationRequest,
    LoginResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account and return authentication tokens",
)
async def register(
    register_data: UserRegisterRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Register a new user account.

    - **email**: Valid email address (unique)
    - **username**: Username (unique, 3-50 characters)
    - **password**: Strong password (min 8 characters, must include uppercase, lowercase, digit, special char)
    - **first_name**: Optional first name
    - **last_name**: Optional last name

    Returns user profile and authentication tokens.
    """
    auth_service = AuthService(session)
    user, tokens = await auth_service.register(register_data)

    return LoginResponse(user=user, tokens=tokens)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login user",
    description="Authenticate user and return tokens",
)
async def login(
    login_data: UserLoginRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Authenticate user with email and password.

    - **email**: User's email address
    - **password**: User's password

    Returns user profile and authentication tokens.
    """
    auth_service = AuthService(session)
    return await auth_service.login(login_data.email, login_data.password)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get new access token using refresh token",
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Refresh access token.

    - **refresh_token**: Valid refresh token

    Returns new access and refresh tokens.
    """
    auth_service = AuthService(session)
    return await auth_service.refresh_token(refresh_data.refresh_token)


@router.post(
    "/verify-email",
    response_model=UserResponse,
    summary="Verify email address",
    description="Verify user email with verification token",
)
async def verify_email(
    verification_data: EmailVerificationRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Verify user email address.

    - **token**: Email verification token

    Returns updated user profile.
    """
    # Verify token
    payload = EmailVerificationService.verify_token(verification_data.token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    user_id = payload.get("sub")

    # Update user verification status
    repo = UserRepository(session)
    user = await repo.verify_email(uuid.UUID(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user
