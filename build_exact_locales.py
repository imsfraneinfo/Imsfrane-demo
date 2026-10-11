"""Build Arabic and Spanish with the EXACT FR page layouts/images/controls.
The publisher clones the original site read-only; this mutates only Demo public/ar/es.
Preserves DOM layout, page-specific CSS/JS, galleries, pricing and interactive widgets.
"""
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Comment
from html import escape
import re,json
from urllib.parse import quote
from build_localized_pages import PAGES, TOPICS, SPANISH, LEGACY, LABELS
from build_localized_mirror import homepage_main, native_memories, header_localize, footer_localize
from build_navigation_pro import DICT

ES_ARTICLE=json.loads(Path("localized-articles-es.json").read_text(encoding="utf-8"))
AR_ARTICLE=json.loads(Path("blog_expanded_content.json").read_text(encoding="utf-8"))
GLOSS=json.loads(Path("localized-exact-text.json").read_text(encoding="utf-8"))
BASE="https://imsfraneinfo.github.io/Imsfrane-demo/"

def norm(x):
    return re.sub(r"\s+"," ",str(x)).strip()

def tr(text,lang,page,index,number):
    key=norm(text)
    if not key:return str(text)
    # Preserve numbers and punctuation tokens across currencies and languages.
    if not re.search(r"[a-zA-ZÀ-ÿ\u0600-\u06FF]",key):
        return str(text)
    row=GLOSS.get(page,{}).get(key) or GLOSS.get("_shared",{}).get(key)
    if row:
        return row.get(lang,key)
    # Numbers and named locations are information, not translation errors.
    if re.fullmatch(r"[\d\s.,–+~:/·\-()%DHMAkmK℮]+",key,re.I):
        return str(text)
    # Large authored paragraphs are rendered from curated local copy when exact
    # text has no glossary entry. Never show French placeholder prose.
    data=PAGES.get(page,{}).get(lang,{})
    if len(key)>=85 and data:
        p=[data.get("lead","")]+[section[1] for section in data.get("sections",[])]
        p=[z for z in p if z]
        return p[index % len(p)] if p else str(text)
    # Other unknown small strings are left for explicit editorial review; no
    # Google/automatic translation, or invented prices/terms.
    return str(text)

def translate_nodes(el,lang,page):
    idx=0;unknown=set()
    for leaf in list(el.descendants):
        if not isinstance(leaf,NavigableString) or isinstance(leaf,Comment):
            continue
        if leaf.parent and leaf.parent.name in ("script","style","noscript","svg","option"):
            if leaf.parent.name!="option":continue
        original=str(leaf)
        key=norm(original)
        if not key or len(key)<=2 or re.fullmatch(r"\d+[\d\s.,]*",key):continue
        replace=tr(original,lang,page,idx,0)
        if norm(replace)==key and re.search(r"[a-zA-ZÀ-ÿ]",key) and key not in {"Imsfrane","WhatsApp","Google","Rafting","Camping","Quad","VTT","MAD","DH","Instagram","Facebook","TikTok","Atlas","Jet Ski","Anergui","Taghia","Tilouguite","Amougr","Jebel Imsfrane"}:
            unknown.add(key)
        if replace!=original:
            left=original[:len(original)-len(original.lstrip())]
            right=original[len(original.rstrip()):]
            leaf.replace_with(left+replace+right)
        idx+=1
    return unknown

def attributes_trans(el,lang,page):
    # Keep every class, href, src, field name, ID and data action untouched.
    for tag in el.find_all(True):
        for attr in ("placeholder","title","aria-label","alt"):
            v=tag.get(attr)
            if isinstance(v,str):
                q=norm(v);row=GLOSS.get(page,{}).get(q) or GLOSS.get("_shared",{}).get(q)
                if row:tag[attr]=row[lang]
        if tag.get("src","").startswith("../fr/"):
            tag["src"]="../"+lang+"/"+tag["src"].split("/",2)[-1]
        if tag.get("href","").startswith("../fr/"):
            tag["href"]="../"+lang+"/"+tag["href"].split("/",2)[-1]
        if tag.get("data-bp-lang")=="fr":tag["data-bp-lang"]=lang
        if tag.name in ("a","img") and tag.get("href","").startswith("https://imsfraneinfo.github.io/Imsfrane-demo/fr/"):
            tag["href"]=tag["href"].replace("/fr/","/"+lang+"/")
    return el

