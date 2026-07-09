# Backend Controllers

HTTP boundary for the backend FastAPI API.

Structure:

- `health/` - liveness endpoint.
- `hotels/` - hotel list and detail endpoints.
- `refresh/` - BrightData refresh status and trigger endpoints.
- `chat/` - SSE chat proxy endpoints.

Routers should stay thin: read request input, call a controller object from
`app.state`, and return the result.
