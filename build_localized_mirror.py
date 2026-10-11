"""Mirror the original French Demo visual template into Arabic and Spanish.
Source FR/EN documents, logo assets, homepage layout, pictures and JS remain unchanged.
"""
from pathlib import Path
from bs4 import BeautifulSoup
from html import escape
import re,json
from build_localized_pages import PAGES,LABELS,TOPICS,SPANISH,ACTIVITY_NAMES,OTHER_ACTIVITIES,request_form
from build_navigation_pro import DICT
E=lambda s:escape(str(s),quote=True)
W={
"ar":{"eyebrow":"اكتشف · استمتع · عِش الأطلس","heroSub":"مغامرة أصيلة في قلب الأطلس الكبير.","discover":"اكتشف الأنشطة","visit":"خطط لرحلتك","review":"آراء زوارنا مهمة.","reviews":"اطّلع على تقييمات زوار تجاربنا المنشورة على Google.","reviewLink":"قراءة التقييمات","activities":"تجارب تناسبك","choose":"اختر مغامرتك.","more":"تفاصيل التجربة","seasonTip":"التجديف نشاط موسمي مرتبط بصبيب النهر، وعادة من مارس إلى يونيو وأحياناً يوليو. يجب تأكيد كل رحلة.","destination":"أكثر من مجرد وجهة","destinationTitle":"الأطلس الكبير، بجماله الأصيل.","destinationBullets":["في جماعة تيلوكيت بإقليم أزيلال","جبال ومضايق وأنهار قريبة","مرشدون محليون يعرفون المنطقة"],"programs":"برامج استكشافية","programTitle":"أيام حافلة بالاكتشاف.","programNames":["قمة جبل مسفران","المضايق والشلالات","الجولة الكبرى"],"programLevels":["متوسط","سهل · 8 كلم","مُجهد · 24 كلم"],"programDetail":"تفاصيل البرنامج","perGroup":"للمجموعة","request":"أرسل طلبك","why":"لماذا تختار فريقنا؟","whyTitle":"مغامرات تجمع الإنسان بالطبيعة.","trust":["مرشدون محليون","طبيعة أصيلة","برنامج يناسبك","تواصل مباشر"],"trustDesc":["معرفة حقيقية بالمسالك والمعالم.","وديان وأنهار وجبال بعيدة عن الصخب.","أنشطة تتكيف مع اهتماماتك ووقتك.","تأكيد التفاصيل قبل الحجز."],"season":"التخطيط في الوقت المناسب","seasonTitle":"لكل فصل مغامرته.","photos":"لحظات لا تُنسى","photosTitle":"ذكريات تُروى بالصور.","viewPhotos":"عرض جميع الصور","explore":"المزيد من الاكتشاف","exploreTitle":"استعد لرحلتك المقبلة.","exploreCards":["دليل الزيارة","مدونة مسفران","متجر المنطقة"],"exploreText":["الوصول والمواصلات وتجهيزات السفر.","مقالات ووجهات وتجارب من الأطلس.","منتجات وتجهيزات مرتبطة بالمغامرة."],"exploreCTA":["اقرأ الدليل","تصفح المقالات","اكتشف المتجر"],"reviewsTitle":"تجارب الزوار على Google","endKicker":"رحلتك المقبلة تبدأ هنا","endTitle":"هل أنت مستعد لاكتشاف مسفران؟","contact":"تواصل معنا عبر واتساب","mountain":"جبل مسفران","photoCaption":"بين النهر والجبل","photoPlace":"الأطلس الكبير · المغرب","price":["ابتداءً من 400 درهم للشخص","ابتداءً من 200 درهم للمجموعة","ابتداءً من 60 درهماً للخيمة/الليلة","ابتداءً من 100 درهم للشخص","ابتداءً من 250 درهماً للكواد","السعر عند الطلب"],"otherPrice":["300 درهم للشخص","300 درهم · قابل للتأكيد","حسب الطلب","حسب الطلب","حسب الطلب","حسب الطلب","حسب الطلب","800 درهم للمجموعة"],"footer":"مغامرات طبيعية أصيلة في جبال مسفران ووديان أحنصال.","rights":"جميع الحقوق محفوظة.","useful":"روابط مفيدة","name":"تيلوكيت، أزيلال، المغرب","seasonNotes":["مارس إلى يونيو · أحياناً يوليو","مناسب حسب المستوى","حسب توفر الخيام","جولة أو استئجار","حسب المسار والتوفر","إقامة محلية"],"see":"اكتشف"},
"es":{"eyebrow":"EXPLORA · RESPIRA · VIVE EL ATLAS","heroSub":"La aventura tiene otra dimensión.","discover":"Descubre las actividades","visit":"Prepara tu viaje","review":"Tu opinión nos importa.","reviews":"Descubre las reseñas publicadas en Google por quienes han vivido nuestras experiencias.","reviewLink":"Leer las reseñas","activities":"TUS PRÓXIMAS EXPERIENCIAS","choose":"Una aventura para cada viajero.","more":"Descubrir","seasonTip":"El rafting es estacional: normalmente de marzo a junio, a veces hasta julio según el caudal. Cada salida debe confirmarse.","destination":"MÁS QUE UN DESTINO","destinationTitle":"El Atlas en su esencia más auténtica.","destinationBullets":["En la comuna de Tilouguite, provincia de Azilal","Montañas, gargantas y ríos cercanos","Experiencias con guías locales"],"programs":"NUESTROS ITINERARIOS","programTitle":"Días para recordar.","programNames":["Cumbre del Jebel Imsfrane","Gargantas y cascadas","Gran recorrido"],"programLevels":["Nivel medio","Fácil · 8 km","Exigente · 24 km"],"programDetail":"Ver programa","perGroup":"por grupo","request":"Solicitar información","why":"POR QUÉ VIAJAR CON NOSOTROS","whyTitle":"Aventuras cercanas y humanas.","trust":["Guías locales","Paisajes auténticos","Experiencias a medida","Contacto directo"],"trustDesc":["Conocimiento de los senderos y del territorio.","Valles y montañas fuera de los circuitos habituales.","Rutas y duraciones adaptadas a cada grupo.","Consulta los detalles antes de reservar."],"season":"PLANIFICA TU VISITA","seasonTitle":"Cada estación tiene su aventura.","photos":"MOMENTOS COMPARTIDOS","photosTitle":"La aventura se cuenta con imágenes.","viewPhotos":"Ver todas las fotos","explore":"SIGUE DESCUBRIENDO","exploreTitle":"Prepara tu escapada.","exploreCards":["Guía práctica","Nuestro blog","Tienda del Atlas"],"exploreText":["Accesos, transporte, equipo y consejos útiles.","Ideas y artículos sobre la región.","Artículos y productos vinculados a la naturaleza."],"exploreCTA":["Consultar la guía","Leer artículos","Visitar la tienda"],"reviewsTitle":"Nuestros visitantes comparten sus experiencias en Google","endKicker":"TU AVENTURA EMPIEZA AQUÍ","endTitle":"¿Listo para descubrir Imsfrane?","contact":"Escríbenos por WhatsApp","mountain":"Jebel Imsfrane","photoCaption":"Entre el río y las montañas","photoPlace":"Alto Atlas · Marruecos","price":["Desde 400 MAD/persona","Desde 200 MAD/grupo","Desde 60 MAD/tienda/noche","Desde 100 MAD/persona","Desde 250 MAD/quad","Precio a consultar"],"otherPrice":["300 MAD/persona","300 MAD · a confirmar","A consultar","A consultar","A consultar","A consultar","A consultar","800 MAD/grupo"],"footer":"Experiencias auténticas entre Imsfrane, Tilouguite y el río Ahansal.","rights":"Todos los derechos reservados.","useful":"Enlaces útiles","name":"Tilouguite, Azilal, Marruecos","seasonNotes":["Marzo–junio · a veces julio","Rutas adaptadas al grupo","Según disponibilidad","Ruta o alquiler","Según el itinerario","Alojamiento local"],"see":"Descubrir"}}
ACTIVITY={"rafting":0,"randonnee":1,"camping":2,"vtt":3,"quad":4,"hebergement":5}
OTHERS={"tubing":0,"jetski":1,"4x4":2,"passage":3,"zrkan":4,"anergui":5,"almou":6,"ahidous":7}
def text(target,value):
    if target is not None: target.clear();target.append(value)
