# Backend

FastAPI service on port `8002`.

Responsibilities:

- serves `/api/hotels` search and lookup endpoints;
- exposes `/api/hotels/refresh` endpoints for BrightData refresh;
- proxies `/api/chat` SSE traffic to the internal `llm` service;
- serves local map/data files from `/data`;
- creates and seeds the PostgreSQL `hotels` table with pgvector embeddings.

Important entry points:

- `Dockerfile` - image used by `docker-compose.yml`.
- `src/app.py` - real application builder and local `python -m src` entry point.
- `src/di/container.py` - service wiring, FastAPI routes, CORS and startup schema setup.
- `data/` - runtime geodata and the seed hotel JSON.

Configuration is loaded from `.env` and compose environment variables. Prefer
adding new runtime settings in `src/config/config.py`.
