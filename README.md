# CZ/SK Hotels Map

Interactive hotel map for Slovakia and Czechia.

The base map uses only OpenStreetMap-derived data copied from
`/home/olegqm/work/boxyland/boxyalnd-locations-searcher`:

- `backend/data/czsk.pmtiles`
- `backend/data/czsk.osm.pbf`
- `backend/data/czsk_boundary.geojson`

Hotel seed data was collected through the BrightData MCP tools and stored in
Postgres. The backend enables `pgvector`, creates a vector embedding for each
hotel, and ranks `/api/hotels?q=...` results with pgvector cosine search.

## Run

Set BrightData and OpenAI tokens in `.env` before using live refresh and chat:

```bash
BRIGHTDATA_API_TOKEN=...
OPENAI_API_KEY=...
```

```bash
docker compose up --build
```

Open http://localhost:5173.

Settings page: http://localhost:5173/#settings

The BrightData refresh button calls the backend, starts `@brightdata/mcp`, scrapes
the current hotel source URLs, stores the refreshed source payload in Postgres,
and recalculates pgvector embeddings.

The map chat button opens a HotelFinder chatbot. Browser requests go through the
backend `/api/chat` SSE proxy to the `llm` service. The LLM service reads
`OPENAI_API_KEY` from `.env`, connects to `mcp-filtering`, and uses MCP tools to
filter hotels stored in Postgres by country, city, rating, text, and contact
availability.

## Refresh OSM Data

The download compose file and scripts mirror the OSM-only flow from the
reference project.

```bash
make download-0
```

To download all data first and then start the application:

```bash
make download-and-up
```

## Local Development

The simplest local workflow is still Compose, because backend, `llm`,
`mcp-filtering` and Postgres communicate over the Compose network:

```bash
docker compose up -d postgres mcp-filtering llm backend
cd frontend
npm install
npm run dev
```

For host-side backend development, use an externally reachable Postgres and set
`DATABASE_URL`, `LLM_URL`, `HOTELS_SEED_PATH` and `BRIGHTDATA_API_TOKEN` in the
shell or `.env` before running:

```bash
cd backend
uvicorn src.app:build_app --factory --reload --host 0.0.0.0 --port 8002
```

## Architecture

Python services follow the same layered shape:

- `src/config` - typed environment configuration
- `src/di` - lazy dependency-injection container
- `src/controller` - thin HTTP or MCP controllers and routers
- `src/model` - Pydantic/domain models and DTOs
- `src/service` - business logic and orchestration
- `src/infra` - PostgreSQL, HTTP, MCP and other adapters
- `src/logger` - shared logging setup

## Project Map

Each main directory has its own `README.md` with local navigation notes.

- `backend/` - public API, static map data, BrightData refresh proxy and chat proxy.
- `frontend/` - Vue/Vite map UI, settings page and chat panel.
- `llm/` - internal FastAPI service that streams LLM chat responses.
- `mcp-filtering/` - FastMCP server exposing hotel filtering tools to the LLM.
- `installation_scripts/` - Dockerfiles and shell scripts used to download or generate map data.
- `.codex/` and `.github/` - agent-facing project instructions.
- `scripts/` - reserved for local utility scripts.
