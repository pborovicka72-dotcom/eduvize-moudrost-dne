import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root=new URL('../',import.meta.url);
const presentation={mode:'web',geometry:null,interaction:'display',kioskLayout:null};
const native={schemaVersion:1,values:{audience:'all',dailyCount:'2',authorRepeat:'avoid',showSourceLink:false,outputType:'web'},segment:null,topics:[],authors:[],presentation};
let form=structuredClone(native),stored=structuredClone(native),auth={connected:true,schoolId:'school-a',profileId:'b'.repeat(32)},token='test-only',mounted,refreshes=0,profileReads=0;
const nodes=new Map();const node=()=>({textContent:'',addEventListener(){}});
const document={getElementById:id=>{if(!nodes.has(id))nodes.set(id,node());return nodes.get(id);},querySelector:()=>node(),addEventListener(){}};
const client={};
const window={document,location:{href:'https://test.skola.eduvize.cz/eduvize-moudrost-dne/config.html'},eduvizeWisdomOutputUrl:()=>('https://test.skola.eduvize.cz/eduvize-moudrost-dne/index.html?audience='+form.values.audience),dispatchEvent(){},addEventListener(){},requestAnimationFrame:fn=>fn(),EduvizeAdminAuth:{ready:Promise.resolve(),status:()=>auth,getToken:()=>token},
 EduvizeProfiles:{request:async(path,options)=>{assert.equal(options.fresh,true);assert.equal(path,'/'+auth.profileId);profileReads++;return {id:auth.profileId,revision:4,apps:{wisdom:{config:structuredClone(stored)}}};}},
 EduvizeOutputModes:{selection:()=>form.presentation.interaction,layoutSelection:()=>form.presentation.kioskLayout,setInteraction(){},setKioskLayout(){}},
 EduvizeOutputClient:{create:opts=>{assert.equal(opts.getAuthorization(),'Bearer test-only');return client;}},
 EduvizeOutputActions:{canonicalSlot:p=>{assert.ok(['web','nsp','kiosk'].includes(p.mode));return JSON.stringify([p.mode,p.geometry]);},mount:opts=>{mounted=opts;return {workflow:'saved-copy-preview',withSavedCommit(){},refresh:async()=>{refreshes++;}};}}
};
const ctx=vm.createContext({window,document,structuredClone,Error,Object,Array,Number,JSON,URL,Event:class{constructor(type){this.type=type;}}});
for(const f of ['assets/settings.js','assets/load-saved-app.js','assets/output-adapter.js','assets/output-controls.js'])vm.runInContext(fs.readFileSync(new URL(f,root),'utf8'),ctx);
const adapter={app:'wisdom',ready:Promise.resolve(),read:()=>structuredClone(form),apply:async v=>{form=structuredClone(v);}};
await window.EduvizeWisdomOutputControls.install(adapter);
assert.equal(refreshes,1);assert.equal(mounted.client,client);
assert.deepEqual(Object.keys(mounted.context()).sort(),['appId','presentation','profileId','schoolId']);
assert.equal(adapter.outputActions.workflow,'saved-copy-preview');assert.equal(mounted.workflow,'saved-copy-preview');assert.equal(mounted.elements.generateButton,undefined);
assert.equal(mounted.resolve,undefined);assert.equal(mounted.context().slotId,undefined);
// Normal Save still reads the native config; no registry action or profile read.
const readsBeforeSave=profileReads,refreshBeforeSave=refreshes;
const toSave=adapter.read();assert.equal(toSave.values.audience,'all');assert.deepEqual(JSON.parse(JSON.stringify(toSave.presentation)),presentation);
assert.equal(toSave.data,undefined);assert.equal(profileReads,readsBeforeSave);assert.equal(refreshes,refreshBeforeSave);
// Unsaved form edits must never become a published payload.
form.values.audience='secondary';
let draft=await mounted.draft({savedCommit:null});assert.equal(draft.payload.audience,'all');assert.equal(profileReads,1);
const readsBeforeCommit=profileReads;const committed=structuredClone(native);committed.values.audience='primary';
const exact=await mounted.draft({savedCommit:{profileId:auth.profileId,appId:'wisdom',revision:5,config:committed}});assert.equal(exact.payload.audience,'primary');assert.equal(profileReads,readsBeforeCommit);
assert.match(await mounted.previewDraftUrl(),/audience=secondary/);assert.match(await mounted.previewDraftUrl(),/preview=1/);assert.equal(profileReads,readsBeforeCommit);
stored.values.audience='primary';draft=await mounted.draft();assert.equal(draft.payload.audience,'primary');assert.equal(profileReads,2);
// Restore through the shared API before native apply, then read actual dimensions.
const kioskConfig=structuredClone(native);
kioskConfig.values.outputType='kiosk';
kioskConfig.presentation={mode:'kiosk',interaction:'interactive',kioskLayout:'menu',geometry:{registryId:'kiosk-viewport',registryVersion:1,orientation:'portrait',width:2160,height:3840}};
let geometry=null,calledBeforeNative=false;
window.EduvizeSegmentSelection={setKioskGeometry:value=>{calledBeforeNative=form.values.outputType==='web';geometry=value;return true;}};
const query=document.querySelector;
document.querySelector=selector=>selector.includes('kiosk-preview iframe')?{getAttribute:key=>String(key==='data-preview-width'?geometry.width:geometry.height)}:query(selector);
await adapter.apply(kioskConfig);assert.equal(calledBeforeNative,true);
assert.equal(adapter.read().presentation.geometry.height,3840);
assert.equal(adapter.read().presentation.geometry.orientation,'portrait');
window.EduvizeSegmentSelection.setKioskGeometry=()=>false;
await assert.rejects(adapter.apply(kioskConfig),/obnovit/);
form=structuredClone(native);document.querySelector=query;
stored={...stored,empty:true};await assert.rejects(mounted.draft(),/uložte|nastavení/i);
stored=structuredClone(native);delete stored.presentation;await assert.rejects(mounted.draft(),/uložte/i);
stored=structuredClone(native);form.presentation.interaction='interactive';await assert.rejects(mounted.draft(),/uložte/i);
form=structuredClone(native);token='';await assert.rejects(mounted.draft(),/Přihlaste/);
token='test-only';const request=window.EduvizeProfiles.request;
window.EduvizeProfiles.request=async(...args)=>{const value=await request(...args);auth={...auth,profileId:'c'.repeat(32)};return value;};
await assert.rejects(mounted.draft(),/profil|účet/i);
assert.equal(adapter.recovery,undefined);
assert.equal(window.EduvizeWisdomRecovery,undefined);
console.log('Wisdom saved-copy-preview: exact Save commit, fresh first Copy, unsaved draft preview, NO recovery registration and guards PASS');
