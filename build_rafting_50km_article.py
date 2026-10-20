"""Publish the four-language illustrated expedition article on the Demo snapshot."""

from pathlib import Path
from html import escape
import json
import re
import xml.etree.ElementTree as ET


SLUG = 'blog-rafting-50-km-bin-el-ouidane'
TEMPLATE = 'blog-guide-rafting-season'
LANGS = ('fr', 'en', 'ar', 'es')
BASE = Path(__file__).parent
DATA = json.loads((BASE / 'rafting-50km-article.json').read_text(encoding='utf-8'))

CSS = '''<style id="rafting-expedition-editorial">
.expedition-hero{background:#102f2b;color:#fff;padding:54px 24px 64px}
.expedition-hero-inner{width:min(1120px,100%);margin:auto;display:grid;grid-template-columns:1.15fr .85fr;gap:48px;align-items:center}
.expedition-hero h1{font:600 clamp(36px,4.3vw,66px)/1.12 Georgia,serif;margin:18px 0 24px;letter-spacing:-.02em;color:#fff}
.expedition-hero p{color:#dae5df;font-size:17px;line-height:1.8}
.expedition-kicker{color:#e0c17a;font-size:12px;font-weight:700;letter-spacing:.1em}
.expedition-hero figure{margin:0;max-width:420px;justify-self:center}
.expedition-hero img,.expedition-photo img{display:block;width:100%!important;height:auto!important;max-height:none!important;aspect-ratio:auto!important;object-fit:contain!important;transform:none!important;border-radius:10px}
.expedition-hero figcaption{font-size:12px;color:#d4dfd8;padding-top:12px;line-height:1.7}
.expedition-photo{margin:24px auto 32px;width:100%;max-width:620px}
.expedition-photo.portrait{max-width:340px}
.expedition-photo-pair{display:grid;grid-template-columns:1fr 1fr;gap:18px;align-items:center;margin:24px 0 32px}
.expedition-photo-pair .expedition-photo{margin:0;max-width:none}
.expedition-article .article-lead{font-size:19px;line-height:1.8;margin-bottom:30px}
.expedition-article>section{margin-bottom:30px}
.expedition-article>section p{font-size:16px;line-height:1.9}
.expedition-article>section h2{font-size:clamp(25px,3vw,34px)}
.expedition-photo figcaption{font-size:13px;color:#617269;line-height:1.7;padding:13px 0;border-bottom:1px solid #dce4db}
.expedition-article section{scroll-margin-top:100px}
html[lang="ar"] .expedition-hero h1{font-family:"Imsfrane Alexandria",Tahoma,sans-serif;line-height:1.65;font-size:clamp(30px,3.5vw,47px);letter-spacing:0}
html[lang="ar"] .expedition-hero p,html[lang="ar"] .expedition-hero figcaption,html[lang="ar"] .expedition-article{font-family:"Imsfrane Tajawal",Tahoma,sans-serif}
@media(max-width:760px){.expedition-hero{padding:32px 20px 38px}.expedition-hero-inner{grid-template-columns:1fr;gap:28px}.expedition-hero h1{font-size:38px}.expedition-hero figure{max-width:460px}.expedition-photo{margin:28px auto 38px}.expedition-hero p{font-size:16px}}
</style>'''

def photo(name, caption, hero=False):
    # Dimensions verified against the original WebP headers.
    dimensions = {
        'IMG_7886.webp': (1152, 1536), 'IMG_6626.webp': (1152, 1536),
        'IMG_2101.webp': (1152, 1536), 'IMG_bivouac-river-meal.webp': (825, 1100),
        'IMG_bivouac-day.webp': (1100, 825), 'IMG_bivouac-dinner.webp': (1400, 1050),
        'IMG_bivouac-night.webp': (1050, 1400),
    }
    width, height = dimensions[name]
    cls = '' if hero else ' class="expedition-photo' + (' portrait' if height > width else '') + '"'
    loading = 'fetchpriority="high"' if hero else 'loading="lazy"'
    return (f'<figure{cls}><img src="/images/{name}" width="{width}" height="{height}" '
            f'alt="{escape(caption, quote=True)}" {loading} decoding="async">'
            f'<figcaption>{escape(caption)}</figcaption></figure>')


