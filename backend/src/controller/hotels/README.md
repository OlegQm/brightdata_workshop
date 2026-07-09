# Backend Hotels Controller

Public hotel API.

Endpoints:

- `GET /api/hotels` - list hotels, optionally by `country` and semantic query `q`.
- `GET /api/hotels/{hotel_id}` - return one hotel or 404.

The controller delegates ranking, filtering and lookup behavior to
`src/service/hotels_service.py`.
