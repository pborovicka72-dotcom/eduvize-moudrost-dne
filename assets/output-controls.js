/* Ordinary Wisdom controls over frozen shared OutputActions V2. No local resolver. */
(function(root){'use strict';
 const canonical=value=>JSON.stringify(value,(_,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b))):v);
 root.EduvizeWisdomManagedOutput=true;
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
   await nativeApply(config);
   if(config.presentation){
    const p=config.presentation;
    if(p.mode!==config.values.outputType)error('INVALID_PRESENTATION','Uložený režim výstupu neodpovídá nastavení.');
    root.EduvizeOutputActions.canonicalSlot(p);
    root.EduvizeOutputModes.setInteraction(p.interaction,{notify:false});
    if(p.mode==='kiosk')root.EduvizeOutputModes.setKioskLayout(p.kioskLayout,{notify:false});
    // The preview is mounted at the saved canonical dimensions, not an old cache.
    if(p.mode==='kiosk'){
     const frame=document.querySelector('.kiosk-preview iframe');
     if(!frame)error('DEPENDENCY_UNAVAILABLE','Náhled kiosku není připravený.');
     root.EduvizePreviewViewport.mount(frame,{host:frame.parentElement,width:p.geometry.width,height:p.geometry.height});
    }
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
   const controls=root.EduvizeOutputActions.mount({client,context,
    draft:async()=>{
     const before=context(),record=await saved.load(before),config=record.config;
     const after=context();
     if(JSON.stringify(before)!==JSON.stringify(after))error('CONTEXT_CHANGED','Školní profil nebo výstup se během načítání změnil.');
     if(!config.presentation||canonical(config.presentation)!==canonical(before.presentation))error('SETTINGS_REQUIRED','Nejprve uložte nastavení a vybraný režim výstupu do Eduvize.');
     return root.EduvizeWisdomOutputAdapter.fromSaved(config,before.presentation);
    },
    elements:{generateButton:document.getElementById('generateOutput'),copyButton:document.getElementById('copyOutput'),openButton:document.getElementById('openOutput'),status}
   });
   const refresh=()=>controls.refresh().catch(e=>{status.textContent=e.message;});
   for(const type of ['change','eduvize-configuration-saved'])document.addEventListener(type,()=>{void refresh();});
   root.addEventListener('eduvize-admin-auth-change',()=>{void refresh();});
   // NSP and kiosk geometry changes are buttons; refresh after their preview update.
   document.querySelector('.edu-output-section').addEventListener('click',event=>{
    if(!event.target.closest('.edu-output-actions'))root.requestAnimationFrame(()=>{void refresh();});
   });
   await refresh();root.EduvizeWisdomOutputControls.actions=controls;
  }
  const ready=start();ready.catch(e=>{const status=document.getElementById('outputStatus');if(status)status.textContent=e.message;});
  return ready;
 }
 root.EduvizeWisdomOutputControls={install,presentation};
})(window);
