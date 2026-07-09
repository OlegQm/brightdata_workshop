# LLM Chat Controller

Chat HTTP routes for the internal LLM service.

Endpoints:

- `POST /api/chat` - stream chat events.
- `DELETE /api/chat/{session_id}` - clear stored session history.

`controller.py` delegates to `ChatService`; `router.py` maps FastAPI requests
to controller methods.
