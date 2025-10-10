"""
Kafka producer for publishing events.
"""

import json
from typing import Optional

from aiokafka import AIOKafkaProducer

from shared.config import kafka_config


class KafkaProducerManager:
    """Manager for Kafka producer."""

    def __init__(self):
        self._producer: Optional[AIOKafkaProducer] = None

    async def start(self):
        """Start Kafka producer."""
        if self._producer is None:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=kafka_config.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
            )
            await self._producer.start()
            print(f"Kafka producer started: {kafka_config.kafka_bootstrap_servers}")

    async def stop(self):
        """Stop Kafka producer."""
        if self._producer:
            await self._producer.stop()
            self._producer = None
            print("Kafka producer stopped")

    async def send_event(self, topic: str, event_data: dict, key: Optional[str] = None):
        """
        Send event to Kafka topic.

        Args:
            topic: Kafka topic name
            event_data: Event data as dictionary
            key: Optional message key
        """
        if not self._producer:
            raise RuntimeError("Kafka producer not started")

        await self._producer.send(topic, value=event_data, key=key)
        print(
            f"Event sent to topic '{topic}': {event_data.get('event_type', 'unknown')}"
        )


# Global instance
_kafka_producer = KafkaProducerManager()


async def get_kafka_producer() -> KafkaProducerManager:
    """Get Kafka producer instance."""
    return _kafka_producer
