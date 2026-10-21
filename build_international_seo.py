"""Improve activity search summaries and practical English trip information."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import re
import xml.etree.ElementTree as ET

META = {
 'en': {
  'rafting': ('Rafting Morocco | Ahansal River Trips in Imsfrane', 'Plan a rafting trip on Morocco’s Ahansal River near Imsfrane. Compare routes, check the March–June season and ask about your dates and local logistics.'),
  'kayak': ('Whitewater Kayaking Morocco | Ahansal & Melloul Logistics', 'Bring your own kayak to Morocco’s Ahansal and Melloul rivers. Arrange river shuttles, bivouacs, meals and Marrakech airport transfers with our local team.'),
  'randonnee': ('Imsfrane Cathedral Hike | High Atlas Local Guided Walks', 'Hike Imsfrane Cathedral in Morocco’s High Atlas with a local guide. Compare the summit, Ahansal gorges and full-day routes, with prices per group.'),
  'vtt': ('Mountain Bike Rental & Atlas MTB Tours | Imsfrane, Morocco', 'Rent a mountain bike in Imsfrane for 150 MAD per bike, for a full day or less. Explore Tilouguite or request a tailored Atlas MTB route via WhatsApp.'),
 },
 'fr': {
  'rafting': ('Rafting au Maroc | Oued Ahansal à Imsfrane', 'Préparez votre descente en rafting sur l’Oued Ahansal à Imsfrane : parcours, saison de mars à juin et organisation locale. Départs selon les conditions.'),
  'kayak': ('Kayak au Maroc | Logistique Ahansal et Melloul', 'Venez avec vos kayaks sur l’Ahansal et le Melloul. Navettes, bivouac, repas et transferts depuis Marrakech organisés avec notre équipe locale.'),
  'randonnee': ('Randonnée Cathédrale Imsfrane | Sommet et gorges de l’Ahansal', 'Explorez le sommet de la Cathédrale Imsfrane et les gorges de l’Ahansal avec un guide local. Trois randonnées dans le Haut Atlas, tarifs par groupe.'),
  'vtt': ('Location VTT à Imsfrane | Circuits dans le Haut Atlas', 'Louez un VTT à Imsfrane pour 150 DH par vélo, une journée ou moins. Explorez Tilouguite ou demandez un circuit sur mesure dans l’Atlas par WhatsApp.'),
 },
 'ar': {
  'rafting': ('الرافتينغ في المغرب | رحلات وادي أحنصال بمسفران', 'خطط لتجربة الرافتينغ في وادي أحنصال قرب مسفران. تعرف على المسارات والموسم المعتاد من مارس إلى يونيو، واستفسر عن المواعيد والتنظيم المحلي.'),
  'kayak': ('الكاياك في المغرب | خدمات وادي أحنصال وملول', 'استكشف وادي أحنصال وملول بقوارب الكاياك الخاصة بكم. ننظم النقل المحلي والتخييم والوجبات والتحويلات من مطار مراكش حسب برنامج المجموعة.'),
  'randonnee': ('المشي الجبلي في مسفران | القمة ومضايق أحنصال', 'اكتشف قمة جبل مسفران ومضايق وادي أحنصال مع مرشد محلي. ثلاثة مسارات للمشي في الأطلس الكبير، مع أسعار محددة للمجموعة.'),
  'vtt': ('كراء الدراجات الجبلية في مسفران | جولات الأطلس', 'اكترِ دراجة جبلية في مسفران مقابل 150 درهماً للدراجة، ليوم كامل أو أقل. اكتشف تيلوكيت أو اطلب برنامج جولة في الأطلس عبر واتساب.'),
 },
 'es': {
  'rafting': ('Rafting en Marruecos | Río Ahansal en Imsfrane', 'Prepara tu descenso de rafting por el río Ahansal en Imsfrane. Consulta rutas, temporada habitual de marzo a junio y logística con nuestro equipo local.'),
  'kayak': ('Kayak en Marruecos | Logística en Ahansal y Melloul', 'Trae tus kayaks a los ríos Ahansal y Melloul. Organizamos traslados fluviales, vivac, comidas y recogidas en el aeropuerto de Marrakech para tu grupo.'),
  'randonnee': ('Senderismo en Imsfrane | Cumbre y gargantas con guía local', 'Descubre la cumbre de la Catedral de Imsfrane y las gargantas del Ahansal con un guía local. Compara tres rutas del Alto Atlas con precios por grupo.'),
  'vtt': ('Alquiler BTT en Imsfrane | Rutas por el Atlas de Marruecos', 'Alquila una bicicleta de montaña en Imsfrane por 150 MAD por bicicleta, un día completo o menos. Pide una ruta a medida por el Atlas por WhatsApp.'),
 },
}

PLANNING = {
 'rafting': [
  ('When can I go rafting on the Ahansal?', 'The usual season is March to June, occasionally July when river levels allow. Ask us to confirm conditions for your dates before travelling; the route and departure depend on the river.'),
  ('How do I arrange a trip from Marrakech?', 'Our base is in the Imsfrane area, in Tilouguite commune, Azilal province. Tell us your starting point and whether you need transport or an overnight stay. We will confirm the meeting point, transfer arrangements and their cost with your programme.'),
  ('Which rafting programme should I book?', 'Send your dates, group size and previous rafting experience. We will recommend a suitable route and confirm the duration, price and included services before you book.'),
 ],
 'kayak': [
  ('Do I need to bring my own kayak?', 'Yes. This service is designed for paddlers, clubs and groups travelling with their own kayaks and equipment. It is a local logistics service; kayak rental is not advertised as part of the offer.'),
  ('Can you arrange airport transfers and river shuttles?', 'We can arrange Marrakech airport transfers, local transport for paddlers and kayaks, meals and bivouacs around the agreed itinerary. An in-water guide is subject to availability. Ask for an itemised programme and quote.'),
  ('What should I send with my enquiry?', 'Include your dates, number of paddlers and boats, experience, preferred river sections and arrival airport. The usual season is March to June; runnable sections depend on water levels and access.'),
 ],
 'randonnee': [
  ('Which Imsfrane hike is right for me?', 'Choose the summit walk for mountain views: around 4–5 hours, 668 metres of ascent and a summit at about 1,868 metres. The gorges and waterfalls walk is around 8 km in 3–4 hours. The Grand Tour combines both in a demanding 24 km day of around 8–10 hours.'),
  ('Are hiking prices per person or per group?', 'The listed guide prices are per group: 300 MAD for the summit, 200 MAD for the gorges and waterfalls, or 400 MAD for the Grand Tour. Ask us to confirm group arrangements and any transport or accommodation separately.'),
  ('Where do we meet our local guide?', 'The walks take place around Imsfrane and the Ahansal valley in Morocco’s High Atlas. Send your accommodation or starting point, date and group size so we can agree on a meeting place and a route suited to your group.'),
 ],
 'vtt': [
  ('How much does mountain bike rental cost?', 'Rental is 150 MAD per bike for exploring Imsfrane, whether you take it for a full day or less. Confirm bike availability, collection and return arrangements with us before setting out.'),
  ('Can I request a longer Atlas MTB trip?', 'Yes. Our routes include Tilouguite–Imsfrane, a bivouac and summit outing, the traverse via Zaouiat Ahansal and Taghia, and options towards Anergui. These programmes have no fixed advertised price: request the itinerary and quote on WhatsApp.'),
  ('What information do you need to plan my ride?', 'Send your dates, group size, cycling experience and preferred distance. The Tilouguite route has about 24 km on the outward leg, with more climbing on the return; longer itineraries require suitable fitness and agreed logistics.'),
 ],
}

CSS = '''<style id="international-trip-planning-style">
.intl-planning{background:#f5f3eb;color:#173b32;padding:48px max(22px,calc((100% - 1120px)/2));font-family:Montserrat,Arial,sans-serif}
.intl-planning h2{font-family:'Cormorant Garamond',Georgia,serif;font-size:clamp(32px,4vw,46px);line-height:1.15;margin:0 0 24px;color:#173b32}
.intl-planning details{border-top:1px solid #d6ddcf;padding:17px 0}.intl-planning summary{font-size:15px;line-height:1.6;font-weight:700;cursor:pointer}.intl-planning p{font-size:14px;line-height:1.9;max-width:850px;margin:15px 0;color:#4a6357}
.intl-planning nav{display:flex;flex-wrap:wrap;gap:12px 22px;margin-top:22px}.intl-planning a{color:#173b32;font-size:13px;line-height:1.7;text-decoration:underline;text-underline-offset:4px}.intl-planning :is(a,summary):focus-visible{outline:3px solid #aa873c;outline-offset:4px}
</style>'''

def set_meta(html, key, value, prop=False):
    pattern = r'<meta\b(?=[^>]*(?:name|property)=["\']' + re.escape(key) + r'["\'])[^>]*>'
    tag = '<meta ' + ('property' if prop else 'name') + '="' + key + '" content="' + escape(value, quote=True) + '">'
    if re.search(pattern, html, re.I):
        return re.sub(pattern, lambda m: tag, html, flags=re.I)
    return html.replace('</head>', tag + '\n</head>', 1)

def build(root):
    root = Path(root)
    for lang, pages in META.items():
        for page, (title, description) in pages.items():
            path = root / lang / page / 'index.html'
            html = path.read_text(encoding='utf-8')
            # Existing titles carry CMS attributes; do not require a bare <title>.
            html, count = re.subn(r'(<title\b[^>]*>).*?</title>', lambda m: m[1] + escape(title) + '</title>', html, count=1, flags=re.S|re.I)
            assert count == 1, path
            for key, value in [('description', description), ('og:title', title), ('og:description', description), ('twitter:title', title), ('twitter:description', description)]:
                html = set_meta(html, key, value, key.startswith('og:'))
            html = re.sub(r'<link\b(?=[^>]*hreflang=)[^>]*>', '', html, flags=re.I)
            alternates = ''.join('<link rel="alternate" hreflang="' + alt + '" href="https://imsfrane.com/' + ('en' if alt == 'x-default' else alt) + '/' + page + '/">' for alt in ('fr','en','ar','es','x-default'))
            html = html.replace('</head>', alternates + '\n</head>', 1)
            html = re.sub(r'<section\b[^>]*id="international-trip-planning"[^>]*>.*?</section>', '', html, flags=re.S)
            html = re.sub(r'<style id="international-trip-planning-style">.*?</style>', '', html, flags=re.S)
            if lang == 'en':
                block = '<section class="intl-planning" id="international-trip-planning" aria-labelledby="international-planning-title"><h2 id="international-planning-title">Plan your visit to Imsfrane</h2>'
                for question, answer in PLANNING[page]:
                    block += '<details><summary>' + escape(question) + '</summary><p>' + escape(answer) + '</p></details>'
                message = 'Hello, I would like to plan a ' + {'rafting':'rafting trip','kayak':'kayaking trip with my own equipment','randonnee':'guided hike','vtt':'mountain bike outing'}[page] + ' in Imsfrane. My dates and group size are: '
                block += '<nav aria-label="Plan your activity"><a href="https://wa.me/212667772551?text=' + quote(message) + '" target="_blank" rel="noopener noreferrer">Ask our local team on WhatsApp ↗</a><a href="/en/guide/">Getting to Imsfrane and planning your stay</a><a href="/en/contact/">Contact and location</a></nav></section>'
                if page == 'rafting':
                    block = block.replace('</nav>', '<a href="/en/blog-rafting-50-km-bin-el-ouidane/">Read the 50 km rafting journey to Bin El Ouidane</a></nav>')
                assert '</main>' in html
                html = html.replace('</main>', block + '</main>', 1).replace('</head>', CSS + '</head>', 1)
            html = html.replace('<html ', '<html data-international-seo="20261021" ', 1) if 'data-international-seo=' not in html else html
            path.write_text(html, encoding='utf-8')
    sitemap = root / 'sitemap.xml'
    if sitemap.is_file():
        ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
        ET.register_namespace('', ns)
        ET.register_namespace('xhtml', 'http://www.w3.org/1999/xhtml')
        tree = ET.parse(sitemap)
        changed = {f'https://imsfrane.com/{lang}/{page}/' for lang,pages in META.items() for page in pages}
        for url in tree.getroot().findall(f'{{{ns}}}url'):
            if url.findtext(f'{{{ns}}}loc') in changed:
                lastmod = url.find(f'{{{ns}}}lastmod')
                if lastmod is None:
                    lastmod = ET.SubElement(url, f'{{{ns}}}lastmod')
                lastmod.text = '2026-10-21'
        tree.write(sitemap, encoding='utf-8', xml_declaration=True)
    print('International search: 16 activity summaries and four English trip-planning sections')

if __name__ == '__main__':
    import sys
    build(sys.argv[1] if len(sys.argv) > 1 else 'public')
