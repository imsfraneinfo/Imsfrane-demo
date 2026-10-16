/* Imsfrane image controls — editable from CloudCannon per page. */
(()=>{'use strict';
if(!document.querySelector('[data-image-control]'))return;
const settingsRoot=new URL('../image-settings/',document.currentScript.src);
const page=location.pathname.split('/').filter(Boolean);
const locale=page.findIndex(part=>/^(fr|en)$/.test(part));
const slug=locale>=0?(page[locale+1]||'index').replace(/\.html$/,''):'home';
const name=locale>=0?page[locale]+'-'+slug:'home';
const css=document.createElement('style');css.textContent='[data-image-control]{--im-x:50%;--im-y:50%;--im-z:1}img[data-image-control]{object-fit:cover!important;object-position:var(--im-x) var(--im-y)!important;transform:scale(var(--im-z));transform-origin:var(--im-x) var(--im-y)}[data-image-control]:not(img){background-position:var(--im-x) var(--im-y)!important;background-size:cover!important}';document.head.append(css);
function apply(data){for(const item of data.images||[]){const el=document.querySelector('[data-image-control="'+CSS.escape(item.id)+'"]');if(!el)continue;const x=Math.max(0,Math.min(100,Number(item.position_x)||0)),y=Math.max(0,Math.min(100,Number(item.position_y)||0)),z=Math.max(100,Math.min(200,Number(item.zoom)||100));el.style.setProperty('--im-x',x+'%');el.style.setProperty('--im-y',y+'%');el.style.setProperty('--im-z',z/100);if(item.fit==='contain'&&el.tagName==='IMG')el.style.setProperty('object-fit','contain','important');}}
fetch(new URL(encodeURIComponent(name)+'.json',settingsRoot),{cache:'no-cache'}).then(r=>r.ok?r.json():null).then(d=>{if(d)apply(d)}).catch(()=>{});
})();

