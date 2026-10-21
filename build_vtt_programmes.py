"""Build the user's five MTB programmes without changing the shared site shell."""
from pathlib import Path
from html import escape as esc
from urllib.parse import quote
import json
import re

DATA = json.loads((Path(__file__).parent / 'vtt-programmes.json').read_text(encoding='utf-8'))
PHOTOS = ['IMG_9763.webp', 'IMG_2604.webp', 'IMG_8810.webp', 'IMG_2667.webp', 'IMG_7410.webp']
GALLERY = ['IMG_8792.webp', 'IMG_2606.webp', 'IMG_2634.webp', 'IMG_2629.webp']
CSS = '''<style id="vtt-five-programmes">
.vt-page{--vt-green:#123d32;--vt-gold:#d8ba72;background:#f8f7f1;color:#183c32;font-family:Montserrat,Arial,sans-serif;overflow:hidden}
.vt-page *{box-sizing:border-box}.vt-page a{color:inherit}.vt-page .vt-shell{width:min(1180px,calc(100% - 40px));margin:auto}
.vt-page h1,.vt-page h2,.vt-page h3{font-family:'Cormorant Garamond',Georgia,serif;letter-spacing:-.025em;line-height:1.05;color:inherit}
.vt-page .vt-eyebrow{font-size:10px;letter-spacing:.16em;font-weight:800;color:#947735;text-transform:uppercase}
.vt-page .vt-hero{background:#102f29;color:#fff;padding:52px 0 58px}
.vt-page .vt-hero-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:64px;align-items:center}
.vt-page .vt-hero h1{font-size:clamp(48px,6.5vw,88px);margin:22px 0 26px;max-width:660px;color:#fff}
.vt-page .vt-hero h1 em{font-weight:500;color:#e0c47d}.vt-page .vt-hero .vt-eyebrow{color:#dfc484}
.vt-page .vt-hero p{color:#d5e1d8;font-size:15px;line-height:1.9;max-width:560px}
.vt-page .vt-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}
.vt-page .vt-button{display:inline-flex;justify-content:center;align-items:center;gap:10px;min-height:48px;padding:14px 19px;border-radius:6px;text-decoration:none;font-size:12px;font-weight:800;line-height:1.5;border:1px solid transparent;background:#123d32;color:#fff}
.vt-page .vt-button.gold{background:#dfc17c;color:#163b30}.vt-page .vt-button.outline{background:transparent;border-color:#809d8c;color:#fff}
.vt-page a:focus-visible,.vt-page summary:focus-visible{outline:3px solid #b48b36;outline-offset:5px}
.vt-page .vt-cover{margin:0;max-width:440px;justify-self:center;width:100%;border-radius:14px;overflow:hidden;background:#24473b}
.vt-page .vt-cover img{display:block;width:100%;height:auto;object-fit:contain}
.vt-page .vt-cover figcaption{font-size:10px;color:#dce7de;line-height:1.6;padding:12px 15px}
.vt-page .vt-section{padding:72px 0}.vt-page .vt-heading{max-width:760px;margin-bottom:34px}
.vt-page .vt-heading h2{font-size:clamp(38px,4.4vw,62px);margin:12px 0 18px}
.vt-page .vt-heading p,.vt-page .vt-practical p{font-size:14px;line-height:1.9;color:#5b7064}
.vt-page .vt-rental{display:grid;grid-template-columns:.8fr 1.2fr;background:#fff;border:1px solid #dde5da;border-radius:14px;overflow:hidden;margin-bottom:40px;scroll-margin-top:100px}
.vt-page .vt-rental-photo{min-height:360px;position:relative;background:#dae1d6}.vt-page .vt-rental-photo img{position:absolute;width:100%;height:100%;object-fit:cover;object-position:50% 75%}
.vt-page .vt-rental-copy{padding:36px}.vt-page .vt-number{display:inline-block;color:#947735;font-size:12px;letter-spacing:.14em;font-weight:800}
.vt-page .vt-rental h3{font-size:clamp(35px,3.7vw,50px);margin:15px 0}.vt-page .vt-price{display:flex;gap:12px;align-items:baseline;margin:18px 0;color:#123d32}.vt-page .vt-price strong{font-size:39px;letter-spacing:-.04em}.vt-page .vt-price span{font-size:12px;color:#687b6c}
.vt-page .vt-summary{font-size:14px;line-height:1.85;color:#5b7064;margin:0 0 20px}
.vt-page .vt-tags{display:flex;gap:7px;flex-wrap:wrap;margin:15px 0 20px}.vt-page .vt-tags span{background:#eff2e8;border:1px solid #e0e6d8;border-radius:999px;color:#3b5a45;font-size:10px;padding:8px 10px;line-height:1.5}
.vt-page .vt-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px;margin-top:18px}
.vt-page .vt-card{border:1px solid #dde5da;border-radius:14px;background:#fff;overflow:hidden;display:flex;flex-direction:column;scroll-margin-top:100px;min-width:0}
.vt-page .vt-card-photo{height:240px;position:relative;background:#dce5d6;overflow:hidden}.vt-page .vt-card-photo img{width:100%;height:100%;object-fit:cover;object-position:50% 80%;display:block}
.vt-page #vtt-programme-4 .vt-card-photo img{object-position:50% 100%!important}
.vt-page .vt-card-photo .vt-number{position:absolute;top:15px;inset-inline-start:16px;padding:9px 11px;background:#123d32;color:#e5ca8c;border-radius:5px}
.vt-page .vt-card-copy{padding:29px;display:flex;flex-direction:column;flex:1}.vt-page .vt-card h3{font-size:35px;margin:0 0 17px}
.vt-page .vt-route{font-size:11px;line-height:1.9;border-inline-start:3px solid #d3b66c;padding-inline-start:12px;color:#536e5a;margin:4px 0 20px;overflow-wrap:anywhere}.vt-page .vt-route strong{display:block;color:#294c3a;font-size:10px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:5px}
.vt-page details{border-top:1px solid #e1e7db;margin:0 0 24px;padding-top:16px}.vt-page summary{cursor:pointer;font-size:12px;font-weight:800;color:#294d3b;line-height:1.7}.vt-page details ol{padding-inline-start:20px;margin:16px 0 0}.vt-page details li{font-size:12px;line-height:1.9;color:#5b7064;margin-bottom:10px;padding-inline-start:4px}
.vt-page .vt-card-bottom{margin-top:auto}.vt-page .vt-quote{font-size:11px;font-weight:700;color:#8f7135;margin-bottom:13px}.vt-page .vt-card-bottom .vt-button{width:100%}
.vt-page .vt-practical{margin-top:36px;padding:25px 30px;border-inline-start:4px solid #bf9b4b;background:#ecefe4;border-radius:0 8px 8px 0}.vt-page .vt-practical h2{font-size:29px;margin:0 0 10px}.vt-page .vt-practical p{margin:0}
.vt-page .vt-gallery-section{background:#eaf0e6;padding:56px 0 65px}.vt-page .vt-gallery{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.vt-page .vt-gallery a{display:block;border-radius:10px;overflow:hidden;background:#cbd8c3;aspect-ratio:3/4}.vt-page .vt-gallery img{width:100%;height:100%;object-fit:cover;object-position:50% 70%;display:block}
html[lang="ar"] .vt-page{font-family:'Imsfrane Tajawal',Tahoma,sans-serif;text-align:right}html[lang="ar"] .vt-page h1,html[lang="ar"] .vt-page h2,html[lang="ar"] .vt-page h3{font-family:'Imsfrane Alexandria',Tahoma,sans-serif;letter-spacing:0;line-height:1.55}html[lang="ar"] .vt-page .vt-hero h1{font-size:clamp(36px,4.5vw,59px)}html[lang="ar"] .vt-page .vt-heading h2{font-size:clamp(29px,3.3vw,43px)}html[lang="ar"] .vt-page .vt-card h3,html[lang="ar"] .vt-page .vt-rental h3{font-size:30px}html[lang="ar"] .vt-page .vt-eyebrow{letter-spacing:0}html[lang="ar"] .vt-page .vt-price{direction:rtl}
@media(max-width:850px){.vt-page .vt-hero-grid{gap:28px;grid-template-columns:1fr 1fr}.vt-page .vt-hero h1{font-size:55px}.vt-page .vt-card-copy{padding:23px}.vt-page .vt-card h3{font-size:31px}}
@media(max-width:640px){.vt-page .vt-shell{width:calc(100% - 30px)}.vt-page .vt-hero{padding:32px 0 35px}.vt-page .vt-hero-grid{grid-template-columns:1fr;gap:29px}.vt-page .vt-hero h1{font-size:54px;margin:18px 0}.vt-page .vt-hero p{font-size:14px}.vt-page .vt-cover{max-width:330px}.vt-page .vt-actions{margin-top:22px}.vt-page .vt-button{font-size:11px}.vt-page .vt-section{padding:44px 0}.vt-page .vt-rental{grid-template-columns:1fr;margin-bottom:30px}.vt-page .vt-rental-photo{min-height:285px}.vt-page .vt-rental-copy{padding:25px}.vt-page .vt-grid{grid-template-columns:1fr;gap:24px}.vt-page .vt-card-photo{height:240px}.vt-page .vt-heading h2{font-size:41px}.vt-page .vt-card h3{font-size:34px}.vt-page .vt-practical{padding:22px}.vt-page .vt-gallery{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.vt-page .vt-gallery-section{padding:40px 0}.vt-page .vt-tags span{font-size:10px}}
html[lang="ar"] .vt-page .quad-r-badge{left:auto;right:21px;text-align:right}
@media(max-width:650px){html[lang="ar"] .vt-page .quad-r-badge{right:10px}}
</style>'''


