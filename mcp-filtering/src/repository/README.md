# MCP Filtering Repository Protocols

Repository interfaces used by MCP tool handlers.

`protocol.py` defines the methods the tool layer needs: `search()` and
`facets()`. Concrete SQL implementation lives in `infra/postgresql`.
