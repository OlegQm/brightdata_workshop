"""Chat request DTOs."""

from __future__ import annotations

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Incoming chat message request."""

    message: str
    session_id: str | None = None
