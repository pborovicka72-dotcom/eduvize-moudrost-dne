/* Pure native Wisdom snapshot whitelist. Scope/revision/storage/restore UI belong to Accounts. */
(function(root){'use strict';
 const choice=(value,allowed)=>{if(!allowed.includes(value))throw Error('Neplatná obnova Moudrosti dne.');return value;};
 const integer=(value,min,max)=>{if(!Number.isSafeInteger(value)||value<min||value>max)throw Error('Neplatná geometrie obnovy.');return value;};
 const list=value=>{if(!Array.isArray(value)||value.length>1000||value.some(x=>typeof x!=='string'||!x.trim()||x.length>300||/https?:\/\//i.test(x))||new Set(value).size!==value.length)throw Error('Neplatný výběr obnovy.');return [...value];};
 function clean(input){
  if(!input||input.schemaVersion!==1||!input.values)throw Error('Nepodporovaná obnova Moudrosti.');
  const v=input.values;
  if(typeof v.showSourceLink!=='boolean')throw Error('Neplatná volba zdroje.');
  const count=String(v.dailyCount);choice(count,['1','2','3']);
  const result={schemaVersion:1,values:{audience:choice(v.audience,['all','primary','secondary']),dailyCount:count,authorRepeat:choice(v.authorRepeat,['avoid','allow']),outputType:choice(v.outputType,['web','nsp','kiosk']),showSourceLink:v.showSourceLink},topics:list(input.topics),authors:list(input.authors),segment:null};
  if(input.segment){const s=input.segment;result.segment={orientation:choice(s.orientation,['landscape','portrait']),style:integer(Number(s.style),1,8),block:integer(Number(s.block),1,20)};}
  result.presentation=null;
  if(input.presentation){
   const p=input.presentation,mode=choice(p.mode,['web','nsp','kiosk']);
   if(mode!==result.values.outputType)throw Error('Nesouhlasí režim obnovy.');
   let geometry=null;
   if(mode!=='web'){
    const g=p.geometry;if(!g||g.registryVersion!==1)throw Error('Neplatná geometrie obnovy.');
    const orientation=choice(g.orientation,['landscape','portrait']);
    if(mode==='nsp')geometry={registryId:choice(g.registryId,['nsp-4k']),registryVersion:1,orientation,layoutId:integer(g.layoutId,1,8),segmentId:integer(g.segmentId,1,20)};
    else{const width=integer(g.width,240,8192),height=integer(g.height,240,8192);if((orientation==='portrait')!==(height>width))throw Error('Neplatná orientace obnovy.');geometry={registryId:choice(g.registryId,['kiosk-viewport']),registryVersion:1,orientation,width,height};}
   }else if(p.geometry!==null)throw Error('Běžná stránka nemá geometrii.');
   result.presentation={mode,geometry,interaction:choice(p.interaction,['display','interactive']),kioskLayout:mode==='kiosk'?choice(p.kioskLayout,['menu','tiles']):null};
  }
  if(input.outputInteraction!==undefined)result.outputInteraction=choice(input.outputInteraction,['display','interactive']);
  if(input.outputKioskLayout!==undefined)result.outputKioskLayout=choice(input.outputKioskLayout,['menu','tiles']);
  return result;
 }
 root.EduvizeWisdomRecovery=Object.freeze({clean});
})(window);
