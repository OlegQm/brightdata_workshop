#!/bin/sh
set -eu

if [ -f /out/czsk.pmtiles ] && [ "$(stat -c%s /out/czsk.pmtiles)" -gt 1048576 ]; then
    echo "==> /out/czsk.pmtiles already exists, skipping."
    exit 0
fi

echo "==> Downloading CZ+SK OSM basemap tiles..."
pmtiles extract \
    https://data.source.coop/protomaps/openstreetmap/v4.pmtiles \
    /out/czsk.pmtiles \
    --bbox=11.8,47.7,22.6,51.2
