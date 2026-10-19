"""Arabic text polish for the published Demo; changes visible text only.

- إغرمَن -> إغرمان in river itinerary.
- Currency abbreviations DH/dh/Dhs/MAD -> درهم in Arabic visible text only.
- Preserve numeric values, script/JSON data, images, links and all DOM markup.
- Leave FR/EN/ES entirely untouched.
"""
from pathlib import Path
import re
from html import escape

# Script/style/comment tokens are passed through unchanged; text nodes only.
TOKENS=re.compile(
    r'(<script\b[^>]*>[\s\S]*?</script>|'
    r'<style\b[^>]*>[\s\S]*?</style>|'
    r'<!--[\s\S]*?-->|'
    r'>([^<>]+)<)',
    re.I
)
UNIT=re.compile(r'(?<![A-Za-z])(?:DH[Ss]?|MAD)(?![A-Za-z])',re.I)
TYPO=re.compile(r'إغرمَن')

def transform(markup:str):
    converted=[0]
    corrected=[0]
    def replace(match):
        original=match.group(0)
        text=match.group(2)
        if text is None:
            return original
        fixed,n=TYPO.subn('إغرمان',text)
        corrected[0]+=n
        fixed,n=UNIT.subn('درهم',fixed)
        converted[0]+=n
        return '>'+fixed+'<'
    updated=TOKENS.sub(replace,markup)
    return updated,converted[0],corrected[0]

def build(root:Path):
    ar=sorted((root/"ar").glob("*.html"))
    if len(ar)<44:raise RuntimeError("Expected at least 44 localized Arabic pages")
    pages=ar+[root/"rafting-content-ar.html"]
    changes={}
    for path in pages:
        source=path.read_text(encoding="utf-8")
        if not re.search(r'<html\b[^>]*\blang="ar"',source,re.I):
            raise RuntimeError("Not an Arabic page: "+str(path))
        new,units,names=transform(source)
        # Strip visible text and compare all non-text markup literally to ensure
        # no styles, numeric values, scripts, links or data structures changed.
        tag_token=re.compile(r'<[^>]+>')
        if tag_token.findall(new)!=tag_token.findall(source):
            raise RuntimeError("Markup was changed, abort: "+str(path))
        if units or names:
            path.write_text(new,encoding="utf-8")
            changes[str(path)]=dict(currency=units,place_name=names)
        remain,n,c=transform(new)
        if remain!=new or n or c:
            raise RuntimeError("Untranslated Arabic text remains: "+str(path))
    rafting=(root/"rafting-content-ar.html").read_text(encoding="utf-8")
    if 'غداء واستراحة في إغرمان' not in rafting or 'إغرمَن' in rafting:
        raise RuntimeError("Rafting place spelling wasn't corrected")
    for amount in ['400','800','2 500','3 000']:
        if not re.search(re.escape(amount)+r'\s+درهم',rafting):
            raise RuntimeError("Missing Arabic-words amount after currency polish: "+amount)
    for loc in ("fr","en","es"):
        for p in (root/loc).glob("*.html"):
            if 'arabic-currency-polish' in p.read_text(encoding="utf-8"):
                raise RuntimeError("Accidental mutation outside Arabic")
    print("[Arabic currency and placenames] "+str(len(changes))+
          " Arabic files polished: "+str(changes))
    return changes

if __name__=="__main__":
    build(Path("public"))
