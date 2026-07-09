"""Concrete PostgreSQL repository for MCP hotel filtering."""

from __future__ import annotations

from typing import Any

from src.infra.postgresql.pool import PostgresPool
from src.model.filter import normalize_limit, normalize_text


class PostgresHotelRepository:
    """Read hotels and filter facets from PostgreSQL."""

    def __init__(self, pool: PostgresPool) -> None:
        """Initialise the repository with a connection factory."""
        self._pool = pool

    def search(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        """Return hotels matching supported MCP filters."""
        where: list[str] = []
        params: dict[str, Any] = {"limit": normalize_limit(filters.get("limit"))}

        country = normalize_text(filters.get("country") or filters.get("country_code"))
        if country in {"sk", "slovakia", "slovensko"}:
            where.append("LOWER(country) = 'slovakia'")
        elif country in {"cz", "czechia", "czech republic", "cesko", "česko"}:
            where.append("LOWER(country) = 'czechia'")

        city = normalize_text(filters.get("city"))
        if city:
            where.append("LOWER(city) LIKE %(city)s")
            params["city"] = f"%{city}%"

        query = normalize_text(filters.get("query") or filters.get("location") or filters.get("text"))
        if query:
            where.append(
                """
                (
                  LOWER(name) LIKE %(query)s OR LOWER(city) LIKE %(query)s OR
                  LOWER(address) LIKE %(query)s OR LOWER(COALESCE(description, '')) LIKE %(query)s OR
                  LOWER(COALESCE(rating, '')) LIKE %(query)s
                )
                """
            )
            params["query"] = f"%{query}%"

        rating = normalize_text(filters.get("rating") or filters.get("stars"))
        if rating:
            where.append("LOWER(COALESCE(rating, '')) LIKE %(rating)s")
            params["rating"] = f"%{rating}%"

        if filters.get("has_contact") is True:
            where.append("(phone IS NOT NULL OR email IS NOT NULL OR website IS NOT NULL)")

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        sql = f"""
            SELECT id, name, country, city, address, latitude, longitude, phone,
                   email, website, rating, description, source_url, source_kind
            FROM hotels
            {where_sql}
            ORDER BY country, city, name
            LIMIT %(limit)s
        """
        with self._pool.connect() as conn:
            return list(conn.execute(sql, params).fetchall())

    def facets(self) -> dict[str, Any]:
        """Return available countries, cities and ratings."""
        with self._pool.connect() as conn:
            countries = conn.execute(
                """
                SELECT country, COUNT(*) AS count
                FROM hotels
                GROUP BY country
                ORDER BY country
                """
            ).fetchall()
            cities = conn.execute(
                """
                SELECT country, city, COUNT(*) AS count
                FROM hotels
                GROUP BY country, city
                ORDER BY country, city
                """
            ).fetchall()
            ratings = conn.execute(
                """
                SELECT rating, COUNT(*) AS count
                FROM hotels
                WHERE rating IS NOT NULL AND rating <> ''
                GROUP BY rating
                ORDER BY rating
                """
            ).fetchall()
        return {"countries": countries, "cities": cities, "ratings": ratings}
