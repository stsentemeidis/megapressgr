// Megapress Admin — front-end logic (talks to the Worker API on the same origin)
const $ = (s) => document.querySelector(s);
const api = (path, opts) => fetch(`/api/${path}`, opts).then(async r => { const j = await r.json().catch(()=>({})); if(!r.ok||j.error) throw new Error(j.error||r.status); return j; });
const esc = (s) => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const MONTHS = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];

// tabs
document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => {
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  t.classList.add('active'); $('#p-'+t.dataset.tab).classList.add('active');
}));

// year select
(function(){ const y=new Date().getFullYear(); const sel=$('#evYear'); for(let i=y+1;i>=y-1;i--){const o=document.createElement('option');o.value=i;o.textContent=i;if(i===y)o.selected=true;sel.appendChild(o);} })();

// type toggle
let evType='event';
$('#evType').querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{$('#evType').querySelectorAll('button').forEach(x=>x.classList.remove('active'));b.classList.add('active');evType=b.dataset.v;}));

// ---- tag chips ----
function chip(container, text, cls){ const c=document.createElement('span'); c.className='chip '+cls; c.innerHTML=esc(text)+(cls==='sug'?' <span class="x">✕</span>':''); if(cls==='sug') c.querySelector('.x').onclick=()=>c.remove(); container.appendChild(c); }
function evTags(){ return [...$('#chips').querySelectorAll('.chip.sug')].map(c=>c.textContent.replace('✕','').trim()); }
$('#tagInput').addEventListener('keydown',e=>{ if(e.key==='Enter'&&e.target.value.trim()){ chip($('#chips'),e.target.value.trim(),'sug'); e.target.value=''; }});
$('#suggestBtn').addEventListener('click', async function(){
  const name=$('#evName').value.trim(); if(!name) return;
  this.innerHTML='<span class="spin"></span> Searching…';
  try{ const {tags}=await api('suggest-tags',{method:'POST',body:JSON.stringify({name})}); (tags||[]).forEach(t=>chip($('#chips'),t,'sug')); }
  catch(e){}
  this.innerHTML='<span class="spark"></span> Suggest tags';
});

// ---- photo picker ----
let files=[];
$('#dz').addEventListener('click',()=>$('#fileInput').click());
$('#fileInput').addEventListener('change',e=>{ files=[...e.target.files]; const t=$('#thumbs'); t.innerHTML=''; files.forEach(f=>{const d=document.createElement('div');d.className='thumb';const img=document.createElement('img');img.src=URL.createObjectURL(f);d.appendChild(img);t.appendChild(d);}); });

$('#publishEv').addEventListener('click', async function(){
  const name=$('#evName').value.trim();
  if(!name){ setStatus('#evStatus','Enter an event name','err'); return; }
  if(!files.length){ setStatus('#evStatus','Add at least one photo','err'); return; }
  const year=parseInt($('#evYear').value,10);
  const base=evType==='exhibition'?'Exhibitions':'Events';
  const folder=`${base}/${name} ${year}`;
  this.disabled=true; setStatus('#evStatus','<span class="spin"></span> Uploading photos…');
  try{
    for(let i=0;i<files.length;i++){ setStatus('#evStatus',`<span class="spin"></span> Uploading ${i+1}/${files.length}…`); await fetch(`/api/upload?folder=${encodeURIComponent(folder)}&name=${encodeURIComponent(files[i].name)}`,{method:'POST',body:files[i]}); }
    setStatus('#evStatus','<span class="spin"></span> Publishing…');
    await api('add-event',{method:'POST',body:JSON.stringify({category:evType,year,name,shortLabel:$('#evShort').value.trim(),caption:$('#evCaption').value.trim(),extraTags:evTags(),folder,photos:files.map(f=>f.name)})});
    setStatus('#evStatus','Published — processing on the server. It appears on the site in a minute or two.','ok');
    $('#evName').value='';$('#evShort').value='';$('#evCaption').value='';$('#chips').innerHTML='';$('#thumbs').innerHTML='';files=[];
  }catch(e){ setStatus('#evStatus','Error: '+e.message,'err'); }
  this.disabled=false;
});

// ---- upcoming ----
$('#upTag').addEventListener('keydown',e=>{ if(e.key==='Enter'&&e.target.value.trim()){ chip($('#upChips'),e.target.value.trim(),'sug'); e.target.value=''; }});
function fmtLabel(start,end){ const s=new Date(start+'T00:00:00'); if(!end||end===start) return `${s.getDate()} ${MONTHS[s.getMonth()]}`; const e=new Date(end+'T00:00:00'); if(s.getMonth()===e.getMonth()) return `${s.getDate()}–${e.getDate()} ${MONTHS[s.getMonth()]}`; return `${s.getDate()} ${MONTHS[s.getMonth()]} – ${e.getDate()} ${MONTHS[e.getMonth()]}`; }
$('#publishUp').addEventListener('click', async function(){
  const name=$('#upName').value.trim(), start=$('#upStart').value;
  if(!name||!start){ setStatus('#upStatus','Enter a name and start date','err'); return; }
  const end=$('#upEnd').value||start; const year=new Date(start+'T00:00:00').getFullYear();
  const tags=[...$('#upChips').querySelectorAll('.chip.sug')].map(c=>c.textContent.replace('✕','').trim());
  this.disabled=true; setStatus('#upStatus','<span class="spin"></span> Publishing…');
  try{ await api('add-upcoming',{method:'POST',body:JSON.stringify({name,startDate:start,endDate:end,dateLabel:fmtLabel(start,end),year,extraTags:tags})}); setStatus('#upStatus','Published — live shortly.','ok'); $('#upName').value='';$('#upStart').value='';$('#upEnd').value='';$('#upChips').innerHTML=''; load(); }
  catch(e){ setStatus('#upStatus','Error: '+e.message,'err'); }
  this.disabled=false;
});

