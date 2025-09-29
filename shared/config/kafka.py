from functools import lru_cache
from typing import Dict, List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # broker settings
    kafka_bootstrap_servers: str = Field(
        default="localhost:9092", description="Kafka bootstrap servers"
    )

    kafka_security_protocol: str = Field(
        default="PLAINTEXT", description="Kafka security protocol"
    )

    kafka_sasl_mechanisms: Optional[str] = Field(
        default=None, description="Kafka SASL mechanisms"
    )

    kafka_sasl_username: Optional[str] = Field(
        default=None, description="Kafka SASL username"
    )

    kafka_sasl_password: Optional[str] = Field(
        default=None, description="Kafka SASL password"
    )

    # producer settings
    kafka_producer_client_id: str = Field(
        default="eduplatform-producer", description="Kafka producer client id"
    )

    kafka_producer_acks: str = Field(
        default="all", description="Kafka producer acks(0, 1, all)"
    )

    kafka_producer_retries: int = Field(default=3, description="Kafka producer retries")

    kafka_producer_batch_size: int = Field(
        default=16384, description="Kafka producer batch size"
    )

    kafka_producer_linger_ms: int = Field(
        default=5, description="Time to wait for more messages to add to the batch"
    )

    kafka_producer_compression_tipe: int = Field(
        default=16384, description="Size batch of producer"
    )

    kafka_producer_max_request_size: int = Field(
        default=1048576, description="Max request size of producer"
    )
    kafka_producer_request_timeout_ms: int = Field(
        default=30000, description="Timeout request of producer"
    )

    # Consumer settings
    kafka_consumer_group_id: str = Field(
        default="eduplatform-consumers", description="Group ID of consumer"
    )
    kafka_consumer_client_id: str = Field(
        default="eduplatform-consumer", description="Client ID of consumer"
    )
    kafka_auto_offset_reset: str = Field(
        default="earliest", description="Strategy reset offset (earliest, latest)"
    )
    kafka_enable_auto_commit: bool = Field(
        default=False, description="Auto commit offset"
    )
    kafka_auto_commit_interval_ms: int = Field(
        default=1000, description="Interval auto commit"
    )
    kafka_session_timeout_ms: int = Field(
        default=10000, description="Timeout session of consumer"
    )
    kafka_heartbeat_interval_ms: int = Field(
        default=3000, description="Interval heartbeat"
    )
    kafka_max_poll_records: int = Field(default=500, description="Max records of poll")
    kafka_max_poll_interval_ms: int = Field(
        default=300000, description="Max interval between poll"
    )
    kafka_fetch_min_bytes: int = Field(default=1, description="Min bytes for fetch")
    kafka_fetch_max_wait_ms: int = Field(
        default=500, description="Max wait time for fetch"
    )

    # Topic settings
    kafka_topic_partitions: int = Field(
        default=3, description="Default number of partitions"
    )
    kafka_topic_replication_factor: int = Field(
        default=1, description="Default replication factor"
    )
    kafka_topic_retention_ms: int = Field(
        default=604800000, description="Time retention of messages (ms)"  # 7 days
    )
    kafka_topic_cleanup_policy: str = Field(
        default="delete", description="Policy cleanup of topics"
    )

    @validator("kafka_bootstrap_servers")
    def validate_bootstrap_servers(cls, v):
        """Validation bootstrap servers."""
        if not v:
            raise ValueError("Kafka bootstrap servers cannot be empty")
        return v

    @validator("kafka_producer_acks")
    def validate_producer_acks(cls, v):
        """Validation setting acks."""
        allowed = ["0", "1", "all", "-1"]
        if str(v) not in allowed:
            raise ValueError(f"Producer acks must be one of {allowed}")
        return v

    @validator("kafka_auto_offset_reset")
    def validate_auto_offset_reset(cls, v):
        """Validation strategy reset offset."""
        allowed = ["earliest", "latest", "none"]
        if v not in allowed:
            raise ValueError(f"Auto offset reset must be one of {allowed}")
        return v

    @property
    def bootstrap_servers_list(self) -> List[str]:
        """List bootstrap servers."""
        return [server.strip() for server in self.kafka_bootstrap_servers.split(",")]

    @property
    def producer_config(self) -> Dict[str, any]:
        """Configuration producer."""
        return {
            "bootstrap_servers": self.bootstrap_servers_list,
            "client_id": self.kafka_producer_client_id,
            "acks": self.kafka_producer_acks,
            "retries": self.kafka_producer_retries,
            "batch_size": self.kafka_producer_batch_size,
            "linger_ms": self.kafka_producer_linger_ms,
            "compression_type": self.kafka_producer_compression_type,
            "max_request_size": self.kafka_producer_max_request_size,
            "request_timeout_ms": self.kafka_producer_request_timeout_ms,
            "security_protocol": self.kafka_security_protocol,
        }

    @property
    def consumer_config(self) -> Dict[str, any]:
        """Configuration consumer."""
        return {
            "bootstrap_servers": self.bootstrap_servers_list,
            "group_id": self.kafka_consumer_group_id,
            "client_id": self.kafka_consumer_client_id,
            "auto_offset_reset": self.kafka_auto_offset_reset,
            "enable_auto_commit": self.kafka_enable_auto_commit,
            "auto_commit_interval_ms": self.kafka_auto_commit_interval_ms,
            "session_timeout_ms": self.kafka_session_timeout_ms,
            "heartbeat_interval_ms": self.kafka_heartbeat_interval_ms,
            "max_poll_records": self.kafka_max_poll_records,
            "max_poll_interval_ms": self.kafka_max_poll_interval_ms,
            "fetch_min_bytes": self.kafka_fetch_min_bytes,
            "fetch_max_wait_ms": self.kafka_fetch_max_wait_ms,
            "security_protocol": self.kafka_security_protocol,
        }

    def get_topic_config(self, topic_name: str) -> Dict[str, any]:
        """
        Get configuration of topic.

        Args:
            topic_name: Name of topic

        Returns:
            Dict: Configuration of topic
        """
        return {
            "topic": topic_name,
            "num_partitions": self.kafka_topic_partitions,
            "replication_factor": self.kafka_topic_replication_factor,
            "config": {
                "retention.ms": str(self.kafka_topic_retention_ms),
                "cleanup.policy": self.kafka_topic_cleanup_policy,
            },
        }


