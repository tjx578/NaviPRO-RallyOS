# Third-party notice — Kepler.gl REA baseline

The inspected source repository `tjx578/kepler.gl-_mapas_rally` is a fork of `keplergl/kepler.gl` and reports the MIT License.

The current NaviPRO REA commit adopts architecture/capability concepts and pins package dependencies for a PREP/REVIEW Map Lab scaffold. It does not vendor the Kepler.gl source tree into NaviPRO.

If Kepler.gl source code is later copied or modified inside this repository, preserve the applicable MIT license and copyright notices in the redistributed source/binary artifacts.

## CesiumJS capability REA (Apache-2.0)

`tjx578/cesium_maps_rally` is a public fork of `CesiumGS/cesium`, licensed Apache-2.0. This project references source modules and scaffolds an optional dependency but does not vendor CesiumJS source. Future distributions of CesiumJS source/binary must preserve the applicable license and required notices. Commercial Cesium ion, photogrammetry, terrain, imagery, third-party I3S/3D Tiles providers, and downloaded datasets carry **separate** use/caching/attribution rights, not guaranteed by CesiumJS Apache license. Do not include credentials in project snapshots.

## StreetComplete REA (GPL-3.0-only) / OSM data (ODbL)

`tjx578/StreetComplete_rally-maps` is a fork of `streetcomplete/StreetComplete`; the source declares **GPL-3.0-only**. NaviPRO's REA uses *capability ideas and architecture patterns*, with independently authored Python code, schemas, tests and docs. **No StreetComplete Kotlin/source code has been copied or linked into NaviPRO.** Integrating/distributing GPL-covered code may change obligations for combined software; perform a separate compatibility/legal review before reusing any upstream implementation.

OpenStreetMap data/derivative databases are governed by **ODbL** and appropriate attribution/share-alike terms separately from StreetComplete source licensing. Tile hosts/imagery/CDN and survey photos may have independent terms. Never publish GPS traces, observation photos or OSM changesets automatically from NaviPRO's agent.
