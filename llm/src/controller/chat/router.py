"""LLM chat router."""

from fastapi import APIRouter, Request

from src.controller.chat.dto.request import ChatRequest
from src.controller.chat.dto.response import ClearSessionResponse

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat")
def chat(request: Request, body: ChatRequest):
    """Accept a user message and stream agent SSE events."""
    return request.app.state.chat_controller.handle_stream(body)


@router.delete("/chat/{session_id}", response_model=ClearSessionResponse)
def clear_session(request: Request, session_id: str) -> ClearSessionResponse:
    """Clear stored chat history for one session."""
    return request.app.state.chat_controller.handle_clear(session_id)
