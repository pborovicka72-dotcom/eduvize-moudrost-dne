/* Payload getter for the shared output-actions owner; no mutation, resolver or UI. */
(function(root){'use strict';
 async function draft(presentation){
  const adapter=root.EduvizeProfileAdapter;
  if(adapter?.app!=='wisdom'||typeof adapter.read!=='function'||typeof adapter.validate!=='function')throw Error('Nastavení Moudrosti dne není připravené.');
  await adapter.ready;await adapter.validate();
  if(root.EduvizeProfileAdapter!==adapter)throw Error('Školní profil se změnil. Načtěte nastavení znovu.');
  const config=adapter.read(),v=config.values;
  return {schemaVersion:1,payloadVersion:1,presentation:structuredClone(presentation),payload:{
   audience:v.audience,dailyCount:Number(v.dailyCount),authorRepeat:v.authorRepeat,
   showSourceLink:v.showSourceLink,topics:[...config.topics],authors:[...config.authors]
  }};
 }
 root.EduvizeWisdomOutputAdapter=Object.freeze({appId:'wisdom',draft});
})(window);
