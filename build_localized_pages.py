"""Publish curated Arabic and Spanish pages and Spanish editorial articles.

This only writes public/ar and public/es on the Demo publishing runner. FR/EN
site originals are never edited; images are sourced from read-only build assets.
"""
from pathlib import Path
from html import escape
from urllib.parse import quote
import json
import re

PAGES=json.loads(Path("localized-pages.json").read_text(encoding="utf-8"))
TOPICS=json.loads(Path("blog_new_topics.json").read_text(encoding="utf-8"))
SPANISH=json.loads(Path("localized-articles-es.json").read_text(encoding="utf-8"))
LEGACY=json.loads(Path("localized-legacy-articles.json").read_text(encoding="utf-8"))
BASE="https://imsfraneinfo.github.io/Imsfrane-demo/"
SIX=(
  ("rafting.html","Rafting","rafting","raft2-800.webp"),
  ("camping.html","Camping","camping","camping-1-800.webp"),
  ("randonnee.html","المشي الجبلي","randonnee","19-800.webp"),
  ("vtt.html","الدراجات الجبلية","vtt","31.webp"),
  ("quad.html","جولات الكواد","quad","27.webp"),
  ("hebergement.html","الإقامة","hebergement","21.webp"),
)
LABELS={
 "ar":{"book":"طلب حجز","explore":"اكتشف أنشطتنا","activities":"أنشطة وتجارب في مسفران",
       "choose":"اختر المغامرة التي تناسبك","details":"اكتشف التفاصيل","read":"اقرأ المقال",
       "contact":"تواصل معنا","more":"تعرّف على المزيد","whatsapp":"تحدث إلينا عبر واتساب",
       "disclaimer":"تخضع الأنشطة للتوفر والظروف الجوية والطبيعية. نؤكد جميع التفاصيل قبل الحجز.",
       "whatsapp_note":"إرسال طلب عبر واتساب لا يعني تأكيد الحجز أو الدفع.",
       "articles":"مقالات ونصائح من منطقة مسفران","ask":"اطلب معلومات عن النشاط",
       "gallery":"صور من مسفران","form_title":"أرسل طلبك إلى الفريق المحلي",
       "form_name":"الاسم (اختياري)","form_activity":"النشاط","form_date":"التاريخ المقترح",
       "form_people":"عدد الأشخاص","form_note":"رسالة أو تفاصيل إضافية (اختيارية)",
       "send":"إرسال الطلب عبر واتساب","all":"اختر النشاط","default":"استفسار عام",
       "prepare":"نساعدك على التخطيط لرحلتك","season":"قد يتغير برنامج الرحلة وفق الأحوال الجوية وحالة المسالك أو صبيب النهر.",
       "about_trip":"مسفران · تيلوكيت · إقليم أزيلال · المغرب"},
 "es":{"book":"Solicitar reserva","explore":"Descubre las actividades","activities":"Experiencias en Imsfrane",
       "choose":"Elige tu próxima aventura","details":"Ver experiencia","read":"Leer artículo",
       "contact":"Contacta con nosotros","more":"Descubre más","whatsapp":"Escríbenos por WhatsApp",
       "disclaimer":"Las actividades dependen de la disponibilidad y de las condiciones meteorológicas y naturales. Confirmaremos todos los detalles antes de reservar.",
       "whatsapp_note":"Enviar una consulta por WhatsApp no implica pago ni reserva confirmada.",
       "articles":"Ideas y consejos para descubrir Imsfrane","ask":"Consultar esta actividad",
       "gallery":"Imágenes de Imsfrane","form_title":"Envía tu solicitud al equipo local",
       "form_name":"Nombre (opcional)","form_activity":"Actividad","form_date":"Fecha prevista",
       "form_people":"Número de participantes","form_note":"Mensaje o información adicional (opcional)",
       "send":"Enviar consulta por WhatsApp","all":"Elige una actividad","default":"Consulta general",
       "prepare":"Te ayudamos a preparar tu viaje","season":"Los itinerarios pueden cambiar según la meteorología, el estado de las pistas o el caudal del río.",
       "about_trip":"Imsfrane · Tilouguite · Provincia de Azilal · Marruecos"},
}
ACTIVITY_NAMES={
"ar":["التجديف في المياه البيضاء","التخييم","المشي الجبلي","الدراجات الجبلية","الكواد","الإقامة"],
"es":["Rafting","Acampada","Senderismo","BTT","Quad","Alojamiento"],
}
HEADS={
"ar":["التعرّف على التجربة","تفاصيل ينبغي معرفتها","الاستعداد للرحلة"],
"es":["Conoce la experiencia","Lo que debes saber","Prepara tu visita"],
}

