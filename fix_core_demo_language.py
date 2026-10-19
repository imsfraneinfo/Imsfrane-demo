"""Fix a real runtime language regression in the Demo's copied core.min.js.

Original site's getPageLanguage() recognizes only French or English and its
initializePageLanguage() always forces HTML direction to LTR. This *overrides*
the Arabic HTML markup on DOMContentLoaded, so Arabic-only CSS cannot match.

Create a NEW multilingual JS asset; retain the original core.min.js untouched
for existing FR and EN pages. Only AR and ES page script URLs are replaced.
"""
from pathlib import Path
import re

DEST="core-multilingual-v2.js"
def patch(root:Path):
    src=root/"js"/"core.min.js"
    if not src.is_file():raise RuntimeError("Original shared JavaScript not found")
    data=src.read_text(encoding="utf-8")
    original='return (htmlElement.getAttribute("lang") || body.getAttribute("data-lang") || "en").toLowerCase().startsWith("fr") ? "fr" : "en";'
    replacement='''const rawLanguage = (htmlElement.getAttribute("lang") || body.getAttribute("data-lang") || "en").toLowerCase().split("-")[0];
return ["fr","en","ar","es"].includes(rawLanguage) ? rawLanguage : "en";'''
    if data.count(original)!=1:raise RuntimeError("Original language detection not as expected")
    data=data.replace(original,replacement,1)
    old_dir='htmlElement.setAttribute("dir", "ltr");'
    new_dir='htmlElement.setAttribute("dir", language === "ar" ? "rtl" : "ltr");'
    if data.count(old_dir)!=1:raise RuntimeError("Original RTL reset not as expected")
    data=data.replace(old_dir,new_dir,1)
    # AR/ES-specific accessible button labels, while FR/EN labels remain as before.
    data=data.replace(
      'if (menuButton) menuButton.setAttribute("aria-label", language === "fr" ? "Ouvrir le menu de navigation" : "Open navigation menu");',
      'if (menuButton) menuButton.setAttribute("aria-label", language === "fr" ? "Ouvrir le menu de navigation" : language === "ar" ? "افتح قائمة التنقل" : language === "es" ? "Abrir el menú de navegación" : "Open navigation menu");',
      1)
    dest=root/"js"/DEST
    dest.write_text(data,encoding="utf-8")
    if src.read_text(encoding="utf-8") == data:
        raise RuntimeError("Attempted to change original core JS in place")
    for lang in ("ar","es"):
        pages=sorted((root/lang).glob("*.html"))
        if len(pages)<44:raise RuntimeError("Missing localized page before core fix")
        count=0
        for page in pages:
            s=page.read_text(encoding="utf-8")
            old='src="../js/core.min.js"'
            new='src="../js/'+DEST+'"'
            if s.count(old)>1:
                raise RuntimeError("Unexpected duplicate original core JS on "+str(page))
            # Independent editorial articles have no original core JS.
            # Their correct lang=ar dir=rtl markup remains untouched.
            if s.count(old)==1:
                page.write_text(s.replace(old,new,1),encoding="utf-8")
                count+=1
        if count<15:
            raise RuntimeError("Expected original core JS on each primary page")
        print("[LANGUAGE BUG FIX]",lang,count,"core-using pages fixed; independent articles preserved")
    for lang in ("fr","en"):
        # The original two languages still load exactly the original file.
        if any(DEST in p.read_text(encoding="utf-8") for p in (root/lang).glob("*.html")):
            raise RuntimeError("Original FR EN JavaScript must stay unchanged")
    print("[LANGUAGE BUG FIX] core no longer overwrites Arabic lang=ar dir=rtl after DOMContentLoaded")

if __name__=="__main__":
    patch(Path("public"))
