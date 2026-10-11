"""Build-time safety gate: verify all four Demo languages share navigation,
core page layout, images, and same-page language links. Never touch official.
"""
from pathlib import Path
from bs4 import BeautifulSoup
import re,sys,json

LANGUAGES=("fr","en","ar","es")
BASEPAGES=("index.html","rafting.html","camping.html","randonnee.html","vtt.html","quad.html",
"hebergement.html","programme.html","memories.html","guide.html","about.html",
"blog.html","store.html","booking.html","contact.html")

def html(root,lang,name):
    path=root/lang/name
    if not path.is_file():raise RuntimeError(f"Missing localized page: {lang}/{name}")
    return path.read_text(encoding="utf-8")

def validate(root):
    verified=0
    for name in BASEPAGES:
        fr=BeautifulSoup(html(root,"fr",name),"html.parser")
        base=fr.find("main")
        if base is None:raise RuntimeError("Main not found: fr/"+name)
        base_imgs=[img.get("src") for img in base.find_all("img") if img.get("src")]
        base_sections=len(base.find_all("section"))
        base_forms=len(base.find_all("form"))
        for lang in LANGUAGES:
            source=html(root,lang,name)
            soup=BeautifulSoup(source,"html.parser")
            main=soup.find("main")
            if main is None:raise RuntimeError(f"Missing main: {lang}/{name}")
            if len(main.find_all("section"))!=base_sections:
                raise RuntimeError(f"Original section design changed: {lang}/{name} "+
                      f"{len(main.find_all('section'))} vs {base_sections}")
            current_imgs=[img.get("src") for img in main.find_all("img") if img.get("src")]
            if current_imgs!=base_imgs:
                raise RuntimeError(f"Original main images altered: {lang}/{name}")
            if len(main.find_all("form"))!=base_forms:
                raise RuntimeError(f"Original forms altered: {lang}/{name}")
            if name=="index.html":
                if len(main.select(".hp-slide"))!=5 or len(main.select(".hp-activity-card"))!=14:
                    raise RuntimeError(f"Homepage premium hero/activities missing: {lang}")
            if name=="memories.html" and len(main.select(".memory-tile img"))!=78:
                raise RuntimeError(f"Original gallery photos missing: {lang}")
            if name=="rafting.html":
                iframe=main.select_one("#raftingExperienceFrame")
                if not iframe:raise RuntimeError(f"Original rafting iframe lost: {lang}")
                target=iframe.get("src","").replace("../","")
                if not (root/target).is_file():
                    raise RuntimeError(f"Localized rafting content missing: {lang}/{target}")
            mini=soup.select(".atnav-langmini")
            if len(mini)!=1:
                raise RuntimeError(f"Duplicate or missing language selector: {lang}/{name}: {len(mini)}")
            if soup.select(".language-switcher") or soup.select(".atnav-languages"):
                raise RuntimeError(f"Obsolete duplicate language controls: {lang}/{name}")
            options=mini[0].select(".atnav-langmini-panel a[lang]")
            if len(options)!=4 or {x.get("lang") for x in options}!=set(LANGUAGES):
                raise RuntimeError(f"Four-language dropdown missing: {lang}/{name}")
            for option in options:
                target=option.get("href","")
                expected="../"+option["lang"]+"/"+name
                if target!=expected:
                    raise RuntimeError(f"Language dropdown doesn't stay on same page: {lang}/{name}: {target}")
                if not (root/option["lang"]/name).is_file():
                    raise RuntimeError(f"Broken translated target: {lang}/{name}: {target}")
            if len(soup.select(".atnav-submenu-link"))!=6:
                raise RuntimeError(f"Activities menu must have 6 page-backed entries: {lang}/{name}")
            if lang in ("ar","es") and (soup.html.get("lang")!=lang):
                raise RuntimeError(f"Document language incorrect: {lang}/{name}")
            if lang=="ar" and soup.html.get("dir")!="rtl":
                raise RuntimeError(f"Missing Arabic RTL: {name}")
            logo=soup.select('img[src="../images/logo-104.webp"]')
            if len(logo)<2:raise RuntimeError(f"Original logo missing: {lang}/{name}")
            verified+=1
    for lang in ("ar","es"):
        full=sorted((root/lang).glob("*.html"))
        if len(full)!=44:raise RuntimeError(f"Expected 44 {lang} pages, got {len(full)}")
    print(f"[SITE LANGUAGE VALIDATION] {verified} primary page-locales passed")
    print("[SITE LANGUAGE VALIDATION] Same layouts, content image assets, 6 nav activities,")
    print("[SITE LANGUAGE VALIDATION] original logo, one 4-language dropdown and preserved routes.")
if __name__=="__main__":
    validate(Path("public"))
