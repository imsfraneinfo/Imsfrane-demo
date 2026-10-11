"""Apply elegant Arabic-only typography on the Demo without touching any layout markup.

Appends font-loading links after the existing per-page styles on public/ar/*.html
and in the independent Arabic rafting iframe page. Does not alter main, images,
scripts, navigation, card structure, FR/EN/ES or original logo.
"""
from pathlib import Path
from html import escape
import re

URL=("https://fonts.googleapis.com/css2?"
     "family=Alexandria:wght@400;500;600;700;800"
     "&family=Tajawal:wght@400;500;600;700;800"
     "&display=swap")

def build(root:Path):
    files=sorted((root/"ar").glob("*.html"))
    if len(files)!=44:
        raise RuntimeError("Expected 44 Arabic routes before font styling")
    files.append(root/"rafting-content-ar.html")
    for file in files:
        source=file.read_text(encoding="utf-8")
        if not re.search(r'<html\b[^>]*\blang="ar"',source):
            raise RuntimeError("Arabic font attempted on a non-Arabic page: "+str(file))
        if "arabic-pro.css" in source:
            raise RuntimeError("Arabic font was inserted twice: "+str(file))
        if "</head>" not in source:
            raise RuntimeError("Cannot add font stylesheet without head: "+str(file))
        url="../arabic-pro.css" if file.parent.name=="ar" else "arabic-pro.css"
        addition=('<link href="'+escape(URL,quote=True)+'" rel="stylesheet"/>'
                  '<link href="'+url+'" rel="stylesheet"/>')
        old_main=re.search(r"<main\b[^>]*>[\s\S]*?</main>",source,re.I)
        result=source.replace("</head>",addition+"</head>",1)
        new_main=re.search(r"<main\b[^>]*>[\s\S]*?</main>",result,re.I)
        if old_main and (new_main is None or new_main.group()!=old_main.group()):
            raise RuntimeError("Arabic typography must not change page main: "+str(file))
        file.write_text(result,encoding="utf-8")
    print("[AR Font] 44 routes + original rafting content styled with Alexandria + Tajawal.")
    print("[AR Font] Main, images, original logo, links and other 3 languages unchanged.")

if __name__=="__main__":build(Path("public"))
