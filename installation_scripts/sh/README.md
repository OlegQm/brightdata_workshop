# Data Download Shell Scripts

Shell entrypoints run inside the data-download containers.

Files:

- `generate_czsk_boundary.sh` - generates `backend/data/czsk_boundary.geojson`.
- `download_czsk_tiles.sh` - downloads/builds `backend/data/czsk.pmtiles`.
- `download_photon_pbf.sh` - downloads `backend/data/czsk.osm.pbf`.

Run them through Makefile or Docker Compose rather than directly on the host,
because the scripts expect container tools and mounted paths.
