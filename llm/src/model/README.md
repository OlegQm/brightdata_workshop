# LLM Models

Reserved package for LLM domain models.

Current request/response schemas live in `controller/chat/dto` because they are
HTTP transport contracts. Add shared domain objects here only when they are used
outside a single controller.
