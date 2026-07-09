# Backend PostgreSQL Infrastructure

Database adapter for hotel storage.

Files:

- `pool.py` - small connection factory returning dict rows.
- `repository.py` - schema creation, seed loading, vector index creation, hotel queries and refresh updates.

The repository owns SQL. Higher layers should call repository methods instead
of opening database connections directly.
