"""
Client for Course Service.
"""

import uuid
from typing import Optional

from shared.clients.http_client import HTTPClient


class CourseServiceClient:
    """Client for communicating with Course Service."""

    def __init__(self, base_url: str = "http://localhost:8002"):
        """
        Initialize Course Service client.

        Args:
            base_url: Base URL of Course Service
        """
        self.client = HTTPClient(base_url)

    async def close(self):
        """Close the client."""
        await self.client.close()

    async def get_course(self, course_id: uuid.UUID) -> Optional[dict]:
        """
        Get course by ID.

        Args:
            course_id: Course ID

        Returns:
            Optional[dict]: Course data or None if not found
        """
        try:
            response = await self.client.get(f"/api/v1/courses/{course_id}")
            return response
        except Exception as e:
            print(f"❌ Error fetching course {course_id}: {e}")
            return None

    async def get_course_lessons(self, course_id: uuid.UUID) -> list[dict]:
        """
        Get all lessons for a course.

        Args:
            course_id: Course ID

        Returns:
            list[dict]: List of lessons
        """
        try:
            response = await self.client.get(f"/api/v1/courses/{course_id}/lessons")
            return response.get("lessons", [])
        except Exception as e:
            print(f"❌ Error fetching lessons for course {course_id}: {e}")
            return []

    async def get_lesson(self, lesson_id: uuid.UUID) -> Optional[dict]:
        """
        Get lesson by ID.

        Args:
            lesson_id: Lesson ID

        Returns:
            Optional[dict]: Lesson data or None if not found
        """
        try:
            response = await self.client.get(f"/api/v1/lessons/{lesson_id}")
            return response
        except Exception as e:
            print(f"❌ Error fetching lesson {lesson_id}: {e}")
            return None
