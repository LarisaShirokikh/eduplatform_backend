"""
Redis configuration for caching and sessions.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisConfig(BaseSettings):
    """Redis configuration."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    redis_password: Optional[str] = Field(default=None)
    redis_max_connections: int = Field(default=20)
    redis_cache_ttl: int = Field(default=3600)


class CeleryRedisConfig(BaseSettings):
    """Redis configuration for Celery."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    celery_broker_url: str = Field(default="redis://localhost:6379/1")
    celery_result_backend: str = Field(default="redis://localhost:6379/1")
    celery_redis_host: str = Field(default="localhost")
    celery_redis_port: int = Field(default=6379)
    celery_redis_db: int = Field(default=1)
    celery_redis_password: Optional[str] = Field(default=None)
    celery_redis_max_connections: int = Field(default=10)


@lru_cache()
def get_redis_config() -> RedisConfig:
    return RedisConfig()


@lru_cache()
def get_celery_redis_config() -> CeleryRedisConfig:
    return CeleryRedisConfig()


redis_config = get_redis_config()
celery_redis_config = get_celery_redis_config()
