"""HTTP client that proxies chat requests to the LLM service."""

from __future__ import annotations

from typing import AsyncGenerator

import httpx


class LlmClient:
    """Small streaming client for the internal LLM service."""

    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        """Initialise the shared async HTTP client."""
        timeout = httpx.Timeout(timeout_seconds, connect=10.0)
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=timeout)

    async def stream_chat(self, payload: dict) -> AsyncGenerator[bytes, None]:
        """Yield raw SSE bytes from the LLM ``/chat`` endpoint."""
        async with self._client.stream(
            "POST",
            f"{self._base_url}/chat",
            json=payload,
            headers={"Accept": "text/event-stream"},
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_bytes():
                yield chunk

    async def clear_session(self, session_id: str) -> None:
        """Forward a session-clear request to the LLM service."""
        response = await self._client.delete(f"{self._base_url}/chat/{session_id}")
        response.raise_for_status()

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()
