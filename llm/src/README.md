# LLM Source

Layered implementation for the chat service.

Directory map:

- `app.py` and `__main__.py` - service startup.
- `config/` - OpenAI, MCP and HTTP settings.
- `di/` - FastAPI app wiring.
- `controller/` - HTTP chat routes.
- `service/` - chat agent orchestration.
- `infra/` - MCP client adapter.
- `model/` - reserved for domain models.
- `logger/` - shared logging setup.

The LLM service should not query PostgreSQL directly. It uses MCP tools exposed
by `mcp-filtering`.
