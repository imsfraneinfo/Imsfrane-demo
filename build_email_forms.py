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
 'fr': ('Parlons de votre séjour','Choisissez un sujet et indiquez-nous ce que vous aimeriez faire à Imsfrane.','Choisir un sujet','Vos dates, l’activité ou l’hébergement souhaité et vos questions…',
        ('Activités de plein air','Hébergements','Séjours et autres demandes'),
        ('Rafting','Kayak en eau vive','Randonnée guidée','VTT','Quad','Camping sauvage','Bivouac','Maison à louer','Gîte Atlas Cathédrale','Week-end à Imsfrane','Séjour sur mesure','Transport et transferts','Itinéraire et accès','Suivi d’une réservation','Boutique','Partenariat','Autre demande')),
 'en': ('Plan your visit','Choose a topic and tell us what you’d like to do in Imsfrane.','Choose a topic','Share your dates, preferred activities or accommodation, and any questions…',
        ('Outdoor activities','Accommodation','Trip planning and other enquiries'),
        ('Rafting','Whitewater kayaking','Guided hiking','Mountain biking','Quad biking','Wild camping','Bivouac','Holiday home rental','Gîte Atlas Cathédrale','Imsfrane weekend trip','Custom itinerary','Transport and transfers','Directions and access','Existing booking','Shop','Partnership','Other enquiry')),
 'es': ('Planifica tu visita','Elige un tema y cuéntanos qué te gustaría hacer en Imsfrane.','Elige un tema','Indica tus fechas, las actividades o el alojamiento que te interesan y tus preguntas…',
        ('Actividades al aire libre','Alojamiento','Viajes y otras consultas'),
        ('Rafting','Kayak en aguas bravas','Senderismo guiado','BTT','Quad','Acampada libre','Vivac','Casa de alquiler','Gîte Atlas Cathédrale','Fin de semana en Imsfrane','Viaje a medida','Transporte y traslados','Cómo llegar','Consulta sobre una reserva','Tienda','Colaboración','Otra consulta')),
 'ar': ('خطّط لزيارتك','اختر موضوعاً وأخبرنا بما ترغب في القيام به في مسفران.','اختر موضوعاً','اذكر مواعيد زيارتك والنشاط أو الإقامة التي تفضّلها وأي أسئلة لديك…',
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

def build(root):
 base='/Imsfrane-demo/' if root.name=='public' else '/'
 for name in ('website-enquiry.js','website-enquiry.css'):
  shutil.copyfile(SOURCE/name,root/name)
 for lang,(email,wa,hint,emailhint) in TEXT.items():
  for route in ('contact','booking'):
   p=root/lang/route/'index.html';s=p.read_text()
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
   s=s.replace('</head>',f'<link rel="stylesheet" href="{base}website-enquiry.css?v=4"></head>',1)
   s=s.replace('</body>',f'<script defer src="{base}website-enquiry.js?v=1"></script></body>',1)
   p.write_text(s)
 booking=root/'booking-new.js';js=booking.read_text()
 old="window.open('https://wa.me/212667772551?text='+encodeURIComponent(msg),'_blank','noopener');"
 new="""if(e.submitter?.dataset.channel==='email'){
 window.ImsEnquiry.send(form,{kind:'booking',name:$('name').value.trim(),email:$('email').value.trim(),subject:t[6],message:msg},$('bookingSendStatus'),e.submitter);
 }else{window.open('https://wa.me/212667772551?text='+encodeURIComponent(msg),'_blank','noopener');}"""
 assert old in js, 'Booking WhatsApp handler changed; review before patching'
 booking.write_text(js.replace(old,new,1))
 for lang in TEXT:
  for route in ('contact','booking'):
   s=(root/lang/route/'index.html').read_text()
   assert 'data-channel="email"' in s and 'data-channel="whatsapp"' in s,(lang,route)
   assert 'website-enquiry.js?v=1' in s
 print('Email + WhatsApp forms prepared for Contact and Booking in FR, EN, ES and AR')

if __name__=='__main__': build(Path(sys.argv[1]) if len(sys.argv)>1 else SOURCE/'public')
