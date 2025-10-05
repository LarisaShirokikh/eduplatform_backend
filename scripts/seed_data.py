"""
Seed database with test data for development.
"""

import asyncio
import sys
from pathlib import Path

from app.repositories.user_repository import UserRepository

from ..app.models.user import UserRole

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_database
from shared.utils import password_hasher


async def seed_users(session: AsyncSession):
    """Seed test users."""
    user_repo = UserRepository(session)

    # Check if users already exist
    if await user_repo.email_exists("admin@eduplatform.com"):
        print("Users already seeded. Skipping...")
        return

    print("Seeding users...")

    # Create admin user
    admin_data = {
        "email": "admin@eduplatform.com",
        "username": "admin",
        "hashed_password": password_hasher.hash_password("Admin123!"),
        "first_name": "Admin",
        "last_name": "User",
        "role": UserRole.ADMIN.value,
        "is_active": True,
        "is_verified": True,
    }
    await user_repo.create(admin_data)
    print("Created admin user: admin@eduplatform.com / Admin123!")

    # Create instructor user
    instructor_data = {
        "email": "instructor@eduplatform.com",
        "username": "instructor",
        "hashed_password": password_hasher.hash_password("Instructor123!"),
        "first_name": "John",
        "last_name": "Instructor",
        "role": UserRole.INSTRUCTOR.value,
        "is_active": True,
        "is_verified": True,
    }
    await user_repo.create(instructor_data)
    print("Created instructor user: instructor@eduplatform.com / Instructor123!")

    # Create student user
    student_data = {
        "email": "student@eduplatform.com",
        "username": "student",
        "hashed_password": password_hasher.hash_password("Student123!"),
        "first_name": "Jane",
        "last_name": "Student",
        "role": UserRole.STUDENT.value,
        "is_active": True,
        "is_verified": True,
    }
    await user_repo.create(student_data)
    print("Created student user: student@eduplatform.com / Student123!")

    await session.commit()
    print("Users seeded successfully!")


async def main():
    """Main seeding function."""
    try:
        print("Starting database seeding...")

        db = get_database()
        async with db.session() as session:
            await seed_users(session)

        print("\nDatabase seeding complete!")
        print("\nTest accounts:")
        print("- Admin: admin@eduplatform.com / Admin123!")
        print("- Instructor: instructor@eduplatform.com / Instructor123!")
        print("- Student: student@eduplatform.com / Student123!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
