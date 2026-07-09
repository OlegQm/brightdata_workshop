# MCP Filtering Tools

Tool registration and payload handling for the FastMCP server.

Current tools:

- `search_hotels(filters_json)` - filters hotels by country, city, text, rating, contact availability and limit.
- `get_available_filters()` - returns countries, cities and ratings present in the database.

The handler accepts JSON strings because LLM tool calls are easiest to validate
and recover when the input is explicit JSON.
