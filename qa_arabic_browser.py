"""Checks the actually deployed Arabic site in headless Chrome, on mobile & desktop.

Verifies fonts are decoded into real FontFace objects (not CSS declarations
with fallback fonts), fully right-to-left aligned headings/body/menu and
same-origin assets. Screenshots are uploaded by the GitHub Actions job.
"""
from pathlib import Path
from urllib.request import urlopen, Request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import json,time,os,sys

ROOT="https://imsfraneinfo.github.io/Imsfrane-demo/"
PATHS=["ar/index.html","ar/camping.html","ar/booking.html","ar/blog.html","ar/rafting.html"]
DIAGNOSTICS=Path("arabic-browser-diagnostics")
DIAGNOSTICS.mkdir(exist_ok=True)
REQ=[("fonts/arabic/Alexandria-VF.woff2","font/woff2"),
("fonts/arabic/Tajawal-Regular.woff2","font/woff2"),
("fonts/arabic/Tajawal-Bold.woff2","font/woff2"),
("arabic-pro.css?v=rtl-arabic-20261011c","text/css")]
for file,typ in REQ:
    with urlopen(Request(ROOT+file,headers={"User-Agent":"Mozilla/5.0"}),timeout=25) as r:
        content=r.read()
        ctype=r.headers.get("content-type","")
        print("NETWORK",file,r.status,len(content),ctype,flush=True)
        if r.status!=200 or len(content)<9000:raise AssertionError("Font/CSS not accessible: "+file)
        if typ=="font/woff2" and not content.startswith(b"wOF2"):
            raise AssertionError("Invalid WOFF2 font delivered for "+file)
