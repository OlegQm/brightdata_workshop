# MCP Filtering Service

FastMCP service on port `8001`.

Responsibilities:

- exposes hotel filtering tools to the LLM service;
- reads hotel records from PostgreSQL;
- returns normalized JSON strings for LangGraph tools.

Important entry points:

- `Dockerfile` - image used by `docker-compose.yml`.
- `src/server.py` - FastMCP startup.
- `src/controller/tools/` - MCP tool registration and request parsing.
- `src/infra/postgresql/` - SQL filtering and facets.

The service is internal-only in compose. Browser and backend requests should not
call it directly.
