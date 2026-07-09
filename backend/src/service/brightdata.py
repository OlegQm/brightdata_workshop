"""BrightData MCP client service."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from fastapi import HTTPException


class BrightDataService:
    """Call the BrightData MCP server through stdio."""

    def __init__(self, api_token: str, timeout_seconds: float) -> None:
        """Initialise the service with a secret token and timeout."""
        self._api_token = api_token
        self._timeout_seconds = timeout_seconds

    @property
    def token_configured(self) -> bool:
        """Return whether a usable BrightData token is configured."""
        return bool(self._api_token.strip())

    async def scrape_batch(self, urls: list[str]) -> list[dict[str, Any]]:
        """Scrape a batch of URLs through the BrightData MCP ``scrape_batch`` tool."""
        if not self.token_configured:
            raise HTTPException(status_code=400, detail="BRIGHTDATA_API_TOKEN is not configured")

        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        server = StdioServerParameters(
            command="npx",
            args=["-y", "@brightdata/mcp"],
            env={**os.environ, "API_TOKEN": self._api_token},
        )
        async with stdio_client(server) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await asyncio.wait_for(
                    session.call_tool("scrape_batch", {"urls": urls}),
                    timeout=self._timeout_seconds,
                )

        text_parts = [getattr(item, "text", "") for item in getattr(result, "content", [])]
        payload_text = "\n".join(part for part in text_parts if part)
        if not payload_text:
            return []
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=502, detail=f"BrightData returned non-JSON payload: {exc}") from exc
        if not isinstance(payload, list):
            raise HTTPException(status_code=502, detail="BrightData returned unexpected payload")
        return payload
