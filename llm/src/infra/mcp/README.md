# LLM MCP Infrastructure

MCP client wiring for LangGraph/LangChain.

`client.py` builds a `MultiServerMCPClient` from `Config.mcp.servers`. The
default server is `hotel-filtering`, served by the `mcp-filtering` container.
