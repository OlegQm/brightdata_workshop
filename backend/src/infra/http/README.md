# Backend HTTP Infrastructure

Internal HTTP clients used by the backend.

`llm_client.py` streams `/api/chat` responses from the `llm` service and clears
chat sessions. Keep browser-facing SSE details in controllers and internal
service URL/timeouts in config.
