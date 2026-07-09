"""Streaming chat proxy controller."""

from __future__ import annotations

from fastapi.responses import StreamingResponse

from src.controller.chat.dto.request import ChatRequest
from src.infra.http.llm_client import LlmClient


class ChatProxyController:
    """Proxy frontend chat traffic to the internal LLM service."""

    def __init__(self, llm_client: LlmClient) -> None:
        """Initialise the proxy with a shared LLM HTTP client."""
        self._llm_client = llm_client

    def handle_stream(self, body: ChatRequest) -> StreamingResponse:
        """Return an SSE streaming response from the LLM service."""
        return StreamingResponse(
            self._llm_client.stream_chat(body.model_dump()),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    async def handle_clear(self, session_id: str) -> dict[str, bool]:
        """Forward session clear to the LLM service."""
        await self._llm_client.clear_session(session_id)
        return {"ok": True}