def rich(target,before,accent):
    if target is not None:
        target.clear();target.append(before+" ")
        em=target.new_tag("em") if hasattr(target,"new_tag") else BeautifulSoup("<em></em>","html.parser").em
        em.string=accent;target.append(em)
def opt(s,selector,value):
    text(s.select_one(selector),value)
def first_text(target,value):
    if target is None:return
    for node in list(target.contents):
        if isinstance(node,str) and node.strip():
            node.replace_with(" "+str(value)+" ");return
    target.insert(0,str(value))
def footer_localize(page,lang):
    t=W[lang];labels=DICT[lang]
    foot=page.select_one("footer.site-footer")
    if not foot:return
    def f(sel,label):text(foot.select_one(sel),label)
    f(".footer-brand .brand-content small",("مغامرات في طبيعة الأطلس" if lang=="ar" else "Aventuras en el Alto Atlas"))
    f(".footer-brand>p",t["footer"])
    groups=foot.select(".footer-column")
    if len(groups)>=3:
        text(groups[0].select_one("h3"),labels["activity"])
        for link in groups[0].select("li a"):
            key=link.get("href","").replace(".html","")
            if key in ACTIVITY:
                i=ACTIVITY[key];val=ACTIVITY_NAMES[lang][{"rafting":0,"camping":1,"randonnee":2,"vtt":3,"quad":4,"hebergement":5}[key]]
                text(link,val)
        text(groups[1].select_one("h3"),t["useful"])
        for link in groups[1].select("li a"):
            name=link.get("href","").replace(".html","")
            k={"programme":"route","guide":"guide","about":"about","blog":"blog","store":"shop","booking":"booking"}.get(name)
            if k:text(link,labels[k])
        text(groups[2].select_one("h3"),labels["contact"])
        text(groups[2].select_one(".footer-contact span"),t["name"])
    line=foot.select_one(".footer-bottom p")
    if line:
        # Keep the date and the brand, only replace the rights sentence.
        for child in list(line.contents):
            if isinstance(child,str) and "Tous droits réservés" in child:
                child.replace_with(" Imsfrane Cathédrale. "+t["rights"])
