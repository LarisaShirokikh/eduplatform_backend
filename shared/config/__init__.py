"""
Configuration module for EduPlatform.
Unites all configurations in one place.
"""

from .base import BaseConfig, ServiceConfig, config, get_config, get_service_config
from .database import (
    DatabaseConfig,
    TestDatabaseConfig,
    db_config,
    get_database_config,
    get_test_database_config,
)
from .kafka import EduPlatformTopics, KafkaConfig, get_kafka_config, kafka_config
from .rabbitmq import (
    EduPlatformQueues,
    EduPlatformRoutingKeys,
    RabbitMQConfig,
    get_rabbitmq_config,
    rabbitmq_config,
)
from .redis import (
    CeleryRedisConfig,
    RedisConfig,
    celery_redis_config,
    get_celery_redis_config,
    get_redis_config,
    redis_config,
)

__all__ = [
    # Base config
    "BaseConfig",
    "ServiceConfig",
    "config",
    "get_config",
    "get_service_config",
    # Database config
    "DatabaseConfig",
    "TestDatabaseConfig",
    "db_config",
    "get_database_config",
    "get_test_database_config",
    # Redis config
    "RedisConfig",
    "CeleryRedisConfig",
    "redis_config",
    "celery_redis_config",
    "get_redis_config",
    "get_celery_redis_config",
    # Kafka config
    "KafkaConfig",
    "EduPlatformTopics",
    "kafka_config",
    "get_kafka_config",
    # RabbitMQ config
    "RabbitMQConfig",
    "EduPlatformQueues",
    "EduPlatformRoutingKeys",
    "rabbitmq_config",
    "get_rabbitmq_config",
]


class AppConfig:
    """
    Central class for access to all configurations.
    Provides a single entry point for all application settings.
    """

    def __init__(self):
        self._base = None
        self._database = None
        self._redis = None
        self._kafka = None
        self._rabbitmq = None

    @property
    def base(self) -> BaseConfig:
        """Base configuration."""
        if self._base is None:
            self._base = get_config()
        return self._base

    @property
    def database(self) -> DatabaseConfig:
        """Configuration of database."""
        if self._database is None:
            self._database = get_database_config()
        return self._database

    @property
    def redis(self) -> RedisConfig:
        """Configuration Redis."""
        if self._redis is None:
            self._redis = get_redis_config()
        return self._redis

    @property
    def kafka(self) -> KafkaConfig:
        """Configuration Kafka."""
        if self._kafka is None:
            self._kafka = get_kafka_config()
        return self._kafka

    @property
    def rabbitmq(self) -> RabbitMQConfig:
        """Configuration RabbitMQ."""
        if self._rabbitmq is None:
            self._rabbitmq = get_rabbitmq_config()
        return self._rabbitmq

    def get_service_config(self, service_name: str, service_port: int) -> ServiceConfig:
        """
        Get configuration for specific service.

        Args:
            service_name: Name of service
            service_port: Port of service

        Returns:
            ServiceConfig: Configuration of service
        """
        return get_service_config(service_name, service_port)

    def validate_all(self) -> bool:
        """
        Validate all configurations.

        Returns:
            bool: True if all configurations are valid

        Raises:
            ValueError: If there are errors in the configuration
        """
        try:
            # Load all configurations for validation
            _ = self.base
            _ = self.database
            _ = self.redis
            _ = self.kafka
            _ = self.rabbitmq
            return True
        except Exception as e:
            raise ValueError(f"Configuration validation failed: {e}")

    def get_service_urls(self) -> dict:
        """
        Get URL of all external services.

        Returns:
            dict: Dictionary with URL of services
        """
        return {
            "database": self.database.database_url,
            "redis": self.redis.redis_url,
            "kafka": f"kafka://{self.kafka.kafka_bootstrap_servers}",
            "rabbitmq": self.rabbitmq.rabbitmq_url,
        }

    def is_development(self) -> bool:
        """Check on development mode."""
        return self.base.is_development

    def is_production(self) -> bool:
        """Check on production mode."""
        return self.base.is_production

    def is_testing(self) -> bool:
        """Check on testing mode."""
        return self.base.is_testing


# Global instance of application configuration
app_config = AppConfig()


def get_app_config() -> AppConfig:
    """
        Get configuration of application.

    Returns:
        AppConfig: Configuration of application
    """
    return app_config
