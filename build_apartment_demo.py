"""Single apartment presentation for the demo only."""
from pathlib import Path
from urllib.parse import quote
import re, shutil

def build(root):
    base='/Imsfrane-demo/'
    assets=Path(__file__).parent/'apartment-assets'
    shutil.copytree(assets,root/'images/apartment',dirs_exist_ok=True)
    shutil.copyfile(root/'images/bab2.webp',root/'images/apartment/bedroom.webp')
    data={
      'fr': ['Maison à louer','Un appartement, rien que pour vous.','Un séjour à Imsfrane avec un salon, une cuisine et un balcon ouvert sur le paysage.', '300 DH','par nuit · appartement entier','Votre appartement','Cuisine','Douche et toilettes','Salon','Chambre pour deux','Deux banquettes','Les photos de l’appartement','Demander les disponibilités','Contactez-nous pour confirmer vos dates et votre réservation.','Tous les hébergements',['Balcon','Salon','Cuisine','Douche et toilettes','Couloir','Vue depuis le balcon'],'Bonjour, je souhaite réserver l’appartement à 300 DH par nuit. Mes dates : … Nombre de voyageurs : …'],
      'en': ['House for rent','An apartment all to yourself.','Stay in Imsfrane with a living room, a kitchen and a balcony overlooking the landscape.','300 MAD','per night · entire apartment','Your apartment','Kitchen','Shower and toilet','Living room','Bedroom for two','Two banquettes','Apartment photos','Check availability','Contact us to confirm your dates and booking.','All accommodation',['Balcony','Living room','Kitchen','Shower and toilet','Hallway','View from the balcony'],'Hello, I would like to book the apartment at 300 MAD per night. Dates: … Number of guests: …'],
      'es': ['Casa de alquiler','Un apartamento solo para ti.','Una estancia en Imsfrane con salón, cocina y un balcón abierto al paisaje.','300 MAD','por noche · apartamento completo','Tu apartamento','Cocina','Ducha y aseo','Salón','Dormitorio para dos','Dos divanes','Fotos del apartamento','Consultar disponibilidad','Contáctanos para confirmar tus fechas y tu reserva.','Todos los alojamientos',['Balcón','Salón','Cocina','Ducha y aseo','Pasillo','Vista desde el balcón'],'Hola, quiero reservar el apartamento a 300 MAD por noche. Fechas: … Número de viajeros: …'],
      'ar': ['منزل للكراء','شقة كاملة ليكم بوحدكم.','إقامة فمسفران، بصالون وكوزينة وبالكون كيطل على المناظر المحيطة.','300 درهم','فالليلة · الشقة كاملة','شنو كاين فالشقة','كوزينة','دوش وطواليط','صالون','بيت نعاس ديال جوج','جوج بانكوات','صور الشقة','سول على التوفر','تواصل معانا باش نأكدو ليك التواريخ والحجز.','جميع خيارات الإقامة',['البالكون','الصالون','الكوزينة','الدوش والطواليط','الممر','الإطلالة من البالكون'],'سلام، بغيت نحجز الشقة بـ300 درهم فالليلة. التواريخ: … عدد الأشخاص: …']
    }
    names=['balcony','living-room','bedroom','kitchen','bathroom','hallway','view']
    for lang,t in data.items():
        t[15].insert(2, t[9])
        p=root/lang/'hebergement/index.html'
        s=p.read_text()
        gallery=''.join(f'<figure><a href="{base}images/apartment/{n}.webp" target="_blank" rel="noopener" aria-label="{label}"><img src="{base}images/apartment/{n}.webp" alt="{label}" width="1152" height="1536" loading="lazy"></a><figcaption>{label}</figcaption></figure>' for n,label in zip(names,t[15]))
        amenities=''.join(f'<li><span aria-hidden="true">✓</span> {x}</li>' for x in t[6:11])
        main=f'''<main class="stay-main apartment-main" id="mainContent" dir="{'rtl' if lang=='ar' else 'ltr'}"><div class="stay-wrap"><a class="stay-breadcrumb" href="{base}{lang}/hebergements/">{t[14]}</a><div class="apartment-intro"><div><span class="stay-eyebrow">IMSFRANE · {t[0]}</span><h1>{t[1]}</h1><p>{t[2]}</p></div><div class="apartment-price"><strong>{t[3]}</strong><span>{t[4]}</span></div></div><div class="apartment-cover"><img src="{base}images/apartment/balcony.webp" alt="{t[15][0]}" width="1152" height="1536" fetchpriority="high"><img src="{base}images/apartment/living-room.webp" alt="{t[15][1]}" width="1152" height="1536"></div><div class="stay-content"><section><h2>{t[5]}</h2><ul class="apartment-amenities">{amenities}</ul></section><aside class="stay-booking"><h2>{t[3]}</h2><p>{t[4]}</p><a class="stay-button" href="https://wa.me/212667772551?text={quote(t[16])}" target="_blank" rel="noopener">{t[12]} ↗</a><p class="stay-note">{t[13]}</p></aside></div><section class="apartment-gallery-section"><h2>{t[11]}</h2><div class="apartment-gallery">{gallery}</div></section></div></main>'''
        s=re.sub(r'<main\b[^>]*>.*?</main>',lambda _:main,s,count=1,flags=re.S)
        s=re.sub(r'<script\b[^>]*src="[^"]*(?:hebergement.min.js|image-controls.js)[^"]*"[^>]*></script>','',s)
        s=re.sub(r'<script\b[^>]*type="application/ld\+json"[^>]*>.*?</script>','',s,flags=re.S)
        s=re.sub(r'<meta\b[^>]*(?:property="og:|name="twitter:|name="description")[^>]*>','',s)
        s=re.sub(r'<title>.*?</title>',f'<title>{t[0]} · {t[3]} | Imsfrane</title>',s,flags=re.S)
        s=s.replace('</head>',f'<link rel="stylesheet" href="{base}apartment-demo.css?v=1"></head>')
        p.write_text(s)
        (root/lang/'hebergement.html').write_text(s)
        chooser=root/lang/'hebergements/index.html'
        chooser.write_text(chooser.read_text().replace(base+'images/bab2.webp',base+'images/apartment/balcony.webp'))
    (root/'apartment-demo.css').write_text('''
.apartment-intro{display:flex;align-items:center;gap:36px;justify-content:space-between;padding:46px 0 32px}.apartment-intro h1{font-size:clamp(36px,5vw,60px);max-width:760px}.apartment-price{flex-shrink:0;background:#e9eee5;border-radius:18px;padding:25px;display:grid;gap:8px}.apartment-price strong{font-size:38px}.apartment-price span{font-size:14px}.apartment-cover{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:36px}.apartment-cover img{width:100%;height:480px;object-fit:cover;border-radius:18px}.apartment-amenities{list-style:none;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:18px;font-size:18px}.apartment-amenities span{color:#53755e;margin-inline-end:8px}.apartment-gallery-section{margin-top:54px}.apartment-gallery{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}.apartment-gallery figure{margin:0}.apartment-gallery img{width:100%;height:auto;aspect-ratio:3/4;object-fit:cover;border-radius:14px;display:block}.apartment-gallery a:focus-visible{outline:3px solid #896944;outline-offset:5px}.apartment-gallery figcaption{padding:12px 0;font-size:15px}.apartment-main .stay-note{margin-bottom:0}@media(max-width:680px){.apartment-intro{display:block;padding-top:30px}.apartment-price{margin-top:24px}.apartment-cover{gap:10px}.apartment-cover img{height:280px}.apartment-gallery{grid-template-columns:1fr 1fr;gap:14px}.apartment-amenities{grid-template-columns:1fr;font-size:17px}}
''')
