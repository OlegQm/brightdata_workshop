"""BrightData refresh response models."""

from __future__ import annotations

from pydantic import BaseModel


class RefreshResult(BaseModel):
    """Summary returned after live hotel data refresh."""

    updated: int
    failed: int
    token_configured: bool
    message: str