opts=Options()
opts.add_argument("--headless=new")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-gpu")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--window-size=1400,1000")
opts.add_argument("--disable-background-networking")
opts.add_argument("--hide-scrollbars")
opts.page_load_strategy="eager"
report=[]
with webdriver.Chrome(options=opts) as driver:
    driver.set_page_load_timeout(50)
    driver.set_script_timeout(40)
    for viewport in ("mobile","desktop"):
        if viewport=="mobile":
            driver.set_window_size(390,844)
        else:driver.set_window_size(1366,900)
        for page in PATHS:
            target=ROOT+page+"?real-browser-check=1"
            driver.get(target)
            if page=="ar/rafting.html":
                # Rafting has an original iframe instead of a heading in parent.
                WebDriverWait(driver,35).until(lambda x: x.execute_script("""
                  let f=document.querySelector('#raftingExperienceFrame');
                  return !!(f && f.contentDocument && f.contentDocument.querySelector('h1'))
                """))
                child=driver.execute_async_script("""
                    let done=arguments[arguments.length-1];
                    let d=document.querySelector('#raftingExperienceFrame').contentDocument;
                    Promise.all([
                      d.fonts.load('700 32px "Imsfrane Alexandria"','مسفران'),
                      d.fonts.load('400 17px "Imsfrane Tajawal"','المغامرة')
                    ]).then(()=> {
                      let h=d.querySelector('h1'),p=d.querySelector('p');
                      done({lang:d.documentElement.lang,dir:d.documentElement.dir,
                        titleFont:getComputedStyle(h).fontFamily,
                        titleAlign:getComputedStyle(h).textAlign,
                        titleDirection:getComputedStyle(h).direction,
                        pFont:p?getComputedStyle(p).fontFamily:'',
                        realFontTitle:d.fonts.check('700 32px "Imsfrane Alexandria"','مسفران'),
                        realFontText:d.fonts.check('400 17px "Imsfrane Tajawal"','المغامرة'),
                        badgeText:d.querySelector('.hero-badge b')?.textContent.trim(),
                        badgeFont:getComputedStyle(d.querySelector('.hero-badge b')).fontFamily,
                        badgeAlign:getComputedStyle(d.querySelector('.hero-badge b')).textAlign,
                        priceText:d.querySelector('.route-price strong')?.textContent.trim(),
                        priceFont:getComputedStyle(d.querySelector('.route-price strong')).fontFamily,
                        heroPriceFont:getComputedStyle(d.querySelector('.hero-stat strong')).fontFamily,
                        expeditionPriceFont:getComputedStyle(d.querySelector('.exp-opt b')).fontFamily,
                        liveCSS:d.querySelector('link[href*="arabic-pro.css"]')?.getAttribute('href')});
                    }).catch(e=>done({error:String(e)}));
                """)
                print("RAFTING IFRAME",json.dumps(child,ensure_ascii=False),flush=True)
                driver.save_screenshot(str(DIAGNOSTICS/(viewport+"-rafting.html.png")))
                if not child or child.get("lang")!="ar" or child.get("dir")!="rtl":
                    raise AssertionError("Arabic rafting iframe is not AR/RTL")
                if not child["realFontTitle"] or not child["realFontText"]:
                    raise AssertionError("Arabic rafting iframe fonts are not decoded")
                if "Imsfrane Alexandria" not in child["titleFont"] or child["titleDirection"]!="rtl":
                    raise AssertionError("Rafting Arabic title font and direction not applied")
                for key in ("badgeFont","priceFont","heroPriceFont","expeditionPriceFont"):
                    if "Imsfrane Alexandria" not in child.get(key,""):
                        raise AssertionError("Still showing OLD serif in rafting "+key+": "+str(child))
                if "الأطلس من جهة النهر" not in child.get("badgeText",""):
                    raise AssertionError("User's rafting badge text not found")
                if "درهم" not in child.get("priceText",""):
                    raise AssertionError("User's Moroccan dirham price not found")
                if "rtl-arabic-20261011e" not in child.get("liveCSS",""):
                    raise AssertionError("Browser cached old RTL stylesheet: "+str(child))
                report.append({"viewport":viewport,"path":page,"iframe":child})
                continue
            WebDriverWait(driver,35).until(lambda x: x.execute_script("return document.readyState!=='loading' && !!document.querySelector('main h1')"))
            # Actually decode remote fonts; CSS family names alone are not proof.
            loaded=driver.execute_async_script("""
                const done=arguments[arguments.length-1];
                Promise.all([
                  document.fonts.load('700 32px "Imsfrane Alexandria"', 'مسفران'),
                  document.fonts.load('400 17px "Imsfrane Tajawal"', 'المغامرة')
                ]).then(a=>done(a.map(x=>x.map(y=>({family:y.family,status:y.status}))))).catch(e=>done({error:String(e)}));
            """)
            metrics=driver.execute_script("""
              const el=x=>document.querySelector(x);
              const sty=x=>{let e=el(x);if(!e)return null;let s=getComputedStyle(e),r=e.getBoundingClientRect();
                return {font:s.fontFamily,fontSize:s.fontSize,weight:s.fontWeight,align:s.textAlign,
                  direction:s.direction,x:Math.round(r.x),right:Math.round(r.right),width:Math.round(r.width),
                  lines:Math.round(r.height/parseFloat(s.lineHeight))||null}};
              return {
                url:location.href,htmlLang:document.documentElement.lang,htmlDir:document.documentElement.dir,
                body:sty('body'), main:sty('main'),h1:sty('main h1'),
                h2:sty('main h2'), paragraph:sty('main p'),
                nav:sty('.atnav-drawer'), navItem:sty('.atnav-drawer .atnav-item'),
                language:sty('.atnav-langmini'),
                fontReady:document.fonts.status,
                loadedTitle:document.fonts.check('700 32px "Imsfrane Alexandria"', 'مسفران'),
                loadedBody:document.fonts.check('400 17px "Imsfrane Tajawal"', 'المغامرة'),
                scrollW:document.documentElement.scrollWidth,
                viewW:document.documentElement.clientWidth
              }""")
            metrics["viewport"]=viewport;metrics["path"]=page;metrics["loadedFonts"]=loaded
            print("BROWSER",json.dumps(metrics,ensure_ascii=False),flush=True)
            report.append(metrics)
            img=DIAGNOSTICS/(viewport+"-"+page.split("/")[-1]+".png")
            driver.save_screenshot(str(img))
            if metrics["htmlDir"]!="rtl" or metrics["htmlLang"]!="ar":
                raise AssertionError("Arabic document direction missing")
            if not metrics["loadedTitle"] or not metrics["loadedBody"] or isinstance(loaded,dict):
                raise AssertionError("Arabic font failed to load in browser")
            h2=metrics["h2"] or metrics["h1"]
            if 'Imsfrane Alexandria' not in h2["font"]:
                raise AssertionError("Arabic display font not actually applied")
            if 'Imsfrane Tajawal' not in metrics["paragraph"]["font"]:
                raise AssertionError("Arabic reading font not actually applied")
            if h2["direction"]!="rtl" or h2["align"]!="right":
                raise AssertionError("Arabic headings not right-to-left")
            if metrics["main"]["direction"]!="rtl" or metrics["paragraph"]["align"]!="right":
                raise AssertionError("Arabic main text not right-to-left")
            if metrics["navItem"] and (metrics["navItem"]["direction"]!="rtl" or metrics["navItem"]["align"]!="right"):
                raise AssertionError("Arabic navigation text not right-to-left")
            if metrics["scrollW"]>metrics["viewW"]+9:
                print("WARNING horizontal overflow",page,viewport,metrics["scrollW"],metrics["viewW"],flush=True)
(DIAGNOSTICS/"measurements.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("PASS",len(report),"real Chrome rendered Arabic page/viewport combinations")
