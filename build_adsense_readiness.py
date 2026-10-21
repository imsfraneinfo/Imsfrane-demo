"""Consolidate retired articles and clean verified publishing defects.

Run last, after the existing article/locale builders. No external dependencies.
This does not submit AdSense or claim approval.
"""
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
import html
import json
import re
import sys

LANGS = ('fr', 'en', 'ar', 'es')
KEEP = {
    'blog-guide-rafting-season', 'blog-guide-imsfrane-summit',
    'blog-guide-ahansal-gorges-walk', 'blog-guide-wild-camping',
    'blog-guide-vtt-imsfrane', 'blog-guide-access-imsfrane',
    'blog-rafting-50-km-bin-el-ouidane',
}
HOST = 'https://imsfrane.com'
ADS = re.compile(r'<script\b(?=[^>]*src=["\'][^"\']*(?:adsbygoogle|fundingchoices))[^>]*>.*?</script>', re.I | re.S)
ROBOTS = re.compile(r'<meta\b(?=[^>]*name=["\'](?:robots|googlebot)["\'])[^>]*>', re.I)
WORDS = {
 'fr': ('Lire le guide complet', 'Politique de confidentialité', 'Notre équipe locale vous accompagne dans la préparation et le déroulement de votre séjour. Pour les demandes et la coordination des activités, votre interlocuteur est Farid Laydi, à Tilouguite, dans la province d’Azilal.'),
 'en': ('Read the full guide', 'Privacy policy', 'Our local team helps you prepare your visit and organise activities during your stay. For enquiries and activity coordination, your contact is Farid Laydi, based in Tilouguite, in Azilal province.'),
 'es': ('Leer la guía completa', 'Política de privacidad', 'Nuestro equipo local te ayuda a preparar la visita y a organizar las actividades durante tu estancia. Para consultas y coordinación, tu contacto es Farid Laydi, en Tilouguite, provincia de Azilal.'),
 'ar': ('اقرأ الدليل الكامل', 'سياسة الخصوصية', 'يساعدكم فريقنا المحلي على إعداد الزيارة وتنظيم الأنشطة خلال إقامتكم. للاستفسار وتنسيق الأنشطة، يمكنكم التواصل مع فريد العايدي في تيلوكيت، بإقليم أزيلال.'),
}

def destination(slug):
    if 'vtt' in slug: return 'blog-guide-vtt-imsfrane'
    if any(k in slug for k in ('camping', 'leave-no-trace')): return 'blog-guide-wild-camping'
    if any(k in slug for k in ('rafting', 'melloul', 'best-seasons')): return 'blog-guide-rafting-season'
    if any(k in slug for k in ('gorges', 'ahansal', 'waterfall', 'wakoudene')): return 'blog-guide-ahansal-gorges-walk'
    if any(k in slug for k in ('tilouguite', 'three-days', 'road-trip', 'amazigh-culture')): return 'blog-guide-access-imsfrane'
    return 'blog-guide-imsfrane-summit'

def redirect(lang, target):
    url = f'/{lang}/{target}/'
    return ('<!doctype html>\n<!-- IMSFRANE_CONSOLIDATED_ARTICLE -->\n'
        f'<html lang="{lang}"'+(' dir="rtl"' if lang == 'ar' else '')+'><head>'
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,follow">'
        f'<title>{html.escape(WORDS[lang][0])} | Imsfrane Cathédrale</title>'
        f'<link rel="canonical" href="{HOST}{url}">'
        f'<meta http-equiv="refresh" content="0;url={url}">'
        f'<script>location.replace({json.dumps(url)}+location.search+location.hash);</script>'
        f'</head><body><p><a href="{url}">{WORDS[lang][0]}</a></p></body></html>\n')

