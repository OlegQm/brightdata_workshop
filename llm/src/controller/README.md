# LLM Controllers

HTTP boundary for the internal LLM service.

Currently contains `chat/`, which exposes endpoints consumed by the backend
chat proxy. Keep transport handling here and agent behavior in `service/chat/`.