def header_localize(doc,lang):
    hdr=doc.select_one("#siteHeader")
    if hdr:
        opt(hdr,".brand-content small","مغامرات طبيعية في الأطلس" if lang=="ar" else "Aventuras en el Alto Atlas")
        first_text(hdr.select_one(".header-book-button"),LABELS[lang]["book"])
    # The existing original site logo and its HTML attributes are never touched.
def homepage_main(root,lang):
    src=(root/"fr/index.html").read_text(encoding="utf-8")
    soup=BeautifulSoup(src,"html.parser")
    main=soup.select_one("main.hp-home")
    if not main:raise RuntimeError("Original premium homepage is missing")
    main=BeautifulSoup(str(main),"html.parser")
    p=PAGES["index"][lang];w=W[lang];l=LABELS[lang]
    opt(main,".hp-eyebrow",w["eyebrow"])
    h1=main.select_one("#hp-h1")
    if h1:
        h1.clear();h1.append("مسفران " if lang=="ar" else "Imsfrane ")
        em=BeautifulSoup("<em></em>","html.parser").em
        em.string="كاتدرال." if lang=="ar" else "Cathédrale."
        h1.append(em);span=BeautifulSoup("<span></span>","html.parser").span;span.string=w["heroSub"];h1.append(span)
    opt(main,".hp-hero-content>p",p["lead"])
    bs=main.select(".hp-hero-buttons a")
    if len(bs)==2:first_text(bs[0],w["discover"]);first_text(bs[1],w["visit"])
    opt(main,".hp-hero-foot",l["about_trip"])
    pic=main.select_one(".hp-hero-picture-note")
    if pic:
        opt(pic,"span",w["photoPlace"]);opt(pic,"strong",w["photoCaption"])
    opt(main,".hp-hero-altitude span",w["mountain"])
    first_text(main.select_one(".hp-scroll"),w["see"])
    opt(main,".hp-review-count", "23 تقييماً معروضاً" if lang=="ar" else "23 reseñas mostradas")
    opt(main,".hp-google-copy h2",w["review"]);opt(main,".hp-google-copy p",w["reviews"])
    first_text(main.select_one(".hp-google-link"),w["reviewLink"])
    opt(main,".hp-activities .hp-kicker",w["activities"])
    rich(main.select_one(".hp-activities h2"),w["choose"],"✦")
    opt(main,".hp-activities .hp-heading p",l["choose"])
    cards=main.select(".hp-activity-card")
    if len(cards)!=14:raise RuntimeError("Home must keep 14 cards")
    for card in cards:
        href=card.select_one(".hp-activity-image").get("href","")
        kind=href.split(".")[0]
        if kind in ACTIVITY:
            i=ACTIVITY[kind];source=ACTIVITY_NAMES[lang][{"rafting":0,"camping":1,"randonnee":2,"vtt":3,"quad":4,"hebergement":5}[kind]]
            desc=PAGES[kind][lang]["lead"]
            note=w["seasonNotes"][i];price=w["price"][i]
        else:
            kind=next((key for key in OTHERS if key in card.get("class",[])[-1] or key in href.lower()),None)
            if kind is None:
                # Card's hp-xxx class; fallback to expected published card order.
                i=cards.index(card)-6
            else:i=OTHERS[kind]
            if i<0 or i>=len(OTHER_ACTIVITIES):raise RuntimeError("Unexpected activity card type")
            other=OTHER_ACTIVITIES[i]
            source=other[2] if lang=="ar" else other[4]
            desc=other[3] if lang=="ar" else other[5]
            note=l["default"];price=w["otherPrice"][i]
        opt(card,".hp-activity-note",note)
        opt(card,"h3",source);opt(card,".hp-activity-body p",desc)
        opt(card,".hp-activity-bottom strong",price)
        opt(card,".hp-activity-bottom a span",w["more"])
        link=card.select_one(".hp-activity-bottom a")
        if link:link["aria-label"]=w["more"]+" "+source
        image=card.select_one("img")
        if image:image["alt"]=source
    opt(main,".hp-season-tip",w["seasonTip"])
    opt(main,".hp-destination .hp-kicker",w["destination"])
    rich(main.select_one(".hp-destination h2"),w["destinationTitle"],"")
    opt(main,".hp-destination-content>p",PAGES["about"][lang]["lead"])
    for li,label in zip(main.select(".hp-destination li"),w["destinationBullets"]):first_text(li,label)
    first_text(main.select_one(".hp-destination .hp-button"),l["guide"] if "guide" in l else DICT[lang]["guide"])
    opt(main,".hp-programs .hp-kicker",w["programs"]);rich(main.select_one(".hp-programs h2"),w["programTitle"],"")
    opt(main,".hp-programs .hp-heading p",PAGES["programme"][lang]["lead"])
    for i,pr in enumerate(main.select(".hp-program")):
        opt(pr,"h3",w["programNames"][i])
        opt(pr,">p",PAGES["programme"][lang]["sections"][i][1])
        spans=pr.select(".hp-program-details span")
        if len(spans)>1:first_text(spans[1],w["programLevels"][i])
        opt(pr,".hp-program-foot small",w["perGroup"])
        first_text(pr.select_one(".hp-program-foot a"),w["programDetail"])
    first_text(main.select_one(".hp-prog-cta"),w["request"])
    opt(main,".hp-trust .hp-kicker",w["why"]);rich(main.select_one(".hp-trust h2"),w["whyTitle"],"")
    for i,item in enumerate(main.select(".hp-trust-item")):
        opt(item,"h3",w["trust"][i]);opt(item,"p",w["trustDesc"][i])
    opt(main,".hp-season .hp-kicker",w["season"]);opt(main,".hp-season h2",w["seasonTitle"])
    opt(main,".hp-season p",PAGES["index"][lang]["sections"][0][1])
    first_text(main.select_one(".hp-season .hp-button"),w["visit"])
    opt(main,".hp-memories .hp-kicker",w["photos"]);rich(main.select_one(".hp-memories h2"),w["photosTitle"],"")
    opt(main,".hp-memories p",PAGES["memories"][lang]["lead"])
    first_text(main.select_one(".hp-plain-link"),w["viewPhotos"])
    opt(main,".hp-explore .hp-kicker",w["explore"]);rich(main.select_one(".hp-explore h2"),w["exploreTitle"],"")
    for i,link in enumerate(main.select(".hp-link-card")):
        opt(link,"h3",w["exploreCards"][i]);opt(link,"p",w["exploreText"][i]);first_text(link.select_one("span"),w["exploreCTA"][i])
    opt(main,".hp-reviews strong",w["reviewsTitle"]);opt(main,".hp-reviews p",w["reviews"])
    first_text(main.select_one(".hp-reviews>a"),w["reviewLink"])
    opt(main,".hp-final .hp-kicker",w["endKicker"]);rich(main.select_one(".hp-final h2"),w["endTitle"],"")
    opt(main,".hp-final p",PAGES["index"][lang]["sections"][2][1])
    buttons=main.select(".hp-final-buttons a")
    if len(buttons)==2:first_text(buttons[0],w["request"]);first_text(buttons[1],w["contact"])
    for el in main.select('a[aria-label],button[aria-label]'):
        if el.get("aria-label","").startswith(("Découvrir","Afficher la photo","Photo ","Galerie photos")):
            el["aria-label"]=w["see"]
    if len(main.select(".hp-slide"))!=5 or len(main.select(".hp-activity-card"))!=14:raise RuntimeError("Original premium visuals missing")
    return str(main)

