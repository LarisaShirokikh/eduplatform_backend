"""
Messaging utilities for event-driven communication.
"""

from .kafka_consumer import KafkaConsumerManager
from .kafka_producer import KafkaProducerManager, get_kafka_producer

__all__ = ["KafkaProducerManager", "KafkaConsumerManager", "get_kafka_producer"]