// ---- pavilions / b2b galleries ----
const GALLERY_FOLDER = { b2b:"B2B", pavInside:"Pavilions/Inside", pavOutside:"Pavilions/Outside" };
let gfiles=[];
$('#gDz').addEventListener('click',()=>$('#gFile').click());
$('#gFile').addEventListener('change',e=>{ gfiles=[...e.target.files]; const t=$('#gThumbs'); t.innerHTML=''; gfiles.forEach(f=>{const d=document.createElement('div');d.className='thumb';const img=document.createElement('img');img.src=URL.createObjectURL(f);d.appendChild(img);t.appendChild(d);}); });
$('#publishG').addEventListener('click', async function(){
  const gallery=$('#gSel').value, folder=GALLERY_FOLDER[gallery];
  if(!gfiles.length){ setStatus('#gStatus','Add at least one photo','err'); return; }
  this.disabled=true; setStatus('#gStatus','<span class="spin"></span> Uploading…');
  try{
    for(let i=0;i<gfiles.length;i++){ setStatus('#gStatus',`<span class="spin"></span> Uploading ${i+1}/${gfiles.length}…`); await fetch(`/api/upload?folder=${encodeURIComponent(folder)}&name=${encodeURIComponent(gfiles[i].name)}`,{method:'POST',body:gfiles[i]}); }
    setStatus('#gStatus','<span class="spin"></span> Publishing…');
    await api('add-gallery',{method:'POST',body:JSON.stringify({gallery,folder,photos:gfiles.map(f=>f.name)})});
    setStatus('#gStatus','Added — processing on the server. Live in a minute or two.','ok');
    $('#gThumbs').innerHTML='';gfiles=[];$('#gFile').value='';
  }catch(e){ setStatus('#gStatus','Error: '+e.message,'err'); }
  this.disabled=false;
});

// ---- monochrome logo processing (browser canvas) ----
function processLogo(file){ return new Promise((res)=>{ const img=new Image(); img.onload=()=>{ const max=200,sc=Math.min(1,max/Math.max(img.width,img.height)); const w=Math.round(img.width*sc),h=Math.round(img.height*sc); const cv=document.createElement('canvas');cv.width=w;cv.height=h;const ctx=cv.getContext('2d');ctx.drawImage(img,0,0,w,h); const d=ctx.getImageData(0,0,w,h); const px=d.data; for(let i=0;i<px.length;i+=4){ const lum=0.299*px[i]+0.587*px[i+1]+0.114*px[i+2]; let a=px[i+3]; if(a>10){ a=Math.round(a*(1-lum/255)); } px[i]=242;px[i+1]=241;px[i+2]=238;px[i+3]=a; } ctx.putImageData(d,0,0); cv.toBlob(b=>res(b),'image/png'); }; img.src=URL.createObjectURL(file); }); }

function wireLogoPicker(inputSel,dzSel,textSel,store){ $(dzSel).addEventListener('click',()=>$(inputSel).click()); $(inputSel).addEventListener('change',async e=>{ if(e.target.files[0]){ store.blob=await processLogo(e.target.files[0]); $(textSel).textContent=e.target.files[0].name+' — ready'; } }); }
const pLogo={}, cLogo={};
wireLogoPicker('#pLogo','#pDz','#pDzText',pLogo);
wireLogoPicker('#cLogo','#cDz','#cDzText',cLogo);

async function saveContact(kind, nameSel, subSel, store, statusSel, textSel){
  const name=$(nameSel).value.trim(); if(!name){ setStatus(statusSel,'Enter a name','err'); return; }
  const id=name.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/(^-|-$)/g,'');
  setStatus(statusSel,'<span class="spin"></span> Saving…');
  try{
    let logo=null;
    if(store.blob){ const r=await fetch(`/api/upload-logo?id=${encodeURIComponent(id)}`,{method:'POST',body:store.blob}); const j=await r.json(); logo=j.url; }
    await api(kind==='partner'?'save-partner':'save-client',{method:'POST',body:JSON.stringify({id,name,sub:$(subSel).value.trim(),logo,svg:null})});
    setStatus(statusSel,'Saved — live shortly.','ok'); $(nameSel).value='';$(subSel).value='';store.blob=null;$(textSel).textContent='Click to choose a logo'; load();
  }catch(e){ setStatus(statusSel,'Error: '+e.message,'err'); }
}
$('#addPartner').addEventListener('click',()=>saveContact('partner','#pName','#pSub',pLogo,'#pStatus','#pDzText'));
$('#addClient').addEventListener('click',()=>saveContact('client','#cName','#cSub',cLogo,'#cStatus','#cDzText'));

