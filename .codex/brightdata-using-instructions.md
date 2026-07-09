# BrightData MCP Usage Instructions

BrightData is tightly integrated into this project: it is the required data
collection and live-refresh path for hotel source data, while the app itself
stores and serves normalized hotel records from Postgres. Treat BrightData as a
first-class project dependency, not as an optional scraper.

## Where BrightData Fits

- Backend service: `backend/src/service/brightdata.py`
  - Starts `@brightdata/mcp` through `npx`.
  - Passes the token as `API_TOKEN`.
  - Calls the BrightData MCP `scrape_batch` tool for hotel source URLs.
- Refresh orchestration: `backend/src/service/refresh_service.py`
  - Reads hotel `source_url` values from Postgres.
  - Sends them to BrightData in batches.
  - Updates contact fields, source payloads and embeddings.
- Database:
  - Hotel records use `source_kind = "brightdata"`.
  - Refreshed raw source data is stored in `source_payload`.
  - `last_refreshed_at` tracks live BrightData updates.
- UI:
  - Settings page triggers `/api/hotels/refresh`.
  - The browser never receives the BrightData token.
- Local agent MCP:
  - `.codex/config.toml` defines the `brightdata` MCP server.
  - It expects `BRIGHTDATA_API_TOKEN` and maps it to `API_TOKEN` for
    `@brightdata/mcp`.

## Token Handling

Use `BRIGHTDATA_API_TOKEN` from `.env` or the current shell environment.

Never:

- Hardcode the token in source files.
- Print the token in logs or final answers.
- Send the token to frontend code.
- Commit `.env`.
- Add the token to README examples beyond placeholder form.

The backend already reads `BRIGHTDATA_API_TOKEN` via `backend/src/config/config.py`.
If you add new BrightData code, pass the token through configuration and DI,
not through ad hoc global reads scattered across modules.

## Agent Workflow

When a task requires collecting, enriching or refreshing hotel data, use
BrightData MCP. Do not replace it with a custom scraper, random HTTP scraping, or
browser automation unless the user explicitly asks for a separate experiment.
BrightData is already woven into the project, so the normal path is:

1. Confirm the target data.
   - Hotels for Slovakia and Czechia are the current domain.
   - Existing records should use the `source_url` already stored in Postgres.
   - New records should include a stable source URL suitable for future refresh.

2. Use BrightData MCP to fetch source pages.
   - In app code, use `BrightDataService.scrape_batch(urls)`.
   - In agent tooling, use the configured `brightdata` MCP server when available.
   - Prefer batch calls for multiple URLs.

3. Normalize the result before storing.
   - Keep canonical fields on the `hotels` table:
     `name`, `country`, `city`, `address`, `latitude`, `longitude`, `phone`,
     `email`, `website`, `rating`, `description`, `source_url`, `source_kind`.
   - Store raw/diagnostic BrightData content in `source_payload`.
   - Recalculate the hotel embedding after description/contact enrichment.

4. Verify through the app surface.
   - `GET /api/hotels`
   - `GET /api/hotels/refresh/status`
   - `POST /api/hotels/refresh`
   - The Settings page at `http://localhost:5173/#settings`

## Running the Project Path

Start the stack:

```bash
docker compose up -d --build
```

Check BrightData refresh readiness:

```bash
curl -fsS http://localhost:8002/api/hotels/refresh/status
```

Trigger live refresh:

```bash
curl -fsS -X POST http://localhost:8002/api/hotels/refresh
```

Expected behavior:

- If `BRIGHTDATA_API_TOKEN` is missing, backend returns a clear 400 error.
- If the token is present, backend starts `@brightdata/mcp` internally and calls
  `scrape_batch`.
- Refreshed rows get `last_refreshed_at`.
- Updated contacts/descriptions are reflected on the map and in hotel details.

## Using BrightData MCP Directly

For direct MCP usage, rely on the configured MCP server in `.codex/config.toml`.
It launches:

```bash
npx -y @brightdata/mcp
```

with:

```bash
API_TOKEN=$BRIGHTDATA_API_TOKEN
```

If you need to inspect available BrightData tools, ask the MCP client/tooling for
the tool list first. Do not assume a tool exists beyond what the server reports.
The app currently depends on `scrape_batch` for URL batch scraping.

Typical payload shape used by backend:

```json
{
  "urls": [
    "https://example-hotel.test/contact",
    "https://example-hotel.test/about"
  ]
}
```

Typical returned data is handled as a JSON array where each item includes status
metadata and a `value` object with page URL/content. Keep parser code defensive:
BrightData can return failed items, empty content, or non-JSON text if the MCP
call fails unexpectedly.

## Code Guidelines

- Keep BrightData integration in `backend/src/service/brightdata.py` unless a new
  adapter is genuinely needed.
- Keep orchestration in `backend/src/service/refresh_service.py`.
- Keep FastAPI handlers thin in `backend/src/controller/refresh`.
- Use dependency injection through `backend/src/di/container.py`.
- Preserve the rule that browser code only triggers backend endpoints; it never
  calls BrightData directly.
- For schema changes, update `PostgresHotelRepository.ensure_schema`.
- For new normalized hotel fields, update:
  - `backend/src/model/hotel.py`
  - `backend/src/infra/postgresql/repository.py`
  - frontend detail/list components if the field is user-facing
  - MCP filtering tools if the field should be searchable by the chatbot

## Chatbot and BrightData Boundary

The chatbot does not scrape. It filters and explains data already stored in
Postgres through the internal `mcp-filtering` service.

If the user asks the chatbot for fresher data, direct them to the Settings
refresh flow. The live refresh uses BrightData, then the chatbot can search the
updated database.

## Quality Checks

After changing BrightData behavior, run:

```bash
python3 -m py_compile $(find backend/src -name '*.py' | sort)
npm run build
docker compose up -d --build
curl -fsS http://localhost:8002/api/hotels/refresh/status
```

If `BRIGHTDATA_API_TOKEN` is configured, also test:

```bash
curl -fsS -X POST http://localhost:8002/api/hotels/refresh
```

Report whether the token was configured without revealing its value.
