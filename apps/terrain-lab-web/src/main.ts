import {Cartesian3,Viewer} from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';
import {loadLocalGeoJson} from './bridge';
import './style.css';

// By default no Cesium ion credentials or external provider requests are configured.
// Terrain is the Cesium ellipsoid, NOT terrain measurements. Never infer height from it.
const viewer=new Viewer('cesiumRoot',{
 baseLayer:false,baseLayerPicker:false,geocoder:false,homeButton:false,
 sceneModePicker:true,animation:true,timeline:true,
 infoBox:false,selectionIndicator:false,navigationHelpButton:false,
 requestRenderMode:true,shadows:false
});
function reset():void{
  // DEMONSTRATION viewport; not an event route and not field-verified.
  viewer.camera.setView({destination:Cartesian3.fromDegrees(115.2,-8.6,65000)});
  viewer.scene.requestRender();
}
reset();
const status=document.querySelector<HTMLOutputElement>('#status')!;
const file=document.querySelector<HTMLInputElement>('#geojsonFile')!;
file.addEventListener('change',async()=>{
  if(!file.files?.[0])return;
  status.textContent='Memeriksa GeoJSON lokal...';
  try{await loadLocalGeoJson(viewer,file.files[0]);status.textContent='GeoJSON visual-only dimuat (belum diverifikasi untuk RouteRevision).';}
  catch(err){status.textContent=`Gagal memuat: ${String(err instanceof Error?err.message:err)}`;}
  file.value='';
});
document.querySelector<HTMLButtonElement>('#cameraReset')!.addEventListener('click',reset);
document.querySelector<HTMLButtonElement>('#clearVisuals')!.addEventListener('click',()=>{
 viewer.dataSources.removeAll(true);viewer.entities.removeAll();status.textContent='Layer analitis dibersihkan. Tidak ada RouteRevision diubah.';viewer.scene.requestRender();
});
window.addEventListener('beforeunload',()=>viewer.destroy(),{once:true});
