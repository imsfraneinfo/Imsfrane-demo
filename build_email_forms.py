"""Add the two enquiry channels after the existing demo builders have run."""
from html import escape
from pathlib import Path
import json,re,shutil,sys

SOURCE=Path(__file__).resolve().parent
TEXT={
 'fr':('Envoyer par e-mail','Envoyer sur WhatsApp','Choisissez l’e-mail ou WhatsApp pour envoyer votre demande. Le téléphone est facultatif pour l’envoi par e-mail.','Requise pour l’envoi par e-mail, facultative pour WhatsApp.'),
 'en':('Send by email','Send on WhatsApp','Send your enquiry by email or WhatsApp. A phone number is optional when sending by email.','Required for email, optional for WhatsApp.'),
 'es':('Enviar por correo','Enviar por WhatsApp','Envía tu solicitud por correo electrónico o WhatsApp. El teléfono es opcional para el envío por correo.','Obligatorio para correo, opcional para WhatsApp.'),
 'ar':('إرسال بالبريد الإلكتروني','إرسال عبر واتساب','اختر إرسال طلبك بالبريد الإلكتروني أو عبر واتساب. رقم الهاتف اختياري عند الإرسال بالبريد الإلكتروني.','مطلوب للإرسال بالبريد الإلكتروني، واختياري لواتساب.')}


# The same service identifiers are used across all four languages.
SUBJECT_GROUPS = (
 ('rafting','kayak','hiking','mountain-bike','quad','camping','bivouac'),
 ('rental-house','gite-atlas'),
 ('weekend','custom-trip','transfer','route','booking','shop','partnership','other'),
)
CONTACT_COPY = {
 'fr': ('Envoyer une demande','Choisissez un sujet et indiquez-nous ce que vous aimeriez faire à Imsfrane.','Choisir un sujet','Vos dates, l’activité ou l’hébergement souhaité et vos questions…',
        ('Activités de plein air','Hébergements','Séjours et autres demandes'),
        ('Rafting','Kayak en eau vive','Randonnée guidée','VTT','Quad','Camping sauvage','Bivouac','Maison à louer','Gîte Atlas Cathédrale','Week-end à Imsfrane','Séjour sur mesure','Transport et transferts','Itinéraire et accès','Suivi d’une réservation','Boutique','Partenariat','Autre demande')),
 'en': ('Send an enquiry','Choose a topic and tell us what you’d like to do in Imsfrane.','Choose a topic','Share your dates, preferred activities or accommodation, and any questions…',
        ('Outdoor activities','Accommodation','Trip planning and other enquiries'),
        ('Rafting','Whitewater kayaking','Guided hiking','Mountain biking','Quad biking','Wild camping','Bivouac','Holiday home rental','Gîte Atlas Cathédrale','Imsfrane weekend trip','Custom itinerary','Transport and transfers','Directions and access','Existing booking','Shop','Partnership','Other enquiry')),
 'es': ('Envía una consulta','Elige un tema y cuéntanos qué te gustaría hacer en Imsfrane.','Elige un tema','Indica tus fechas, las actividades o el alojamiento que te interesan y tus preguntas…',
        ('Actividades al aire libre','Alojamiento','Viajes y otras consultas'),
        ('Rafting','Kayak en aguas bravas','Senderismo guiado','BTT','Quad','Acampada libre','Vivac','Casa de alquiler','Gîte Atlas Cathédrale','Fin de semana en Imsfrane','Viaje a medida','Transporte y traslados','Cómo llegar','Consulta sobre una reserva','Tienda','Colaboración','Otra consulta')),
 'ar': ('أرسل استفسارك','اختر موضوعاً وأخبرنا بما ترغب في القيام به في مسفران.','اختر موضوعاً','اذكر مواعيد زيارتك والنشاط أو الإقامة التي تفضّلها وأي أسئلة لديك…',
        ('الأنشطة في الهواء الطلق','الإقامة','الرحلات والاستفسارات الأخرى'),
        ('التجديف النهري','الكاياك في المياه السريعة','المشي الجبلي مع مرشد','الدراجات الجبلية','الدراجات الرباعية','التخييم في الطبيعة','المبيت في المخيم','منزل للإيجار','Gîte Atlas Cathédrale','عطلة نهاية الأسبوع في مسفران','رحلة حسب الطلب','النقل والتنقلات','الطريق وكيفية الوصول','متابعة حجز','المتجر','الشراكات','استفسار آخر')),
}