def subpage_main(lang,page):
    data=PAGES[page][lang];t=LABELS[lang];w=W[lang]
    image=E("../images/"+PAGES[page]["img"])
    title=E(data["title"])
    para=E(data["lead"])
    hero=(f'<section class="hp-hero"><div class="hp-hero-inner"><div class="hp-hero-content">'
       f'<span class="hp-eyebrow">{E(data["kicker"])}</span><h1>{title}</h1><p>{para}</p>'
       f'<div class="hp-hero-buttons"><a class="hp-button hp-button-gold" href="booking.html">{E(t["book"])} ↗</a>'
       f'<a class="hp-button hp-button-outline" href="#details">{E(t["more"])} ↗</a></div>'
       f'<div class="hp-hero-foot">{E(t["about_trip"])}</div></div>'
       f'<div class="hp-hero-visual hp-hero-slider"><div class="hp-slide-track"><div class="hp-slide is-active">'
       f'<img class="hp-hero-image" src="{image}" alt="{title}" decoding="async" fetchpriority="high" style="object-position:center 70%"></div></div>'
       f'<div class="hp-hero-picture-note"><span>{E(w["photoPlace"])}</span><strong>{E(data["kicker"])}</strong></div></div>'
       f'</div></section>')
    features=''.join(f'<div class="hp-trust-item"><div class="hp-trust-icon"><i class="fa-solid fa-compass"></i></div>'
       f'<h3>{E(h)}</h3><p>{E(p)}</p></div>' for h,p in data["sections"])
    details=(f'<section class="hp-trust" id="details"><div class="hp-container"><div class="hp-heading">'
       f'<span class="hp-kicker">{E(data["kicker"])}</span><h2>{title}</h2></div>'
       f'<div class="hp-trust-grid">{features}</div></div></section>')
    further=''
    if page in ("booking","contact"):
        further=request_form(lang)
    elif page=="blog":
        arts=[]
        for topic in TOPICS:
            name=SPANISH[topic["slug"]][0] if lang=="es" else topic["ar"]
            desc=SPANISH[topic["slug"]][1] if lang=="es" else topic["descar"]
            arts.append(f'<article class="hp-activity-card"><a class="hp-activity-image" href="blog-guide-{E(topic["slug"])}.html">'
               f'<img src="{E(topic["image"])}" alt="{E(name)}" loading="lazy" decoding="async"></a>'
               f'<div class="hp-activity-body"><h3>{E(name)}</h3><p>{E(desc)}</p>'
               f'<div class="hp-activity-bottom"><a href="blog-guide-{E(topic["slug"])}.html">{E(w["more"])} ↗</a></div></div></article>')
        further=f'<section class="hp-activities"><div class="hp-container"><div class="hp-activity-grid">{"".join(arts)}</div></div></section>'
    elif page=="memories":
        photos=["21.webp","24.webp","27.webp","29.webp","31.webp","19.webp","20-800.webp","guide-800.webp"]
        further='<section class="hp-memories hp-container"><div class="hp-memories-heading"><div class="hp-heading"><h2>'+E(w["photosTitle"])+'</h2></div></div><div class="hp-memories-grid">'+''.join('<a href="../images/'+img+'"><img loading="lazy" src="../images/'+img+'" alt="Imsfrane Cathédrale"></a>' for img in photos)+'</div></section>'
    elif page=="index":pass
    else:
        items=[]
        for slug in ("rafting","camping","randonnee","vtt","quad","hebergement"):
            if slug==page:continue
            d=PAGES[slug][lang]
            items.append(f'<article class="hp-activity-card"><a class="hp-activity-image" href="{slug}.html">'
                f'<img loading="lazy" decoding="async" src="../images/{E(PAGES[slug]["img"])}" alt="{E(d["title"])}"></a>'
                f'<div class="hp-activity-body"><h3>{E(ACTIVITY_NAMES[lang][{"rafting":0,"camping":1,"randonnee":2,"vtt":3,"quad":4,"hebergement":5}[slug]])}</h3>'
                f'<p>{E(d["lead"])}</p><div class="hp-activity-bottom"><a href="{slug}.html">{E(w["more"])} ↗</a></div></div></article>')
        further=f'<section class="hp-activities"><div class="hp-container"><div class="hp-heading"><h2>{E(w["choose"])}</h2></div><div class="hp-activity-grid">{"".join(items)}</div></div></section>'
    ending=(f'<section class="hp-final"><div class="hp-container"><span class="hp-kicker">{E(w["endKicker"])}</span>'
       f'<h2>{E(w["endTitle"])}</h2><p>{E(t["disclaimer"])}</p>'
       f'<div class="hp-final-buttons"><a class="hp-button hp-button-gold" href="booking.html">{E(w["request"])} ↗</a>'
       f'<a class="hp-button hp-button-outline" href="https://wa.me/212667772551" target="_blank" rel="noopener noreferrer">'
       f'{E(w["contact"])}</a></div></div></section>')
    return f'<main id="mainContent" class="hp-home" style="padding:0;max-width:none;margin:0">{hero}{details}{further}{ending}</main>'
