from functools import lru_cache
from typing import Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf=8", case_sensetive=False, extra="ignore"
    )

    database_url: str = Field(
        default="postgresql+psycorg://eduuser:edupass@localhost:5432/eduplatform",
        description="Main URL",
    )

    user_db_url: Optional[str] = Field(
        default=None, description=" URL for user database"
    )

    course_db_url: Optional[str] = Field(
        default=None, description=" URL for course database"
    )

    progress_db_url: Optional[str] = Field(
        default=None, description=" URL for progress database"
    )

    certificate_db_url: Optional[str] = Field(
        default=None, description=" URL for certificate database"
    )

    # connection pool settings
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

    # Qwery settings
