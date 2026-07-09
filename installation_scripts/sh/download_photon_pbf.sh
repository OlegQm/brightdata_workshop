#!/bin/sh
# Downloads Czech Republic and Slovakia OSM extracts from Geofabrik,
# then merges them into a single czsk.osm.pbf for Nominatim import.
set -eu

DATA_DIR=/data
CZ_PBF="$DATA_DIR/cz.osm.pbf"
SK_PBF="$DATA_DIR/sk.osm.pbf"
MERGED_PBF="$DATA_DIR/czsk.osm.pbf"

if [ -f "$MERGED_PBF" ]; then
  echo "==> $MERGED_PBF already exists, skipping."
  exit 0
fi

echo "[1/3] Downloading CZ OSM extract (~400 MB)..."
curl -fL --progress-bar \
  "https://download.geofabrik.de/europe/czech-republic-latest.osm.pbf" \
  -o "$CZ_PBF"

echo "[2/3] Downloading SK OSM extract (~80 MB)..."
curl -fL --progress-bar \
  "https://download.geofabrik.de/europe/slovakia-latest.osm.pbf" \
  -o "$SK_PBF"

echo "[3/3] Merging into czsk.osm.pbf..."
osmium merge "$CZ_PBF" "$SK_PBF" -o "$MERGED_PBF" --overwrite

rm -f "$CZ_PBF" "$SK_PBF"
echo "Done в†’ $MERGED_PBF"
