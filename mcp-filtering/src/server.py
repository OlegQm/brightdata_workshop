"""FastMCP server entry point for hotel filtering tools."""

from __future__ import annotations

import fastmcp

from src.config.config import Config
from src.di.container import Container


def main() -> int:
    """Load config, register tools, and run the streamable-HTTP MCP server."""
    config = Config()
    container = Container(config=config)
    mcp = fastmcp.FastMCP("hotel-filtering")
    container.tool_handler.register(mcp)
    mcp.run(
        transport="streamable-http",
        host=config.server.host,
        port=config.server.port,
    )
    return 0
