"""Lazy PostgreSQL connection factory."""

from __future__ import annotations

import psycopg
from psycopg.rows import dict_row


class PostgresPool:
    """Create PostgreSQL connections for repository methods."""

    def __init__(self, dsn: str) -> None:
        """Store the DSN without opening a connection."""
        self._dsn = dsn

    def connect(self) -> psycopg.Connection:
        """Open and return a dict-row PostgreSQL connection."""
        return psycopg.connect(self._dsn, row_factory=dict_row)
