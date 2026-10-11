"""Deploy the approved Triplan-inspired navigation on all four Demo languages.

Never edit the official GitHub repo, rewrite images/logos, or replace page main content.
Only HTML in public/fr, public/en, public/ar and public/es is patched during the Demo build.
"""
from __future__ import annotations

from pathlib import Path
from html import escape
from collections import Counter
import re

ICON_PATHS = {
    "home": '<path d="m3 11 9-8 9 8M5 10v11h14V10M9 21v-7h6v7"/>',
    "water": '<path d="M2 8c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2 2-2 4-2M2 13c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2 2-2 4-2M2 18c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2 2-2 4-2"/>',
    "tent": '<path d="M3 20 12 5l9 15H3ZM7 20l5-8 5 8M12 5v-2"/>',
    "hike": '<circle cx="15.5" cy="3.5" r="1.6"/><path d="m13 8-3 4-5-1M13 8l3 5 4 1M13 8l-1-2M10 12l3 3-2 6M13 15l4 2 1 4M5 21l2-5 3-4"/>',
    "bike": '<circle cx="5.5" cy="17.5" r="3.5"/><circle cx="18.5" cy="17.5" r="3.5"/><path d="M5.5 17.5 10 10h4l4.5 7.5H11l-4-7h-2M10 10l-1-2h-2M14 10l1-2h3"/>',
    "quad": '<circle cx="5" cy="18" r="3"/><circle cx="19" cy="18" r="3"/><path d="M8 18h8l-2-6-3-3H7l-3 5M11 9h5l2-3M7 9l-2-2M15 13h5l1 2"/>',
    "bed": '<path d="M3 4v16M3 17h18v3M4 12h17v5H4V12ZM5 9h6v3H5V9ZM13 9h6v3h-6V9Z"/>',
    "close": '<path d="M18 6 6 18M6 6l12 12"/>',
    "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "route": '<circle cx="6" cy="19" r="2"/><path d="M9 19h7a5 5 0 0 0 0-10h-8a4 4 0 1 1 0-8h10"/>',
    "book": '<path d="M4 4h15v17H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2ZM4 17h15M7 8h9"/>',
    "camera": '<path d="M3 7h4l2-3h6l2 3h4v13H3V7Z"/><circle cx="12" cy="13" r="4"/>',
    "shop": '<path d="M4 9 6 3h12l2 6v12H4V9ZM3 9h18M9 21v-8h6v8"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 11h18M8 16l2 2 5-5"/>',
    "chat": '<path d="M4 5h16v12H9l-5 4V5ZM7 9h10M7 13h7"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 11v6M12 7v.4"/>',
}