def esc(x):return escape(str(x),quote=True)
def photo(src):
    if src.startswith("../images/"):return src
    return "../images/"+src

def alternates(root,page,lang):
    # Exact one-to-one links only: no misleading hreflang pointing to an unrelated page.
    names=("fr","en","ar","es")
    tag=[]
    for code in names:
        if code==lang or (root/code/page).is_file():
            tag.append('<link rel="alternate" hreflang="'+code+'" href="'+esc(BASE+code+'/'+page)+'">')
    tag.append('<link rel="alternate" hreflang="x-default" href="'+esc(BASE+'fr/'+page)+'">')
    return "".join(tag)

def head(lang,file,title,desc,image,root):
    return (f'<!doctype html><html lang="{lang}"'+(' dir="rtl"' if lang=="ar" else '')+'>'
        +'<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        +'<meta name="theme-color" content="#0b2a1e"><meta name="robots" content="index,follow">'
        +'<title>'+esc(title)+' | Imsfrane Cathédrale</title>'
        +'<meta name="description" content="'+esc(desc)+'">'
        +'<link rel="canonical" href="'+esc(BASE+lang+'/'+file)+'">'
        +alternates(root,file,lang)
        +'<meta property="og:type" content="'+("article" if file.startswith("blog-guide-") else "website")+'">'
        +'<meta property="og:title" content="'+esc(title)+'">'
        +'<meta property="og:description" content="'+esc(desc)+'">'
        +'<meta property="og:image" content="'+esc(BASE+photo(image).replace("../",""))+'">'
        +'<meta property="og:url" content="'+esc(BASE+lang+'/'+file)+'">'
        +'<meta property="og:locale" content="'+("ar_MA" if lang=="ar" else "es_ES")+'">'
        +'<meta name="twitter:card" content="summary_large_image">'
        +'<link rel="preconnect" href="https://fonts.googleapis.com">'
        +'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        +'<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Cairo:wght@400;500;600;700;800&display=swap" rel="stylesheet">'
        +'<link rel="stylesheet" href="../localized-site.css"></head>')

def cards(lang):
    t=LABELS[lang]
    out=[]
    for i,(p,_,_,image) in enumerate(SIX):
        title=ACTIVITY_NAMES[lang][i]
        desc=PAGES[p[:-5]][lang]["lead"]
        out.append('<article class="locale-card"><a href="'+p+'" aria-label="'+esc(title)+'">'
            +'<img loading="lazy" decoding="async" src="'+photo(image)+'" alt="'+esc(title)+'"></a>'
            +'<div class="locale-card-body"><h3>'+esc(title)+'</h3><p>'+esc(desc[:160].rsplit(" ",1)[0])+'…</p>'
            +'<a class="locale-card-link" href="'+p+'">'+esc(t["details"])+' ↗</a></div></article>')
    return ('<section class="locale-section" id="activities"><div class="locale-wrap">'
        +'<div class="locale-heading"><span class="locale-kicker">'+esc(t["activities"])+'</span><h2>'+esc(t["choose"])+'</h2></div>'
        +'<div class="locale-activity-grid">'+''.join(out)+'</div></div></section>')

