"""Dependency-injection container for the MCP filtering service."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from src.config.config import Config
from src.controller.tools.handler import ToolHandler
from src.infra.postgresql.pool import PostgresPool
from src.infra.postgresql.repository import PostgresHotelRepository
from src.logger.logger import init_logger


@dataclass
class Container:
    """Lazy DI container that wires MCP infrastructure and tools."""

    config: Config

    def __post_init__(self) -> None:
        """Initialise logging once the container is constructed."""
        init_logger(self.config.service.log_level)

    @cached_property
    def _pool(self) -> PostgresPool:
        """Lazily construct the PostgreSQL connection factory."""
        return PostgresPool(self.config.db.url)

    @cached_property
    def _hotel_repository(self) -> PostgresHotelRepository:
        """Lazily construct the hotel repository."""
        return PostgresHotelRepository(self._pool)

    @cached_property
    def tool_handler(self) -> ToolHandler:
        """Lazily construct the MCP tool handler."""
        return ToolHandler(self._hotel_repository)
