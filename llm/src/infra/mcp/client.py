"""Build a MultiServerMCPClient from config."""

from __future__ import annotations

from langchain_mcp_adapters.client import MultiServerMCPClient

from src.config.config import Config


def build_mcp_client(config: Config) -> MultiServerMCPClient:
    """Construct an MCP client wired to all configured MCP servers."""
    return MultiServerMCPClient(config.mcp.servers)
