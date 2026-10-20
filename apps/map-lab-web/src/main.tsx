import React from 'react';
import {createRoot} from 'react-dom/client';
import {Provider} from 'react-redux';
import {applyMiddleware, combineReducers, createStore} from 'redux';
import KeplerGl from '@kepler.gl/components';
import keplerGlReducer, {enhanceReduxMiddleware} from '@kepler.gl/reducers';
import {initNaviProMapLabCapabilities} from './navipro-kepler-config';

initNaviProMapLabCapabilities();

const middleware = enhanceReduxMiddleware([]);
const store = createStore(combineReducers({keplerGl: keplerGlReducer}), applyMiddleware(...middleware));

function App() {
  const width = window.innerWidth;
  const height = window.innerHeight;
  return (
    <div style={{width: '100vw', height: '100vh'}}>
      <KeplerGl id="navipro-map-lab" width={width} height={height} appName="NaviPRO Map Lab" version="REA v1" theme="dark" />
    </div>
  );
}

createRoot(document.getElementById('root')!).render(
  <React.StrictMode><Provider store={store}><App /></Provider></React.StrictMode>
);
