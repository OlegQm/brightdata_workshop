"""Backend chat proxy router."""

from fastapi import APIRouter, Request

from src.controller.chat.dto.request import ChatRequest

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat")
async def chat(request: Request, body: ChatRequest):
    """Proxy a chat request to the LLM service and stream SSE back."""
    return request.app.state.chat_proxy_controller.handle_stream(body)


@router.delete("/chat/{session_id}")
async def clear_session(request: Request, session_id: str) -> dict[str, bool]:
    """Clear a chat session in the LLM service."""
    return await request.app.state.chat_proxy_controller.handle_clear(session_id)
