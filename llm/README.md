# LLM Service

Internal FastAPI service on port `8003`.

Responsibilities:

- receives chat requests from the backend;
- runs a LangGraph ReAct agent backed by OpenAI;
- connects to the `mcp-filtering` service for hotel-search tools;
- streams SSE events back to the backend.

Important entry points:

- `Dockerfile` - image used by `docker-compose.yml`.
- `src/app.py` - real FastAPI builder and local `python -m src` entry point.
- `src/service/chat/` - chat session, prompt and streaming logic.
- `src/infra/mcp/` - MCP client wiring.

Required environment:

- `OPENAI_API_KEY`
- `OPENAI_MODEL` optional, defaults to `gpt-4.1-mini`
- `MCP_FILTERING_URL` optional in compose, defaults to the internal service URL.
