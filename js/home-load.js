/* Non-critical homepage integrations follow visitor interaction. */
(function(){
 'use strict';
 let activated=false;
 function activate(){
  if(activated)return;
  activated=true;
  document.querySelectorAll('script[data-ims-ads][data-deferred-src]').forEach(placeholder=>{
   const script=document.createElement('script');
   script.async=true;
   script.crossOrigin='anonymous';
   script.src=placeholder.dataset.deferredSrc;
   placeholder.replaceWith(script);
  });
 }
 window.addEventListener('pointerdown',activate,{once:true,passive:true});
 window.addEventListener('keydown',activate,{once:true});
 window.addEventListener('scroll',activate,{once:true,passive:true});
})();
