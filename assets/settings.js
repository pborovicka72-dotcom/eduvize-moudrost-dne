/* Local drafts only. Public displays never use this storage as configuration. */
(function(root){
 'use strict';
 const id=value=>/^[a-f0-9]{32}$/.test(value||'')?value:'';
 function context(){
  const auth=root.EduvizeAdminAuth?.status();
  // An authenticated identity wins over URL input. Neither is authorization.
  if(auth?.schoolId)return {school:id(auth.schoolId),profile:id(auth.profileId)};
  return {school:'',profile:id(new URL(location.href).searchParams.get('edu-profile'))};
 }
 function storageKey(){const c=context();return 'eduvize-wisdom-v5:'+ (c.school||'anonymous')+':'+(c.profile||'local');}
 function assertContext(key){if(key!==storageKey())throw Error('Změnil se účet nebo profil. Před uložením načtěte nastavení vybraného profilu nebo obnovte stránku.');}
 function scoped(){const c=context();return !!(c.school||c.profile);}
 function validate(config){
  if(!config||config.schemaVersion!==1)throw Error('Nepodporovaná verze nastavení Moudrosti dne.');
  const v=config.values;
  if(!v||!['all','primary','secondary'].includes(v.audience)||!['1','2','3'].includes(String(v.dailyCount))||!['avoid','allow'].includes(v.authorRepeat)||!['nsp','web','kiosk'].includes(v.outputType)||typeof v.showSourceLink!=='boolean')throw Error('Neplatné nastavení Moudrosti dne.');
  for(const field of ['topics','authors']){
   const values=config[field],catalog=root.EduvizeWisdomCatalog?.[field];
   if(!Array.isArray(values)||values.length>1000||values.some(x=>typeof x!=='string'||!x.trim()||x.length>300)||new Set(values).size!==values.length)throw Error('Neplatný výběr témat nebo autorů.');
   if(catalog&&values.some(x=>!catalog.includes(x)))throw Error('Nastavení obsahuje neznámé téma nebo autora.');
  }
  if(config.segment!==null&&config.segment!==undefined){
   const s=config.segment,layouts=root.EduvizeNSPLayouts?.layouts;
   if(!['landscape','portrait'].includes(s.orientation)||!Number.isInteger(Number(s.style))||!Number.isInteger(Number(s.block))||Number(s.style)<1||Number(s.block)<1||!layouts?.[s.orientation]?.[s.style]?.[s.block-1])throw Error('Neplatný segment Newline.');
  }
  return config;
 }
 root.EduvizeWisdomSettings=Object.freeze({storageKey,scoped,validate,assertContext});
})(window);