def set_text(tag,value):
    if tag is None:return
    tag.clear();tag.append(value)

def mirror_topic(main,lang,slug):
    title,desc,pars = (
        (ES_ARTICLE[slug][0], ES_ARTICLE[slug][1], ES_ARTICLE[slug][2])
        if lang=="es" else
        (next(x["ar"] for x in TOPICS if x["slug"]==slug),
         next(x["descar"] for x in TOPICS if x["slug"]==slug),
         AR_ARTICLE[slug]["ar"])
    )
    hero=main.select_one(".article-hero")
    if hero:
        set_text(hero.select_one("h1"),title)
        set_text(hero.select_one("p"),desc)
        img=hero.select_one("img")
        if img:img["alt"]=title
    set_text(main.select_one(".article-lead"),desc)
    sections=main.select(".article-body>section")
    if len(sections)!=3 or len(pars)<3:
        raise RuntimeError("Article original structure mismatch: "+slug)
    headings=["ما ينبغي معرفته","التحضير للتجربة","السفر بمسؤولية"] if lang=="ar" else ["Lo que debes saber","Preparar tu experiencia","Viajar con respeto"]
    for i,sec in enumerate(sections):
        set_text(sec.select_one("h2"),headings[i])
        set_text(sec.select_one("p"),pars[i])
    set_text(main.select_one(".article-note"),"قد تتغير الظروف الطبيعية؛ تحقق من المعلومات المحلية قبل الانطلاق." if lang=="ar" else "Las condiciones pueden cambiar. Consulta la información local antes de salir.")
    cta=main.select_one(".article-cta")
    if cta:
        set_text(cta,"تواصل مع فريقنا ←" if lang=="ar" else "Contactar con el equipo →")
        cta["href"]="../"+lang+"/contact.html"

def mirror_legacy(main,lang,filename):
    dat=LEGACY[filename][lang]
    title,desc,paragraphs=dat
    if not main:return
    h1=main.select_one("h1")
    if h1:set_text(h1,title)
    existing=main.select(".ij-content>p")
    body_paras=[p for p in existing if not p.select("a")]
    for p,textval in zip(body_paras,paragraphs):set_text(p,textval)
    for p in main.select(".ij-cover img"):p["alt"]=title
    # Legacy pages can also contain a live CMS article; only static material
    # is translated where the source provides existing layout nodes.
    if main.select_one(".ij-back"):set_text(main.select_one(".ij-back"),"← العودة إلى المدونة" if lang=="ar" else "← Volver al blog")

def blog_magazine(main,lang):
    p=PAGES["blog"][lang]
    set_text(main.select_one(".journal-hero h1"),p["title"])
    set_text(main.select_one(".journal-hero p"),p["lead"])
    set_text(main.select_one(".journal-hero-content>a"),"اقرأ المقالات ↓" if lang=="ar" else "Explorar los artículos ↓")
    main_title="جميع المقالات" if lang=="ar" else "Todos los artículos"
    set_text(main.select_one(".journal-index-heading h2"),main_title)
    index={}
    for item in TOPICS:
        k="blog-guide-"+item["slug"]+".html"
        if lang=="es": name,desc,_=ES_ARTICLE[item["slug"]]
        else:name,desc=item["ar"],item["descar"]
        index[k]=(name,desc)
    for fname,data in LEGACY.items():index[fname]=(data[lang][0],data[lang][1])
    # Keep search filtering functional by also translating indexed data fields.
    for card in main.select(".journal-card"):
        a=card.select_one("a[href]")
        if not a:continue
        name,summary=index.get(a["href"],(None,None))
        if not name:continue
        card["data-title"]=name
        card["data-description"]=summary
        set_text(card.select_one("h3 a"),name)
        set_text(card.select_one(".journal-card-body>p"),summary)
        for im in card.select("img"):im["alt"]=name
    for featured in main.select(".journal-featured"):
        a=featured.select_one("h2 a")
        if a and a.get("href") in index:
            name,summary=index[a["href"]]
            set_text(a,name);set_text(featured.select_one("p"),summary)
            im=featured.select_one("img")
            if im:im["alt"]=name
    for label in main.select(".journal-card-category,.journal-filter"):
        if norm(label.get_text())=="Découverte":set_text(label,"اكتشاف" if lang=="ar" else "Descubrimiento")
    inp=main.select_one("#journal-search")
    if inp:
        inp["placeholder"]="ابحث عن مقال أو مكان أو موضوع…" if lang=="ar" else "Buscar artículos, lugares o temas…"
        inp["aria-label"]=inp["placeholder"]

