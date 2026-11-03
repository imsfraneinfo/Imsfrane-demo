"""One accessible, four-language footer for every public demo page.
Run last so page builders cannot reintroduce their older footer variants.
The business name and contact digits must never be translated or reordered.
"""
from pathlib import Path
from html import escape
from datetime import datetime,timezone
import re,json
ROOT=Path('public');BASE='/Imsfrane-demo/'
BRAND='Imsfrane Cathédrale';PHONE='+212 667 772 551';EMAIL='imsfraneinfo@gmail.com'
T={
'fr':dict(kicker='LE HAUT ATLAS VOUS ATTEND',title='Votre prochaine aventure commence ici.',cta='Parlons de votre séjour',tag='Aventures dans le Haut Atlas',about='Au pied de la Cathédrale, explorez les montagnes, la rivière et les sentiers de Msfrane avec notre équipe locale.',explore='Préparer votre séjour',experiences='Nos expériences',contact='Restons en contact',links=['Programme','Hébergement','Guide pratique','Galerie photos','Le journal','Boutique','Notre équipe','Réservation'],activities=['Rafting','Kayak','Randonnée','Camping','VTT','Quad'],tel='Téléphone',mail='E-mail',place='Sur place',address='Tilouguite · Msfrane\nProvince d’Azilal, Maroc',note='Dates et disponibilités à confirmer avec notre équipe.',rights='Tous droits réservés.',privacy='Politique de confidentialité',home='Accueil',wa='WhatsApp'),
'en':dict(kicker='THE HIGH ATLAS IS CALLING',title='Your next adventure starts here.',cta='Let’s plan your stay',tag='Adventures in the High Atlas',about='At the foot of the Cathedral, explore Msfrane’s mountains, river and trails with our local team.',explore='Plan your stay',experiences='Our experiences',contact='Get in touch',links=['Programme','Accommodation','Visitor guide','Photo gallery','The journal','Shop','Our team','Booking'],activities=['Rafting','Kayak','Hiking','Camping','Mountain biking','Quad biking'],tel='Phone',mail='Email',place='Find us',address='Tilouguite · Msfrane\nAzilal province, Morocco',note='Confirm dates and availability with our team.',rights='All rights reserved.',privacy='Privacy policy',home='Home',wa='WhatsApp'),
'es':dict(kicker='EL ALTO ATLAS TE ESPERA',title='Tu próxima aventura empieza aquí.',cta='Hablemos de tu estancia',tag='Aventuras en el Alto Atlas',about='Al pie de la Catedral, descubre las montañas, el río y los senderos de Msfrane con nuestro equipo local.',explore='Prepara tu estancia',experiences='Nuestras experiencias',contact='Contacta con nosotros',links=['Programa','Alojamiento','Guía de visita','Galería de fotos','El diario','Tienda','Nuestro equipo','Reservas'],activities=['Rafting','Kayak','Senderismo','Acampada','BTT','Quad'],tel='Teléfono',mail='Correo electrónico',place='Dónde estamos',address='Tilouguite · Msfrane\nProvincia de Azilal, Marruecos',note='Confirma las fechas y la disponibilidad con nuestro equipo.',rights='Todos los derechos reservados.',privacy='Política de privacidad',home='Inicio',wa='WhatsApp'),
'ar':dict(kicker='الأطلس الكبير في انتظارك',title='مغامرتك المقبلة تبدأ من هنا.',cta='خطط لإقامتك معنا',tag='مغامرات في الأطلس الكبير',about='عند سفح جبل مسفران، اكتشف الجبال والوادي والمسارات الطبيعية برفقة فريقنا المحلي.',explore='خطط لرحلتك',experiences='تجاربنا',contact='تواصل معنا',links=['البرنامج','الإقامة','دليل الزيارة','معرض الصور','المدونة','المتجر','فريقنا','الحجز'],activities=['التجديف','الكاياك','المشي الجبلي','التخييم','الدراجات الجبلية','جولات الدراجات الرباعية'],tel='الهاتف',mail='البريد الإلكتروني',place='موقعنا',address='تيلوكيت · مسفران\nإقليم أزيلال، المغرب',note='تواصل مع فريقنا لتأكيد المواعيد والتوفر.',rights='جميع الحقوق محفوظة.',privacy='سياسة الخصوصية',home='الرئيسية',wa='واتساب')}
ICONS={
'phone':'<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .3 2 .7 2.9a2 2 0 0 1-.5 2.1L8 10a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c.9.4 1.9.6 2.9.7a2 2 0 0 1 1.7 2z"/>',
'mail':'<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>',
'pin':'<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0z"/><circle cx="12" cy="10" r="2.5"/>',
'instagram':'<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/>',
'facebook':'<path d="M14 22V12h3l.5-4H14V6c0-1 .4-2 2-2h2V1h-3c-3 0-5 2-5 5v2H7v4h3v10"/>',
'whatsapp':'<path d="M21 11.5a9 9 0 0 1-13.4 7.8L3 21l1.7-4.5A9 9 0 1 1 21 11.5z"/><path d="M8 7c-1 3 3 7 6 7l1-2-2-1-1 1-3-3 1-1-1-2z"/>',
 'tiktok':'<path d="M14 3v12a5 5 0 1 1-4-4.9V14a2 2 0 1 0 1 1V3h3c.5 3 2 4.5 5 5V5c-2-.4-3-1.2-3-2"/>'}
