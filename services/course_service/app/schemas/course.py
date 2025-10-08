import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from ..models.course import CourseLevel, CourseStatus


class CourseBase(BaseModel):
    """Base course schema."""

    title: str = Field(..., min_length=3, max_length=200)
    slug: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    short_description: Optional[str] = Field(None, max_length=500)
    level: CourseLevel = Field(default=CourseLevel.BEGINNER)
    category: str = Field(..., min_length=2, max_length=100)
    language: str = Field(default="en", max_length=10)
    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    is_free: bool = Field(default=False)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    preview_video_url: Optional[str] = Field(None, max_length=500)


class CourseCreate(CourseBase):
    """Schema for creating a course."""

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Validate slug format."""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "Slug must contain only letters, numbers, hyphens, and underscores"
            )
        return v.lower()


class CourseUpdate(BaseModel):
    """Schema for updating a course."""

    title: Optional[str] = Field(None, min_length=3, max_length=200)
    slug: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    short_description: Optional[str] = Field(None, max_length=500)
    level: Optional[CourseLevel] = None
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    language: Optional[str] = Field(None, max_length=10)
    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    is_free: Optional[bool] = None
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    preview_video_url: Optional[str] = Field(None, max_length=500)
    status: Optional[CourseStatus] = None


class CourseResponse(CourseBase):
    """Schema for course response."""

    id: uuid.UUID
    instructor_id: uuid.UUID
    status: CourseStatus
    is_published: bool
    published_at: Optional[datetime]
    student_count: int
    rating: Decimal
    review_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CourseListResponse(BaseModel):
    """Schema for paginated course list."""

    courses: list[CourseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
