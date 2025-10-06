"""
Configuration for API Gateway.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GatewayConfig(BaseSettings):
    """API Gateway specific configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Игнорировать лишние поля из .env
    )

    # Service URLs
    user_service_url: str = Field(
        default="http://localhost:8001", description="User service URL"
    )
    course_service_url: str = Field(
        default="http://localhost:8002", description="Course service URL"
    )
    progress_service_url: str = Field(
        default="http://localhost:8003", description="Progress service URL"
    )
    notification_service_url: str = Field(
        default="http://localhost:8004", description="Notification service URL"
    )

    # Rate limiting
    rate_limit_requests: int = Field(default=100, description="Requests per window")
    rate_limit_window: int = Field(default=60, description="Window in seconds")


gateway_config = GatewayConfig()
