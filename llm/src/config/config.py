"""Application configuration loaded from environment variables and ``.env``."""

from __future__ import annotations

import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.logger import LogLevel

_BASE_PREFIX = "LLM__"


def default_mcp_servers() -> dict[str, dict]:
    """Return the default MCP server mapping used by the chat agent."""
    return {
        "hotel-filtering": {
            "url": "http://mcp-filtering:8001/mcp",
            "transport": "streamable_http",
        }
    }


class OpenAI(BaseSettings):
    """OpenAI API settings."""

    api_key: str = ""
    model: str = "gpt-4.1-mini"


class Mcp(BaseSettings):
    """MCP server connection settings."""

    servers: dict[str, dict] = Field(default_factory=default_mcp_servers)


class Http(BaseSettings):
    """HTTP server binding settings."""

    host: str = "0.0.0.0"
    port: int = 8003


class Service(BaseSettings):
    """General service settings."""

    log_level: LogLevel = LogLevel.INFO


class Config(BaseSettings):
    """Root LLM service settings."""

    openai: OpenAI = OpenAI()
    mcp: Mcp = Mcp()
    http: Http = Http()
    service: Service = Service()

    model_config = SettingsConfigDict(
        env_prefix=_BASE_PREFIX,
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
    )

    def model_post_init(self, __context: object) -> None:
        """Apply compose-level environment variables for compatibility."""
        if os.getenv("OPENAI_API_KEY"):
            self.openai.api_key = os.environ["OPENAI_API_KEY"]
        if os.getenv("OPENAI_MODEL"):
            self.openai.model = os.environ["OPENAI_MODEL"]
        if os.getenv("MCP_FILTERING_URL"):
            self.mcp.servers = {
                "hotel-filtering": {
                    "url": os.environ["MCP_FILTERING_URL"],
                    "transport": "streamable_http",
                }
            }
