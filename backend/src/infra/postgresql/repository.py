"""Concrete PostgreSQL repository for hotel data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import psycopg
from psycopg.types.json import Jsonb

from src.infra.postgresql.pool import PostgresPool
from src.model.hotel import Hotel


class PostgresHotelRepository:
    """Read and write hotel records in PostgreSQL.

    Args:
        pool: Shared PostgreSQL connection factory.
        seed_path: JSON file used to seed the database when empty.
        embedding_dimensions: Number of dimensions in stored pgvector values.
    """

    def __init__(self, pool: PostgresPool, seed_path: Path, embedding_dimensions: int) -> None:
        """Initialise the repository with all schema settings."""
        self._pool = pool
        self._seed_path = seed_path
        self._embedding_dimensions = embedding_dimensions

    def ensure_schema(self, embed_record) -> None:
        """Create hotel schema and seed records if the table is empty.

        Args:
            embed_record: Callable that receives a seed record and returns a
                pgvector literal string.
        """
        with self._pool.connect() as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS hotels (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    country TEXT NOT NULL,
                    city TEXT NOT NULL,
                    address TEXT NOT NULL,
                    latitude DOUBLE PRECISION NOT NULL,
                    longitude DOUBLE PRECISION NOT NULL,
                    phone TEXT,
                    email TEXT,
                    website TEXT,
                    rating TEXT,
                    description TEXT,
                    source_url TEXT NOT NULL,
                    source_kind TEXT NOT NULL DEFAULT 'brightdata',
                    source_payload JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                    last_refreshed_at TIMESTAMPTZ,
                    embedding vector({self._embedding_dimensions}) NOT NULL
                )
                """
            )
            conn.execute("ALTER TABLE hotels ADD COLUMN IF NOT EXISTS source_payload JSONB NOT NULL DEFAULT '{}'::jsonb")
            conn.execute("ALTER TABLE hotels ADD COLUMN IF NOT EXISTS last_refreshed_at TIMESTAMPTZ")
            conn.execute(f"ALTER TABLE hotels ADD COLUMN IF NOT EXISTS embedding vector({self._embedding_dimensions})")
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS hotels_embedding_idx
                ON hotels USING hnsw (embedding vector_cosine_ops)
                """
            )
            count = conn.execute("SELECT COUNT(*) AS count FROM hotels").fetchone()["count"]
            if count == 0 and self._seed_path.exists():
                self.seed(conn, embed_record)
            conn.commit()

    def seed(self, conn: psycopg.Connection, embed_record) -> None:
        """Insert seed hotels from the configured JSON file.

        Args:
            conn: Open PostgreSQL connection inside the startup transaction.
            embed_record: Callable returning vector literal for a hotel record.
        """
        records: list[dict[str, Any]] = json.loads(self._seed_path.read_text(encoding="utf-8"))
        for record in records:
            record["embedding"] = embed_record(record)
            record["source_payload"] = Jsonb(record.copy())
            self.upsert_seed_record(conn, record)

    def upsert_seed_record(self, conn: psycopg.Connection, record: dict[str, Any]) -> None:
        """Insert or update a single seed hotel record."""
        conn.execute(
            """
            INSERT INTO hotels (
                id, name, country, city, address, latitude, longitude,
                phone, email, website, rating, description, source_url,
                source_kind, source_payload, embedding
            )
            VALUES (
                %(id)s, %(name)s, %(country)s, %(city)s, %(address)s,
                %(latitude)s, %(longitude)s, %(phone)s, %(email)s, %(website)s,
                %(rating)s, %(description)s, %(source_url)s, %(source_kind)s,
                %(source_payload)s, %(embedding)s::vector
            )
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                country = EXCLUDED.country,
                city = EXCLUDED.city,
                address = EXCLUDED.address,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                phone = EXCLUDED.phone,
                email = EXCLUDED.email,
                website = EXCLUDED.website,
                rating = EXCLUDED.rating,
                description = EXCLUDED.description,
                source_url = EXCLUDED.source_url,
                source_kind = EXCLUDED.source_kind,
                source_payload = EXCLUDED.source_payload,
                embedding = EXCLUDED.embedding
            """,
            record,
        )

    def list(self, *, country: str | None, query_embedding: str | None) -> list[Hotel]:
        """Return hotels, optionally filtered by country and semantic query."""
        params: dict[str, Any] = {}
        filters: list[str] = []
        if country:
            filters.append("LOWER(country) = %(country)s")
            params["country"] = country.lower()
        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        if query_embedding:
            params["query_embedding"] = query_embedding
            order_sql = "embedding <=> %(query_embedding)s::vector, country, city, name"
        else:
            order_sql = "country, city, name"
        sql = f"""
            SELECT id, name, country, city, address, latitude, longitude, phone,
                   email, website, rating, description, source_url, source_kind
            FROM hotels
            {where_sql}
            ORDER BY {order_sql}
        """
        with self._pool.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [Hotel(**row) for row in rows]

    def get(self, hotel_id: str) -> Hotel | None:
        """Return one hotel by id, or ``None`` when absent."""
        with self._pool.connect() as conn:
            row = conn.execute(
                """
                SELECT id, name, country, city, address, latitude, longitude, phone,
                       email, website, rating, description, source_url, source_kind
                FROM hotels
                WHERE id = %(hotel_id)s
                """,
                {"hotel_id": hotel_id},
            ).fetchone()
        return Hotel(**row) if row else None

    def refresh_status(self) -> dict[str, Any]:
        """Return aggregate refresh status metrics."""
        with self._pool.connect() as conn:
            return conn.execute(
                """
                SELECT
                  COUNT(*) AS total,
                  COUNT(last_refreshed_at) AS refreshed,
                  MAX(last_refreshed_at) AS last_refreshed_at
                FROM hotels
                """
            ).fetchone()

    def select_for_refresh(self) -> list[dict[str, Any]]:
        """Return all hotels with source URLs for BrightData refresh."""
        with self._pool.connect() as conn:
            return conn.execute(
                """
                SELECT id, name, country, city, address, latitude, longitude, phone,
                       email, website, rating, description, source_url, source_kind
                FROM hotels
                ORDER BY country, city, name
                """
            ).fetchall()

    def update_refreshed(self, record: dict[str, Any]) -> None:
        """Update a hotel with refreshed BrightData-derived fields."""
        with self._pool.connect() as conn:
            conn.execute(
                """
                UPDATE hotels
                SET phone = %(phone)s,
                    email = %(email)s,
                    description = %(description)s,
                    source_payload = %(source_payload)s,
                    last_refreshed_at = NOW(),
                    embedding = %(embedding)s::vector
                WHERE id = %(id)s
                """,
                record,
            )
            conn.commit()
