"""
Progress tracking API routes.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_db_session
from shared.dependencies.auth import get_current_user

from ..clients.course_client import CourseServiceClient
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

    # Get course info from Course Service
    course_client = CourseServiceClient()
    try:
        course = await course_client.get_course(enrollment.course_id)

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        # Get lessons count
        lessons = await course_client.get_course_lessons(enrollment.course_id)
        total_lessons = len(lessons)

        print(f"📚 Enrolling user {current_user.id} in course: {course.get('title')}")
        print(f"📖 Total lessons: {total_lessons}")

    finally:
        await course_client.close()

    # Create enrollment
    progress = await repo.enroll_user(
        user_id=current_user.id,
        course_id=enrollment.course_id,
        total_lessons=total_lessons,
    )

    await session.commit()

    # TODO: Emit enrollment.created event to Kafka
    print(f"✅ User enrolled successfully")

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

    # Get lesson info from Course Service
    course_client = CourseServiceClient()
    try:
        lesson = await course_client.get_lesson(data.lesson_id)

        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found",
            )

        course_id = uuid.UUID(lesson.get("course_id"))

        print(f"📝 Marking lesson complete: {lesson.get('title')}")

    finally:
        await course_client.close()

    # Get or create course progress
    course_progress = await repo.get_user_course_progress(current_user.id, course_id)

    if not course_progress:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enrolled in this course. Please enroll first.",
        )

    # Get or create lesson progress
    lesson_progress = await repo.get_lesson_progress(current_user.id, data.lesson_id)

    if not lesson_progress:
        # Create new lesson progress
        lesson_progress = await repo.create_lesson_progress(
            course_progress_id=course_progress.id,
            user_id=current_user.id,
            lesson_id=data.lesson_id,
        )

    # Mark as complete (only if not already completed)
    if not lesson_progress.is_completed:
        lesson_progress = await repo.mark_lesson_complete(lesson_progress.id)

        # Update course progress
        completed_count = course_progress.completed_lessons + 1
        await repo.update_progress(course_progress.id, completed_count)

        print(
            f"✅ Lesson completed! Progress: {completed_count}/{course_progress.total_lessons}"
        )

        # Check if course is completed
        if completed_count >= course_progress.total_lessons:
            print(f"🎉 Course completed!")
            # TODO: Emit course.completed event to Kafka
            # TODO: Generate certificate

    # Update time spent
    lesson_progress.time_spent += data.time_spent

    await session.commit()

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
