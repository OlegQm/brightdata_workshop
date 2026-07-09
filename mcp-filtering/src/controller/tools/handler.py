"""MCP tool handler for hotel filtering."""

from __future__ import annotations

import json

import fastmcp

from src.repository.protocol import HotelRepository


class ToolHandler:
    """Implement and register MCP tools."""

    def __init__(self, hotel_repository: HotelRepository) -> None:
        """Initialise the handler with repository dependencies."""
        self._hotels = hotel_repository

    def register(self, mcp: fastmcp.FastMCP) -> None:
        """Register all hotel filtering tools on a FastMCP server."""
        mcp.add_tool(self.search_hotels)
        mcp.add_tool(self.get_available_filters)

    async def search_hotels(self, filters_json: str) -> str:
        """Search collected CZ/SK hotels by country, city, free text, rating and contact availability.

        Args:
            filters_json: JSON object with optional keys: country,
                country_code, city, query, location, rating, stars,
                has_contact and limit.

        Returns:
            JSON array string of normalized hotel dictionaries.
        """
        filters = self._parse_filters(filters_json)
        return json.dumps(self._hotels.search(filters), ensure_ascii=False, default=str)

    async def get_available_filters(self) -> str:
        """Return available countries, cities and ratings from the hotel database."""
        return json.dumps(self._hotels.facets(), ensure_ascii=False, default=str)

    def _parse_filters(self, filters_json: str) -> dict:
        """Parse a JSON filter object and return an empty dict on invalid input."""
        try:
            filters = json.loads(filters_json or "{}")
        except json.JSONDecodeError:
            filters = {}
        return filters if isinstance(filters, dict) else {}
