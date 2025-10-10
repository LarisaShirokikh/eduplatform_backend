"""
Kafka consumer for consuming events.
"""

import asyncio
import json
from typing import Callable, Optional

from aiokafka import AIOKafkaConsumer

from shared.config import kafka_config


class KafkaConsumerManager:
    """Manager for Kafka consumer."""

    def __init__(self, group_id: str):
        self.group_id = group_id
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._running = False

    async def start(self):
        """Start Kafka consumer."""
        if self._consumer is None:
            self._consumer = AIOKafkaConsumer(
                bootstrap_servers=kafka_config.kafka_bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=True,
            )
            await self._consumer.start()
            print(f"✅ Kafka consumer started: {self.group_id}")

    async def stop(self):
        """Stop Kafka consumer."""
        self._running = False
        if self._consumer:
            await self._consumer.stop()
            self._consumer = None
            print(f"❌ Kafka consumer stopped: {self.group_id}")

    async def consume(self, topics: list[str], handler: Callable):
        """
        Consume messages from topics and handle them.

        Args:
            topics: List of Kafka topics to subscribe to
            handler: Async function to handle each message
        """
        if not self._consumer:
            raise RuntimeError("Consumer not started")

        # Subscribe to topics
        self._consumer.subscribe(topics)
        print(f"📡 Subscribed to topics: {topics}")

        self._running = True

        try:
            async for message in self._consumer:
                if not self._running:
                    break

                try:
                    print(
                        f"📨 Received event from {message.topic}: {message.value.get('event_type', 'unknown')}"
                    )
                    await handler(message.value)
                except Exception as e:
                    print(f"❌ Error handling message: {e}")
                    # Continue processing other messages

        except asyncio.CancelledError:
            print("Consumer task cancelled")
        except Exception as e:
            print(f"❌ Consumer error: {e}")
        finally:
            self._running = False
