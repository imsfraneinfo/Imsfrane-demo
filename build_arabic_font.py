"""Arabic-only self-hosted font and layout loader for the Demo site.

Downloads freely licensed fonts at BUILD TIME from Google Fonts' public OFL
repository, converts the source TTF to efficient WOFF2, and hosts them on the
same GitHub Pages origin. This eliminates mobile dependence on Google Fonts
network availability. Only modifies <head> of existing Arabic pages.
"""
from pathlib import Path
from html import escape
from urllib.request import Request, urlopen
from fontTools.ttLib import TTFont
import io
import re

FONT_REPOSITORY="https://raw.githubusercontent.com/google/fonts/main/ofl/"
FONTS=(
  ("Alexandria-VF.woff2", "alexandria/Alexandria%5Bwght%5D.ttf"),
  ("Tajawal-Regular.woff2","tajawal/Tajawal-Regular.ttf"),
  ("Tajawal-Medium.woff2","tajawal/Tajawal-Medium.ttf"),
  ("Tajawal-Bold.woff2","tajawal/Tajawal-Bold.ttf"),
  ("Tajawal-ExtraBold.woff2","tajawal/Tajawal-ExtraBold.ttf"),
)
VERSION="rtl-arabic-20261011d"

def download(url: str) -> bytes:
    req=Request(url,headers={"User-Agent":"Imsfrane-Demo-Build/1.0"})
    with urlopen(req,timeout=40) as response:
        return response.read()

def copy_fonts(root:Path):
    directory=root/"fonts"/"arabic"
    directory.mkdir(parents=True,exist_ok=True)
    for filename,relative in FONTS:
        ttf=download(FONT_REPOSITORY+relative)
        if not ttf.startswith((b"\x00\x01\x00\x00",b"OTTO")):
            raise RuntimeError("Downloaded Arabic font isn't a valid TTF: "+relative)
        font=TTFont(io.BytesIO(ttf))
        if filename.startswith("Alexandria") and "fvar" not in font:
            raise RuntimeError("Expected variable Alexandria font")
        font.flavor="woff2"
        path=directory/filename
        font.save(str(path))
        if path.stat().st_size<9000:
            raise RuntimeError("Suspicious Arabic font size: "+filename)
        print("[Arabic self-hosted font] "+filename+" "+str(path.stat().st_size)+" bytes")
        font.close()
    # Redistribute with the upstream SIL Open Font License for both families.
    for family in ("alexandria","tajawal"):
        license=download(FONT_REPOSITORY+family+"/OFL.txt")
        if b"OFL" not in license and b"Open Font License" not in license:
            raise RuntimeError("Missing font license")
        (directory/("LICENSE-"+family+".txt")).write_bytes(license)
    return directory

def build(root:Path):
    directory=copy_fonts(root)
    files=sorted((root/"ar").glob("*.html"))
    if len(files)!=44:
        raise RuntimeError("Expected 44 Arabic routes before font styling")
    files.append(root/"rafting-content-ar.html")
    for file in files:
        source=file.read_text(encoding="utf-8")
        if not re.search(r'<html\b[^>]*\blang="ar"',source):
            raise RuntimeError("Arabic font attempted on non-Arabic page: "+str(file))
        if "arabic-pro.css" in source:
            raise RuntimeError("Arabic font was inserted twice: "+str(file))
        if "</head>" not in source:
            raise RuntimeError("Cannot load CSS without head: "+str(file))
        prefix="../" if file.parent.name=="ar" else ""
        preload=(f'<link rel="preload" as="font" type="font/woff2" crossorigin '
                 f'href="{prefix}fonts/arabic/Alexandria-VF.woff2"/>')
        stylesheet=f'<link rel="stylesheet" href="{prefix}arabic-pro.css?v={VERSION}"/>'
        original_main=re.search(r'<main\b[^>]*>[\s\S]*?</main>',source,re.I)
        # Do not load duplicate Google Fonts; the two Arabic font families are
        # now on this same site, while the existing original styles remain.
        result=source.replace("</head>",preload+stylesheet+"</head>",1)
        updated_main=re.search(r'<main\b[^>]*>[\s\S]*?</main>',result,re.I)
        if original_main and (not updated_main or original_main.group()!=updated_main.group()):
            raise RuntimeError("Arabic font altered original page content: "+str(file))
        file.write_text(result,encoding="utf-8")
    print("[Arabic self-hosted] 44 Arabic pages and rafting iframe updated.")
    print("[Arabic self-hosted] Original FR EN ES and page main content untouched.")

if __name__=="__main__":
    build(Path("public"))
