# Backend Chat DTOs

Pydantic request models for backend chat endpoints.

Keep browser-facing payload shape here. Internal LLM payload changes should be
translated in `backend/src/controller/chat/controller.py` or
`backend/src/infra/http/llm_client.py`.