def refine_contact(html, lang):
    heading, intro, placeholder, message, groups, labels = CONTACT_COPY[lang]
    choices = iter(labels)
    options = [f'<option value="" selected disabled>{escape(placeholder)}</option>']
    for group, keys in zip(groups, SUBJECT_GROUPS, strict=True):
        options.append(f'<optgroup label="{escape(group)}">')
        options.extend(f'<option value="{key}">{escape(next(choices))}</option>' for key in keys)
        options.append('</optgroup>')
    html, count = re.subn(r'(<select\b[^>]*\bid="contactSubject"[^>]*>).*?(</select>)',
                          lambda m: m[1] + ''.join(options) + m[2], html, count=1, flags=re.S)
    assert count == 1, f'Missing subject selector: {lang}'
    html = re.sub(r'(<textarea\b[^>]*\bid="contactMessage"[^>]*\bplaceholder=")[^"]*',
                  lambda m: m[1] + escape(message), html, count=1)
    header = f'<div class="enquiry-intro"><h2 id="enquiryTitle">{escape(heading)}</h2><p>{escape(intro)}</p></div>'
    return re.sub(r'<form\b[^>]*\bid="contactForm"[^>]*>', lambda m: m[0][:-1] + ' aria-labelledby="enquiryTitle">' + header, html, count=1)


PAGE_COPY = {
 'fr': ('Contact','Organisons votre séjour à Imsfrane','Une question sur les activités, l’hébergement ou votre arrivée ? Écrivez-nous pour préparer votre visite.','Contacter notre équipe','Téléphone','E-mail','Où nous trouver','Tilouguite, Azilal, Maroc','Voir sur la carte'),
 'en': ('Contact','Let’s plan your Imsfrane visit','Ask us about activities, accommodation or getting here. We’ll help you plan your stay.','Reach our team','Phone','Email','Find us','Tilouguite, Azilal, Morocco','View on map'),
 'es': ('Contacto','Planifica tu visita a Imsfrane','Escríbenos si tienes dudas sobre las actividades, el alojamiento o cómo llegar.','Contacta con el equipo','Teléfono','Correo electrónico','Dónde estamos','Tilouguite, Azilal, Marruecos','Ver en el mapa'),
 'ar': ('التواصل','خطّط لزيارتك إلى مسفران','راسلنا للاستفسار عن الأنشطة والإقامة وكيفية الوصول، وسنساعدك في التخطيط لزيارتك.','تواصل مع فريقنا','الهاتف','البريد الإلكتروني','موقعنا','تيلوكيت، أزيلال، المغرب','عرض الموقع على الخريطة'),
}

def rebuild_contact_page(html, lang, base):
    kicker, title, intro, team, phone, email, where, address, map_text = map(escape, PAGE_COPY[lang])
    form = re.search(r'<form\b[^>]*\bid="contactForm"[^>]*>.*?</form>', html, flags=re.S)
    assert form, f'Missing contact form: {lang}'
    image = base + 'images/contact-rafting-bottom.webp'
    page = f'''<main id="mainContent" class="contact-landing">
      <header class="contact-landing-header">
        <p class="contact-eyebrow">{kicker} · Imsfrane Cathédrale</p>
        <h1>{title}</h1><p>{intro}</p>
      </header>
      <div class="contact-landing-grid">
        {form[0]}
        <aside class="contact-landing-aside">
          <img src="{image}" alt="" width="640" height="360" loading="lazy" decoding="async">
          <div class="contact-aside-content">
            <h2>{team}</h2>
            <dl>
              <div><dt>WhatsApp</dt><dd><a href="https://wa.me/212667772551"><bdi dir="ltr">+212 667 772 551</bdi></a></dd></div>
              <div><dt>{phone}</dt><dd><a href="tel:+212667772551"><bdi dir="ltr">+212 667 772 551</bdi></a></dd></div>
              <div><dt>{email}</dt><dd><a href="mailto:imsfraneinfo@gmail.com"><bdi dir="ltr">imsfraneinfo@gmail.com</bdi></a></dd></div>
              <div><dt>{where}</dt><dd>{address}</dd></div>
            </dl>
            <a class="contact-map-link" href="https://www.google.com/maps/search/?api=1&amp;query=Tilouguite%20Azilal%20Morocco">{map_text}</a>
          </div>
        </aside>
      </div>
    </main>'''
    html, count = re.subn(r'<main\b[^>]*\bid="mainContent"[^>]*>.*?</main>', lambda _: page, html, count=1, flags=re.S)
    assert count == 1, f'Missing contact main: {lang}'
    return html


