# Backend Services

Application logic for the backend.

Files:

- `hotels_service.py` - hotel listing, semantic ranking and lookup.
- `refresh_service.py` - BrightData refresh orchestration and record updates.
- `brightdata.py` - BrightData MCP scraping integration.
- `embedding.py` - deterministic embeddings and pgvector literal formatting.

Controllers should call services; services may use repositories and external
adapters.
