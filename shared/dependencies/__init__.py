"""
Shared dependencies for FastAPI applications.
"""

from .auth import get_current_active_user, get_current_user, get_current_user_id

__all__ = [
    "get_current_user",
    "get_current_active_user",
    "get_current_user_id",
]