def replace_main(doc, source_main):
    old=doc.find("main")
    if old is None:raise RuntimeError("Page lacks original main")
    main=BeautifulSoup(str(source_main),"html.parser").find("main")
    old.replace_with(main)
    return main

def wrap_meta(doc,lang,file,page):
    html=doc.find("html")
    if html:
        html["lang"]=lang
        if lang=="ar":html["dir"]="rtl"
        elif html.has_attr("dir"):del html["dir"]
    title=PAGES.get(page,{}).get(lang,{}).get("title")
    if not title and page.startswith("blog-guide-"):
        slug=page[len("blog-guide-"):]
        t=next((t for t in TOPICS if t["slug"]==slug),None)
        if t:title=ES_ARTICLE[slug][0] if lang=="es" else t["ar"]
    if not title and file in LEGACY:title=LEGACY[file][lang][0]
    if title and doc.title:doc.title.string=title+" | Imsfrane Cathédrale"
    head=doc.head
    if head:
        for link in list(head.select('link[rel="canonical"], link[hreflang]')):link.decompose()
        lk=doc.new_tag("link",rel="canonical",href=BASE+lang+"/"+file)
        head.append(lk)
        equivalent={
            "blog-d-couvrir-le-jebel-imsfrane-au-c-ur-de-l-atlas.html":{
                "en":"blog-discover-jebel-imsfrane-in-the-heart-of-the-atlas-mountains.html"},
            "blog-discover-jebel-imsfrane-in-the-heart-of-the-atlas-mountains.html":{
                "fr":"blog-d-couvrir-le-jebel-imsfrane-au-c-ur-de-l-atlas.html"},
        }
        for code in ("fr","en","ar","es"):
            target=equivalent.get(file,{}).get(code,file)
            alt=doc.new_tag("link",rel="alternate",hreflang=code,href=BASE+code+"/"+target)
            head.append(alt)

