"""
Configuration RabbitMQ for message queues.
"""

from functools import lru_cache
from typing import Dict, List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitMQConfig(BaseSettings):
    """Configuration RabbitMQ."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Connection settings
    rabbitmq_url: str = Field(
        default="amqp://eduuser:edupass@localhost:5672/",
        description="URL RabbitMQ server",
    )
    rabbitmq_host: str = Field(default="localhost", description="Host RabbitMQ")
    rabbitmq_port: int = Field(default=5672, description="Port RabbitMQ")
    rabbitmq_username: str = Field(default="eduuser", description="User RabbitMQ")
    rabbitmq_password: str = Field(default="edupass", description="Password RabbitMQ")
    rabbitmq_vhost: str = Field(default="/", description="Virtual host RabbitMQ")
    rabbitmq_ssl: bool = Field(default=False, description="SSL RabbitMQ")

    # Connection pool settings
    rabbitmq_connection_attempts: int = Field(
        default=3, description="Number of connection attempts"
    )
    rabbitmq_retry_delay: int = Field(
        default=5, description="Delay between connection attempts (seconds)"
    )
    rabbitmq_heartbeat: int = Field(
        default=600, description="Interval heartbeat (seconds)"
    )
    rabbitmq_blocked_connection_timeout: int = Field(
        default=300, description="Timeout blocked connection"
    )

    # Exchange settings
    rabbitmq_exchange: str = Field(default="eduplatform", description="Main exchange")
    rabbitmq_exchange_type: str = Field(default="topic", description="Type exchange")
    rabbitmq_exchange_durable: bool = Field(
        default=True, description="Exchange durable"
    )

    # Queue settings
    rabbitmq_queue_prefix: str = Field(default="edu", description="Queue prefix")
    rabbitmq_queue_durable: bool = Field(
        default=True, description="Queues durable by default"
    )
    rabbitmq_queue_exclusive: bool = Field(
        default=False, description="Queues exclusive by default"
    )
    rabbitmq_queue_auto_delete: bool = Field(
        default=False, description="Auto delete queues by default"
    )

    # Message settings
    rabbitmq_message_ttl: int = Field(
        default=3600000,  # 1 hour in milliseconds
        description="TTL messages by default (ms)",
    )
    rabbitmq_delivery_mode: int = Field(
        default=2, description="Delivery mode (1=non-persistent, 2=persistent)"
    )
    rabbitmq_priority_max: int = Field(default=10, description="Max priority messages")

    # Consumer settings
    rabbitmq_consumer_prefetch_count: int = Field(
        default=10, description="Number of prefetch messages"
    )
    rabbitmq_consumer_prefetch_size: int = Field(
        default=0, description="Size prefetch (0 = unlimited)"
    )
    rabbitmq_consumer_auto_ack: bool = Field(
        default=False, description="Auto confirmation messages"
    )

    # Dead letter settings
    rabbitmq_dead_letter_exchange: str = Field(
        default="eduplatform.dlx", description="Dead letter exchange"
    )
    rabbitmq_dead_letter_ttl: int = Field(
        default=86400000, description="TTL for dead letter queue"  # 24 hours
    )

    @validator("rabbitmq_url")
    def validate_rabbitmq_url(cls, v):
        """Validation RabbitMQ URL."""
        if not v.startswith("amqp://") and not v.startswith("amqps://"):
            raise ValueError("RabbitMQ URL must start with amqp:// or amqps://")
        return v

    @validator("rabbitmq_exchange_type")
    def validate_exchange_type(cls, v):
        """Validation type exchange."""
        allowed = ["direct", "topic", "headers", "fanout"]
        if v not in allowed:
            raise ValueError(f"Exchange type must be one of {allowed}")
        return v

    @validator("rabbitmq_delivery_mode")
    def validate_delivery_mode(cls, v):
        """Validation delivery mode."""
        if v not in [1, 2]:
            raise ValueError(
                "Delivery mode must be 1 (non-persistent) or 2 (persistent)"
            )
        return v

    @property
    def connection_params(self) -> Dict[str, any]:
        """Parameters connection to RabbitMQ."""
        return {
            "host": self.rabbitmq_host,
            "port": self.rabbitmq_port,
            "login": self.rabbitmq_username,
            "password": self.rabbitmq_password,
            "virtualhost": self.rabbitmq_vhost,
            "connection_attempts": self.rabbitmq_connection_attempts,
            "retry_delay": self.rabbitmq_retry_delay,
            "heartbeat": self.rabbitmq_heartbeat,
            "blocked_connection_timeout": self.rabbitmq_blocked_connection_timeout,
        }

    def get_queue_name(self, service: str, queue_type: str) -> str:
        """
        Generate queue name.

        Args:
            service: Name of service
            queue_type: Type of queue

        Returns:
            str: All name of queue
        """
        return f"{self.rabbitmq_queue_prefix}.{service}.{queue_type}"

    def get_routing_key(self, service: str, action: str, entity: str = None) -> str:
        """
        Generate routing key.

        Args:
            service: Name of service
            action: Action (created, updated, deleted and etc.)
            entity: Entity (optional)

        Returns:
            str: Routing key
        """
        if entity:
            return f"{service}.{entity}.{action}"
        return f"{service}.{action}"

    def get_queue_config(self, queue_name: str, **kwargs) -> Dict[str, any]:
        """
        Get configuration of queue.

        Args:
            queue_name: Name of queue
            **kwargs: Additional parameters

        Returns:
            Dict: Configuration of queue
        """
        config = {
            "name": queue_name,
            "durable": kwargs.get("durable", self.rabbitmq_queue_durable),
            "exclusive": kwargs.get("exclusive", self.rabbitmq_queue_exclusive),
            "auto_delete": kwargs.get("auto_delete", self.rabbitmq_queue_auto_delete),
            "arguments": {
                "x-message-ttl": kwargs.get("ttl", self.rabbitmq_message_ttl),
                "x-max-priority": kwargs.get(
                    "max_priority", self.rabbitmq_priority_max
                ),
                "x-dead-letter-exchange": kwargs.get(
                    "dlx", self.rabbitmq_dead_letter_exchange
                ),
            },
        }

        # Remove None values
        config["arguments"] = {
            k: v for k, v in config["arguments"].items() if v is not None
        }

        return config


# Queues for EduPlatform
class EduPlatformQueues:
    """Constants queues for EduPlatform."""

    # Notification queues
    EMAIL_QUEUE = "email"
    SMS_QUEUE = "sms"
    PUSH_QUEUE = "push"

    # File processing queues
    VIDEO_PROCESSING_QUEUE = "video.processing"
    IMAGE_PROCESSING_QUEUE = "image.processing"
    DOCUMENT_PROCESSING_QUEUE = "document.processing"

    # Certificate queues
    CERTIFICATE_GENERATION_QUEUE = "certificate.generation"
    CERTIFICATE_VALIDATION_QUEUE = "certificate.validation"

    # Analytics queues
    ANALYTICS_EVENTS_QUEUE = "analytics.events"
    METRICS_CALCULATION_QUEUE = "metrics.calculation"

    # Background tasks
    CLEANUP_QUEUE = "cleanup"
    BACKUP_QUEUE = "backup"
    REPORT_GENERATION_QUEUE = "report.generation"

    @classmethod
    def get_all_queues(cls) -> List[str]:
        """Get list of all queues."""
        return [
            value
            for name, value in cls.__dict__.items()
            if not name.startswith("_") and isinstance(value, str)
        ]


# Routing keys for EduPlatform
class EduPlatformRoutingKeys:
    """Routing keys for EduPlatform."""

    # User events
    USER_REGISTERED = "user.user.registered"
    USER_UPDATED = "user.user.updated"
    USER_DELETED = "user.user.deleted"

    # Course events
    COURSE_CREATED = "course.course.created"
    COURSE_UPDATED = "course.course.updated"
    COURSE_ENROLLED = "course.enrollment.created"

    # Lesson events
    LESSON_COMPLETED = "progress.lesson.completed"
    COURSE_COMPLETED = "progress.course.completed"

    # Notification events
    SEND_EMAIL = "notification.email.send"
    SEND_SMS = "notification.sms.send"
    SEND_PUSH = "notification.push.send"

    # File events
    PROCESS_VIDEO = "file.video.process"
    PROCESS_IMAGE = "file.image.process"

    # Certificate events
    GENERATE_CERTIFICATE = "certificate.certificate.generate"
    VALIDATE_CERTIFICATE = "certificate.certificate.validate"


@lru_cache()
def get_rabbitmq_config() -> RabbitMQConfig:
    """
    Get configuration RabbitMQ.
    Use caching to optimize performance.
    """
    return RabbitMQConfig()


# Global instance of configuration RabbitMQ
rabbitmq_config = get_rabbitmq_config()