DICT = {
    "fr": {
        "home": "Accueil", "activity": "Activités", "route": "Programmes",
        "booking": "Réservation", "book": "Réserver", "gallery": "Galerie & souvenirs",
        "guide": "Guide pratique", "about": "Qui sommes-nous ?", "blog": "Blog",
        "shop": "Boutique", "contact": "Contact", "heading": "EXPLORER IMSFRANE",
        "services": "NOS SERVICES", "prepare": "PRÉPARER VOTRE SÉJOUR",
        "more": "PLUS D’INFO", "hike": "Randonnée", "vtt": "VTT",
        "quad": "Quad", "stay": "Hébergement",
        "menu_open": "Ouvrir le menu", "menu_close": "Fermer le menu",
        "nav": "Menu de navigation Imsfrane Cathédrale",
    },
    "en": {
        "home": "Home", "activity": "Activities", "route": "Programs",
        "booking": "Booking", "book": "Book now", "gallery": "Gallery & memories",
        "guide": "Travel guide", "about": "About us", "blog": "Blog",
        "shop": "Shop", "contact": "Contact", "heading": "EXPLORE IMSFRANE",
        "services": "OUR SERVICES", "prepare": "PLAN YOUR STAY",
        "more": "MORE INFORMATION", "hike": "Hiking", "vtt": "Mountain biking",
        "quad": "Quad biking", "stay": "Accommodation",
        "menu_open": "Open menu", "menu_close": "Close menu",
        "nav": "Imsfrane Cathédrale site menu",
    },
    "ar": {
        "home": "الرئيسية", "activity": "الأنشطة", "route": "البرامج",
        "booking": "طلب حجز", "book": "احجز رحلتك", "gallery": "الصور والذكريات",
        "guide": "دليل الزيارة", "about": "من نحن؟", "blog": "المدونة",
        "shop": "المتجر", "contact": "اتصل بنا", "heading": "اكتشف مسفران",
        "services": "تجاربنا", "prepare": "خطّط لرحلتك",
        "more": "معلومات إضافية", "hike": "المشي الجبلي", "vtt": "الدراجات الجبلية",
        "quad": "جولات الكواد", "stay": "الإقامة",
        "menu_open": "افتح القائمة", "menu_close": "أغلق القائمة",
        "nav": "قائمة موقع مسفران كاتدرال",
    },
    "es": {
        "home": "Inicio", "activity": "Actividades", "route": "Programas",
        "booking": "Reservas", "book": "Reservar", "gallery": "Galería y recuerdos",
        "guide": "Guía práctica", "about": "Quiénes somos", "blog": "Blog",
        "shop": "Tienda", "contact": "Contacto", "heading": "DESCUBRE IMSFRANE",
        "services": "NUESTROS SERVICIOS", "prepare": "PREPARA TU VIAJE",
        "more": "MÁS INFORMACIÓN", "hike": "Senderismo", "vtt": "Bicicleta de montaña",
        "quad": "Rutas en quad", "stay": "Alojamiento",
        "menu_open": "Abrir menú", "menu_close": "Cerrar menú",
        "nav": "Menú de Imsfrane Cathédrale",
    },
}

ACTIVITIES = (
    ("rafting.html", "Rafting", "water"),
    ("camping.html", "Camping", "tent"),
    ("randonnee.html", "hike", "hike"),
    ("vtt.html", "vtt", "bike"),
    ("quad.html", "quad", "quad"),
    ("hebergement.html", "stay", "bed"),
)
PLAN = (
    ("programme.html", "route", "route"),
    ("booking.html", "booking", "calendar"),
)
MORE = (
    ("memories.html", "gallery", "camera"),
    ("guide.html", "guide", "book"),
    ("about.html", "about", "info"),
    ("blog.html", "blog", "book"),
    ("store.html", "shop", "shop"),
    ("contact.html", "contact", "chat"),
)

def clean(v):
    return escape(str(v), quote=True)

def icon(name):
    if name not in ICON_PATHS:
        raise RuntimeError(f"Unknown menu icon: {name}")
    return f'<svg aria-hidden="true"><use href="#atnav-i-{name}"></use></svg>'

