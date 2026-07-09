"""Logging helpers for the LLM service."""

from __future__ import annotations

import sys
from enum import StrEnum

from loguru import logger


class LogLevel(StrEnum):
    """Supported service log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


def init_logger(level: LogLevel) -> None:
    """Configure loguru output."""
    logger.remove()
    logger.add(sys.stdout, level=level.value)
