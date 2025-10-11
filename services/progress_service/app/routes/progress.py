"""
Progress tracking API routes.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_db_session
from shared.dependencies.auth import get_current_user

from ..repositories.progress_repository import ProgressRepository
from ..schemas.progress import (
    CourseProgressResponse,
    EnrollmentRequest,
    LessonProgressResponse,
    MarkLessonCompleteRequest,
)

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.post(
    "/enroll",
    response_model=CourseProgressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll in course",
)
async def enroll_in_course(
    enrollment: EnrollmentRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Enroll current user in a course.

    Requires authentication.
    """
    repo = ProgressRepository(session)

    # Check if already enrolled
    existing = await repo.get_user_course_progress(
        current_user.id, enrollment.course_id
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course",
        )

    # TODO: Get actual lesson count from Course Service
    # For now, use placeholder
    total_lessons = 10

    # Create enrollment
    progress = await repo.enroll_user(
        user_id=current_user.id,
        course_id=enrollment.course_id,
        total_lessons=total_lessons,
    )

    await session.commit()

    # TODO: Emit enrollment.created event to Kafka

    return progress


@router.get(
    "/my-courses",
    response_model=list[CourseProgressResponse],
    summary="Get my enrolled courses",
)
async def get_my_courses(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get all courses current user is enrolled in.

    Requires authentication.
    """
    repo = ProgressRepository(session)
    enrollments = await repo.get_user_enrollments(current_user.id)
    return enrollments


@router.get(
    "/course/{course_id}",
    response_model=CourseProgressResponse,
    summary="Get course progress",
)
async def get_course_progress(
    course_id: uuid.UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get progress for specific course.

    Requires authentication.
    """
    repo = ProgressRepository(session)

    progress = await repo.get_user_course_progress(current_user.id, course_id)

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enrolled in this course",
        )

    return progress


@router.post(
    "/lesson/complete",
    response_model=LessonProgressResponse,
    summary="Mark lesson as complete",
)
async def mark_lesson_complete(
    data: MarkLessonCompleteRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Mark a lesson as completed.

    Requires authentication.
    """
    repo = ProgressRepository(session)

    # Get or create lesson progress
    lesson_progress = await repo.get_lesson_progress(current_user.id, data.lesson_id)

    if not lesson_progress:
        # TODO: Get course_id from Lesson Service
        # For now, return error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Need to enroll in course first",
        )

    # Mark as complete
    lesson_progress = await repo.mark_lesson_complete(lesson_progress.id)

    # Update time spent
    lesson_progress.time_spent += data.time_spent

    await session.commit()

    # TODO: Update course progress
    # TODO: Emit progress.updated event to Kafka

    return lesson_progress


@router.get(
    "/lesson/{lesson_id}",
    response_model=LessonProgressResponse,
    summary="Get lesson progress",
)
async def get_lesson_progress(
    lesson_id: uuid.UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get progress for specific lesson.

    Requires authentication.
    """
    repo = ProgressRepository(session)

    lesson_progress = await repo.get_lesson_progress(current_user.id, lesson_id)

    if not lesson_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson progress not found",
        )

    return lesson_progress
