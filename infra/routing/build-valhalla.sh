#!/bin/sh
set -eu
valhalla_build_config \
  --mjolnir-tile-dir /data/tiles \
  --mjolnir-tile-extract /data/tiles.tar \
  --mjolnir-admin /data/admins.sqlite > /data/valhalla.json
valhalla_build_admins -c /data/valhalla.json /input/admin.osm.pbf
valhalla_build_tiles -c /data/valhalla.json --concurrency 2 /input/roads.osm.pbf
valhalla_build_extract -c /data/valhalla.json -v
