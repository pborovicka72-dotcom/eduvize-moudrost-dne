/* Only the shared runtime supplies identity, publication, presentation and theme. */
(function(root){'use strict';
const $=id=>document.getElementById(id),shell=document.querySelector('.web-shell'),status=$('publication-status');
let timer=null,current=null;
function stop(){clearInterval(timer);timer=null;current=null;}
function hash(text){let h=2166136261;for(let i=0;i<text.length;i++)h=Math.imul(h^text.charCodeAt(i),16777619);return h>>>0;}
function clock(now=new Date()){
 const p=Object.fromEntries(new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Prague',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).formatToParts(now).map(x=>[x.type,x.value]));
 return {day:p.year+'-'+p.month+'-'+p.day,minutes:Number(p.hour)*60+Number(p.minute)};
}
function choose(payload,now){
 const {day,minutes}=clock(now),s=payload.settings;
 const pool=[...payload.quotes].sort((a,b)=>hash(day+'|'+a.id)-hash(day+'|'+b.id)||a.id.localeCompare(b.id));
 const count=Math.min(s.dailyCount,pool.length),quotes=[],authors=new Set();
 for(const q of pool){if(quotes.length===count)break;if(s.authorRepeat==='avoid'&&authors.has(q.author)&&pool.length>count)continue;quotes.push(q);authors.add(q.author);}
 for(const q of pool){if(quotes.length===count)break;if(!quotes.includes(q))quotes.push(q);}
 return quotes[Math.min(count-1,Math.floor(minutes/(1440/count)))];
}
function show(){
 if(!current)return;
 const q=choose(current.payload),s=current.payload.settings;
 $('quote').textContent=q.text;$('author').textContent=q.author;$('topic').textContent=q.topic;
 $('quote').dataset.length=q.text.length>300?'long':q.text.length>170?'medium':'short';
 const title=q.work_title.trim();$('work').textContent=/^(Rozhovor nebo doložený veřejný výrok|.*u zahraničních autorů český překlad)/i.test(title)?'':title;
 $('work').hidden=!$('work').textContent;
 const link=$('sourceLink');link.hidden=true;link.removeAttribute('href');
 if(s.showSourceLink&&current.presentation.interaction==='interactive'){
  try{const u=new URL(q.source_url);if(u.protocol==='https:'&&!u.username&&!u.password){link.href=u.href;link.textContent='Ověřit zdroj · '+u.hostname.replace(/^www\./,'');link.hidden=false;}}catch{}
 }
 $('footer').textContent=q.source?'Původ citátu: '+q.source:'';$('footer').hidden=!q.source;
}
function size(){
 if(!current)return;
 const {presentation:p,metrics:m}=current,html=document.documentElement;
 for(const mode of ['web','nsp','kiosk'])html.classList.toggle(mode+'-output',p.mode===mode);
 html.dataset.secondarySources=p.mode!=='web'&&(m.geometry.width/m.geometry.height>=2.7||(m.geometry.width<=1200&&m.geometry.height<=720))?'hidden':'visible';
 for(const [k,v] of Object.entries(m.header))shell.style.setProperty('--edu-header-'+k,v+'px');
 for(const [k,v] of Object.entries(m.text))shell.style.setProperty('--edu-text-'+k,v+'px');
 if(p.mode==='web'){
  for(const k of ['width','height','min-height','position','left','top','transform','transform-origin'])shell.style.removeProperty(k);
 }else{
  const w=m.geometry.width,h=m.geometry.height;
  Object.assign(shell.style,{width:w+'px',height:h+'px',minHeight:'0',position:'absolute',left:'50%',top:'50%',transform:'translate(-50%,-50%) scale('+Math.min(root.innerWidth/w,root.innerHeight/h)+')',transformOrigin:'center center'});
 }
}
function verify(payload){
 if(!payload?.settings||!Array.isArray(payload.quotes)||!payload.quotes.length||payload.quotes.length>1000||!Number.isInteger(payload.settings.dailyCount)||payload.settings.dailyCount<1||payload.settings.dailyCount>3)throw Error('Invalid Wisdom publication');
 for(const q of payload.quotes)for(const key of ['id','text','author','topic','work_title','source','source_url'])if(typeof q[key]!=='string')throw Error('Invalid quote');
}
root.addEventListener('resize',()=>{size();});
// Exposed pure selection enables deterministic timezone and rotation regression tests.
root.EduvizeWisdomPublished=Object.freeze({choose,clock});
try{root.EduvizeOutputRuntime.start({appId:'wisdom',
 render(snapshot,metrics,{signal}){
  stop();verify(snapshot.payload);if(signal.aborted)return;
  current={payload:snapshot.payload,presentation:snapshot.presentation,metrics};
  signal.addEventListener('abort',stop,{once:true});shell.hidden=false;status.hidden=true;size();show();
  timer=setInterval(()=>{if(!document.hidden)show();},60000);
 },
 clear(){stop();shell.hidden=true;for(const id of ['quote','author','topic','work','footer'])$(id).textContent='';$('sourceLink').hidden=true;$('sourceLink').removeAttribute('href');status.hidden=false;status.textContent='Výstup není dostupný.';},
 onError(){if(!current){status.hidden=false;status.textContent='Výstup se nepodařilo ověřit. Zkusíme to znovu.';}}
});}catch{stop();shell.hidden=true;status.hidden=false;status.textContent='Výstup není dostupný.';}
})(window);