def article(root, lang):
    d = DATA[lang]
    source = (root / lang / TEMPLATE / 'index.html').read_text(encoding='utf-8')
    source = source.replace(TEMPLATE, SLUG)
    source = re.sub(r'<title>.*?</title>', '<title>' + escape(d['title']) + ' | Imsfrane Cathédrale</title>', source, count=1, flags=re.S)
    for key, value in [('description', d['description']), ('og:title', d['title']), ('og:description', d['description']), ('og:image', 'https://imsfrane.com/images/IMG_7886.webp')]:
        pattern = r'(<meta\b(?=[^>]*(?:name|property)="' + re.escape(key) + r'")[^>]*content=")[^"]*(")'
        source = re.sub(pattern, lambda m: m[1] + escape(value, quote=True) + m[2], source)
    schema = {
        '@context': 'https://schema.org', '@type': 'BlogPosting',
        'headline': d['title'], 'description': d['description'], 'inLanguage': lang,
        'mainEntityOfPage': {'@type': 'WebPage', '@id': f'https://imsfrane.com/{lang}/{SLUG}/'},
        'image': ['https://imsfrane.com/images/' + name for name in (
            'IMG_7886.webp', 'IMG_bivouac-day.webp', 'IMG_bivouac-night.webp')],
        'author': {'@type': 'Organization', 'name': 'Imsfrane Cathédrale'},
        'publisher': {'@type': 'Organization', 'name': 'Imsfrane Cathédrale'},
        'datePublished': '2026-10-20', 'dateModified': '2026-10-20',
        'wordCount': len(' '.join(p for s in d['sections'] for p in s['paragraphs']).split()),
    }
    source = re.sub(r'<script type="application/ld\+json">.*?</script>',
                    lambda m: '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + '</script>', source, count=1, flags=re.S)
    source = source.replace('</head>', CSS + '</head>', 1)
    source = re.sub(r'<html\b[^>]*>', f'<html lang="{lang}" dir="' + ('rtl' if lang == 'ar' else 'ltr') + '">', source, count=1)
    toc = '<nav class="article-toc" aria-label="' + escape(d['toc']) + '"><strong>' + escape(d['toc']) + '</strong><ol>'
    toc += ''.join(f'<li><a href="#expedition-{i}">{escape(s["title"])}</a></li>' for i, s in enumerate(d['sections'], 1)) + '</ol></nav>'
    sections = []
    for i, s in enumerate(d['sections'], 1):
        section = f'<section id="expedition-{i}"><h2>{escape(s["title"])}</h2>'
        section += ''.join('<p>' + escape(p) + '</p>' for p in s['paragraphs'])
        if s.get('image') and s.get('second_image'):
            section += '<div class="expedition-photo-pair">' + photo(s['image'], s['caption']) + photo(s['second_image'], s['second_caption']) + '</div>'
        elif s.get('image'):
            section += photo(s['image'], s['caption'])
        sections.append(section + '</section>')
    hero_caption = {
        'fr': 'Un groupe équipé pour le rafting dans la région d’Imsfrane.',
        'en': 'A group equipped for rafting in the Imsfrane region.',
        'ar': 'مجموعة مجهزة للرافتينغ في منطقة مسفران.',
        'es': 'Un grupo equipado para el rafting en la región de Imsfrane.',
    }[lang]
    main = ('<main><header class="expedition-hero"><div class="expedition-hero-inner"><div>'
            '<span class="expedition-kicker">AHANSAL · 50 KM · ' + {'ar': 'يومان', 'fr': '2 JOURS', 'en': '2 DAYS', 'es': '2 DÍAS'}[lang] + '</span>'
            '<h1>' + escape(d['title']) + '</h1><p>' + escape(d['subtitle']) + '</p></div>'
            + photo('IMG_7886.webp', hero_caption, True) + '</div></header>'
            '<div class="article-layout"><article class="article-body expedition-article">'
            '<p class="article-lead">' + escape(d['lead']) + '</p>' + ''.join(sections)
            + '<aside class="article-note">' + escape(d['note']) + '</aside>'
            + f'<a class="article-cta" href="/{lang}/contact/">' + escape(d['cta']) + '</a></article></div></main>')
    source, count = re.subn(r'<main\b[^>]*>.*?</main>', lambda m: main, source, count=1, flags=re.S)
    assert count == 1
    target = root / lang / SLUG / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding='utf-8')
    # Legacy links remain usable, matching the official clean-route convention.
    (root / lang / (SLUG + '.html')).write_text(
        f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="robots" content="noindex,follow">'
        f'<meta http-equiv="refresh" content="0;url=/{lang}/{SLUG}/"><link rel="canonical" href="https://imsfrane.com/{lang}/{SLUG}/">'
        f'</head><body><a href="/{lang}/{SLUG}/">{escape(d["title"])}</a></body></html>', encoding='utf-8')


