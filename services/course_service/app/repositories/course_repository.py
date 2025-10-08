"""
Course repository for database operations.
"""

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import BaseRepository

from ..models.course import Course, CourseStatus


class CourseRepository(BaseRepository[Course]):
    """Repository for Course model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Course, session)

    async def get_by_slug(self, slug: str) -> Optional[Course]:
        """
        Get course by slug.

        Args:
            slug: Course slug

        Returns:
            Optional[Course]: Found course or None
        """
        result = await self.session.execute(select(Course).where(Course.slug == slug))
        return result.scalar_one_or_none()

    async def slug_exists(
        self, slug: str, exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Check if slug already exists.

        Args:
            slug: Slug to check
            exclude_id: Optional course ID to exclude from check

        Returns:
            bool: True if slug exists
        """
        query = select(Course).where(Course.slug == slug)
        if exclude_id:
            query = query.where(Course.id != exclude_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_published(self, skip: int = 0, limit: int = 100) -> list[Course]:
        """
        Get all published courses with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            list[Course]: List of published courses
        """
        result = await self.session.execute(
            select(Course)
            .where(Course.is_published == True)
            .order_by(Course.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_instructor(
        self, instructor_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Course]:
        """
        Get courses by instructor with pagination.

        Args:
            instructor_id: Instructor ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            list[Course]: List of courses by instructor
        """
        result = await self.session.execute(
            select(Course)
            .where(Course.instructor_id == instructor_id)
            .order_by(Course.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_category(
        self, category: str, skip: int = 0, limit: int = 100
    ) -> list[Course]:
        """
        Get courses by category with pagination.

        Args:
            category: Course category
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            list[Course]: List of courses in category
        """
        result = await self.session.execute(
            select(Course)
            .where(Course.category == category, Course.is_published == True)
            .order_by(Course.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_total(self) -> int:
        """Get total count of published courses."""
        result = await self.session.execute(
            select(func.count()).select_from(Course).where(Course.is_published == True)
        )
        return result.scalar() or 0

    async def publish_course(self, course_id: uuid.UUID) -> Optional[Course]:
        """
        Publish a course.

        Args:
            course_id: Course ID

        Returns:
            Optional[Course]: Updated course or None
        """
        from datetime import datetime

        return await self.update(
            course_id,
            {
                "is_published": True,
                "status": CourseStatus.PUBLISHED,
                "published_at": datetime.utcnow(),
            },
        )

    async def unpublish_course(self, course_id: uuid.UUID) -> Optional[Course]:
        """
        Unpublish a course.

        Args:
            course_id: Course ID

        Returns:
            Optional[Course]: Updated course or None
        """
        return await self.update(
            course_id, {"is_published": False, "status": CourseStatus.DRAFT}
        )
