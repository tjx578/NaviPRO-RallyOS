import {Cartesian3,Color,GeoJsonDataSource,Viewer,Cesium3DTileset, CesiumTerrainProvider} from 'cesium';
import {allowlistedAssetUrl} from './provider-policy';

// Visualization DTO: never writable to canonical RouteRevision.
export type GeoPointE7={lat_e7:number;lon_e7:number};
export type RouteVisualOverlay={route_revision_id:string;status:'CONFIRMED_READONLY'|'CANDIDATE';ordered_points:readonly GeoPointE7[]};
export type AssetManifest={asset_id:string;kind:'CESIUM_3D_TILES'|'TERRAIN_MESH';provider_id:string;source_sha256:string;url:string;license_ref:string|null};

function checkPoint(p:GeoPointE7):void {
  if(!Number.isInteger(p.lat_e7)||!Number.isInteger(p.lon_e7)||Math.abs(p.lat_e7)>900000000||Math.abs(p.lon_e7)>1800000000)throw new Error('Invalid GeoPointE7');
}
export function addRouteVisualOverlay(viewer:Viewer,route:RouteVisualOverlay):void {
  if(!route.route_revision_id || route.ordered_points.length<2)throw new Error('Route visualization needs a revision and >=2 points');
  const flat:number[]=[];
  route.ordered_points.forEach(p=>{checkPoint(p);flat.push(p.lon_e7/1e7,p.lat_e7/1e7);});
  viewer.entities.add({id:`route-visual-${route.route_revision_id}-${route.status}`,
    name:`Visual only: ${route.route_revision_id}`,
    polyline:{positions:Cartesian3.fromDegreesArray(flat),width:4,material:route.status==='CONFIRMED_READONLY'?Color.CYAN:Color.ORANGE,clampToGround:false}});
  viewer.scene.requestRender();
}
export async function loadLocalGeoJson(viewer:Viewer,file:File):Promise<void>{
  if(file.size>20_000_000)throw new Error('Demo ingest cap 20MB; large datasets need separate tile pipeline');
  if(!/\.(geojson|json)$/i.test(file.name))throw new Error('File must be GeoJSON/JSON');
  const contents=await file.text();
  const data=JSON.parse(contents) as {type?:string};
  if(!['Feature','FeatureCollection'].includes(data?.type??''))throw new Error('Unsupported JSON: expected GeoJSON Feature or FeatureCollection');
  const layer=await GeoJsonDataSource.load(data,{clampToGround:false});
  await viewer.dataSources.add(layer);
  await viewer.flyTo(layer);
  viewer.scene.requestRender();
}
export async function addApproved3DTiles(viewer:Viewer,asset:AssetManifest,allowOrigins:string[]=[]):Promise<void>{
  if(asset.kind!=='CESIUM_3D_TILES'||!asset.asset_id||!asset.provider_id||!asset.license_ref||!/^[a-f\d]{64}$/i.test(asset.source_sha256))throw new Error('Asset manifest missing provenance/rights');
  const tileset=await Cesium3DTileset.fromUrl(allowlistedAssetUrl(asset.url,allowOrigins));
  viewer.scene.primitives.add(tileset);
  await viewer.zoomTo(tileset);
}
export async function attachApprovedTerrain(viewer:Viewer,asset:AssetManifest,allowOrigins:string[]=[]):Promise<void>{
  if(asset.kind!=='TERRAIN_MESH'||!asset.provider_id||!asset.license_ref||!/^[a-f\d]{64}$/i.test(asset.source_sha256))throw new Error('Terrain manifest missing provenance/rights');
  viewer.terrainProvider=await CesiumTerrainProvider.fromUrl(allowlistedAssetUrl(asset.url,allowOrigins));
  // Terrain heights remain analytic only and must carry a separately declared vertical datum.
  viewer.scene.requestRender();
}
