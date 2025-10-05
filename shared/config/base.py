"""
Base configuration for all services in EduPlatform.
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """Base configuration for all services."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Application
    app_name: str = Field(default="EduPlatform")
    app_version: str = Field(default="0.1.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expire_minutes: int = Field(default=30)

    # CORS
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:8080")
    cors_methods: str = Field(default="GET,POST,PUT,DELETE,OPTIONS")
    cors_headers: str = Field(default="Content-Type,Authorization")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def cors_methods_list(self) -> List[str]:
        return [method.strip() for method in self.cors_methods.split(",")]

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        return self.environment == "testing"


class ServiceConfig(BaseConfig):
    """Configuration for specific service."""

    service_name: str = Field(..., description="Service name")
    service_port: int = Field(..., description="Service port")


@lru_cache()
def get_config() -> BaseConfig:
    return BaseConfig()


@lru_cache()
def get_service_config(service_name: str, service_port: int) -> ServiceConfig:
    return ServiceConfig(service_name=service_name, service_port=service_port)


config = get_config()