def icon(name):return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">'+ICONS[name]+'</svg>'
def dest(lang,slug):
 p=ROOT/lang/slug/'index.html'
 if p.is_file():return BASE+lang+'/'+slug+'/'
 p=ROOT/lang/(slug+'.html')
 if p.is_file():return BASE+lang+'/'+slug+'.html'
 raise FileNotFoundError(f'Footer destination missing: {lang}/{slug}')
def markup(lang):
 d=T[lang];home=BASE+lang+'/'
 stays='hebergements' if (ROOT/lang/'hebergements/index.html').is_file() else 'hebergement'
 links=''.join('<li><a href="'+dest(lang,slug)+'">'+escape(label)+'</a></li>' for slug,label in zip(['programme',stays,'guide','memories','blog','store','about','booking'],d['links']))
 acts=''.join('<li><a href="'+dest(lang,slug)+'">'+escape(label)+'</a></li>' for slug,label in zip(['rafting','kayak','randonnee','camping','vtt','quad'],d['activities']))
 socials=''.join('<a href="'+url+'" target="_blank" rel="noopener noreferrer" aria-label="'+label+'">'+icon(name)+'</a>' for name,label,url in [('instagram','Instagram','https://www.instagram.com/imsfrane_cathedrale'),('facebook','Facebook','https://www.facebook.com/Imsfranecathedrale'),('tiktok','TikTok','https://www.tiktok.com/@imsfrane_cathedrale'),('whatsapp',d['wa'],'https://wa.me/212667772551')])
 return f'''<footer id="ims-footer" class="site-footer ims-footer-pro" lang="{lang}" dir="{'rtl' if lang=='ar' else 'ltr'}"><div class="fp-wrap">
<div class="fp-invite"><div><span class="fp-kicker">{d['kicker']}</span><h2>{d['title']}</h2></div><a class="fp-cta" href="https://wa.me/212667772551" target="_blank" rel="noopener noreferrer">{icon('whatsapp')}<span>{d['cta']}</span></a></div>
<div class="fp-grid"><div class="fp-brand"><a class="fp-logo-link" href="{home}" aria-label="{d['home']} · {BRAND}"><img class="fp-logo" src="{BASE}images/logo-104.webp" width="58" height="58" alt="{BRAND}" loading="lazy" decoding="async"><span><bdi class="fp-brand-name" dir="ltr">{BRAND}</bdi><span class="fp-brand-tag">{d['tag']}</span></span></a><p class="fp-about">{d['about']}</p><div class="fp-socials">{socials}</div></div>
<nav class="fp-explore" aria-label="{d['explore']}"><h3 class="fp-heading">{d['explore']}</h3><ul class="fp-links">{links}</ul></nav>
<nav class="fp-experiences" aria-label="{d['experiences']}"><h3 class="fp-heading">{d['experiences']}</h3><ul class="fp-links">{acts}</ul></nav>
<div class="fp-contact"><h3 class="fp-heading">{d['contact']}</h3><div class="fp-contact-list">
<a class="fp-contact-item fp-phone" href="tel:+212667772551"><span class="fp-icon">{icon('phone')}</span><span><span class="fp-contact-label">{d['tel']}</span><bdi class="fp-contact-value fp-ltr" dir="ltr">{PHONE}</bdi></span></a>
<a class="fp-contact-item" href="mailto:{EMAIL}"><span class="fp-icon">{icon('mail')}</span><span><span class="fp-contact-label">{d['mail']}</span><bdi class="fp-contact-value fp-email fp-ltr" dir="ltr">{EMAIL}</bdi></span></a>
<div class="fp-contact-item"><span class="fp-icon">{icon('pin')}</span><span><span class="fp-contact-label">{d['place']}</span><span class="fp-contact-value">{d['address'].replace(chr(10),'<br>')}</span></span></div>
</div><p class="fp-contact-note">{d['note']}</p></div></div>
<div class="fp-bottom"><p>© <span id="currentYear">{datetime.now(timezone.utc).year}</span> <bdi dir="ltr" class="fp-ltr">{BRAND}</bdi>. {d['rights']}</p><a class="ims-privacy-link" href="{dest(lang,'privacy')}">{d['privacy']}</a></div>
</div></footer>'''