def add_to_blog(root, lang):
    d = DATA[lang]
    path = root / lang / 'blog' / 'index.html'
    html = path.read_text(encoding='utf-8')
    # The official source may already contain the approved article after promotion.
    # Replace its existing card rather than inserting a duplicate on each build.
    html = re.sub(r'<article class="journal-card"[^>]*>.*?</article>',
                  lambda m: '' if SLUG in m[0] else m[0], html, flags=re.S)
    html = re.sub(r'<section class="journal-hero">.*?</section>', '', html, count=1, flags=re.S)
    label = {'fr': 'Le journal', 'en': 'The journal', 'ar': 'المدونة', 'es': 'El blog'}[lang]
    if 'journal-list-title' not in html:
        html = html.replace('<main class="journal-page" id="mainContent">',
                            '<main class="journal-page" id="mainContent" data-blog-layout="compact-nohero">'
                            f'<h1 class="journal-list-title">{label}</h1>', 1)
        html = html.replace('</head>', '<style id="blog-list-nohero">'
                            'main.journal-page .journal-list-title{font-size:30px;line-height:1.4;color:#193d33;max-width:1220px;margin:24px auto 0;padding:0 20px}'
                            'main.journal-page .journal-featured{margin:24px auto 40px}'
                            '@media(max-width:900px){main.journal-page .journal-featured{margin:20px 18px 32px}}'
                            '</style></head>', 1)
    href = f'/{lang}/{SLUG}/'
    title, description = escape(d['title'], quote=True), escape(d['description'], quote=True)
    card = (f'<article class="journal-card" data-title="{title}" data-description="{description}" data-category="{d["category"]}" data-date="2026-10-20">'
            f'<a class="journal-card-image" href="{href}"><img src="/images/IMG_7886.webp" alt="{title}" loading="lazy" decoding="async" style="object-position:50% 100%!important"></a>'
            f'<div class="journal-card-body"><span class="journal-card-category">{d["category"]}</span><h3><a href="{href}">{title}</a></h3><p>{description}</p>'
            f'<div class="journal-card-foot"><span>20 · 10 · 2026</span><a href="{href}">{d["read"]}</a></div></div></article>')
    marker = '<div class="journal-grid" id="journal-grid">'
    assert marker in html
    html = html.replace(marker, marker + card, 1)
    replacements = {
        'fr': [('Six guides pratiques, écrits', 'Des récits et guides pratiques, écrits'), ('Nos six grands guides', 'Nos récits et guides'), ('6 dossiers approfondis', '7 articles et guides')],
        'en': [('Our six essential guides', 'Our stories and practical guides'), ('6 detailed guides', '7 stories and guides')],
        'ar': [('أدلتنا الستة المفصلة', 'مقالاتنا وأدلتنا المفصلة'), ('6 أدلة مفصلة', '7 مقالات وأدلة')],
        'es': [('Nuestras seis guías', 'Nuestros relatos y guías'), ('6 guías detalladas', '7 artículos y guías')],
    }
    for old, new in replacements[lang]:
        html = html.replace(old, new)
    # Highlight the new story without removing any of the six existing guides.
    featured = (f'<section class="journal-featured"><div class="journal-featured-copy"><span class="journal-kicker">'
                + {'fr': 'Nouveau récit', 'en': 'New expedition story', 'ar': 'رحلة جديدة في المدونة', 'es': 'Nuevo relato'}[lang]
                + f'</span><h2><a href="{href}">{title}</a></h2><p>{description}</p><a class="journal-primary-link" href="{href}">{d["read"]}</a></div>'
                + f'<a class="journal-featured-photo" href="{href}"><img src="/images/IMG_7886.webp" alt="{title}" loading="lazy" style="object-position:50% 100%!important"></a></section>')
    html, count = re.subn(r'<section class="journal-featured">.*?</section>', lambda m: featured, html, count=1, flags=re.S)
    assert count == 1
    path.write_text(html, encoding='utf-8')


