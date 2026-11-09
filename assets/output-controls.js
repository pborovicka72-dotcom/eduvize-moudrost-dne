/* Ordinary Wisdom controls over frozen shared OutputActions V2. No local resolver. */
(function(root){'use strict';
 const canonical=value=>JSON.stringify(value,(_,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b))):v);
 root.EduvizeWisdomManagedOutput=true;
 root.EduvizeWisdomSavedWorkflow=true;
 const error=(code,message)=>{throw Object.assign(new Error(message),{code});};
 function presentation(config){
  const mode=config.values.outputType;
  const interaction=root.EduvizeOutputModes.selection();
  if(!['display','interactive'].includes(interaction))error('INVALID_PRESENTATION','Vyberte způsob ovládání výstupu.');
  let geometry=null,kioskLayout=null;
  if(mode==='nsp'){
   const segment=config.segment;
   geometry={registryId:'nsp-4k',registryVersion:1,orientation:segment?.orientation,layoutId:Number(segment?.style),segmentId:Number(segment?.block)};
  }else if(mode==='kiosk'){
   const frame=document.querySelector('.kiosk-preview iframe[data-preview-width][data-preview-height]');
   const width=Number(frame?.getAttribute('data-preview-width')),height=Number(frame?.getAttribute('data-preview-height'));
   if(!Number.isInteger(width)||!Number.isInteger(height)||width<240||height<240)error('INVALID_PRESENTATION','Počkejte na načtení rozměrů náhledu kiosku.');
   geometry={registryId:'kiosk-viewport',registryVersion:1,orientation:height>width?'portrait':'landscape',width,height};
   kioskLayout=root.EduvizeOutputModes.layoutSelection();
  }else if(mode!=='web')error('INVALID_PRESENTATION','Vyberte platný režim výstupu.');
  const result={mode,geometry,interaction,kioskLayout};
  root.EduvizeOutputActions.canonicalSlot(result);
  return result;
 }
 function install(adapter){
  if(adapter.app!=='wisdom')throw Error('Wrong Wisdom adapter');
  const nativeRead=adapter.read.bind(adapter),nativeApply=adapter.apply.bind(adapter);
  // Ordinary cloud Save persists the complete native configuration + Presentation.
  // It remains owned by the existing profile controller and never calls registry.
  adapter.read=()=>{const config=nativeRead();return {...config,presentation:presentation(config)};};
  adapter.apply=async config=>{
   const p=config.presentation;
   if(p){
    if(p.mode!==config.values.outputType||!['display','interactive'].includes(p.interaction))error('INVALID_PRESENTATION','Uložený režim výstupu neodpovídá nastavení.');
    root.EduvizeOutputActions.canonicalSlot(p);
    if(p.mode==='kiosk'){
     if(!['menu','tiles'].includes(p.kioskLayout))error('INVALID_PRESENTATION','Neplatné rozložení kiosku.');
     const {width,height,orientation}=p.geometry;
     if(root.EduvizeSegmentSelection?.setKioskGeometry?.({width,height,orientation})!==true)error('DEPENDENCY_UNAVAILABLE','Rozměry uloženého kiosku se nepodařilo obnovit.');
    }
   }
   // Shared setter retains kiosk geometry across the native mode/preview refresh.
   await nativeApply(config);
   if(p){
    root.EduvizeOutputModes.setInteraction(p.interaction,{notify:false});
    if(p.mode==='kiosk')root.EduvizeOutputModes.setKioskLayout(p.kioskLayout,{notify:false});
   }
  };
  async function start(){
   await adapter.ready;await root.EduvizeAdminAuth.ready;
   const status=document.getElementById('outputStatus');
   const client=root.EduvizeOutputClient.create({getAuthorization:()=>{
    const token=root.EduvizeAdminAuth.getToken('configurations')||root.EduvizeAdminAuth.getToken('documents');
    return token?'Bearer '+token:null;
   }});
   const saved=root.EduvizeSavedOutputSettings.create();
   const context=()=>{
    const auth=root.EduvizeAdminAuth.status();
    if(!auth?.connected||!auth.schoolId||!/^[a-f0-9]{32}$/.test(auth.profileId||''))error('CONTEXT_REQUIRED','Přihlaste se ke škole a vyberte uložený profil.');
    return {schoolId:String(auth.schoolId),profileId:auth.profileId,appId:'wisdom',presentation:presentation(nativeRead())};
   };
   const controls=root.EduvizeOutputActions.mount({client,context,workflow:'saved-copy-preview',
    draft:async({savedCommit}={})=>{
     const before=context();
     if(savedCommit&&(savedCommit.profileId!==before.profileId||savedCommit.appId!==before.appId||!Number.isSafeInteger(savedCommit.revision)||savedCommit.revision<0))error('INVALID_SAVED_COMMIT','Nelze ověřit uložené nastavení.');
     const config=savedCommit?structuredClone(savedCommit.config):(await saved.load(before)).config;
     const after=context();
     if(JSON.stringify(before)!==JSON.stringify(after))error('CONTEXT_CHANGED','Školní profil nebo výstup se během načítání změnil.');
     if(!config.presentation||canonical(config.presentation)!==canonical(before.presentation))error('SETTINGS_REQUIRED','Nejprve uložte nastavení a vybraný režim výstupu do Eduvize.');
     return root.EduvizeWisdomOutputAdapter.fromSaved(config,before.presentation);
    },
    previewDraftUrl:()=>{const url=new URL(root.eduvizeWisdomOutputUrl(),root.location.href);url.searchParams.set('preview','1');return url.href;},
    elements:{copyButton:document.getElementById('copyOutput'),openButton:document.getElementById('openOutput'),status}
   });
   adapter.outputActions=controls;
   adapter.recovery={read:()=>{const value=nativeRead();let pending=null;try{pending=presentation(value);}catch(e){if(!['INVALID_PRESENTATION','INVALID_GEOMETRY'].includes(e.code))throw e;}return root.EduvizeWisdomRecovery.clean({...value,presentation:pending});},apply:async value=>{const config=root.EduvizeWisdomRecovery.clean(value);await adapter.apply(config);return {presentationPending:config.presentation===null};},clean:root.EduvizeWisdomRecovery.clean};
   const local=document.getElementById('saveLocal');if(local)local.hidden=true;
   const cloudSave=document.querySelector('[data-edu-profile-save]');if(cloudSave)cloudSave.textContent='Uložit nastavení';
   document.addEventListener('click',event=>{if(event.isTrusted&&event.target.closest('#allTopics,#noneTopics,#allAuthors,#noneAuthors'))document.dispatchEvent(new Event('eduvize-profile-change',{bubbles:true}));});
   const refresh=()=>controls.refresh().catch(e=>{status.textContent=e.message;});
   for(const type of ['change','eduvize-configuration-saved'])document.addEventListener(type,()=>{void refresh();});
   root.addEventListener('eduvize-admin-auth-change',()=>{void refresh();});
   // NSP and kiosk geometry changes are buttons; refresh after their preview update.
   document.querySelector('.edu-output-section').addEventListener('click',event=>{
    if(!event.target.closest('.edu-output-actions'))root.requestAnimationFrame(()=>{void refresh();});
   });
   root.dispatchEvent(new Event('eduvize-profile-adapter-ready'));
   await refresh();root.EduvizeWisdomOutputControls.actions=controls;
  }
  const ready=start();ready.catch(e=>{const status=document.getElementById('outputStatus');if(status)status.textContent=e.message;});
  return ready;
 }
 root.EduvizeWisdomOutputControls={install,presentation};
})(window);