def build():
 (ROOT/'footer-pro.css').write_text(Path('footer-pro.css').read_text())
 (ROOT/'footer-pro.js').write_text(Path('footer-pro.js').read_text())
 footers={l:markup(l) for l in T};changed=[]
 for lang,content in footers.items():(ROOT/f'footer-pro-content-{lang}.json').write_text(json.dumps({'html':content},ensure_ascii=False))
 for path in sorted(ROOT.rglob('*.html')):
  rel=path.relative_to(ROOT)
  if any(part in ('admin','Imsfrane-demo') for part in rel.parts) or rel.name.startswith('qa-mobile'):continue
  source=path.read_text(encoding='utf-8')
  if not re.search(r'<footer\b',source,re.I):
   if str(rel)!='404.html':continue
   source=source.replace('</body>','<footer></footer></body>')
  # Ignore footer examples embedded as literal source in developer interfaces.
  if not re.search(r'<html\b',source,re.I):continue
  match=re.search(r'<html\b[^>]*\blang=["\']([^"\']+)',source,re.I)
  lang=next((part for part in rel.parts if part in T),match[1][:2] if match and match[1][:2] in T else 'fr')
  count=0
  def replace_footer(m):
   nonlocal count
   count+=1
   return footers[lang] if count==1 else ''
  source=re.sub(r'<footer\b[^>]*>.*?</footer\s*>',replace_footer,source,flags=re.S|re.I)
  source=re.sub(r'<link\b[^>]*href=["\'][^"\']*footer-pro\.css[^"\']*["\'][^>]*>','',source,flags=re.I)
  source=source.replace('</head>',f'<link rel="stylesheet" href="{BASE}footer-pro.css?v=1"></head>',1)
  source=re.sub(r'<script\b[^>]*src=["\'][^"\']*footer-pro\.js[^"\']*["\'][^>]*>.*?</script>','',source,flags=re.S|re.I)
  source=source.replace('</body>',f'<script defer src="{BASE}footer-pro.js?v=1"></script></body>',1)
  path.write_text(source,encoding='utf-8');changed.append(str(rel))
 (ROOT/'footer-build-report.json').write_text(json.dumps({'pages':changed,'count':len(changed),'locales':list(T),'phone':PHONE,'brand':BRAND},ensure_ascii=False,indent=2))
 print(f'Unified footer on {len(changed)} public HTML pages; phone isolated LTR in all four languages.')
if __name__=='__main__':build()