def build(root):
    for lang in LANGS:
        article(root, lang)
        add_to_blog(root, lang)
    # The shared navigation replaces the static back-link at runtime. A flat
    # blog.html link resolves inside the article's clean directory and 404s.
    navigation = root / 'navigation-pro.js'
    script = navigation.read_text(encoding='utf-8')
    old = 'link.href="blog.html";'
    new = 'var blogBase=location.pathname.indexOf("/Imsfrane-demo/")===0?"/Imsfrane-demo/":"/";var blogSlash=String.fromCharCode(47);link.href=blogBase+lang+blogSlash+"blog"+blogSlash;'
    assert old in script or new in script, 'Unknown blog return-link implementation'
    navigation.write_text(script.replace(old, new), encoding='utf-8')
    # Refresh the browser's cached navigation on every article using this bar.
    for lang in LANGS:
        for path in (root / lang).rglob('*.html'):
            html = path.read_text(encoding='utf-8')
            if 'article-nav' in html:
                # Render the final link in HTML. Even a cached older script can
                # no longer replace it with a relative blog.html destination.
                label = {'fr': 'Tous les articles', 'en': 'All articles', 'ar': 'جميع المقالات', 'es': 'Todos los artículos'}[lang]
                arrow = '→' if lang == 'ar' else '←'
                back = (f'<nav class="ims-blog-return" aria-label="{label}">'
                        f'<a data-article-back="static-v2" href="https://imsfrane.com/{lang}/blog/" aria-label="{label}">'
                        f'<span class="ims-blog-return-arrow" aria-hidden="true">{arrow}</span><span>{label}</span></a></nav>')
                html = re.sub(r'<header class="article-nav">.*?</header>', lambda m: back, html, count=1, flags=re.S)
                html = re.sub(r'(/navigation-pro\.js)(?:\?[^"\s>]*)?', r'\1?v=blog-return-static-v2', html)
                path.write_text(html, encoding='utf-8')
    sitemap = root / 'sitemap.xml'
    if sitemap.exists():
        text = sitemap.read_text(encoding='utf-8')
        items = []
        for lang in LANGS:
            if f'https://imsfrane.com/{lang}/{SLUG}/</loc>' in text:
                continue
            alternate = ''.join(f'<xhtml:link rel="alternate" hreflang="{other}" href="https://imsfrane.com/{other}/{SLUG}/"/>' for other in LANGS)
            items.append(f'<url><loc>https://imsfrane.com/{lang}/{SLUG}/</loc><lastmod>2026-10-20</lastmod>{alternate}</url>')
        if 'xmlns:xhtml=' not in text:
            text = text.replace('<urlset ', '<urlset xmlns:xhtml="http://www.w3.org/1999/xhtml" ', 1)
        text = text.replace('</urlset>', ''.join(items) + '</urlset>')
        ET.fromstring(text)
        sitemap.write_text(text, encoding='utf-8')
    print('Published illustrated 50 km expedition article in FR, EN, AR and ES')


if __name__ == '__main__':
    import sys
    build(Path(sys.argv[1] if len(sys.argv) > 1 else 'public'))
