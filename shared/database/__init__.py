"""
Database модуль для EduPlatform.
Содержит базовые модели, подключения и репозитории.
"""

from .base import (
    AuditMixin,
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    VersionMixin,
    metadata,
)
from .connection import (
    DatabaseConnection,
    close_all_connections,
    get_database,
    get_db_session,
)
from .repository import BaseRepository

__all__ = [
    # Base models
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
    "AuditMixin",
    "VersionMixin",
    "metadata",
    # Connection
    "DatabaseConnection",
    "get_database",
    "get_db_session",
    "close_all_connections",
    # Repository
    "BaseRepository",
]
