"""Build compact booking cards from the official booking templates for the demo."""
from pathlib import Path
import re
import sys

COMPACT = """
<style id="compact-booking-cards">
#choices.choices { grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }
#choices .choice { display:flex; flex-direction:column; border-radius:12px; min-width:0; }
#choices .choice.selected { border:1px solid #1d6746; box-shadow:0 0 0 2px #dcefe0; }
#choices .choice-image { height:clamp(72px,9vw,105px); background:#edf1e9; }
#choices .choice-image img { object-fit:contain; transform:none; }
#choices .choice-icon { display:none; }
#choices .choice-selected { inset:6px 6px auto auto; width:20px; height:20px; font-size:12px; }
#choices .choice-content { padding:8px 9px 10px; min-height:0; gap:3px; }
#choices .choice-content strong { font-size:13px; overflow-wrap:anywhere; }
#choices .choice-content small, #choices .choice-time { font-size:11px; line-height:1.35; }
@media(max-width:560px) {
  #choices.choices { grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }
  #choices .choice-image { height:78px; }
}
</style>
"""

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
    localized = {
        'ar': ('اختر تجربتك','اختر التواريخ','أرسل الطلب','درهم','لكل دراجة'),
        'en': ('Explore','Choose your dates','Send enquiry','MAD','per bike'),
        'es': ('Explora','Elige las fechas','Envía la solicitud','MAD','por bicicleta'),
        'fr': ('Explorez','Choisissez les dates','Envoyez la demande','MAD','par vélo'),
    }
    step_labels = {key: values[:3] for key, values in localized.items()}
    for i, original in enumerate(('Explore','Choose your dates','Send enquiry')):
        page = page.replace(f'<span>0{i+1} · {original}</span>',
                            f'<span data-booking-step="{i}">{localized[lang][i]}</span>', 1)
    page = page.replace('function render(){', 'const STEPS='+json.dumps(step_labels,ensure_ascii=False)+';\n'
        'const BIKE='+json.dumps({k:v[4] for k,v in localized.items()},ensure_ascii=False)+';\n'
        'function render(){document.querySelectorAll("[data-booking-step]").forEach(el=>{el.textContent=STEPS[lang][Number(el.dataset.bookingStep)]});')
    page = page.replace('+" MAD";','+(lang==="ar"?" درهم":" MAD");').replace(
        '(txt()[unitKeys[s.unit]]||"")', '(s.id==="vtt"?BIKE[lang]:(txt()[unitKeys[s.unit]]||""))')
    page = page.replace('function summary(){', 'function quadTotal(people){return selected.id==="quadDuo"?Math.floor(people/2)*300+(people%2)*250:people*250}\nfunction summary(){')
    page = page.replace('selected.price*(selected.unit===', '(["quad","quadDuo"].includes(selected.id)?quadTotal(p):selected.price*(selected.unit===')
    page = page.replace('?nights*p:p);', '?nights*p:p));').replace('?n*p:p));', '?n*p:p)));')
    page = page.replace('رافتينغ ·', 'التجديف ·')
    return page.replace('</head>', COMPACT + '</head>', 1)

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
