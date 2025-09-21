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
