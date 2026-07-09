"""Hotel filtering DTOs used by MCP tools."""

from __future__ import annotations

from typing import Any


def normalize_text(value: Any) -> str:
    """Return a stripped lowercase text value."""
    return str(value or "").strip().lower()


def normalize_limit(value: Any) -> int:
    """Return a safe result limit between 1 and 50."""
    try:
        return min(max(int(value), 1), 50)
    except (TypeError, ValueError):
        return 12
