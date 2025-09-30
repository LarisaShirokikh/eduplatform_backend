"""
Base event schemas for Kafka messaging.
All events inherit from BaseEvent to ensure consistent structure.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """
    Base class for all Kafka events.
    Ensures consistent structure across all events.
    """

    event_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique event identifier"
    )
    event_type: str = Field(..., description="Type of event")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Event creation timestamp"
    )
    service: str = Field(..., description="Service that produced the event")
    version: str = Field(default="1.0", description="Event schema version")
    correlation_id: Optional[uuid.UUID] = Field(
        default=None, description="ID to correlate related events"
    )
    user_id: Optional[uuid.UUID] = Field(
        default=None, description="User who triggered the event"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional event metadata"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v),
        }

    def to_kafka_message(self) -> Dict[str, Any]:
        """Convert event to Kafka message format."""
        return self.model_dump(mode="json")

    @classmethod
    def from_kafka_message(cls, message: Dict[str, Any]) -> "BaseEvent":
        """Create event from Kafka message."""
        return cls(**message)


class EventMetadata(BaseModel):
    """Common metadata for events."""

    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