def sprite():
    return (
        '<svg aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" '
        'style="position:absolute;width:0;height:0;overflow:hidden" width="0" height="0">'
        + ''.join(f'<symbol id="atnav-i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k,v in ICON_PATHS.items())
        + '</svg>'
    )

def page_name(current_file, lang, key):
    if key in DICT[lang]:
        return DICT[lang][key]
    return key

def menu_link(filename, key, symbol, lang, current_file, sub=False):
    current = ' aria-current="page"' if current_file == filename else ''
    label = page_name(current_file, lang, key)
    ico = f'<span class="atnav-subicon">{icon(symbol)}</span>' if sub else f'<span class="atnav-item-icon">{icon(symbol)}</span>'
    css = "atnav-submenu-link" if sub else "atnav-item"
    return f'<a class="{css}" href="{clean(filename)}"{current}>{ico}<span>{clean(label)}</span></a>'

def nav(lang, current_file, root, logo_prefix):
    t = DICT[lang]
    opposite = "en" if lang == "fr" else "fr"
    active = "true" if current_file in {p[0] for p in ACTIVITIES} else "false"
    # Like the approved preview, open the activities section by default.
    act = ''.join('<li>'+menu_link(p,key,ic,lang,current_file,sub=True)+'</li>' for p,key,ic in ACTIVITIES)
    groups = (
        '<span class="atnav-label">'+clean(t["services"])+'</span>'
        +'<button class="atnav-item atnav-toggle" id="atnavActivities" type="button" aria-expanded="true" aria-controls="atnavActivityList">'
        +'<span class="atnav-item-icon">'+icon("hike")+'</span><span>'+clean(t["activity"])+'</span>'
        +'<span class="atnav-chevron">'+icon("chevron")+'</span></button>'
        +'<div class="atnav-activities" id="atnavActivityList"><ul class="atnav-submenu">'+act+'</ul></div>'
        +'<span class="atnav-label atnav-label-separated">'+clean(t["prepare"])+'</span>'
        +'<div class="atnav-secondary">'
        +''.join(menu_link(p,key,ic,lang,current_file) for p,key,ic in PLAN)
        +'</div>'
        +'<span class="atnav-label atnav-label-separated">'+clean(t["more"])+'</span>'
        +'<div class="atnav-secondary">'
        +''.join(menu_link(p,key,ic,lang,current_file) for p,key,ic in MORE)
        +'</div>'
    )
    langs = '<div class="atnav-languages" aria-label="Language">'
    for code in ("fr","en","ar","es"):
        # Use exactly matching translated URL when available; otherwise go to
        # that language's editorial blog or homepage, never invent a missing page.
        target_file = current_file if (root/code/current_file).is_file() else ("blog.html" if current_file.startswith("blog") else "index.html")
        if not (root/code/target_file).is_file():
            raise RuntimeError("Language menu target missing: "+code+"/"+target_file)
        href = "../"+code+"/"+target_file
        label = "العربية" if code == "ar" else code.upper()
        langs += '<a href="'+clean(href)+'" lang="'+code+'"'+(' aria-current="page"' if lang == code else '')+'>'+label+'</a>'
    langs += '</div>'
    return (
      '<div class="atnav-backdrop" id="atnavBackdrop" aria-hidden="true"></div>'
      +'<aside class="atnav-drawer" id="atnavDrawer" role="dialog" aria-modal="true" aria-hidden="true" '
      +'aria-label="'+clean(t["nav"])+'" inert>'
      +'<div class="atnav-drawer-inner">'
      +'<div class="atnav-drawer-top">'
      +'<div class="atnav-drawer-brand">'
      +'<img alt="Logo Imsfrane Cathédrale" src="'+clean(logo_prefix+'images/logo-104.webp')+'" width="53" height="53">'
      +'<span><strong>Imsfrane Cathédrale</strong><small>HIGH ATLAS · MOROCCO</small></span></div>'
      +'<button type="button" id="atnavClose" class="atnav-close" aria-label="'+clean(t["menu_close"])+'">'+icon("close")+'</button></div>'
      +'<div class="atnav-intro"><span class="atnav-intro-title">'+clean(t["heading"])+'</span><span class="atnav-mark">MENU</span></div>'
      +'<nav aria-label="'+clean(t["nav"])+'">'
      +menu_link("index.html","home","home",lang,current_file)
      +groups
      +'</nav>'
      +'<div class="atnav-actions">'
      +'<a class="atnav-book" href="booking.html">'+icon("calendar")+clean(t["book"])+'</a>'
      +'<a class="atnav-whatsapp" href="https://wa.me/212667772551" target="_blank" rel="noopener noreferrer">'+icon("chat")+'WhatsApp</a>'
      +'</div>'
      +'</div></aside>'
    )

def compact_language(lang, current_file, root):
    labels={"fr":"Français","en":"English","ar":"العربية","es":"Español"}
    opts=[]
    for code in ("fr","en","ar","es"):
        equivalent={
            "blog-d-couvrir-le-jebel-imsfrane-au-c-ur-de-l-atlas.html":{
                "en":"blog-discover-jebel-imsfrane-in-the-heart-of-the-atlas-mountains.html"},
            "blog-discover-jebel-imsfrane-in-the-heart-of-the-atlas-mountains.html":{
                "fr":"blog-d-couvrir-le-jebel-imsfrane-au-c-ur-de-l-atlas.html"},
        }
        target=current_file if (root/code/current_file).is_file() else equivalent.get(current_file,{}).get(code,"blog.html" if current_file.startswith("blog") else "index.html")
        if not (root/code/target).is_file():raise RuntimeError("Missing compact language target")
        opts.append('<a href="../'+code+'/'+target+'" lang="'+code+'"'
           +(' aria-current="page"' if lang==code else '')+'>'
           +'<span class="atnav-lang-code">'+code.upper()+'</span><span>'+labels[code]+'</span></a>')
    return ('<div class="atnav-langmini">'
      +'<button type="button" class="atnav-langmini-trigger" aria-haspopup="true" aria-expanded="false"'
      +' aria-label="'+clean("اختيار اللغة" if lang=="ar" else "Elegir idioma" if lang=="es" else "Choose language" if lang=="en" else "Choisir la langue")+'">'
      +'<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/></svg>'
      +'<span class="atnav-lang-current">'+lang.upper()+'</span>'
      +'<svg class="atnav-mini-chevron" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg></button>'
      +'<div class="atnav-langmini-panel" hidden>'+''.join(opts)+'</div></div>')

def trigger(lang):
    t=DICT[lang]
    return ('<button type="button" class="atnav-open" id="atnavOpen" '
            'aria-controls="atnavDrawer" aria-expanded="false" aria-label="'+clean(t["menu_open"])+'">'
            +icon("menu")+'</button>')

def desktop_nav(lang, page):
    t=DICT[lang]
    items=(("index.html","home"),("programme.html","route"),("guide.html","guide"),("contact.html","contact"))
    return ('<nav class="atnav-desktop" aria-label="'+clean(t["nav"])+'">'
      +''.join('<a href="'+clean(f)+'"'+(' aria-current="page"' if page==f else '')+'>'+clean(t[k])+'</a>' for f,k in items)
      +'</nav>')

def article_header(lang, logo_prefix):
    return ('<header class="atnav-article-header">'
            +'<a class="atnav-article-brand" href="index.html">'
            +'<img src="'+clean(logo_prefix+'images/logo-104.webp')+'" alt="Logo Imsfrane Cathédrale" width="45" height="45">'
            +'<span>Imsfrane Cathédrale</span></a>'
            +'<div class="atnav-article-actions">'
            +'<a class="atnav-article-book" href="booking.html">'+clean(DICT[lang]["book"])+'</a>'
            +trigger(lang)+'</div></header>')

def patch(path, lang, root):
    source=path.read_text(encoding="utf-8")
    if 'id="atnavDrawer"' in source:
        raise RuntimeError(f"Duplicate premium menu in {path}")
    if '</head>' not in source or '</body>' not in source or '<body' not in source:
        raise RuntimeError(f"Missing basic HTML document in {path}")
    before_main=re.search(r'<main\b[^>]*>[\s\S]*?</main>',source,flags=re.I)
    if not before_main and path.name not in {"article.html"}:
        raise RuntimeError(f"Missing main content in {path}")
    current=path.name
    # Every language lives one folder beneath public/. Cross-language targets
    # are checked before rendering; no locale is linked to a missing page.
    logo_prefix="../"
    old_brand_logos=re.findall(r'<img\b[^>]*\bsrc="\.\./images/logo-104\.webp"[^>]*>',source,flags=re.I)
    header_regex=r'<header\b[^>]*\bid="siteHeader"[^>]*>[\s\S]*?</header>'
    match=re.search(header_regex,source,flags=re.I)
    if match:
        if len(old_brand_logos)!=2:
            raise RuntimeError(f"Must preserve header/footer original logo: {path}")
        original_header=match.group(0)
        btn=re.search(r'<button\b[^>]*\bid="menuButton"[^>]*>[\s\S]*?</button>',original_header,flags=re.I)
        if not btn:
            raise RuntimeError(f"Missing existing menu button: {path}")
        new_header=original_header[:btn.end()]+trigger(lang)+original_header[btn.end():]
        actions='<div class="header-actions">'
        if actions not in new_header:
            raise RuntimeError(f"Header actions missing: {path}")
        new_header=new_header.replace(actions,desktop_nav(lang,current)+actions,1)
        locale_block=re.search(r'(<div[^>]*class="language-switcher"[^>]*>[\s\S]*?</div>)',new_header,re.I)
        if not locale_block:raise RuntimeError("Original FR EN selector missing")
        original_langs=locale_block.group(1)
        if lang in ("ar","es"):
            original_langs=original_langs.replace(' aria-current="page"','').replace('class="language-button active editable"','class="language-button editable"').replace('class="language-button active"','class="language-button"')
        # Exactly ONE compact four-language selector. No legacy EN/FR buttons.
        new_header=new_header[:locale_block.start()]+compact_language(lang,current,root)+new_header[locale_block.end():]
        source=source[:match.start()]+new_header+sprite()+nav(lang,current,root,logo_prefix)+source[match.end():]
    else:
        # Standalone editorial articles have no site-wide header; supply a compact
        # branded header without modifying their original article or footer.
        body_match=re.search(r'<body\b[^>]*>',source,flags=re.I)
        if body_match is None:
            raise RuntimeError(f"Article body tag missing: {path}")
        article_markup=article_header(lang,logo_prefix)
        article_markup=article_markup.replace('<div class="atnav-article-actions">','<div class="atnav-article-actions">'+compact_language(lang,current,root),1)
        insertion=sprite()+article_markup+nav(lang,current,root,logo_prefix)
        source=source[:body_match.end()]+insertion+source[body_match.end():]
    class_body=re.search(r'<body\b[^>]*\bclass="([^"]*)"',source,flags=re.I)
    if class_body:
        value=class_body.group(1)
        new_body=class_body.group(0).replace('class="'+value+'"','class="'+value+' atnav-ready"')
        source=source[:class_body.start()]+new_body+source[class_body.end():]
    else:
        source=re.sub(r'<body\b', '<body class="atnav-ready"',source,count=1,flags=re.I)
    # Add search-engine alternates only where corresponding translations exist.
    for code in ("ar","es"):
        target=root/code/current
        if target.is_file() and not re.search(r'<link[^>]*hreflang="'+code+r'"',source,flags=re.I):
            source=source.replace('</head>','<link rel="alternate" hreflang="'+code+'" href="https://imsfraneinfo.github.io/Imsfrane-demo/'+code+'/'+current+'"></head>',1)
    source=source.replace('</head>','<link rel="stylesheet" href="../navigation-pro.css"></head>',1)
    source=source.replace('</body>','<script defer src="../navigation-pro.js"></script></body>',1)
    # Full content preservation check: the exact text, markup and internal structure
    # of the existing page main must be byte-for-byte identical.
    after_main=re.search(r'<main\b[^>]*>[\s\S]*?</main>',source,flags=re.I)
    if (before_main.group(0) if before_main else None)!=(after_main.group(0) if after_main else None):
        raise RuntimeError(f"Main content changed: {path}")
    changed_brand_logos=re.findall(r'<img\b[^>]*\bsrc="\.\./images/logo-104\.webp"[^>]*>',source,flags=re.I)
    if any(changed_brand_logos.count(tag)<n for tag,n in Counter(old_brand_logos).items()):
        raise RuntimeError(f"Original branded logo was modified: {path}")
    if len(re.findall(r'class="atnav-submenu-link"',source))!=6:
        raise RuntimeError(f"Wrong number of activities in navigation: {path}")
    if source.count('id="atnavDrawer"')!=1 or source.count('id="atnavOpen"')!=1:
        raise RuntimeError(f"Navigation markup invalid: {path}")
    path.write_text(source,encoding="utf-8")

def build(root: Path):
    counts={}
    for lang in ("fr","en","ar","es"):
        folder=root/lang
        pages=sorted(folder.glob("*.html"))
        if not pages:
            raise RuntimeError("No Demo pages found: "+lang)
        for page in pages:
            patch(page,lang,root)
        counts[lang]=len(pages)
        print(f"[Menu PRO] {lang}: {len(pages)} pages, 6 linked activities, original page content unchanged")
    return counts

if __name__=="__main__":
    build(Path("public"))