def photo_gallery(lang):
    t=LABELS[lang]
    imgs=[
      ("21.webp","Imsfrane Cathédrale"),("24.webp","Ahansal rafting"),("27.webp","Quad"),
      ("29.webp","Camping"),("31.webp","Mountain biking"),("19.webp","Jebel Imsfrane"),
    ]
    return '<section class="locale-section"><div class="locale-wrap"><div class="locale-heading"><h2>'+esc(t["gallery"])+'</h2></div><div class="locale-photo-grid">'+''.join('<img src="'+photo(im)+'" alt="'+esc(label)+'" loading="lazy" decoding="async">' for im,label in imgs)+'</div></div></section>'

def article_cards(lang):
    t=LABELS[lang]
    result=[]
    for topic in TOPICS:
        if lang=="es":
            title,desc,_=SPANISH[topic["slug"]]
        else:
            title,desc=topic["ar"],topic["descar"]
        slug="blog-guide-"+topic["slug"]+".html"
        result.append('<a href="'+slug+'"><img src="'+esc(topic["image"])+'" alt="'+esc(title)+'" loading="lazy" decoding="async"><span class="locale-blog-copy"><strong>'+esc(title)+'</strong><span>'+esc(desc)+'</span></span></a>')
    return ('<section class="locale-section" id="articles"><div class="locale-wrap">'
       +'<div class="locale-heading"><h2>'+esc(t["articles"])+'</h2></div>'
       +'<div class="locale-blog-grid">'+''.join(result)+'</div></div></section>')

def request_form(lang):
    t=LABELS[lang]
    options=['<option value="">'+esc(t["all"])+'</option>']
    for i,(p,_,_,_) in enumerate(SIX):
        options.append('<option value="'+esc(ACTIVITY_NAMES[lang][i])+'">'+esc(ACTIVITY_NAMES[lang][i])+'</option>')
    return ('<section class="locale-section" id="request"><div class="locale-wrap">'
       +'<div class="locale-heading"><h2>'+esc(t["form_title"])+'</h2></div>'
       +'<form class="locale-request" id="localeRequest" data-language="'+lang+'">'
       +'<label>'+esc(t["form_name"])+'<input name="name" maxlength="100" autocomplete="name"></label>'
       +'<label>'+esc(t["form_activity"])+'<select name="activity" required>'+''.join(options)+'</select></label>'
       +'<label>'+esc(t["form_date"])+'<input type="date" name="date" required></label>'
       +'<label>'+esc(t["form_people"])+'<input type="number" min="1" max="100" name="people" value="2" required></label>'
       +'<label>'+esc(t["form_note"])+'<textarea name="message" rows="4" maxlength="1200"></textarea></label>'
       +'<button type="submit">'+esc(t["send"])+' ↗</button>'
       +'<small>'+esc(t["whatsapp_note"])+'</small></form></div></section>')

def footer(lang):
    t=LABELS[lang]
    return '<footer class="locale-footer">© Imsfrane Cathédrale · '+esc(t["about_trip"])+' · <a href="contact.html">'+esc(t["contact"])+'</a></footer><script defer src="../localized-site.js"></script></body></html>'

