import {defineConfig} from 'vite';
import {viteStaticCopy} from 'vite-plugin-static-copy';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const cesiumBaseUrl='cesiumStatic';
const source=path.resolve(fileURLToPath(new URL('.',import.meta.url)),'node_modules/cesium/Build/Cesium');
export default defineConfig({
  define:{CESIUM_BASE_URL:JSON.stringify(`/${cesiumBaseUrl}`)},
  plugins:[viteStaticCopy({targets:[
    {src:path.join(source,'Assets'),dest:cesiumBaseUrl},
    {src:path.join(source,'ThirdParty'),dest:cesiumBaseUrl},
    {src:path.join(source,'Workers'),dest:cesiumBaseUrl},
    {src:path.join(source,'Widgets'),dest:cesiumBaseUrl}
  ]})],
  server:{host:'127.0.0.1'},
});
