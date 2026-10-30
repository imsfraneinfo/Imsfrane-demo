"""Demo-only accommodation selector and Gite Atlas preview. Standard library only."""
from pathlib import Path
import re, sys, shutil
root=Path(sys.argv[1] if len(sys.argv)>1 else 'public')
base='/Imsfrane-demo/'
photo='https://images.trvl-media.com/lodging/120000000/119200000/119191800/119191751/d97d4be8.jpg?impolicy=resizecrop&ra=fill&rh=900&rw=1400'
photo2='https://cdn.audleytravel.com/1050/749/79/8001040-kasbah-du-toubkal-high-atlas-mountains.webp'
texts={
'fr':['Hébergement','Maison à louer','Choisissez votre séjour','Deux façons de vivre Imsfrane.','Retrouvez la maison à louer ou découvrez notre nouvelle page Gîte Atlas Cathédrale.','Voir la maison','Découvrir le gîte','Une pause au cœur de l’Atlas','Préparez votre séjour à Gîte Atlas Cathédrale avec notre équipe.','Photos d’ambiance provisoires, issues du web : elles ne représentent pas Gîte Atlas Cathédrale.','Votre séjour, à votre rythme','Échangeons sur vos dates, le nombre de voyageurs et les repas souhaités pour préparer une proposition adaptée.','Nuitées & repas','Formules et tarifs à confirmer avec le gîte.','Autour de votre séjour','Randonnée, gorges et activités : programme à organiser selon vos envies et les disponibilités.','Demander des informations','Tarif sur demande','Disponibilités, équipements et conditions à confirmer avant réservation.','Tous les hébergements'],
'en':['Accommodation','House for rent','Choose your stay','Two ways to experience Imsfrane.','Explore the existing rental house or discover our new Gîte Atlas Cathédrale page.','View the house','Discover the gîte','A pause in the heart of the Atlas','Plan your stay at Gîte Atlas Cathédrale with our team.','Temporary web mood photos: they do not depict Gîte Atlas Cathédrale.','A stay at your own pace','Tell us your dates, party size and meal preferences so we can prepare a suitable proposal.','Nights & meals','Packages and prices to be confirmed with the gîte.','Around your stay','Hiking, gorges and activities: a programme arranged around your wishes and availability.','Ask for information','Price on request','Availability, amenities and conditions to be confirmed before booking.','All accommodation'],
'es':['Alojamiento','Casa de alquiler','Elige tu estancia','Dos formas de vivir Imsfrane.','Descubre la casa de alquiler o nuestra nueva página Gîte Atlas Cathédrale.','Ver la casa','Descubrir el alojamiento','Una pausa en el corazón del Atlas','Prepara tu estancia en Gîte Atlas Cathédrale con nuestro equipo.','Fotos de ambiente provisionales de la web: no representan Gîte Atlas Cathédrale.','Una estancia a tu ritmo','Indícanos las fechas, el número de viajeros y las comidas deseadas para preparar una propuesta.','Noches y comidas','Fórmulas y precios por confirmar con el alojamiento.','Durante tu estancia','Senderismo, gargantas y actividades según tus preferencias y disponibilidad.','Solicitar información','Precio a consultar','Disponibilidad, instalaciones y condiciones por confirmar antes de reservar.','Todos los alojamientos'],
'ar':['الإقامة','منزل للكراء','اختر إقامتك','طريقتان للاستمتاع بمسفران.','اكتشف المنزل المتاح للكراء أو صفحة نزل أطلس كاتدرال الجديدة.','اكتشف المنزل','اكتشف النزل','استراحة في قلب الأطلس','خطط لإقامتك في نزل أطلس كاتدرال بمساعدة فريقنا.','صور توضيحية مؤقتة من الإنترنت، ولا تمثل نزل أطلس كاتدرال.','إقامة تناسب رغباتك','أخبرنا بمواعيد زيارتك وعدد المسافرين والوجبات المطلوبة لنعد لك اقتراحاً مناسباً.','المبيت والوجبات','تُؤكّد الصيغ والأثمنة مع النزل.','أنشطة خلال إقامتك','المشي الجبلي والمضايق والأنشطة: برنامج حسب رغباتك والتوفر.','اطلب المعلومات','الثمن عند الطلب','يجب تأكيد التوفر والتجهيزات والشروط قبل الحجز.','جميع خيارات الإقامة']}
css='''
.stay-menu{margin:3px 0}.stay-menu summary{cursor:pointer;list-style:none;display:flex;align-items:center;gap:12px;padding:12px 16px;color:inherit;font:inherit;border-radius:12px}.stay-menu summary:after{content:'+';margin-inline-start:auto}.stay-menu[open] summary:after{content:'−'}.stay-menu-links{padding-inline-start:30px;display:grid;gap:3px}.stay-menu-links a{padding:12px 14px;display:block;color:inherit;border-inline-start:2px solid #bc8c54;text-decoration:none}.stay-menu a:hover{background:#f1eadf;color:#183b32}
.stay-main{background:#f7f5ef;color:#183b32;padding-bottom:80px}.stay-wrap{max-width:1160px;margin:auto;padding:0 24px}.stay-intro{padding:70px 0 36px}.stay-eyebrow{text-transform:uppercase;font:600 12px/1.5 Inter,sans-serif;letter-spacing:2px;color:#896944}.stay-main h1{font:600 clamp(38px,6vw,72px)/1.08 'Playfair Display',serif;margin:18px 0 24px;max-width:850px}.stay-main p{font-size:17px;line-height:1.8;max-width:720px}.stay-grid{display:grid;grid-template-columns:1fr 1fr;gap:28px}.stay-card{background:#fff;border:1px solid #deded3;border-radius:20px;overflow:hidden}.stay-card img{width:100%;height:310px;object-fit:cover}.stay-card-body{padding:28px}.stay-main h2{font:600 30px/1.3 'Playfair Display',serif;margin:10px 0 20px}.stay-button{display:inline-flex;background:#173d32;color:#fff!important;padding:14px 22px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:16px}.stay-button:hover{background:#2e5a48}.stay-hero{width:100%;height:clamp(280px,42vw,520px);object-fit:cover;border-radius:20px}.stay-note{font-size:12px!important;color:#726b60;margin:12px 0 38px}.stay-content{display:grid;grid-template-columns:1.5fr 1fr;gap:48px;padding-top:20px}.stay-booking{align-self:start;background:#e9eee5;border:1px solid #d4dfcf;border-radius:18px;padding:28px}.stay-detail{padding:22px 0;border-bottom:1px solid #deded3}.stay-second{width:100%;height:300px;object-fit:cover;border-radius:14px;margin-top:24px}.stay-breadcrumb{display:inline-block;color:#536858;margin-top:30px}.stay-main[dir=rtl] h1,.stay-main[dir=rtl] h2{font-family:Tajawal,Arial,sans-serif}@media(max-width:680px){.stay-grid,.stay-content{grid-template-columns:1fr}.stay-intro{padding-top:38px}.stay-card img{height:240px}.stay-content{gap:24px}.stay-wrap{padding:0 18px}}
'''
(root/'stays-demo.css').write_text(css)
for lang,t in texts.items():
    folder=root/lang
    source=(folder/'hebergement/index.html').read_text()
    house=base+lang+'/hebergement/'
    listing=base+lang+'/hebergements/'
    gite=base+lang+'/gite-atlas/'
    def render(main,title,route):
        s=re.sub(r'<main\b[^>]*>.*?</main>',main,source,count=1,flags=re.S)
        s=re.sub(r'<title\b[^>]*>.*?</title>','<title>'+title+' | Imsfrane Cathédrale</title>',s,flags=re.S)
        s=re.sub(r'<meta\b[^>]*(?:property="og:|name="twitter:|name="description")[^>]*>','',s)
        s=re.sub(r'<link\b[^>]*(?:rel="canonical"|rel="alternate"|rel="preload")[^>]*>','',s)
        s=re.sub(r'<script\b[^>]*src="[^"]*(?:hebergement.min.js|image-controls.js)[^"]*"[^>]*></script>','',s)
        s=re.sub(r'<script\b[^>]*src="[^"]*adsbygoogle[^"]*"[^>]*></script>','',s)
        s=s.replace('</head>',f'<link rel="stylesheet" href="{base}stays-demo.css?v=1"><meta name="robots" content="noindex,follow"></head>')
        for code in texts:
            s=s.replace(base+code+'/hebergement/',base+code+'/'+route+'/') if False else s
        # Only switch the compact language picker, preserving all other links.
        s=re.sub(r'(<div class="atnav-langmini-panel".*?</div>)',lambda m:re.sub(r'/(fr|en|ar|es)/hebergement/',lambda x:'/'+x[1]+'/'+route+'/',m[0]),s,flags=re.S)
        return s
    common=f'class="stay-main" id="mainContent" dir="{"rtl" if lang=="ar" else "ltr"}"'
    name='نزل أطلس كاتدرال' if lang=='ar' else 'Gîte Atlas Cathédrale'
    main=f'''<main {common}><div class="stay-wrap"><div class="stay-intro"><span class="stay-eyebrow">{t[0]} · IMSFRANE</span><h1>{t[2]}</h1><h2>{t[3]}</h2><p>{t[4]}</p></div><div class="stay-grid"><article class="stay-card"><img src="{base}images/bab2.webp" alt="{t[1]}"><div class="stay-card-body"><span class="stay-eyebrow">01 · IMSFRANE</span><h2>{t[1]}</h2><a class="stay-button" href="{house}">{t[5]} ↗</a></div></article><article class="stay-card"><img src="{photo}" alt="{t[9]}"><div class="stay-card-body"><span class="stay-eyebrow">02 · GÎTE ATLAS</span><h2>{name}</h2><a class="stay-button" href="{gite}">{t[6]} ↗</a><p class="stay-note">{t[9]}</p></div></article></div></div></main>'''
    (folder/'hebergements').mkdir(exist_ok=True)
    (folder/'hebergements/index.html').write_text(render(main,t[0],'hebergements'))
    main=f'''<main {common}><div class="stay-wrap"><a class="stay-breadcrumb" href="{listing}">← {t[19]}</a><div class="stay-intro"><span class="stay-eyebrow">{t[7]}</span><h1>{name}</h1><p>{t[8]}</p></div><img class="stay-hero" src="{photo}" alt="{t[9]}"><p class="stay-note">{t[9]}</p><div class="stay-content"><section><h2>{t[10]}</h2><p>{t[11]}</p><div class="stay-detail"><h2>{t[12]}</h2><p>{t[13]}</p></div><div class="stay-detail"><h2>{t[14]}</h2><p>{t[15]}</p></div><img class="stay-second" loading="lazy" src="{photo2}" alt="{t[9]}"><p class="stay-note">{t[9]}</p></section><aside class="stay-booking"><span class="stay-eyebrow">GÎTE ATLAS CATHÉDRALE</span><h2>{t[17]}</h2><p>{t[18]}</p><a class="stay-button" target="_blank" rel="noopener" href="https://wa.me/212667772551?text=Bonjour%2C%20je%20souhaite%20des%20informations%20sur%20Gite%20Atlas%20Cathedrale.">{t[16]} ↗</a></aside></div></div></main>'''
    (folder/'gite-atlas').mkdir(exist_ok=True)
    (folder/'gite-atlas/index.html').write_text(render(main,name,'gite-atlas'))
    for p in folder.rglob('*.html'):
        s=p.read_text()
        if '<body' not in s:continue
        # Only navigation links change. Existing house page main remains untouched.
        pattern=r'<a\b[^>]*class="atnav-submenu-link"[^>]*href="[^"]*/hebergement/(?:"|\?)[^>]*>.*?</a>'
        submenu=f'<details class="stay-menu"><summary>{t[0]}</summary><div class="stay-menu-links"><a href="{house}">{t[1]}</a><a href="{gite}">{name}</a></div></details>'
        s=re.sub(pattern,lambda m:submenu,s,flags=re.S)
        # Other entry points (home card, footer) lead to the two-option listing.
        if p not in [folder/'hebergement/index.html',folder/'hebergement.html',folder/'hebergements/index.html',folder/'gite-atlas/index.html']:
            s=s.replace('href="'+house+'"','href="'+listing+'"')
            # Restore the direct house link in submenu.
            s=s.replace(f'<a href="{listing}">{t[1]}</a>',f'<a href="{house}">{t[1]}</a>')
        if 'stays-demo.css' not in s:s=s.replace('</head>',f'<link rel="stylesheet" href="{base}stays-demo.css?v=1"></head>')
        p.write_text(s)
if Path('gite-atlas-form.html').exists():shutil.copyfile('gite-atlas-form.html',root/'gite-atlas-form.html')
print('Built accommodation selector and Gite Atlas preview in four languages.')
