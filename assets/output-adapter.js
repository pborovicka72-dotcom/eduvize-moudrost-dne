/* Strict saved native Wisdom config -> registry draft; never read unsaved form. */
(function(root){'use strict';
 const canonical=value=>JSON.stringify(value,(_,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b))):v);
 async function fromSaved(config,presentation){
  if(!config)throw Object.assign(Error('Nejprve uložte nastavení do Eduvize.'),{code:'SETTINGS_REQUIRED'});
  root.EduvizeWisdomSettings.validate(config);
  if(canonical(config.presentation)!==canonical(presentation))throw Object.assign(Error('Nejprve uložte vybraný režim výstupu do Eduvize.'),{code:'SETTINGS_REQUIRED'});
  const v=config.values;
  return {schemaVersion:1,payloadVersion:1,presentation:structuredClone(presentation),payload:{
   audience:v.audience,dailyCount:Number(v.dailyCount),authorRepeat:v.authorRepeat,
   showSourceLink:v.showSourceLink,topics:[...config.topics],authors:[...config.authors]
  }};
 }
 root.EduvizeWisdomOutputAdapter=Object.freeze({appId:'wisdom',fromSaved,draft:(presentation,config)=>fromSaved(config,presentation)});
})(window);
