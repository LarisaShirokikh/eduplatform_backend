"""
Progress repository for database operations.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import BaseRepository

from ..models.lesson_progress import LessonProgress
from ..models.progress import CourseProgress, EnrollmentStatus


class ProgressRepository(BaseRepository[CourseProgress]):
    """Repository for CourseProgress model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(CourseProgress, session)

    async def get_user_course_progress(
        self, user_id: uuid.UUID, course_id: uuid.UUID
    ) -> Optional[CourseProgress]:
        """
        Get progress for specific user and course.

        Args:
            user_id: User ID
            course_id: Course ID

        Returns:
            Optional[CourseProgress]: Progress or None
        """
        result = await self.session.execute(
            select(CourseProgress).where(
                CourseProgress.user_id == user_id,
                CourseProgress.course_id == course_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_user_enrollments(
        self, user_id: uuid.UUID, status: Optional[EnrollmentStatus] = None
    ) -> list[CourseProgress]:
        """
        Get all enrollments for a user.

        Args:
            user_id: User ID
            status: Optional status filter

        Returns:
            list[CourseProgress]: List of enrollments
        """
        query = select(CourseProgress).where(CourseProgress.user_id == user_id)

        if status:
            query = query.where(CourseProgress.status == status)

        query = query.order_by(CourseProgress.enrolled_at.desc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def enroll_user(
        self, user_id: uuid.UUID, course_id: uuid.UUID, total_lessons: int
    ) -> CourseProgress:
        """
        Enroll user in a course.

        Args:
            user_id: User ID
            course_id: Course ID
            total_lessons: Total number of lessons in course

        Returns:
            CourseProgress: Created progress record
        """
        progress_data = {
            "user_id": user_id,
            "course_id": course_id,
            "total_lessons": total_lessons,
            "status": EnrollmentStatus.ACTIVE,
        }

        return await self.create(progress_data)

    async def update_progress(
        self, progress_id: uuid.UUID, completed_lessons: int
    ) -> Optional[CourseProgress]:
        """
        Update course progress.

        Args:
            progress_id: Progress ID
            completed_lessons: Number of completed lessons

        Returns:
            Optional[CourseProgress]: Updated progress
        """
        progress = await self.get_by_id(progress_id)

        if not progress:
            return None

        # Calculate completion percentage
        completion_percentage = (
            (completed_lessons / progress.total_lessons * 100)
            if progress.total_lessons > 0
            else 0
        )

        update_data = {
            "completed_lessons": completed_lessons,
            "completion_percentage": round(completion_percentage, 2),
        }

        # Mark as completed if 100%
        if completion_percentage >= 100:
            from datetime import datetime

            update_data["status"] = EnrollmentStatus.COMPLETED
            update_data["completed_at"] = datetime.utcnow()

        return await self.update(progress_id, update_data)

    async def get_lesson_progress(
        self, user_id: uuid.UUID, lesson_id: uuid.UUID
    ) -> Optional[LessonProgress]:
        """
        Get lesson progress for user.

        Args:
            user_id: User ID
            lesson_id: Lesson ID

        Returns:
            Optional[LessonProgress]: Lesson progress or None
        """
        result = await self.session.execute(
            select(LessonProgress).where(
                LessonProgress.user_id == user_id,
                LessonProgress.lesson_id == lesson_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_lesson_progress(
        self, course_progress_id: uuid.UUID, user_id: uuid.UUID, lesson_id: uuid.UUID
    ) -> LessonProgress:
        """
        Create lesson progress record.

        Args:
            course_progress_id: Course progress ID
            user_id: User ID
            lesson_id: Lesson ID

        Returns:
            LessonProgress: Created lesson progress
        """
        lesson_progress = LessonProgress(
            course_progress_id=course_progress_id,
            user_id=user_id,
            lesson_id=lesson_id,
        )

        self.session.add(lesson_progress)
        await self.session.flush()
        return lesson_progress

    async def mark_lesson_complete(
        self, lesson_progress_id: uuid.UUID
    ) -> Optional[LessonProgress]:
        """
        Mark lesson as completed.

        Args:
            lesson_progress_id: Lesson progress ID

        Returns:
            Optional[LessonProgress]: Updated lesson progress
        """
        from datetime import datetime

        lesson_progress = await self.session.get(LessonProgress, lesson_progress_id)

        if not lesson_progress:
            return None

        lesson_progress.is_completed = True
        lesson_progress.completion_percentage = 100
        lesson_progress.completed_at = datetime.utcnow()

        await self.session.flush()
        return lesson_progress
