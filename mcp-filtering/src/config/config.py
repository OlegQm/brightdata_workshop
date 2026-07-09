"""Configuration loaded from environment variables."""

from __future__ import annotations

import os

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.logger import LogLevel

_BASE_PREFIX = "MCP_FILTERING__"


class Db(BaseSettings):
    """PostgreSQL connection settings."""

    url: str = "postgresql://hotels:hotels@postgres:5432/hotels"


class Server(BaseSettings):
    """FastMCP server binding settings."""

    host: str = "0.0.0.0"
    port: int = 8001


class Service(BaseSettings):
    """General MCP service settings."""

    log_level: LogLevel = LogLevel.INFO


class Config(BaseSettings):
    """Root MCP filtering configuration."""

    db: Db = Db()
    server: Server = Server()
    service: Service = Service()

    model_config = SettingsConfigDict(
        env_prefix=_BASE_PREFIX,
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
    )

    def model_post_init(self, __context: object) -> None:
        """Apply legacy ``DATABASE_URL`` when provided by compose."""
        if os.getenv("DATABASE_URL"):
            self.db.url = os.environ["DATABASE_URL"]