def meta_replace(s,lang,page):
    title=PAGES[page][lang]["title"];desc=PAGES[page][lang]["lead"]
    s=re.sub(r'<html\b[^>]*>',f'<html lang="{lang}"'+(' dir="rtl"' if lang=="ar" else '')+'>',s,count=1,flags=re.I)
    s=re.sub(r'<title\b[^>]*>[\s\S]*?</title>',"<title>"+E(title)+" | Imsfrane Cathédrale</title>",s,count=1,flags=re.I)
    s=re.sub(r'<meta[^>]+name="description"[^>]*>',"",s,flags=re.I)
    s=s.replace('</head>',f'<meta name="description" content="{E(desc[:290])}"></head>',1)
    # Remove old official canonical and alternates, replace with Demo-only links.
    s=re.sub(r'<link\b(?=[^>]*\b(?:rel="canonical"|hreflang=|rel="alternate"))[^>]*>',"",s,flags=re.I)
    s=s.replace('</head>',f'<link rel="canonical" href="https://imsfraneinfo.github.io/Imsfrane-demo/{lang}/{page}.html"></head>',1)
    for code in ("fr","en","ar","es"):
        s=s.replace('</head>',f'<link rel="alternate" hreflang="{code}" href="https://imsfraneinfo.github.io/Imsfrane-demo/{code}/{page}.html"></head>',1)
    s=re.sub(r'<body\b([^>]*)\bdata-lang="fr"',lambda m:'<body'+m.group(1)+'data-lang="'+lang+'"',s,count=1,flags=re.I)
    return s