// ---- stats ----
let statsData=[];
function renderStats(){ const el=$('#statsEdit'); el.innerHTML=''; statsData.forEach((s,i)=>{ const row=document.createElement('div'); row.className='statrow'+(s.fixed?' fixed':''); const dis=s.fixed?'disabled':''; row.innerHTML=`<div><span class="mini">Number</span><input type="text" value="${esc(s.value)}" data-i="${i}" data-k="value" ${dis}></div><div><span class="mini">Unit</span><input type="text" value="${esc(s.unit)}" data-i="${i}" data-k="unit" ${dis}></div><div><span class="mini">Label</span><input type="text" value="${esc(s.label)}" data-i="${i}" data-k="label" ${dis}></div>`; el.appendChild(row); }); el.querySelectorAll('input:not([disabled])').forEach(inp=>inp.addEventListener('input',()=>{ statsData[inp.dataset.i][inp.dataset.k]=inp.value; })); }
$('#saveStats').addEventListener('click', async function(){ setStatus('#sStatus','<span class="spin"></span> Saving…'); try{ await api('save-stats',{method:'POST',body:JSON.stringify(statsData)}); setStatus('#sStatus','Saved — live shortly.','ok'); }catch(e){ setStatus('#sStatus','Error: '+e.message,'err'); } });

// ---- manage list + partners/clients lists ----
let mFilter='all', DATA={};
function renderManage(){
  const rows=[];
  (DATA.events||[]).forEach(e=>rows.push({type:e.category,label:e.category==='event'?'Event':'Exhibition',id:e.id,name:e.name,meta:`${e.category==='event'?'Event':'Exhibition'} · ${e.year}`,count:`${(e.photos||[]).length} photos`,delType:'event'}));
  (DATA.upcoming||[]).forEach(u=>rows.push({type:'upcoming',id:u.id,name:u.name,meta:`Upcoming · ${u.dateLabel||''} ${u.year||''}`,count:'—',delType:'upcoming'}));
  const el=$('#mlist'); el.innerHTML='';
  rows.filter(r=>mFilter==='all'||r.type===mFilter).forEach(r=>{ const d=document.createElement('div'); d.className='mrow'; d.innerHTML=`<span></span><div><div class="m-name">${esc(r.name)}</div><div class="m-meta">${esc(r.meta)}</div></div><div class="m-count">${r.count}</div><button class="del-btn">Delete</button>`; d.querySelector('.del-btn').addEventListener('click',async function(){ if(!confirm('Delete "'+r.name+'"? This cannot be undone.'))return; this.textContent='…'; try{ await api('delete',{method:'POST',body:JSON.stringify({type:r.delType,id:r.id})}); d.remove(); }catch(e){ this.textContent='Delete'; alert('Error: '+e.message); } }); el.appendChild(d); });
  if(!el.children.length) el.innerHTML='<p class="status">Nothing here.</p>';
}
document.querySelectorAll('.ftype').forEach(b=>b.addEventListener('click',()=>{ document.querySelectorAll('.ftype').forEach(x=>x.classList.remove('active')); b.classList.add('active'); mFilter=b.dataset.type; renderManage(); }));
function renderContacts(listSel, arr, delType){ const el=$(listSel); el.innerHTML=''; (arr||[]).forEach(x=>{ const d=document.createElement('div'); d.className='mrow'; const logo=x.logo?`<span class="plogo"><img src="${x.logo}"></span>`:(x.svg?`<span class="plogo" style="color:var(--dim)">${x.svg}</span>`:`<span class="plogo"><span>${esc((x.name||'').slice(0,3).toUpperCase())}</span></span>`); d.innerHTML=`${logo}<div><div class="m-name">${esc(x.name)}</div><div class="m-meta">${esc(x.sub||'')}</div></div><span></span><button class="del-btn">Remove</button>`; d.querySelector('.del-btn').addEventListener('click',async function(){ this.textContent='…'; try{ await api('delete',{method:'POST',body:JSON.stringify({type:delType,id:x.id})}); d.remove(); }catch(e){ this.textContent='Remove'; alert('Error: '+e.message); } }); el.appendChild(d); }); }

function setStatus(sel,msg,cls){ const el=$(sel); el.className='status'+(cls?' '+cls:''); el.innerHTML=msg; }

async function load(){ try{ DATA=await api('data',{method:'GET'}); statsData=DATA.stats||[]; renderStats(); renderManage(); renderContacts('#plist',DATA.partners,'partner'); renderContacts('#clist',DATA.clients,'client'); }catch(e){ $('#mlist').innerHTML='<p class="status err">Could not load data: '+e.message+'</p>'; } }
load();