def wa(d, name):
    return 'https://wa.me/212667772551?text=' + quote(d['message'].format(name=name), safe='')


def tags(program):
    return '<div class="vt-tags">' + ''.join('<span>' + esc(t) + '</span>' for t in program['tags']) + '</div>'


def detail(d, program):
    return '<details><summary>' + esc(d['details']) + '</summary><ol>' + ''.join('<li>' + esc(p) + '</li>' for p in program['steps']) + '</ol></details>'


def button(d, program, rental=False):
    label = d['rentalButton'] if rental else d['ask']
    return f'<a class="vt-button" href="{esc(wa(d, program["name"]), quote=True)}" target="_blank" rel="noopener noreferrer">{esc(label)} <span aria-hidden="true">↗</span></a>'


def render(lang):
    d = DATA[lang]
    rental = d['programs'][0]
    body = (f'<main class="vt-page" id="mainContent" data-vtt-version="restored-hero-20261021">'
            '<section class="vt-hero"><div class="vt-shell vt-hero-grid"><div>'
            f'<div class="vt-eyebrow">{esc(d["eyebrow"])}</div><h1>{d["hero"]}</h1><p>{esc(d["intro"])}</p>'
            f'<div class="vt-actions"><a class="vt-button gold" href="#vtt-programmes">{esc(d["choose"])}</a>'
            f'<a class="vt-button outline" href="{esc(wa(d, d["title"]), quote=True)}" target="_blank" rel="noopener noreferrer">WhatsApp ↗</a></div></div>'
            f'<figure class="vt-cover"><img src="/images/IMG_7394.webp" width="1152" height="1536" alt="{esc(d["photoAlt"])}" fetchpriority="high" decoding="async">'
            f'<figcaption>{esc(d["galleryText"])}</figcaption></figure></div></section>'
            '<section class="vt-section" id="vtt-programmes"><div class="vt-shell"><div class="vt-heading">'
            f'<span class="vt-eyebrow">VTT · MTB · BTT</span><h2>{esc(d["programmes"])}</h2><p>{esc(d["programmesIntro"])}</p></div>'
            '<article class="vt-rental" id="vtt-programme-1"><div class="vt-rental-photo">'
            f'<img src="/images/{PHOTOS[0]}" alt="{esc(d["photoAlt"])}" loading="lazy" decoding="async"></div><div class="vt-rental-copy">'
            f'<span class="vt-number">01 · {esc(d["rental"])}</span><h3>{esc(rental["name"])}</h3><p class="vt-summary">{esc(rental["summary"])}</p>'
            f'<div class="vt-price"><strong><bdi>150</bdi> {"درهماً" if lang == "ar" else "DH" if lang == "fr" else "MAD"}</strong><span>{esc(d["perBike"])}</span></div>'
            + tags(rental) + detail(d, rental) + button(d, rental, True) + '</div></article>'
            f'<span class="vt-eyebrow">{esc(d["circuits"])}</span><div class="vt-grid">')
    for i, program in enumerate(d['programs'][1:], 2):
        body += (f'<article class="vt-card" id="vtt-programme-{i}"><div class="vt-card-photo">'
                 f'<img src="/images/{PHOTOS[i-1]}" alt="{esc(d["photoAlt"])}" loading="lazy" decoding="async"><span class="vt-number">{i:02d}</span></div>'
                 f'<div class="vt-card-copy"><h3>{esc(program["name"])}</h3><p class="vt-summary">{esc(program["summary"])}</p>'
                 + tags(program) + f'<div class="vt-route"><strong>{esc(d["route"])}</strong>{esc(program["route"])}</div>'
                 + detail(d, program) + f'<div class="vt-card-bottom"><p class="vt-quote">{esc(d["quote"])}</p>'
                 + button(d, program) + '</div></div></article>')
    body += ('</div><aside class="vt-practical"><h2>' + esc(d['practical']) + '</h2><p>' + esc(d['practicalText']) + '</p></aside></div></section>'
             '<section class="vt-gallery-section"><div class="vt-shell"><div class="vt-heading"><h2>' + esc(d['gallery']) + '</h2><p>' + esc(d['galleryText']) + '</p></div><div class="vt-gallery">')
    for name in GALLERY:
        body += f'<a href="/images/{name}" target="_blank" rel="noopener" aria-label="{esc(d["fullPhoto"])}"><img src="/images/{name}" alt="{esc(d["photoAlt"])}" loading="lazy" decoding="async"></a>'
    return body + '</div></div></section></main>'


