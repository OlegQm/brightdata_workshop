# Backend Config

Typed runtime configuration for the backend.

`config.py` reads nested `BACKEND__...` environment variables from `.env` and
also accepts legacy compose variables:

- `DATABASE_URL`
- `HOTELS_SEED_PATH`
- `BRIGHTDATA_API_TOKEN`
- `LLM_URL`

Add new backend settings here before wiring them through `di/container.py`.
