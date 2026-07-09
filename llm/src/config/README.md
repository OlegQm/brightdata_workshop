# LLM Config

Typed runtime configuration for the LLM service.

`config.py` reads nested `LLM__...` variables and compose-compatible variables:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `MCP_FILTERING_URL`

Use `mcp.servers` when adding more MCP tool servers.
