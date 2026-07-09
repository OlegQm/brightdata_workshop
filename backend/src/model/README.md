# Backend Models

Pydantic models returned by backend endpoints and passed through services.

Files:

- `hotel.py` - normalized hotel response shape.
- `refresh.py` - BrightData refresh result shape.

Update these models when changing API responses; then update frontend consumers
and documentation at the same time.
