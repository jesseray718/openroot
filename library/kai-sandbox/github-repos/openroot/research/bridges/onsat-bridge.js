'use strict';
const fs = require('fs');
const args = process.argv.slice(2);
function getArg(flag, def) { const i=args.indexOf(flag); return i!==-1?args[i+1]:def; }
const LAT=parseFloat(getArg('--lat','36.8767')), LON=parseFloat(getArg('--lon','-89.5882')), RADIUS=parseInt(getArg('--radius','200')), OUTFILE=getArg('--output','onsat-data.json');
const STREAMS=[
  {id:'soil_moisture',    name:'Soil Moisture',          fullerE:9.6, thermalUse:'labyrinth siting',        waterUse:'CRITICAL'},
  {id:'solar_irradiance', name:'Solar Irradiance',       fullerE:9.1, thermalUse:'CRITICAL — panel angle',  waterUse:'LOW'},
  {id:'ground_temp',      name:'Ground Temperature',     fullerE:8.8, thermalUse:'CRITICAL — 35F depth',    waterUse:'MEDIUM'},
  {id:'crop_stress',      name:'Crop Stress NDVI',       fullerE:8.3, thermalUse:'LOW',                     waterUse:'HIGH'},
  {id:'humidity',         name:'Humidity & Rainfall',    fullerE:7.9, thermalUse:'HIGH — desiccant sizing', waterUse:'HIGH'},
  {id:'night_cooling',    name:'Night-Sky Cooling Index',fullerE:7.4, thermalUse:'HIGH — Cold Tank B lid',  waterUse:'MEDIUM'},
];
console.log(`\nOPENROOT × ONSAT  ${LAT}, ${LON}  radius: ${RADIUS}km\n`);
const results=STREAMS.map(s=>{
  const url=`https://www.onsat.com/api/${s.id}?lat=${LAT}&lon=${LON}&radius_km=${RADIUS}`;
  console.log(`[Ε${s.fullerE}] ${s.name}\n  ${url}\n  Thermal: ${s.thermalUse} | Water: ${s.waterUse}\n`);
  return {...s, url, status:'url_generated — add onsat auth token', lat:LAT, lon:LON};
});
const out={generated:new Date().toISOString(), operator:'jesseray718/Sikeston MO/Node Zero', location:{lat:LAT,lon:LON,radiusKm:RADIUS}, thermalHardConstraints:{wetCure:'21 days minimum',desiccant:'intake — before labyrinth',tunnel:'FILLED SOLID aerocement',tanks:'TWO: A=hot, B=cold',noClaim:'Never >100% thermodynamic efficiency'}, streams:results, nextStep:'onsat.com account → auth token → paste responses here'};
fs.writeFileSync(OUTFILE, JSON.stringify(out,null,2));
console.log(`✓ ${OUTFILE}\n  One pour. One node. One warrior at a time.\n`);
