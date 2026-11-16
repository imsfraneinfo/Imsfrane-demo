"""Build compact booking cards from the official booking templates for the demo."""
from pathlib import Path
import re
import sys

DETAILS = {
    "≈ 2 h": ("≈ 2 h", "≈ 2 hr", "≈ 2 h", "حوالي ساعتين"),
    "≈ 4 h": ("≈ 4 h", "≈ 4 hr", "≈ 4 h", "حوالي 4 ساعات"),
    "2 days": ("2 jours", "2 days", "2 días", "يومان"),
    "4 days · min. 4": ("4 jours · min. 4", "4 days · min. 4", "4 días · mín. 4", "4 أيام · من 4 أشخاص"),
    "4–5 h": ("4–5 h", "4–5 hr", "4–5 h", "4–5 ساعات"),
    "3–4 h": ("3–4 h", "3–4 hr", "3–4 h", "3–4 ساعات"),
    "8–10 h": ("8–10 h", "8–10 hr", "8–10 h", "8–10 ساعات"),
    "1 night": ("1 nuit", "1 night", "1 noche", "ليلة واحدة"),
    "1 day": ("1 jour", "1 day", "1 día", "يوم واحد"),
    "1 h": ("1 h", "1 hr", "1 h", "ساعة واحدة"),
    "15 min": ("15 min", "15 min", "15 min", "15 دقيقة"),
    "Weekend": ("Week-end", "Weekend", "Fin de semana", "نهاية الأسبوع"),
    "On request": ("Sur demande", "On request", "Bajo petición", "حسب الطلب"),
    "Tailor-made": ("Sur mesure", "Tailor-made", "A medida", "حسب الطلب"),
}

def update_catalog(page, lang):
    import json

    assert 'const PHOTO=' in page and 'function renderChoices()' in page
    rates = {'rafting30': (800, 'person'), 'rafting50': (None, 'request'),
             'rafting4': (4000, 'person'), 'camp': (1000, 'person')}
    for activity, (amount, unit) in rates.items():
        value = 'null' if amount is None else str(amount)
        page, count = re.subn(
            rf'(\{{id:"{activity}",icon:"[^"]+",)price:(?:\d+|null),unit:"[^"]+"',
            rf'\g<1>price:{value},unit:"{unit}"', page,
        )
        assert count == 1, activity

    page = page.replace('detail:"5–7 h"', 'detail:"4–5 h"')
    quad_start = page.index('{id:"quad"')
    quad_end = page.index('\n', quad_start)
    quad = page[quad_start:quad_end].replace('Quad · 1 heure','Quad · 1 personne').replace(
        'Quad biking · 1 hour','Quad · 1 rider').replace('Quad · 1 hora','Quad · 1 persona').replace(
        'كواد · ساعة','دراجة رباعية · شخص واحد')
    duo = quad.replace('id:"quad"','id:"quadDuo"').replace('price:250','price:300').replace(
        'Quad · 1 personne','Quad · 2 personnes').replace('Quad · 1 rider','Quad · 2 riders').replace(
        'Quad · 1 persona','Quad · 2 personas').replace('دراجة رباعية · شخص واحد','دراجة رباعية · شخصان')
    page = page[:quad_start] + quad + '\n' + duo + page[quad_end:]
    page = page.replace('"quad","jetski"', '"quad","quadDuo","jetski"').replace(
        'img.src=PHOTO[s.id]||PHOTO.other', 'img.src=PHOTO[s.id==="quadDuo"?"quad":s.id]||PHOTO.other')
    page = page.replace('Week-end camping','Week-end nature').replace(
        'Camping weekend','Nature weekend').replace('Fin de semana camping','Fin de semana en la naturaleza').replace(
        'ويكاند تخييم','عطلة نهاية الأسبوع في الطبيعة')
    page = page.replace('const today=new Date();', 'const D=' + json.dumps(DETAILS, ensure_ascii=False) + ';\nconst today=new Date();')
    page = page.replace('duration.textContent=s.detail||""', 'duration.textContent=D[s.detail]?.[["fr","en","es","ar"].indexOf(lang)]||""')
    bike_labels = {'ar': 'لكل دراجة', 'en': 'per bike', 'es': 'por bicicleta', 'fr': 'par vélo'}
    page = page.replace('function render(){', 'const BIKE='
                        + json.dumps(bike_labels, ensure_ascii=False) + ';\nfunction render(){')
    page = page.replace('+" MAD";','+(lang==="ar"?" درهم":" MAD");').replace(
        '(txt()[unitKeys[s.unit]]||"")', '(s.id==="vtt"?BIKE[lang]:(txt()[unitKeys[s.unit]]||""))')
    page = page.replace('function summary(){', 'function quadTotal(people){return selected.id==="quadDuo"?Math.floor(people/2)*300+(people%2)*250:people*250}\nfunction summary(){')
    page = page.replace('selected.price*(selected.unit===', '(["quad","quadDuo"].includes(selected.id)?quadTotal(p):selected.price*(selected.unit===')
    page = page.replace('?nights*p:p);', '?nights*p:p));').replace('?n*p:p));', '?n*p:p)));')
    page = page.replace('رافتينغ ·', 'التجديف ·')
    return build_editorial(page, lang)

