"""Locate Arabic-only sideways shift after opening language dropdown on real mobile Chrome."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from pathlib import Path
import json,time
URL="https://imsfraneinfo.github.io/Imsfrane-demo/ar/index.html?layout-debug=20261011"
DIR=Path("arabic-layout-debug")
DIR.mkdir(exist_ok=True)
o=Options()
o.add_argument("--headless=new")
o.add_argument("--no-sandbox")
o.add_argument("--disable-dev-shm-usage")
o.add_argument("--window-size=350,850")
with webdriver.Chrome(options=o) as b:
  b.set_page_load_timeout(55)
  for width in (345,390):
    b.execute_cdp_cmd("Emulation.setDeviceMetricsOverride",{"width":width,"height":760,"deviceScaleFactor":2,"mobile":True})
    b.get(URL)
    WebDriverWait(b,30).until(lambda x:x.execute_script("return document.readyState !== 'loading' && document.querySelector('.atnav-langmini-trigger')"))
    b.execute_async_script("const done=arguments[0];document.fonts.ready.then(()=>setTimeout(done,400))")
    def snap(label):
      r=b.execute_script(r"""
      function box(sel) {
        const e=document.querySelector(sel); if (!e)return null;
        let r=e.getBoundingClientRect(),s=getComputedStyle(e);
        return {x:+r.x.toFixed(1),y:+r.y.toFixed(1),width:+r.width.toFixed(1),right:+r.right.toFixed(1),
          left:s.left,rightCss:s.right,marginL:s.marginLeft,marginR:s.marginRight,position:s.position,dir:s.direction,transform:s.transform,display:s.display};
      }
      return {rootDir:document.documentElement.dir,lang:document.documentElement.lang,
        winX:window.scrollX,winY:window.scrollY,scrollLeft:document.scrollingElement.scrollLeft,
        scrollWidth:document.documentElement.scrollWidth,bodyScrollWidth:document.body.scrollWidth,
        docWidth:document.documentElement.clientWidth,
        vv:visualViewport?{offsetLeft:visualViewport.offsetLeft,pageLeft:visualViewport.pageLeft,width:visualViewport.width}:null,
        boxes:Object.fromEntries(['html','body','#siteHeader','#siteHeader .header-inner','#siteHeader .brand',
           '#siteHeader .header-actions','.atnav-open','.atnav-langmini','.atnav-langmini-trigger',
           '.atnav-langmini-panel','main','.hp-home .hp-hero','.hp-home .hp-hero-inner',
           '.hp-home .hp-hero-content','.hp-home .hp-hero-visual','.hp-home .hp-google-reviews',
           '.atnav-drawer','.atnav-backdrop','.hp-home .hp-hero-buttons'].map(x=>[x,box(x)]))}""")
      print("STATE",label,width,json.dumps(r,ensure_ascii=False),flush=True)
      b.save_screenshot(str(DIR/(str(width)+"-"+label+".png")))
      return r
    initial=snap("initial")
    button=b.find_element("css selector",".atnav-langmini-trigger")
    button.click()
    time.sleep(.35)
    opened=snap("langmenu-open")
    # focus the Arabic link without navigating; could trigger browser horizontal auto scroll
    b.execute_script('document.querySelector(\'.atnav-langmini-panel a[lang="ar"]\').focus()')
    time.sleep(.3)
    focused=snap("langmenu-focused")
    b.execute_script('document.querySelector(".atnav-langmini-trigger").click()')
    time.sleep(.2)
    closed=snap("langmenu-closed")
    b.execute_script('document.querySelector(".atnav-open").click()')
    time.sleep(.35)
    nav=snap("nav-open")
    print("RESULT",width,"shift after menu",opened["boxes"]["main"]["x"]-initial["boxes"]["main"]["x"],
      "scroll",opened["scrollLeft"],"nav",nav["scrollLeft"],flush=True)
print("Arabic horizontal-shift diagnosis complete.")
