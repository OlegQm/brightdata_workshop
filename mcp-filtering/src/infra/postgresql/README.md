# MCP Filtering PostgreSQL Infrastructure

Database adapter for MCP hotel tools.

Files:

- `pool.py` - connection factory returning dict rows.
- `repository.py` - SQL filtering for tool calls and facet aggregation.

Tool handlers should depend on the repository protocol, not raw database
connections.
