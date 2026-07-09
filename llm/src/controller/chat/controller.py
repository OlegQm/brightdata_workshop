"""Chat controller that wraps ChatService into SSE responses."""

from __future__ import annotations

from sse_starlette.sse import EventSourceResponse

from src.controller.chat.dto.request import ChatRequest
from src.controller.chat.dto.response import ClearSessionResponse
from src.service.chat.chat_service import ChatService


class ChatController:
    """HTTP adapter for the chat service."""

    def __init__(self, service: ChatService) -> None:
        """Initialise the controller with a chat service."""
        self._service = service

    def handle_stream(self, body: ChatRequest) -> EventSourceResponse:
        """Create a session if needed and stream one user turn."""
        session_id = body.session_id or self._service.new_session_id()
        return EventSourceResponse(self._service.stream(session_id, body.message))

    def handle_clear(self, session_id: str) -> ClearSessionResponse:
        """Clear chat history for a session."""
        self._service.clear_session(session_id)
        return ClearSessionResponse(ok=True)