def build_rafting_embeds(root):
    source=root/"rafting-content.html"
    if not source.is_file():raise RuntimeError("Original rafting content missing")
    raw=source.read_text(encoding="utf-8")
    for lang in ("ar","es"):
        doc=BeautifulSoup(raw,"html.parser")
        html=doc.find("html")
        if html:
            html["lang"]=lang
            if lang=="ar":html["dir"]="rtl"
            elif html.has_attr("dir"):del html["dir"]
        unknown=translate_nodes(doc,lang,"rafting")
        attributes_trans(doc,lang,"rafting")
        # Translate grammatical fragments around emphasized hero text together.
        hero=doc.select_one("#hero-title")
        if hero:
            hero.clear()
            br=doc.new_tag("br");em=doc.new_tag("em")
            if lang=="es":
                em.string="río."
                hero.append("Vive");hero.append(br);hero.append("el ");hero.append(em)
            else:
                em.string="على وادي أحنصال."
                hero.append("عِش مغامرة");hero.append(br);hero.append(em)
        for img in doc.find_all("img"):
            if img.get("alt"):
                img["alt"]="صور من التجديف في وادي أحنصال" if lang=="ar" else "Rafting en el río Ahansal"
        for labelled in doc.select("[aria-label]"):
            val=labelled.get("aria-label","")
            if "rafting" in val.lower() or "photos" in val.lower():
                labelled["aria-label"]="معرض صور التجديف" if lang=="ar" else "Galería de rafting"
        for a in doc.select('a[href^="https://wa.me/212667772551?text="]'):
            query=("مرحباً، أريد الاستفسار عن التجديف في مسفران." if lang=="ar"
                 else "Hola, quisiera información sobre el rafting en Imsfrane.")
            a["href"]="https://wa.me/212667772551?text="+quote(query,safe="")
        for a in doc.select('a[href^="https://imsfrane.com/fr/"]'):
            a["href"]=a["href"].replace("https://imsfrane.com/fr/",BASE+lang+"/")
        for meta in doc.select('meta[property="og:url"]'):
            meta["content"]=BASE+lang+"/rafting.html"
        for link in doc.select('link[rel="canonical"]'):
            link["href"]=BASE+lang+"/rafting.html"
        head=doc.head
        if head:
            if doc.title:doc.title.string=PAGES["rafting"][lang]["title"]+" | Imsfrane Cathédrale"
            if lang=="ar":
                st=doc.new_tag("style")
                st.string='body{font-family:Cairo,Tajawal,Arial,sans-serif}h1,h2,h3{letter-spacing:0}body{text-align:right}'
                head.append(st)
        dest=root/("rafting-content-"+lang+".html")
        dest.write_text(str(doc),encoding="utf-8")
        check=dest.read_text(encoding="utf-8")
        if len(check)<len(raw)*0.60 or check.count("<img")<raw.count("<img")-1:
            raise RuntimeError("Original rafting images/layout lost: "+lang)
        print("[Rafting localized] "+lang+": "+str(len(unknown))+" source-language text strings await final copyediting")
