"""
Course management API routes.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_db_session
from shared.dependencies.auth import get_current_user

from ..repositories.course_repository import CourseRepository
from ..schemas.course import (
    CourseCreate,
    CourseListResponse,
    CourseResponse,
    CourseUpdate,
)

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post(
    "/",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new course",
)
async def create_course(
    course_data: CourseCreate,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Create a new course.

    Requires authentication. Only instructors and admins can create courses.
    """
    # Check user role
    if current_user.role not in ["instructor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can create courses",
        )

    repo = CourseRepository(session)

    # Check if slug exists
    if await repo.slug_exists(course_data.slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course with this slug already exists",
        )

    # Create course
    course_dict = course_data.model_dump()
    course_dict["instructor_id"] = current_user.id

    course = await repo.create(course_dict)
    await session.commit()

    return course


@router.get(
    "/",
    response_model=CourseListResponse,
    summary="List courses",
)
async def list_courses(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get list of published courses with pagination.

    Does not require authentication.
    """
    repo = CourseRepository(session)

    skip = (page - 1) * page_size

    # Get courses
    if category:
        courses = await repo.get_by_category(category, skip=skip, limit=page_size)
    else:
        courses = await repo.get_published(skip=skip, limit=page_size)

    # Get total count
    total = await repo.count_total()
    total_pages = (total + page_size - 1) // page_size

    return CourseListResponse(
        courses=courses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/my",
    response_model=list[CourseResponse],
    summary="Get my courses",
)
async def get_my_courses(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get courses created by current user.

    Requires authentication.
    """
    repo = CourseRepository(session)
    courses = await repo.get_by_instructor(current_user.id)
    return courses


@router.get(
    "/{course_id}",
    response_model=CourseResponse,
    summary="Get course by ID",
)
async def get_course(
    course_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get course details by ID.

    Does not require authentication for published courses.
    """
    repo = CourseRepository(session)
    course = await repo.get(course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Only show published courses to non-owners
    if not course.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    return course


@router.get(
    "/slug/{slug}",
    response_model=CourseResponse,
    summary="Get course by slug",
)
async def get_course_by_slug(
    slug: str,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get course details by slug.

    Does not require authentication for published courses.
    """
    repo = CourseRepository(session)
    course = await repo.get_by_slug(slug)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    if not course.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    return course


@router.put(
    "/{course_id}",
    response_model=CourseResponse,
    summary="Update course",
)
async def update_course(
    course_id: uuid.UUID,
    course_data: CourseUpdate,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Update course details.

    Requires authentication. Only course owner or admin can update.
    """
    repo = CourseRepository(session)
    course = await repo.get(course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Check ownership
    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # Check slug uniqueness if updating
    if course_data.slug and course_data.slug != course.slug:
        if await repo.slug_exists(course_data.slug, exclude_id=course_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course with this slug already exists",
            )

    # Update course
    update_dict = course_data.model_dump(exclude_unset=True)
    updated_course = await repo.update(course_id, update_dict)
    await session.commit()

    return updated_course


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete course",
)
async def delete_course(
    course_id: uuid.UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Delete a course.

    Requires authentication. Only course owner or admin can delete.
    """
    repo = CourseRepository(session)
    course = await repo.get(course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Check ownership
    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    await repo.delete(course_id)
    await session.commit()

    return None


@router.post(
    "/{course_id}/publish",
    response_model=CourseResponse,
    summary="Publish course",
)
async def publish_course(
    course_id: uuid.UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Publish a course.

    Requires authentication. Only course owner or admin can publish.
    """
    repo = CourseRepository(session)
    course = await repo.get(course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Check ownership
    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    published_course = await repo.publish_course(course_id)
    await session.commit()

    return published_course
