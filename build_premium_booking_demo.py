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
    return build_journey(page, lang)

JOURNEY = {
    'ar': ('التجربة', 'تفاصيل الرحلة', 'مراجعة الطلب', 'السابق', 'أكمل الحجز', 'راجع طلبك',
           'راجع التجربة والتواريخ والثمن التقديري، ثم اختر كيف ترسل الطلب.',
           'يجب أن يكون تاريخ المغادرة بعد تاريخ الوصول.', 'تاريخ المغادرة *'),
    'fr': ('Expérience', 'Détails du séjour', 'Vérification', 'Retour', 'Continuer', 'Vérifier ma demande',
           'Vérifiez votre expérience, vos dates et le tarif estimé, puis choisissez le mode d’envoi.',
           'La date de départ doit être postérieure à la date d’arrivée.', 'Date de départ *'),
    'en': ('Experience', 'Trip details', 'Review', 'Back', 'Continue', 'Review my request',
           'Check your experience, dates and estimated price, then choose how to send your request.',
           'Check-out must be after check-in.', 'Check-out date *'),
    'es': ('Experiencia', 'Detalles del viaje', 'Revisión', 'Atrás', 'Continuar', 'Revisar mi solicitud',
           'Comprueba la experiencia, las fechas y el precio estimado, y elige cómo enviar tu solicitud.',
           'La salida debe ser posterior a la llegada.', 'Fecha de salida *'),
}


def build_journey(source, lang):
    import json
    from bs4 import BeautifulSoup

    location = Path(__file__).resolve().parent
    page = BeautifulSoup(source, 'html.parser')
    hero = page.select_one('.hero-inner')
    copy = page.new_tag('div')
    for child in list(hero.contents):
        copy.append(child.extract())
    hero.append(copy)
    hero.append(page.new_tag('img', src='/images/rando-IMG_6167.webp', alt='',
                            attrs={'class': 'journey-photo', 'fetchpriority': 'high'}))

    form = page.select_one('#bookingForm')
    form.select_one('.how-it-works').decompose()
    form.select_one('.badge').decompose()
    for divider in form.select('.divider'):
        divider.decompose()
    headers = form.select('.section-title')
    steps = page.new_tag('ol', attrs={'class': 'journey-steps'})
    for index, label in enumerate(JOURNEY[lang][:3]):
        item = page.new_tag('li', attrs={'data-booking-step': str(index)})
        item.string = label
        if index == 0:
            item['aria-current'] = 'step'
        steps.append(item)
    form.insert(0, steps)
    page.select_one('.shell')['data-stage'] = '0'

    experience, details, review = [page.new_tag('section', attrs={'class': 'journey-panel'})
                                   for _ in range(3)]
    for header in headers:
        header.h2['tabindex'] = '-1'
    for child in list(form.children):
        if child is steps:
            continue
        if child is headers[1] or child is headers[2] or details.contents:
            details.append(child.extract())
        else:
            experience.append(child.extract())
    headers[2]['class'].append('journey-contact')
    heading = page.new_tag('h2', id='journeyReviewTitle', tabindex='-1')
    heading.string = JOURNEY[lang][2]
    hint = page.new_tag('p', id='journeyReviewHint', attrs={'class': 'hint'})
    hint.string = JOURNEY[lang][6]
    review.extend([heading, hint])
    details['hidden'] = ''
    review['hidden'] = ''
    form.extend([experience, details, review])

    actions = page.new_tag('div', attrs={'class': 'journey-actions'})
    for direction, label in [('Prev', JOURNEY[lang][3]), ('Next', JOURNEY[lang][4])]:
        button = page.new_tag('button', id='journey'+direction, type='button',
                              attrs={'class': 'journey-'+direction.lower()})
        button.string = label
        if direction == 'Prev':
            button['hidden'] = ''
        actions.append(button)
    form.append(actions)
    submit = page.new_tag('div', id='journeySubmit', hidden='')
    buttons = page.select('.summary [data-channel]')
    buttons[0].insert_before(submit)
    for button in buttons:
        submit.append(button.extract())

    css = page.new_tag('style', id='booking-journey-style')
    css.string = (location / 'booking-journey.css').read_text(encoding='utf-8')
    page.head.append(css)
    script = page.find('script')
    js = script.string
    js = js.replace('renderChoices();$("pricingNote")', 'renderChoices();renderJourney();$("pricingNote")')
    js = js.replace('e.preventDefault();if(!$("bookingForm").reportValidity())return;',
                    'e.preventDefault();if(stage!==2)return;channel=e.submitter?.dataset.channel||"wa";if(!$("bookingForm").reportValidity())return;')
    js = re.sub(r'activeGroup=Object.keys\(GROUPS\)\.find\(g=>g!=="all"&&GROUPS\[g\]\.includes\(s.id\)\)\|\|"all";', '', js)
    js = js.replace('const requested=', 'const JOURNEY='+json.dumps(JOURNEY,ensure_ascii=False)+';\n'
                    +(location / 'booking-journey.js').read_text(encoding='utf-8')+'\nconst requested=',1)
    script.string.replace_with(js)
    return str(page)


def build(root, official):
    prefix = '/Imsfrane-demo'
    for lang in ('fr', 'en', 'es', 'ar'):
        file = Path(lang) / 'booking' / 'index.html'
        page = update_catalog((official / file).read_text(encoding='utf-8'), lang)
        page = page.replace('https://imsfrane.com/', 'https://imsfraneinfo.github.io/Imsfrane-demo/')
        page = page.replace('"/images/', f'"{prefix}/images/')
        page = re.sub(r'<meta name="robots"[^>]*>', '<meta name="robots" content="noindex,follow">', page)
        for destination in (root / file, root / lang / 'booking.html'):
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(page, encoding='utf-8')
        if lang == 'fr':
            (root / 'booking-premium.html').write_text(page, encoding='utf-8')

if __name__ == '__main__':
    build(Path(sys.argv[1]), Path('/tmp/official'))
