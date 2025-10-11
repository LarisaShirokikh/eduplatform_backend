"""
Progress Service schemas.
"""

from .progress import (
    CourseProgressResponse,
    EnrollmentRequest,
    LessonProgressResponse,
    MarkLessonCompleteRequest,
)

__all__ = [
    "CourseProgressResponse",
    "EnrollmentRequest",
    "LessonProgressResponse",
    "MarkLessonCompleteRequest",
]
