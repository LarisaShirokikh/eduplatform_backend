"""
Notification API routes.
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_db_session
from shared.dependencies.auth import get_current_user

from ..repositories.notification_repository import NotificationRepository
from ..schemas.notification import NotificationListResponse, NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "/",
    response_model=NotificationListResponse,
    summary="Get user notifications",
)
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get all notifications for current user.

    Requires authentication.
    """
    repo = NotificationRepository(session)

    # Get notifications
    notifications = await repo.get_by_user(current_user.id, skip=skip, limit=limit)

    # Get unread count
    unread = await repo.get_unread(current_user.id)

    return NotificationListResponse(
        notifications=notifications,
        total=len(notifications),
        unread_count=len(unread),
    )


@router.get(
    "/unread",
    response_model=list[NotificationResponse],
    summary="Get unread notifications",
)
async def get_unread_notifications(
    limit: int = Query(50, ge=1, le=100),
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get unread notifications for current user.

    Requires authentication.
    """
    repo = NotificationRepository(session)
    notifications = await repo.get_unread(current_user.id, limit=limit)
    return notifications


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark notification as read",
)
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Mark notification as read.

    Requires authentication.
    """
    repo = NotificationRepository(session)

    # Mark as read
    notification = await repo.mark_as_read(notification_id)
    await session.commit()

    return notification
