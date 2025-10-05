from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    database_url: str = Field(
        default="postgresql+psycopg://eduuser:edupass@localhost:5432/eduplatform",  # Changed: psycopg instead of psycopg2
        description="Main database URL",
    )

    user_db_url: Optional[str] = Field(
        default=None, description="URL for user database"
    )

    course_db_url: Optional[str] = Field(
        default=None, description="URL for course database"
    )

    progress_db_url: Optional[str] = Field(
        default=None, description="URL for progress database"
    )

    certificate_db_url: Optional[str] = Field(
        default=None, description="URL for certificate database"
    )

    # Connection pool settings
    db_pool_size: int = Field(default=20, description="Size of the connection pool")
    db_max_overflow: int = Field(
        default=30, description="Maximum number of connections to allow in the pool"
    )
    db_pool_timeout: int = Field(
        default=30, description="Timeout for the connection pool"
    )
    db_pool_recycle: int = Field(
        default=3600, description="Time to recycle the connection pool"
    )
    db_pool_pre_ping: bool = Field(
        default=True, description="Enable pre-ping for the connection pool"
    )

    # Query settings
    db_echo: bool = Field(default=False, description="Echo SQL queries to console")

    @field_validator(
        "database_url",
        "user_db_url",
        "course_db_url",
        "progress_db_url",
        "certificate_db_url",
    )
    @classmethod
    def validate_database_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate database URL format."""
        if v is None:
            return v
        # Updated: Added psycopg to valid prefixes
        if not v.startswith(
            (
                "postgresql://",
                "postgresql+psycopg://",
                "postgresql+psycopg2://",
                "postgresql+asyncpg://",
            )
        ):
            raise ValueError(
                "Database URL must start with postgresql://, postgresql+psycopg://, postgresql+psycopg2://, or postgresql+asyncpg://"
            )
        return v

    def get_service_db_url(self, service_name: str) -> str:
        """
        Get database URL for specific service.

        Args:
            service_name: Name of the service (user, course, progress, certificate)

        Returns:
            str: Database URL for the service
        """
        service_urls = {
            "user": self.user_db_url,
            "course": self.course_db_url,
            "progress": self.progress_db_url,
            "certificate": self.certificate_db_url,
        }
        return service_urls.get(service_name) or self.database_url


class TestDatabaseConfig(DatabaseConfig):
    """Configuration for test database."""

    database_url: str = Field(
        default="postgresql+psycopg://eduuser:edupass@localhost:5432/eduplatform_test",  # Changed: psycopg instead of psycopg2
        description="Test database URL",
    )

    db_echo: bool = Field(
        default=True, description="Echo SQL queries to console in tests"
    )


@lru_cache()
def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    return DatabaseConfig()


@lru_cache()
def get_test_database_config() -> TestDatabaseConfig:
    """Get test database configuration."""
    return TestDatabaseConfig()


# Global instances
db_config = get_database_config()