def render_page(page,lang,root):
    data=PAGES[page][lang];t=LABELS[lang];img=PAGES[page]["img"];file=page+".html"
    desc=data["lead"]
    pos="center 76%" if page=="camping" else "center"
    # Do not embed unverified travel-time, instant-booking or payment claims.
    result=head(lang,file,data["title"],desc,img,root)
    result+='<body class="locale-page">'
    result+='<main class="locale-main"><section class="locale-hero" style="--lc-image:url('+photo(img)+');--lc-position:'+pos+'">'
    result+='<div class="locale-wrap"><span class="locale-kicker">'+esc(data["kicker"])+'</span>'
    result+='<h1>'+esc(data["title"])+'</h1><p>'+esc(desc)+'</p>'
    result+='<a class="locale-hero-cta" href="'+('booking.html' if page!="booking" else '#request')+'">'+esc(t["book"])+' ↗</a>'
    result+='<a class="locale-hero-cta locale-hero-secondary" href="'+('#activities' if page=="index" else '#details')+'">'+esc(t["explore"] if page=="index" else t["more"])+'</a>'
    result+='<div class="locale-breadcrumb">'+esc(t["about_trip"])+'</div></div></section>'
    result+='<section class="locale-section" id="details"><div class="locale-wrap">'
    result+='<div class="locale-feature-grid">'
    for i,(heading,paragraph) in enumerate(data["sections"]):
        result+='<article class="locale-feature"><b>0'+str(i+1)+'</b><h3>'+esc(heading)+'</h3><p>'+esc(paragraph)+'</p></article>'
    result+='</div></div></section>'
    if page=="index":result+=cards(lang)+photo_gallery(lang)
    if page=="memories":result+=photo_gallery(lang)
    if page=="blog":result+=article_cards(lang)
    if page in ("booking","contact"):result+=request_form(lang)
    result+='<div class="locale-wrap"><div class="locale-cta"><h2>'+esc(t["prepare"])+'</h2>'
    result+='<p>'+esc(t["disclaimer"])+'</p><a href="booking.html">'+esc(t["book"])+' ↗</a>'
    result+='<a class="secondary" href="https://wa.me/212667772551" target="_blank" rel="noopener noreferrer">'+esc(t["whatsapp"])+'</a>'
    result+='</div></div></main>'
    result+=footer(lang)
    if result.count('<main')!=1 or result.count('<h1')!=1:raise RuntimeError("Malformed localized page "+lang+"/"+file)
    return result

def render_es_article(topic,root):
    slug=topic["slug"]
    file="blog-guide-"+slug+".html"
    title,summary,pars=SPANISH[slug]
    if len(pars)!=3:raise RuntimeError("Spanish article missing sections: "+slug)
    result=head("es",file,title,summary,topic["image"],root)
    result+='<body class="locale-page"><main class="locale-main"><section class="locale-hero" style="--lc-image:url('+esc(topic["image"])+')">'
    result+='<div class="locale-wrap"><span class="locale-kicker">CUADERNO DE VIAJE · IMSFRANE</span>'
    result+='<h1>'+esc(title)+'</h1><p>'+esc(summary)+'</p>'
    result+='<a class="locale-hero-cta" href="blog.html">← Volver al blog</a></div></section>'
    result+='<section class="locale-section"><div class="locale-wrap"><div class="locale-feature-grid">'
    for i,paragraph in enumerate(pars):
        result+='<article class="locale-feature"><b>0'+str(i+1)+'</b><h2>'+esc(HEADS["es"][i])+'</h2><p>'+esc(paragraph)+'</p></article>'
    result+='</div><div class="locale-info" style="margin-top:30px">Las condiciones naturales pueden cambiar. Confirma siempre la información local antes de iniciar una ruta o una actividad acuática.</div></div></section>'
    result+='<div class="locale-wrap"><div class="locale-cta"><h2>¿Te apetece conocer Imsfrane?</h2><p>Consúltanos tus fechas y te orientaremos según el clima y las actividades disponibles.</p><a href="booking.html">Planificar mi aventura ↗</a><a href="blog.html" class="secondary">Más artículos</a></div></div>'
    result+='</main>'+footer("es")
    return result


