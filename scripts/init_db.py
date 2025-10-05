"""
Database initialization script.
Creates database and runs migrations.
"""

import asyncio
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from shared.config import db_config


async def create_database():
    """Create database if it doesn't exist."""
    # Ensure we're using psycopg driver
    db_url = db_config.database_url
    if "postgresql://" in db_url and "+" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://")

    # Connect to default postgres database
    engine = create_async_engine(
        db_url.replace("/eduplatform", "/postgres"),
        isolation_level="AUTOCOMMIT",
    )

    async with engine.connect() as conn:
        # Check if database exists
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname='eduplatform'")
        )
        exists = result.scalar()

        if not exists:
            print("Creating database 'eduplatform'...")
            await conn.execute(text("CREATE DATABASE eduplatform"))
            print("Database created successfully!")
        else:
            print("Database 'eduplatform' already exists.")

    await engine.dispose()


async def main():
    """Main initialization function."""
    try:
        print("Initializing EduPlatform database...")
        await create_database()
        print("\nDatabase initialization complete!")
        print("\nNext steps:")
        print("1. Run migrations: alembic upgrade head")
        print("2. Seed data: python scripts/seed_data.py")
    except Exception as e:
        print(f"Error initializing database: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