def build(root):
    for lang in ("ar","es"):
        for page in PAGES:
            src=(root/"fr"/(page+".html")).read_text(encoding="utf-8")
            if src.count('src="../images/logo-104.webp"')!=2:raise RuntimeError("Original shell logo changed: "+page)
            if page=="index":main=homepage_main(root,lang)
            else:main=subpage_main(lang,page)
            old=re.search(r'<main\b[^>]*>[\s\S]*?</main>',src,re.I)
            if not old:raise RuntimeError("Source missing main: "+page)
            src=src[:old.start()]+main+src[old.end():]
            # Remove source page-specific JS for cloned localized pages; retain core and
            # homepage five-slide autoplay. Arabic/Spanish booking uses its own JS.
            if page!="index":
                src=re.sub(r'<script\b[^>]*src="\.\./(?:booking-pro\.js|store-pro\.js|js/pages/[^"]*|js/imsfrane-[^"]*|home-pro\.js)"[^>]*></script>',"",src,flags=re.I)
            if '../home-pro.css' not in src:
                src=src.replace('</head>','<link rel="stylesheet" href="../home-pro.css"></head>',1)
            if page in ("booking","contact"):
                src=src.replace('</head>','<link rel="stylesheet" href="../localized-site.css"></head>',1)
                src=src.replace('</body>','<script defer src="../localized-site.js"></script></body>',1)
            src=meta_replace(src,lang,page)
            doc=BeautifulSoup(src,"html.parser")
            header_localize(doc,lang);footer_localize(doc,lang)
            src=str(doc)
            if src.count('src="../images/logo-104.webp"')!=2:raise RuntimeError("Mirrored header/footer logo modified: "+lang+"/"+page)
            if src.count('<main')!=1:raise RuntimeError("Main count mismatch")
            if page=="index" and (src.count('data-slide="')!=5 or src.count('hp-activity-card')!=14):
                raise RuntimeError("Original slider/cards removed")
            (root/lang/(page+".html")).write_text(src,encoding="utf-8")
        print(f"[Mirror] {lang}: 15 core pages reusing the source French design, real original logo, homepage hero and 14 activities.")
if __name__=="__main__":build(Path("public"))
