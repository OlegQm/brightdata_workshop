# MCP Filtering Source

Layered implementation of the hotel-filtering MCP server.

Directory map:

- `server.py` and `__main__.py` - FastMCP startup.
- `config/` - PostgreSQL and server settings.
- `di/` - dependency wiring.
- `controller/tools/` - MCP tools and payload parsing.
- `infra/postgresql/` - concrete database access.
- `repository/` - repository protocol for tool handlers.
- `model/` - filter normalization helpers.
- `logger/` - shared logging setup.

Keep MCP tool behavior in `controller/tools` and SQL details in
`infra/postgresql`.