ENQUIRY_TOPICS_BY_PAGE = {
    '': 'custom-trip',
    'rafting': 'rafting',
    'kayak': 'kayak',
    'randonnee': 'hiking',
    'vtt': 'mountain-bike',
    'quad': 'quad',
    'camping': 'camping',
    'hebergement': 'rental-house',
    'hebergements': 'rental-house',
    'gite-atlas': 'gite-atlas',
    'programme': 'custom-trip',
    'guide': 'route',
    'store': 'shop',
}

def embed_contact_forms(root, base, lang):
    locale = root / lang
    source = (locale / 'contact/index.html').read_text()
    form = re.search(r'<form\b[^>]*\bid="contactForm"[^>]*>.*?</form>', source, flags=re.S)
    assert form, f'Missing reusable contact form: {lang}'
    pages = {locale / route / 'index.html': topic for route, topic in ENQUIRY_TOPICS_BY_PAGE.items()}
    pages.update({path: 'rafting' for path in (locale / 'rafting').glob('*/index.html')})
    added = 0
    for path, topic in pages.items():
        if not path.is_file():
            continue
        html = path.read_text()
        if 'class="embedded-enquiry"' in html:
            continue
        assert 'id="contactForm"' not in html and 'id="bookingForm"' not in html, path
        selected = form[0].replace('value="" selected disabled', 'value="" disabled', 1)
        option = f'<option value="{topic}">'
        assert option in selected, topic
        selected = selected.replace(option, f'<option value="{topic}" selected>', 1)
        section = f'<section class="embedded-enquiry" aria-labelledby="enquiryTitle">{selected}</section>'
        if path == locale / 'index.html':
            anchor = r'(<section\b[^>]*\bid="activities"[^>]*>.*?</section>)(?=\s*<section\b[^>]*\bid="destination")'
            html, count = re.subn(anchor, lambda match: match[0] + section, html, count=1, flags=re.S)
        else:
            html, count = re.subn(r'</main>', lambda _: section + '</main>', html, count=1, flags=re.I)
        assert count == 1, f'Missing enquiry insertion point: {path}'
        html = html.replace('</head>', f'<link rel="stylesheet" href="{base}website-enquiry.css?v=6"></head>', 1)
        html = html.replace('</body>', f'<script defer src="{base}website-enquiry.js?v=1"></script></body>', 1)
        path.write_text(html)
        added += 1
    print(f'Embedded contact form in {added} pages ({lang})')

