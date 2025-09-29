"""
Shared module for EduPlatform.
Contains common components used by all microservices.
"""

__version__ = "0.1.0"
__author__ = "EduPlatform Team"

from .config import app_config, get_app_config

__all__ = [
    "app_config",
    "get_app_config",
]
