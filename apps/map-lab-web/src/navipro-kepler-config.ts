import {initApplicationConfig} from '@kepler.gl/utils';

// Capability-parity baseline from tjx578/kepler.gl-_mapas_rally @ 3.3.0-alpha.11.
// PREP/REVIEW only. This config never grants route authority.
export function initNaviProMapLabCapabilities() {
  initApplicationConfig({
    enableRasterTileLayer: true,
    enableWMSLayer: true,
    enableFlowLayer: true,
    enableBitmapLayer: true,
    enableA5Layer: true,
    enableGeohashLayer: true,
    enableAnnotations: true,
    enableDrawOnMapSketches: true,
    enableMapNavigationControl: true,
    enableMapScale: true,
    enableSwipeMode: true,
    enableGlobeView: true,
    enableLayerGroups: true,
    enableThemeToggle: true,
    enableColumnStats: true,
    enableRemoteFileFormatSelector: true,
    acceptedFileFormats: [
      'csv', 'tsv', 'dsv', 'json', 'geojson', 'ndjson', 'jsonl',
      'geojsonl', 'ndgeojson', 'ldgeojson', 'kml', 'gpx', 'tcx',
      'arrow', 'feather', 'parquet'
    ],
    rasterServerUseLatestTitiler: true,
    rasterServerMaxRetries: 2,
    rasterServerRetryDelay: 500,
    rasterServerMaxPerServerRequests: 6,
    maxPitch: 75
  });
}
