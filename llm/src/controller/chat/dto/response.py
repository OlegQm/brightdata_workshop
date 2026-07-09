"""Chat response DTOs."""

from __future__ import annotations

from pydantic import BaseModel


class ClearSessionResponse(BaseModel):
    """Response returned after clearing a chat session."""

    ok: bool
