# Installation Scripts

Helpers for generating or downloading local map data.

Subdirectories:

- `dockerfiles/` - build environments for data download/generation jobs.
- `sh/` - shell scripts run inside those containers.

These scripts are orchestrated by `docker-compose.data-download.yml` and the
Makefile targets:

```bash
make download-0
make download-and-up
```

Generated artifacts are written to `backend/data/`.
