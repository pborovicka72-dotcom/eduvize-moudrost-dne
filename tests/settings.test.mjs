import {test} from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
const source=file=>readFileSync(new URL('../assets/'+file,import.meta.url),'utf8');
function environment(saved={},query=''){
 const data=new Map(Object.entries(saved)),nodes=Object.fromEntries(['display','quote','author','topic','work','sourceLink','footer'].map(k=>[k,{dataset:{},removeAttribute(){}}]));
 const window={addEventListener(){}},context={window,document:{baseURI:'https://test.skola.eduvize.cz/eduvize-moudrost-dne/index.html',getElementById:k=>nodes[k]},location:{href:'https://test.skola.eduvize.cz/eduvize-moudrost-dne/index.html'+query,search:query},localStorage:{getItem:k=>data.get(k)||null,setItem:(k,v)=>data.set(k,v)},URL,URLSearchParams,console,setInterval(){},fetch:async()=>({ok:true,json:async()=>[{id:'a',language:'cs',text:'Citát A',author:'Autor A',topic:'A'},{id:'b',language:'cs',text:'Citát B',author:'Autor B',topic:'B'}]})};
 vm.createContext(context);vm.runInContext(source('settings.js'),context);vm.runInContext(source('wisdom.js'),context);
 return {window,context,nodes,data};
}
test('public output ignores foreign local filters, including empty URL selections',async()=>{
 for(const query of ['', '?audience=all&dailyCount=1&authorRepeat=avoid&showSourceLink=0']){
  const clean=environment({},query),foreign=environment({'eduvize-wisdom-v4':JSON.stringify({topics:['missing'],authors:['missing']})},query);
  clean.window.EduvizeWisdom.initDisplay();foreign.window.EduvizeWisdom.initDisplay();await new Promise(r=>setTimeout(r,0));
  assert.equal(foreign.nodes.quote.textContent,clean.nodes.quote.textContent);assert.match(clean.nodes.quote.textContent,/Citát/);
 }
});
test('explicit URL filters still select the requested author',async()=>{
 const e=environment({},'?author=Autor+A');e.window.EduvizeWisdom.initDisplay();await new Promise(r=>setTimeout(r,0));assert.equal(e.nodes.author.textContent,'Autor A');
});
test('school/profile drafts are isolated and authenticated identity wins over query',()=>{
 const e=environment({'eduvize-wisdom-v4':JSON.stringify({topics:['legacy']})},'?edu-profile='+'c'.repeat(32));let profile='a'.repeat(32),school='b'.repeat(32);
 e.window.EduvizeAdminAuth={status:()=>({schoolId:school,profileId:profile})};const s=e.window.EduvizeWisdomSettings,k=s.storageKey();e.data.set(k,JSON.stringify({topics:['own']}));assert.equal(e.window.EduvizeWisdom.read().topics[0],'own');
 profile='d'.repeat(32);assert.notEqual(s.storageKey(),k);assert.equal(e.window.EduvizeWisdom.read().topics.length,0);assert.throws(()=>s.assertContext(k));
 school='e'.repeat(32);assert.notEqual(s.storageKey(),k);
});
test('validate the complete cloud configuration before any form mutation',()=>{
 const e=environment(),s=e.window.EduvizeWisdomSettings;e.window.EduvizeWisdomCatalog={topics:['A'],authors:['Autor A']};e.window.EduvizeNSPLayouts={layouts:{landscape:{1:[[3840,2160]]}}};
 const valid={schemaVersion:1,values:{audience:'all',dailyCount:'2',authorRepeat:'avoid',outputType:'nsp',showSourceLink:false},topics:['A'],authors:[],segment:{orientation:'landscape',style:1,block:1}};
 assert.equal(s.validate(valid),valid);
 for(const change of [{schemaVersion:2},{topics:['unknown']},{authors:['Autor A','Autor A']},{segment:{orientation:'landscape',style:999,block:1}},{values:{...valid.values,dailyCount:4}}])assert.throws(()=>s.validate({...valid,...change}));
});
