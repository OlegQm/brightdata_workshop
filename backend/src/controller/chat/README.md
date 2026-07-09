# Backend Chat Controller

SSE proxy from browser chat requests to the internal `llm` service.

Files:

- `router.py` - `/api/chat` POST and `/api/chat/{session_id}` DELETE routes.
- `controller.py` - forwards streaming and session-clear requests via `LlmClient`.
- `dto/` - request schemas.

The frontend talks only to the backend. It does not call the LLM service
directly.
