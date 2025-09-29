"""
Base model for all tables in EduPlatform.
Contains common fields and methods for all entities.
"""

import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """
    Base class for all models.
    Defines common fields and methods.
    """

    # Disable automatic creation of tables
    __abstract__ = True

    # Common fields for all models
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier of the record",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Date and time of creation of the record",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Date and time of the last update of the record",
    )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model to a dictionary.

        Returns:
            Dict: Dictionary with data of the model
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Update the model from a dictionary.

        Args:
            data: Dictionary with data for update
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self) -> str:
        """String representation of the model."""
        attrs = ", ".join(
            f"{key}={value!r}"
            for key, value in self.to_dict().items()
            if not key.startswith("_")
        )
        return f"{self.__class__.__name__}({attrs})"


class TimestampMixin:
    """
    Mixin for adding timestamps to models.
    Use if base Base does not fit.
    Use if base Base does not fit.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """
    Mixin for soft deletion of records.
    Records are marked as deleted, but remain in the DB.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, comment="Date of deletion"
    )

    @property
    def is_deleted(self) -> bool:
        """Check if the record is deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Mark the record as deleted."""
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore the deleted record."""
        self.deleted_at = None


class AuditMixin:
    """
    Mixin for audit changes.
    Tracks who created and updated the record.
    """

    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, comment="ID user who created the record"
    )

    updated_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, comment="ID user who updated the record"
    )


class VersionMixin:
    """
    Mixin for versioning records.
    Useful for optimistic locking.
    """

    version: Mapped[int] = mapped_column(
        default=1, nullable=False, comment="Version of the record"
    )

    def increment_version(self) -> None:
        """Increment the version of the record."""
        self.version += 1


# Metadata for migrations Alembic
metadata = Base.metadata
