# Backend Data

Runtime data mounted into the backend container at `/app/data`.

Expected files:

- `hotels_seed.json` - small seed dataset committed with the project.
- `czsk.pmtiles` - generated/downloaded vector map tiles.
- `czsk.osm.pbf` - downloaded OSM extract for Czechia and Slovakia.
- `czsk_boundary.geojson` - generated CZ/SK boundary used by the map.

Large geodata files are intentionally ignored by Git. Recreate them with:

```bash
make download-0
```

The backend exposes this directory through FastAPI static files at `/data`.
