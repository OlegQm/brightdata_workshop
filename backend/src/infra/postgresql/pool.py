"""Lazy PostgreSQL connection factory."""

from __future__ import annotations

import psycopg
from psycopg.rows import dict_row


class PostgresPool:
    """Small synchronous PostgreSQL connection factory.

    Args:
        dsn: PostgreSQL DSN used for every new connection.
    """

    def __init__(self, dsn: str) -> None:
        """Store the DSN without opening a connection."""
        self._dsn = dsn.replace("postgresql+psycopg://", "postgresql://")

    def connect(self) -> psycopg.Connection:
        """Open and return a new dict-row PostgreSQL connection."""
        return psycopg.connect(self._dsn, row_factory=dict_row)

    async def close(self) -> None:
        """Compatibility hook for the DI container shutdown path."""
        return None