def build(root):
    for lang, d in DATA.items():
        path = root / lang / 'vtt' / 'index.html'
        html = path.read_text(encoding='utf-8')
        original_hero = re.search(r'<section\b(?=[^>]*class="quad-r-hero")[^>]*>.*?</section>', html, re.S)
        assert original_hero, f'Original VTT hero missing: {path}'
        hero = original_hero[0]
        # Keep the established collage, title and hero framing. Only its old
        # two-hour offer copy is refreshed to match the five approved programmes.
        hero = re.sub(r'<p class="quad-r-summary">.*?</p>', lambda m: '<p class="quad-r-summary">' + esc(d['intro']) + '</p>', hero, count=1, flags=re.S)
        rental_label, programmes_label, request_label = {
            'fr': ('Location VTT', 'Programmes VTT', 'Sur demande'),
            'en': ('Bike rental', 'MTB programmes', 'On request'),
            'ar': ('كراء الدراجات', 'برامج للدراجات', 'عند الطلب'),
            'es': ('Alquiler BTT', 'Programas BTT', 'Bajo petición'),
        }[lang]
        currency = 'درهم' if lang == 'ar' else 'DH' if lang == 'fr' else 'MAD'
        stats = (f'<div class="quad-r-stats"><div><strong><bdi>150 {currency}</bdi></strong><small>{rental_label}</small></div>'
                 f'<div><strong>5</strong><small>{programmes_label}</small></div>'
                 f'<div><strong>{request_label}</strong><small>WhatsApp</small></div></div>')
        hero = re.sub(r'<div class="quad-r-stats">.*?</div></div></div>(?=<div class="quad-r-media">)', lambda m: stats + '</div>', hero, count=1, flags=re.S)
        main = re.sub(r'<section class="vt-hero">.*?</section>', lambda m: hero, render(lang), count=1, flags=re.S)
        main = main.replace('<section class="vt-gallery-section">', '<section class="vt-gallery-section" id="gallery">')
        html, count = re.subn(r'<main\b[^>]*>.*?</main>', lambda m: main, html, count=1, flags=re.S)
        assert count == 1, path
        html = re.sub(r'<title>.*?</title>', '<title>' + esc(d['title']) + ' | Imsfrane Cathédrale</title>', html, count=1, flags=re.S)
        for key, value in [('description', d['intro']), ('og:title', d['title']), ('og:description', d['intro']), ('og:image', 'https://imsfrane.com/images/IMG_2606.webp')]:
            pattern = r'(<meta\b(?=[^>]*(?:name|property)="' + re.escape(key) + r'")[^>]*content=")[^"]*(")'
            html = re.sub(pattern, lambda m: m[1] + esc(value, quote=True) + m[2], html)
        # Remove the obsolete page's inline lightbox handlers and route-specific JS.
        html = re.sub(r'<script>function show\(el\).*?</script>', '', html, flags=re.S)
        html = re.sub(r'<script\b[^>]*src="/js/pages/vtt\.min\.js"[^>]*>\s*</script>', '', html)
        schema = {'@context': 'https://schema.org', '@type': 'Service', 'name': d['title'], 'description': d['intro'],
                  'serviceType': 'Mountain bike rental and tours', 'areaServed': 'Imsfrane, Tilouguite, Morocco',
                  'provider': {'@type': 'TravelAgency', 'name': 'Imsfrane Cathédrale', 'url': 'https://imsfrane.com/'},
                  'offers': {'@type': 'Offer', 'name': d['programs'][0]['name'], 'price': '150', 'priceCurrency': 'MAD', 'url': f'https://imsfrane.com/{lang}/vtt/'}}
        html = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + '</script>', html, count=1, flags=re.S)
        html = html.replace('</head>', CSS + '</head>', 1)
        path.write_text(html, encoding='utf-8')
    print('VTT: five user-supplied programmes published in four languages')


if __name__ == '__main__':
    import sys
    build(Path(sys.argv[1] if len(sys.argv) > 1 else 'public'))
