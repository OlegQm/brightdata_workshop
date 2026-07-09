#!/bin/bash
# Download Natural Earth 10m countries and extract CZ+SK boundary as GeoJSON.
# Uses ogr2ogr (GDAL) - no Python dependencies needed.
# Output: /data/czsk_boundary.geojson (or $1 if provided).
set -e

OUTPUT="${1:-/data/czsk_boundary.geojson}"

if [ -f "$OUTPUT" ]; then
  echo "==> $OUTPUT already exists, skipping."
  exit 0
fi

NE_URL="https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip"
TMP_ZIP="/tmp/ne_countries.zip"
TMP_DIR="/tmp/ne_countries"
TMP_RAW="/tmp/czsk_raw.geojson"

echo "==> Downloading Natural Earth 10m countries..."
python3 -c "import urllib.request; urllib.request.urlretrieve('$NE_URL', '$TMP_ZIP')"

echo "==> Extracting archive..."
mkdir -p "$TMP_DIR"
python3 -c "import zipfile; zipfile.ZipFile('$TMP_ZIP').extractall('$TMP_DIR')"

SHP=$(find "$TMP_DIR" -name '*.shp' | head -1)
if [ -z "$SHP" ]; then
  echo "ERROR: No .shp file found in archive" >&2
  exit 1
fi

echo "==> Extracting CZ+SK from $SHP ..."
ogr2ogr -f GeoJSON "$TMP_RAW" "$SHP" \
  -where "ISO_A2 IN ('CZ','SK') OR ISO_A2_EH IN ('CZ','SK')" \
  -makevalid

LAYER_NAME=$(ogrinfo -al -so "$TMP_RAW" | grep 'Layer name:' | head -1 | sed 's/Layer name: //')
echo "==> Dissolving and fixing topology (layer: $LAYER_NAME)..."
mkdir -p "$(dirname "$OUTPUT")"
ogr2ogr -f GeoJSON "$OUTPUT" "$TMP_RAW" \
  -dialect SQLite \
  -sql "SELECT ST_Union(ST_Buffer(geometry, 0)) AS geometry FROM \"$LAYER_NAME\""

rm -rf "$TMP_ZIP" "$TMP_DIR" "$TMP_RAW"

SIZE=$(du -k "$OUTPUT" | cut -f1)
echo "==> Done: $OUTPUT (${SIZE} KB)"