def build(root):
 base='/Imsfrane-demo/' if root.name=='public' else '/'
 for name in ('website-enquiry.js','website-enquiry.css'):
  shutil.copyfile(SOURCE/name,root/name)
 for lang,(email,wa,hint,emailhint) in TEXT.items():
  for route in ('contact','booking'):
   p=root/lang/route/'index.html';s=p.read_text()
   if 'data-channel="email"' in s and 'data-channel="whatsapp"' in s:
    continue
   s=re.sub(r'<(?:script|link)\b[^>]*(?:src|href)=["\'][^"\']*website-enquiry\.(?:js|css)[^"\']*["\'][^>]*>(?:</script>)?','',s)
   if route=='contact':
    s=refine_contact(s,lang)
    s=re.sub(r'<script\b[^>]*src="[^"]*pages/contact\.min\.js[^"]*"[^>]*></script>','',s)
    s=re.sub(r'<div class="contact-form-actions">.*?</div>','<div class="enquiry-actions"><button type="submit" id="sendEmail" class="enquiry-email" data-channel="email">'+email+'</button><button type="submit" id="sendWhatsApp" class="enquiry-whatsapp" data-channel="whatsapp">'+wa+'</button></div><p class="enquiry-hint">'+hint+'</p>',s,count=1,flags=re.S)
    s=s.replace('class="contact-form-message"','class="contact-form-message enquiry-status" data-enquiry-status')
    s=re.sub(r'(<input\b[^>]*id="contactPhone"[^>]*?)\srequired(?:="")?',r'\1',s)
    s=re.sub(r'(<input\b[^>]*id="contactEmail")',r'\1 required',s)
    s=re.sub(r'(<small\b[^>]*data-cms-text="contact-t41"[^>]*>).*?(</small>)',lambda m:m[1]+emailhint+m[2],s,flags=re.S)
   else:
    s=re.sub(r'<button type="submit" class="bk-send">.*?</button>\s*<p>.*?</p>', '<div class="enquiry-actions"><button type="submit" class="bk-send enquiry-email" data-channel="email">'+email+'</button><button type="submit" class="bk-send enquiry-whatsapp" data-channel="whatsapp">'+wa+'</button></div><p class="enquiry-hint">'+hint+'</p><p id="bookingSendStatus" class="enquiry-status" data-enquiry-status role="status" aria-live="polite"></p>',s,count=1,flags=re.S)
    s=s.replace('id="phone" type="tel" autocomplete="tel" minlength="6" maxlength="30" required','id="phone" type="tel" autocomplete="tel" minlength="6" maxlength="30"')
    s=s.replace('id="email" type="email"','id="email" required type="email"')
   trap='<label class="enquiry-trap" aria-hidden="true">Website<input name="website" tabindex="-1" autocomplete="off"></label>'
   s=s.replace('</form>',trap+'</form>',1)
   if route=='contact':
    s=rebuild_contact_page(s,lang,base)
   s=s.replace('</head>',f'<link rel="stylesheet" href="{base}website-enquiry.css?v=6"></head>',1)
   s=s.replace('</body>',f'<script defer src="{base}website-enquiry.js?v=1"></script></body>',1)
   p.write_text(s)
 for lang in TEXT:
  embed_contact_forms(root,base,lang)
 booking=root/'booking-new.js';js=booking.read_text()
 old="window.open('https://wa.me/212667772551?text='+encodeURIComponent(msg),'_blank','noopener');"
 new="""if(e.submitter?.dataset.channel==='email'){
 window.ImsEnquiry.send(form,{kind:'booking',name:$('name').value.trim(),email:$('email').value.trim(),subject:t[6],message:msg},$('bookingSendStatus'),e.submitter);
 }else{window.open('https://wa.me/212667772551?text='+encodeURIComponent(msg),'_blank','noopener');}"""
 if 'window.ImsEnquiry.send(form' not in js:
  assert old in js, 'Booking WhatsApp handler changed; review before patching'
  booking.write_text(js.replace(old,new,1))
 for lang in TEXT:
  for route in ('contact','booking'):
   s=(root/lang/route/'index.html').read_text()
   assert 'data-channel="email"' in s and 'data-channel="whatsapp"' in s,(lang,route)
   assert 'website-enquiry.js?v=1' in s
 print('Email + WhatsApp forms prepared for Contact and Booking in FR, EN, ES and AR')

if __name__ == '__main__':
 from build_social_previews import build as build_social_previews

 root = Path(sys.argv[1]) if len(sys.argv)>1 else SOURCE/'public'
 build(root)
 build_social_previews(root, 'https://imsfraneinfo.github.io/Imsfrane-demo')
 if root.name == 'public':
  from build_monochrome_demo import build as build_monochrome_demo

  # Finish the demo palette and link the menu brand to the localized home.
  build_monochrome_demo(root)

  from build_summit_card_demo import build as build_summit_card_demo

  # Finish the demo hiking page after the palette has been applied.
  build_summit_card_demo(root)

  from build_arabic_demo_review import build as build_arabic_demo_review

  build_arabic_demo_review(root)
