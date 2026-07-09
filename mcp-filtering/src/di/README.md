# MCP Filtering Dependency Injection

`container.py` wires the MCP filtering service graph.

It owns logger initialization, PostgreSQL pool construction, repository
construction and the `ToolHandler` instance used by `src/server.py`.
