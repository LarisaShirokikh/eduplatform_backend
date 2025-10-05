"""
User management API routes.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_db_session
from shared.dependencies.auth import get_current_active_user, get_current_user

from ..models.user import User, UserRole
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserResponse, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Get authenticated user's profile information",
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's profile.

    Requires authentication.
    """
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
    description="Update authenticated user's profile information",
)
async def update_my_profile(
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Update current user's profile.

    - **first_name**: Optional first name
    - **last_name**: Optional last name
    - **bio**: Optional biography
    - **avatar_url**: Optional avatar URL

    Requires authentication.
    """
    repo = UserRepository(session)

    # Prepare update data (only non-None fields)
    update_dict = update_data.model_dump(exclude_unset=True)

    if not update_dict:
        return current_user

    updated_user = await repo.update(current_user.id, update_dict)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return updated_user


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user account",
    description="Deactivate authenticated user's account",
)
async def delete_my_account(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Deactivate current user's account.

    This does not permanently delete the account, but deactivates it.

    Requires authentication.
    """
    repo = UserRepository(session)
    await repo.deactivate_user(current_user.id)
    return None


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Get public user profile by ID",
)
async def get_user_by_id(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get user profile by ID (public information only).

    Does not require authentication.
    """
    repo = UserRepository(session)
    user = await repo.get(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="List users",
    description="Get list of users (admin only)",
)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get list of all users.

    Requires admin role.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    repo = UserRepository(session)
    users = await repo.get_active_users(skip=skip, limit=limit)

    return users