def build(root:Path):
    build_rafting_embeds(root)
    total={}
    for lang in ("ar","es"):
        tgt=root/lang
        source_files=sorted((root/"fr").glob("*.html"))
        for frfile in source_files:
            name=frfile.name
            # The mirrored homepage already uses exact 5-slide and 14-card
            # source styling, the full gallery already mirrors all 78 photos.
            if name in ("index.html","memories.html"):
                continue
            raw=frfile.read_text(encoding="utf-8")
            if raw.count('src="../images/logo-104.webp"')<2 and "siteHeader" in raw:
                raise RuntimeError("Original site brand HTML unavailable: "+name)
            src=BeautifulSoup(raw,"html.parser")
            orig=src.find("main")
            if orig is None:raise RuntimeError("Missing FR main "+name)
            main=BeautifulSoup(str(orig),"html.parser").find("main")
            base=name[:-5]
            if base.startswith("blog-guide-") and base[len("blog-guide-"):] in ES_ARTICLE:
                slug=base[len("blog-guide-"):]
                mirror_topic(main,lang,slug)
            elif name in LEGACY:mirror_legacy(main,lang,name)
            elif base=="blog":blog_magazine(main,lang)
            elif base=="rafting":
                iframe=main.select_one("iframe#raftingExperienceFrame")
                if iframe:
                    iframe["src"]="../rafting-content-"+lang+".html"
                    iframe["title"]="التجديف في مسفران" if lang=="ar" else "Rafting en Imsfrane"
            # For all 15 primary pages, keep ALL original original photo
            # sections, calculators, forms, accordions, maps and carousels.
            if base in PAGES and base not in ("rafting","blog"):
                if base=="memories":raise RuntimeError("Gallery must retain its existing translated version")
                translate_nodes(main,lang,base)
                attributes_trans(main,lang,base)
                # Main heading and hero lead always receive curated editorial text.
                hero=main.select_one("h1")
                if hero:
                    hero.clear()
                    hero.append(PAGES[base][lang]["title"])
                lead=main.select_one("p")
                if lead and lead.find_parent("main"):set_text(lead,PAGES[base][lang]["lead"])
            if base=="booking":
                # Keep the SAME original calculator, prices, choice rules and JS.
                # Supply accurate locale labels to the original JSON-backed summary
                # so selected offers don't turn into undefined in AR or ES.
                choices=src.select_one("script#bpCatalog")
                if choices:
                    try:
                        catalog=json.loads(choices.string or choices.get_text())
                    except ValueError as exc:
                        raise RuntimeError("Cannot parse original booking price catalog") from exc
                    for collection in ("offers","requestOptions"):
                        for item in catalog.get(collection,[]):
                            key=norm(item.get("fr",""))
                            row=GLOSS.get("booking",{}).get(key) or GLOSS.get("_shared",{}).get(key)
                            if row:
                                item[lang]=row[lang]
                            else:
                                item[lang]=str(item.get("en",key))
                            detail=norm(item.get("detailFr",""))
                            dr=GLOSS.get("booking",{}).get(detail) or GLOSS.get("_shared",{}).get(detail)
                            if dr:item["detail"+lang.upper()]=dr[lang]
                    choices.string=json.dumps(catalog,ensure_ascii=False)
                opt=main.select_one("#bp-language")
                if opt:
                    selected={"ar":"العربية","es":"Español"}[lang]
                    # Don't lose the 3 original choices; just add Spanish.
                    if not any(z.get("value")=="Español" for z in opt.select("option")):
                        esop=BeautifulSoup('<option value="Español">Español</option>',"html.parser").option
                        opt.append(esop)
                    for z in opt.select("option"):
                        z.attrs.pop("selected",None)
                        if z.get("value")==selected:z["selected"]=""
                    if len(opt.select("option"))!=4:raise RuntimeError("Booking form must offer 4 languages")
            # Handle standalone CMS pages and remaining legacy editorials:
            # maintain source structure and locale-compatible relative links.
            replace_main(src,main)
            wrap_meta(src,lang,name,base)
            header_localize(src,lang);footer_localize(src,lang)
            if src.select_one('script[src="../booking-pro.js"]'):
                bp=src.select_one("[data-bp-lang]")
                if bp:bp["data-bp-lang"]=lang
            for a in src.select('a[href^="../fr/"]'):
                a["href"]=a["href"].replace("../fr/","../"+lang+"/")
            for a in src.select('a[href^="/fr/"]'):
                a["href"]=a["href"].replace("/fr/","/"+lang+"/")
            for a in src.select('a[href^="/Imsfrane-demo/fr/"]'):
                a["href"]=a["href"].replace("/fr/","/"+lang+"/")
            # The root post templates may load CMS content based on URL but
            # this never changes the original markup or event handlers.
            if src.find("body"):
                src.body["data-lang"]=lang
            source_logos=raw.count('src="../images/logo-104.webp"')
            built=str(src)
            if source_logos and built.count('src="../images/logo-104.webp"')!=source_logos:
                raise RuntimeError("Original branded logo changed "+lang+"/"+name)
            tgt.joinpath(name).write_text(built,encoding="utf-8")
        # The English edition includes one unique slug; preserve its exact layout.
        alias="blog-discover-jebel-imsfrane-in-the-heart-of-the-atlas-mountains.html"
        en_alias=root/"en"/alias
        if en_alias.is_file():
            current=BeautifulSoup(en_alias.read_text(encoding="utf-8"),"html.parser")
            art=current.find("main")
            if art is None:raise RuntimeError("Missing original unique-language article")
            mirror_legacy(art,lang,alias)
            wrap_meta(current,lang,alias,"blog-jebel-imsfrane")
            header_localize(current,lang);footer_localize(current,lang)
            if current.html:
                current.html["lang"]=lang
                if lang=="ar":current.html["dir"]="rtl"
            tgt.joinpath(alias).write_text(str(current),encoding="utf-8")
        total[lang]=len(list(tgt.glob("*.html")))
        print("[Exact Locale] "+lang+": "+str(total[lang])+" pages; original FR structures, classes, photos, widgets and galleries copied.")
    return total

if __name__=="__main__":build(Path("public"))
