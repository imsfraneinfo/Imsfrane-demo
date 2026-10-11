"""Fix visual ordering of amounts embedded in RTL Arabic, Demo only.

Arabic prose stays RTL. Prices need independent LTR bidi isolation so
2 500 never renders as 500 2 next to Arabic dirham labels.
No change in numeric value or in FR/EN/ES.
"""
from pathlib import Path
from bs4 import BeautifulSoup
import re

CURRENCY=re.compile(r"^\s*(\d{1,3}(?:[ \u00a0\u202f]\d{3})+|\d+)\s+(درهم(?:اً)?)\s*$",re.U)
SELECTORS=(
 ".route-price strong",".exp-opt b",
 ".hero-stat strong",".hp-activity-bottom strong",
 ".hp-program-foot strong",".bp-offer-price",
 ".bp-summary strong",".sp-price",".guide-price",
)

def make_price(tag,doc):
    original=tag.get_text(" ",strip=True)
    match=CURRENCY.match(original)
    if not match:return False
    number,word=match.groups()
    bdi=doc.new_tag("bdi",attrs={"dir":"ltr","class":"ar-price-number"})
    bdi.string=re.sub(r"[ \u00a0\u202f]","\u00a0",number)
    unit=doc.new_tag("span",attrs={"dir":"rtl","class":"ar-price-unit"})
    unit.string=word
    tag.clear()
    tag.append(bdi)
    tag.append(" ")
    tag.append(unit)
    tag["class"]=list(dict.fromkeys(tag.get("class",[])+["ar-formatted-price"]))
    return True

def build(root:Path):
    pages=sorted((root/"ar").glob("*.html"))+[root/"rafting-content-ar.html"]
    if len(pages)!=45:raise RuntimeError("Expected 44 Arabic routes and rafting iframe")
    total=0
    for path in pages:
        source=path.read_text(encoding="utf-8")
        if not re.search(r'<html\b[^>]*\blang="ar"',source,re.I):
            raise RuntimeError("Not Arabic: "+str(path))
        image_count=len(re.findall(r"<img\b",source,re.I))
        section_count=len(re.findall(r"<section\b",source,re.I))
        doc=BeautifulSoup(source,"html.parser")
        count=0
        for tag in doc.select(",".join(SELECTORS)):
            if make_price(tag,doc):count+=1
        if path.name=="rafting-content-ar.html":
            values=[(x.select_one("bdi").get_text().replace("\u00a0",""),x.select_one(".ar-price-unit").get_text())
                    for x in doc.select(".exp-opt .ar-formatted-price")]
            if values!=[("2500","درهم"),("3000","درهم")]:
                raise RuntimeError("Expedition price mismatch: "+str(values))
            card=doc.select_one(".route-price strong.ar-formatted-price")
            if not card or card.select_one("bdi").get_text().replace("\u00a0","")!="2500":
                raise RuntimeError("Rafting 2-day price was not isolated")
        if count:
            result=str(doc)
            if len(re.findall(r"<img\b",result,re.I))!=image_count:
                raise RuntimeError("Bidi fix changed image count")
            if len(re.findall(r"<section\b",result,re.I))!=section_count:
                raise RuntimeError("Bidi fix changed section count")
            path.write_text(result,encoding="utf-8")
            total+=count
        print("[AR PRICE BIDI]",path.name,count,"dirham values isolated")
    if total<3:raise RuntimeError("Expected at least 3 Arabic monetary values")
    print("[AR PRICE BIDI] Done: "+str(total)+" correct RTL currency prices; FR/EN/ES unchanged.")

if __name__=="__main__":
    build(Path("public"))