EDITORIAL = {
    'ar': ('تاريخ المغادرة *', 'يجب أن يكون تاريخ المغادرة بعد تاريخ الوصول.', 'اختر تجربة من إمسفران'),
    'fr': ('Date de départ *', 'La date de départ doit être après la date d’arrivée.', 'Choisissez une expérience à Imsfrane'),
    'en': ('Check-out date *', 'Check-out must be after check-in.', 'Choose an Imsfrane experience'),
    'es': ('Fecha de salida *', 'La salida debe ser posterior a la llegada.', 'Elige una experiencia en Imsfrane'),
}


def build_editorial(source, lang):
    import json
    from bs4 import BeautifulSoup

    location = Path(__file__).resolve().parent
    page = BeautifulSoup(source, 'html.parser')
    robots = page.find('meta', attrs={'name': 'robots'})
    if robots is None:
        robots = page.new_tag('meta', attrs={'name': 'robots'})
        page.head.append(robots)
    robots['content'] = 'noindex,follow'

    shell = page.select_one('.shell')
    form = page.select_one('#bookingForm')
    summary = page.select_one('.summary')
    library = page.new_tag('section', attrs={'class': 'booking-library'})
    form.select_one('.how-it-works').decompose()
    form.select_one('.badge').decompose()
    introduction = form.select_one('.section-title')
    heading = introduction.h2.extract()
    introduction.decompose()
    form.select_one('[data-i="hint1"]').decompose()
    form.select_one('.divider').decompose()
    library.extend([heading, form.select_one('#bookingTabs').extract(), form.select_one('#choices').extract()])
    form.append(form.select_one('#pricingNote').extract())

    article = page.new_tag('div', attrs={'class': 'booking-main'})
    feature = page.new_tag('section', attrs={'class': 'booking-feature'})
    feature.append(page.new_tag('img', id='bookingFeaturePhoto', alt='', fetchpriority='high'))
    feature_copy = page.new_tag('div', attrs={'class': 'booking-feature-copy', 'aria-live': 'polite'})
    title = page.new_tag('h2', id='bookingFeatureTitle')
    title.string = EDITORIAL[lang][2]
    feature_copy.extend([title, page.new_tag('p', id='bookingFeatureDetail')])
    feature.append(feature_copy)
    article.extend([feature, form.extract(), summary.extract()])
    shell.extend([library, article])

    css = page.new_tag('style', id='booking-editorial-style')
    css.string = (location / 'booking-editorial.css').read_text(encoding='utf-8')
    page.head.append(css)
    script = page.find('script')
    js = script.string
    js = js.replace('renderChoices();$("pricingNote")', 'renderChoices();updateFeature();$("pricingNote")')
    js = js.replace('renderChoices();summary()});', 'renderChoices();updateFeature();summary()});')
    js = re.sub(r'activeGroup=Object.keys\(GROUPS\)\.find\(g=>g!=="all"&&GROUPS\[g\]\.includes\(s.id\)\)\|\|"all";', '', js)
    js = js.replace('if(end&&end<start){$("endDate").setCustomValidity(txt().dateError);',
                    'if(end&&(end<start||($("endDate").required&&end===start))){$("endDate").setCustomValidity(EDITORIAL[lang][1]);')
    js = js.replace('e.preventDefault();if(!$("bookingForm").reportValidity())return;',
                    'e.preventDefault();channel=e.submitter?.dataset.channel||"wa";if(!$("bookingForm").reportValidity())return;')
    js = js.replace('const requested=', 'const EDITORIAL='+json.dumps(EDITORIAL,ensure_ascii=False)+';\n'
                    +(location / 'booking-editorial.js').read_text(encoding='utf-8')+'\nconst requested=',1)
    script.string.replace_with(js)
    return str(page)


def build(root, official):
    prefix = '/Imsfrane-demo'
    for lang in ('fr', 'en', 'es', 'ar'):
        file = Path(lang) / 'booking' / 'index.html'
        page = update_catalog((official / file).read_text(encoding='utf-8'), lang)
        page = page.replace('https://imsfrane.com/', 'https://imsfraneinfo.github.io/Imsfrane-demo/')
        page = page.replace('"/images/', f'"{prefix}/images/')
        for destination in (root / file, root / lang / 'booking.html'):
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(page, encoding='utf-8')
        if lang == 'fr':
            (root / 'booking-premium.html').write_text(page, encoding='utf-8')

if __name__ == '__main__':
    build(Path(sys.argv[1]), Path('/tmp/official'))