class EduPlatformTopics:
    # User events
    USER_REGISTERED = "user.registered"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"

    # Course events
    COURSE_CREATED = "course.created"
    COURSE_UPDATED = "course.updated"
    COURSE_PUBLISHED = "course.published"
    COURSE_DELETED = "course.deleted"
    COURSE_ENROLLED = "course.enrolled"
    COURSE_UNENROLLED = "course.unenrolled"

    # Lesson events
    LESSON_CREATED = "lesson.created"
    LESSON_UPDATED = "lesson.updated"
    LESSON_COMPLETED = "lesson.completed"
    LESSON_STARTED = "lesson.started"

    # Progress events
    PROGRESS_UPDATED = "progress.updated"
    COURSE_COMPLETED = "course.completed"

    # Certificate events
    CERTIFICATE_REQUESTED = "certificate.requested"
    CERTIFICATE_ISSUED = "certificate.issued"
    CERTIFICATE_REVOKED = "certificate.revoked"

    # File events
    FILE_UPLOADED = "file.uploaded"
    VIDEO_PROCESSING_STARTED = "video.processing.started"
    VIDEO_PROCESSING_COMPLETED = "video.processing.completed"
    VIDEO_PROCESSING_FAILED = "video.processing.failed"

    # Notification events
    NOTIFICATION_SEND = "notification.send"
    EMAIL_SEND = "email.send"
    SMS_SEND = "sms.send"
    PUSH_SEND = "push.send"

    @classmethod
    def get_all_topics(cls) -> List[str]:
        """Get list of all topics."""
        return [
            value
            for name, value in cls.__dict__.items()
            if not name.startswith("_") and isinstance(value, str)
        ]


@lru_cache()
def get_kafka_config() -> KafkaConfig:
    """
    Get configuration of Kafka.
    Use caching to optimize performance.
    """
    return KafkaConfig()


# Global instance of configuration Kafka
kafka_config = get_kafka_config()