def build(root):
    root = Path(root)
    changed = set()
    def write(p, text):
        if p.read_text(encoding='utf-8') != text:
            p.write_text(text, encoding='utf-8'); changed.add(str(p.relative_to(root)))
    retired = {}
    for lang in LANGS:
        for p in (root/lang).glob('blog-*/index.html'):
            slug = p.parent.name
            if slug in KEEP: continue
            target = destination(slug)
            retired[f'/{lang}/{slug}/'] = f'/{lang}/{target}/'
            retired[f'/{lang}/{slug}.html'] = f'/{lang}/{target}/'
            write(p, redirect(lang, target))
            old = root/lang/(slug+'.html')
            if old.exists(): write(old, redirect(lang, target))

    # Update links, not image filenames or arbitrary article text.
    link_pattern = re.compile(r'(?P<prefix>href\s*=\s*["\'])(?P<url>[^"\']+)(?P<end>["\'])', re.I)
    def fix_link(m):
        u = urlsplit(html.unescape(m['url']))
        if u.netloc and u.netloc not in ('imsfrane.com', 'www.imsfrane.com'): return m[0]
        if u.path not in retired: return m[0]
        url = retired[u.path] + ('?'+u.query if u.query else '')
        # Old section anchors do not exist in the consolidated guide.
        return m['prefix']+url+m['end']

    for p in root.rglob('*.html'):
        if any(part.startswith('.') for part in p.relative_to(root).parts): continue
        text = p.read_text(encoding='utf-8')
        text = link_pattern.sub(fix_link, text)
        # Utility/error/redirect pages must not request advertising.
        utility = p.name in ('404.html', 'members.html', 'members-preview.html', 'article.html', 'blog-post.html')
        is_redirect = bool(re.search(r'<meta\b(?=[^>]*http-equiv=["\']refresh["\'])', text, re.I))
        if utility or is_redirect or p == root/'index.html':
            text = ADS.sub('', text)
        if utility and '</head>' in text:
            text = ROBOTS.sub('', text).replace('</head>', '<meta name="robots" content="noindex,follow"></head>', 1)
        # Remove the obsolete publisher identifier from any remaining HTML.
        text = text.replace('ca-pub-3106160668387388', 'ca-pub-5598024978912334')
        write(p, text)

    for lang in LANGS:
        p = root/lang/'about/index.html'
        text = p.read_text(encoding='utf-8')
        replacements = {
          'Les portraits originaux de notre équipe seront ajoutés ici.': '',
          'Our team photographs will be added here in their original quality.': '',
          'Aquí añadiremos los retratos originales del equipo.': '',
          'ستُضاف هنا صور فريقنا الأصلية.': '',
        }
        for old, new in replacements.items(): text = text.replace(old, new)
        marker = '<!-- IMSFRANE_LOCAL_CONTACT -->'
        if marker not in text:
            text = re.sub(r'(<p class="team-note">.*?</p>)', lambda m:m[0]+marker+'<p>'+WORDS[lang][2]+'</p>', text, count=1, flags=re.S)
        # About pages had copied contact-page social metadata.
        title = html.unescape(re.search(r'<title[^>]*>(.*?)</title>',text,re.S)[1])
        desc = html.unescape(re.search(r'<meta\b(?=[^>]*name="description")(?=[^>]*content="([^"]*)")[^>]*>', text)[1])
        def meta(m):
            tag=m[0]
            if re.search(r'(?:property|name)="(?:og:title|twitter:title|og:image:alt|twitter:image:alt)"', tag):
                return re.sub(r'content="[^"]*"', 'content="'+html.escape(title, quote=True)+'"', tag)
            if re.search(r'(?:property|name)="(?:og:description|twitter:description)"', tag):
                return re.sub(r'content="[^"]*"', 'content="'+html.escape(desc, quote=True)+'"', tag)
            return tag
        text = re.sub(r'<meta\b[^>]*>',meta,text)
        write(p,text)

    # Visible policy links must also exist without running JavaScript.
    for lang in LANGS:
        for p in (root/lang).rglob('*.html'):
            text=p.read_text(encoding='utf-8')
            if '</footer>' not in text or 'ims-privacy-link' in text: continue
            text=text.replace('</footer>', f'<p><a class="ims-privacy-link" href="/{lang}/privacy/">{WORDS[lang][1]}</a></p></footer>',1)
            write(p,text)

    # Remove unpublished implementation instructions from the public policy.
    consent = {
      'fr': ('à configurer et publier dans Google AdSense', 'permettant de gérer les choix applicables'),
      'en': ('once configured and published in Google AdSense', 'to manage the applicable choices'),
      'es': ('una vez configurada y publicada en Google AdSense', 'para gestionar las opciones aplicables'),
      'ar': ('بعد إعدادها ونشرها في Google AdSense', 'لإدارة الخيارات المناسبة'),
    }
    for lang,(old,new) in consent.items():
        p=root/lang/'privacy/index.html';write(p,p.read_text(encoding='utf-8').replace(old,new))

    # A 404 is served at the missing URL; relative links would break again.
    p=root/'404.html';text=p.read_text(encoding='utf-8')
    text=re.sub(r'((?:href|src)=["\'])(?=(?:css|images|en|fr)/)',r'\1/',text)
    text=text.replace('href="/en/index.html"','href="/en/"').replace('href="/fr/index.html"','href="/fr/"')
    text=re.sub(r'href="/(en|fr)/([a-z]+)\.html"',r'href="/\1/\2/"',text)
    if 'href="/ar/"' not in text:
        text=text.replace('<div class="error-links">','<div class="error-links"><a href="/ar/" lang="ar" dir="rtl">العربية</a><a href="/es/" lang="es">Español</a>')
    write(p,text)

    p=root/'index.html';text=p.read_text(encoding='utf-8')
    if 'href="/ar/"' not in text:
        text=text.replace('</p>',' · <a href="/ar/" lang="ar" dir="rtl">العربية</a> · <a href="/es/" lang="es">Español</a></p>',1)
    write(p,text)

    p=root/'ads.txt'
    write(p,'google.com, pub-5598024978912334, DIRECT, f08c47fec0942fa0\n')
    p=root/'sitemap.xml'
    tree=ET.parse(p); ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
    for entry in list(tree.getroot()):
        loc=entry.find(ns+'loc')
        if loc is not None and urlsplit(loc.text).path in retired:
            tree.getroot().remove(entry)
    ET.register_namespace('',ns[1:-1]);ET.register_namespace('xhtml','http://www.w3.org/1999/xhtml')
    text=ET.tostring(tree.getroot(),encoding='unicode')
    write(p,"<?xml version='1.0' encoding='utf-8'?>\n"+text)
    print(json.dumps({'changed_files':len(changed),'retired_article_routes':len(retired)//2,'kept_articles_per_language':len(KEEP)},ensure_ascii=False))
    return changed

if __name__ == '__main__':
    build(Path(sys.argv[1] if len(sys.argv)>1 else 'public'))
