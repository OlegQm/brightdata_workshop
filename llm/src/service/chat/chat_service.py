"""Chat service that manages session history and streams agent responses."""

from __future__ import annotations

import asyncio
import json
import re
import uuid
from typing import AsyncGenerator

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from src.config.config import Config
from src.service.chat.prompts import SYSTEM_PROMPT

HOTELS_RE = re.compile(r"<<<HOTELS_JSON>>>(.*?)<<<END_HOTELS>>>", re.DOTALL)
HOTELS_START_MARKER = "<<<HOTELS_JSON>>>"


class ChatService:
    """Manage chat sessions and stream LangGraph agent events as SSE dicts."""

    def __init__(self, config: Config, mcp_client) -> None:
        """Initialise the service with config and a shared MCP client."""
        self._config = config
        self._mcp_client = mcp_client
        self._sessions: dict[str, list] = {}

    def new_session_id(self) -> str:
        """Return a fresh session identifier."""
        return str(uuid.uuid4())

    def clear_session(self, session_id: str) -> None:
        """Remove stored history for a session."""
        self._sessions.pop(session_id, None)

    async def stream(self, session_id: str, user_message: str) -> AsyncGenerator[dict[str, str], None]:
        """Stream token/status/done events for a single user message."""
        yield self._sse("session", {"session_id": session_id})

        if not self._config.openai.api_key.strip():
            yield self._sse("token", {"token": "OPENAI_API_KEY is not configured in .env."})
            yield self._sse("done", {})
            return

        history = self._sessions.setdefault(session_id, [])
        history.append(HumanMessage(content=user_message))
        tools = await self._mcp_client.get_tools()
        llm = ChatOpenAI(
            model=self._config.openai.model,
            api_key=self._config.openai.api_key,
            streaming=True,
        )
        agent = create_react_agent(model=llm, tools=tools, prompt=SYSTEM_PROMPT)

        full_response = ""
        visible_buffer = ""
        hotels_block_started = False
        marker_tail_len = len(HOTELS_START_MARKER) - 1
        any_tool_started = False

        try:
            async for event in agent.astream_events({"messages": history}, version="v2"):
                event_type = event.get("event")
                if event_type == "on_tool_start":
                    if not any_tool_started:
                        any_tool_started = True
                        visible_buffer = ""
                        yield self._sse("discard", {"discard": True})
                    yield self._sse("status", {"status": "thinking"})
                    await asyncio.sleep(0)
                    continue
                if event_type != "on_chat_model_stream":
                    continue

                chunk = event["data"]["chunk"]
                token = chunk.content if hasattr(chunk, "content") else ""
                if not token:
                    continue
                full_response += token

                if hotels_block_started:
                    continue
                visible_buffer += token
                marker_index = visible_buffer.find(HOTELS_START_MARKER)
                if marker_index >= 0:
                    visible_token = visible_buffer[:marker_index].rstrip()
                    if visible_token:
                        yield self._sse("token", {"token": visible_token})
                    hotels_block_started = True
                    visible_buffer = ""
                    continue
                if len(visible_buffer) > marker_tail_len:
                    visible_token = visible_buffer[:-marker_tail_len]
                    visible_buffer = visible_buffer[-marker_tail_len:]
                    yield self._sse("token", {"token": visible_token})
                    await asyncio.sleep(0)
        except Exception as exc:
            yield self._sse("token", {"token": f"Chat service error: {exc}"})
            yield self._sse("done", {})
            return

        if visible_buffer and not hotels_block_started:
            yield self._sse("token", {"token": visible_buffer})

        hotels = self._extract_hotels(full_response)
        history.append(AIMessage(content=full_response))
        self._sessions[session_id] = history
        yield self._sse("done", {"hotels": hotels} if hotels is not None else {})

    def _extract_hotels(self, full_response: str):
        """Extract the hidden hotel JSON block from an agent response."""
        match = HOTELS_RE.search(full_response)
        if not match:
            return None
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            return None

    def _sse(self, event: str, data: dict) -> dict[str, str]:
        """Return an EventSourceResponse-compatible event dict."""
        return {"event": event, "data": json.dumps(data, ensure_ascii=False)}
