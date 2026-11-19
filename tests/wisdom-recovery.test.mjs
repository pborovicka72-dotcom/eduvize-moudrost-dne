import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const window={};vm.runInNewContext(fs.readFileSync(new URL('../assets/wisdom-recovery.js',import.meta.url),'utf8'),{window,Error,Object,Array,Number,String,Set});
const clean=window.EduvizeWisdomRecovery.clean;
const config={schemaVersion:1,values:{audience:'all',dailyCount:'2',authorRepeat:'avoid',outputType:'nsp',showSourceLink:false,password:'DO-NOT-KEEP'},topics:['Humor'],authors:['Mark Twain'],segment:{orientation:'portrait',style:1,block:1},presentation:{mode:'nsp',interaction:'display',kioskLayout:null,geometry:{registryId:'nsp-4k',registryVersion:1,orientation:'portrait',layoutId:1,segmentId:1}},access_token:'DO-NOT-KEEP'};
const result=clean(config);assert.equal(JSON.stringify(result).includes('DO-NOT-KEEP'),false);
config.authors.push('Other');assert.equal(result.authors.length,1);
assert.equal(clean({...config,presentation:null}).presentation,null);
for(const delta of [{values:{...config.values,dailyCount:'9'}},{authors:['https://example.org/?token=private']},{topics:[{}]},{presentation:{...config.presentation,geometry:{...config.presentation.geometry,segmentId:0}}}])assert.throws(()=>clean({...config,...delta}));
for(const orientation of ['landscape','portrait']){
 const geometry={registryId:'kiosk-viewport',registryVersion:1,orientation,width:orientation==='portrait'?2160:3840,height:orientation==='portrait'?3840:2160};
 const input={...config,values:{...config.values,outputType:'kiosk'},presentation:{mode:'kiosk',geometry,interaction:'interactive',kioskLayout:'menu'}};
 assert.equal(clean(input).presentation.geometry.orientation,orientation);
 assert.throws(()=>clean({...input,presentation:{...input.presentation,geometry:{...geometry,orientation:orientation==='portrait'?'landscape':'portrait'}}}));
}
assert.equal(clean({...config,values:{...config.values,outputType:'web'},presentation:{mode:'web',geometry:null,interaction:'display',kioskLayout:null}}).presentation.geometry,null);
console.log('Wisdom pure recovery whitelist: native fields, pending geometry, credentials excluded, all modes, copied snapshots PASS');