def render_legacy_article(lang, filename, data, root):
    title,summary,paragraphs=data[lang]
    if len(paragraphs)!=3:
        raise RuntimeError("Each legacy language article needs three original sections: "+filename)
    image=data["img"]
    t=LABELS[lang]
    result=head(lang,filename,title,summary,image,root)
    result+='<body class="locale-page"><main class="locale-main"><section class="locale-hero" style="--lc-image:url('+photo(image)+')">'
    result+='<div class="locale-wrap"><span class="locale-kicker">'+esc(t["articles"])+'</span>'
    result+='<h1>'+esc(title)+'</h1><p>'+esc(summary)+'</p>'
    result+='<a class="locale-hero-cta" href="blog.html">'+("→ العودة إلى المدونة" if lang=="ar" else "← Volver al blog")+'</a></div></section>'
    result+='<section class="locale-section"><div class="locale-wrap"><div class="locale-feature-grid">'
    for i,paragraph in enumerate(paragraphs):
        result+='<article class="locale-feature"><b>0'+str(i+1)+'</b><h2>'+esc(HEADS[lang][i])+'</h2><p>'+esc(paragraph)+'</p></article>'
    result+='</div><div class="locale-info" style="margin-top:30px">'+esc(t["season"])+'</div></div></section>'
    result+='<div class="locale-wrap"><div class="locale-cta"><h2>'+esc(t["prepare"])+'</h2>'
    result+='<p>'+esc(t["disclaimer"])+'</p><a href="booking.html">'+esc(t["book"])+' ↗</a>'
    result+='<a href="blog.html" class="secondary">'+esc(t["articles"])+'</a></div></div></main>'
    result+=footer(lang)
    return result

def polish_existing_ar_articles(root):
    ar=root/"ar"
    for topic in TOPICS:
        path=ar/("blog-guide-"+topic["slug"]+".html")
        if not path.is_file():raise RuntimeError("Missing previously authored Arabic article: "+str(path))
        value=path.read_text(encoding="utf-8")
        if 'lang="ar"' not in value:raise RuntimeError("Arabic article language mismatch")
        value=value.replace('الظروف يمكن تتبدل، تأكد من المعلومات المحلية قبل الانطلاق.',
          'قد تتغير الظروف الطبيعية؛ تحقق من المعلومات المحلية قبل الانطلاق.')
        value=value.replace('الرافتينغ والروندوني والتخييم', 'التجديف والمشي الجبلي والتخييم')
        path.write_text(value,encoding="utf-8")

def build(root:Path):
    ar=root/"ar";es=root/"es"
    ar.mkdir(parents=True,exist_ok=True);es.mkdir(parents=True,exist_ok=True)
    if set(PAGES)!={"index","rafting","camping","randonnee","vtt","quad","hebergement","programme","memories","guide","about","blog","store","booking","contact"}:
        raise RuntimeError("Missing one of 15 main localized pages")
    if len(TOPICS)!=20 or set(SPANISH)!={t["slug"] for t in TOPICS}:
        raise RuntimeError("Spanish articles not mapped one to one with 20 original topics")
    for lang,folder in (("ar",ar),("es",es)):
        for page in PAGES:
            (folder/(page+".html")).write_text(render_page(page,lang,root),encoding="utf-8")
    for topic in TOPICS:
        (es/("blog-guide-"+topic["slug"]+".html")).write_text(render_es_article(topic,root),encoding="utf-8")
    if len(LEGACY)!=9:
        raise RuntimeError("Expected nine editorial legacy article routes")
    for filename,data in LEGACY.items():
        for lang,folder in (("ar",ar),("es",es)):
            (folder/filename).write_text(render_legacy_article(lang,filename,data,root),encoding="utf-8")
    polish_existing_ar_articles(root)
    for lang,folder in (("ar",ar),("es",es)):
        count=len(list(folder.glob("*.html")))
        if count!=44:
            raise RuntimeError("Expected 44 fully localized pages in "+lang+", got "+str(count))
        print("[Localisation] "+lang+": 44 pages, including 15 core pages and 29 editorial articles.")
    print("[Localisation] Arabic and Spanish: 15 original destination pages each; 29 editorial routes each.")
    print("[Localisation] No auto translation, no false immediate reservations, all Arabic uses RTL.")

if __name__=="__main__":
    build(Path("public"))
