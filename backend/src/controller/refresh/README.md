# Backend Refresh Controller

BrightData refresh API used by the settings page.

Endpoints:

- `GET /api/hotels/refresh/status` - token/config and refresh metrics.
- `POST /api/hotels/refresh` - scrape source URLs through BrightData and update rows.

The heavy work lives in `src/service/refresh_service.py`.
