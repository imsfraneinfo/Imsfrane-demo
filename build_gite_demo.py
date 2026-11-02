"""Real Gite Atlas accommodation, demo only; reuse the apartment design."""
from pathlib import Path
import re, shutil, json
from html import escape

DATA = {
'fr': {
'name':'Gîte Atlas Cathédrale','tag':'UNE ESCALE FACE À IMSFRANE','intro':'Prenez le temps de séjourner face à la Cathédrale d’Imsfrane. Chambres pour deux, en couple, à trois ou à quatre, terrasse ouverte sur la montagne et espaces extérieurs : choisissez votre séjour dans l’Atlas.',
'nav':['Le gîte','Chambres et espaces','Nos formules','Réservation'],'about':'Votre séjour au pied des paysages de l’Atlas','amenities':['Wi-Fi','Parking gratuit','Espace pour les tentes','Vue sur le mont Imsfrane'],
'rooms':[
('Des chambres pour vos voyages à deux','Des chambres à deux lits individuels accueillent les voyageurs qui souhaitent partager une chambre tout en gardant leur propre lit. Des chambres pour trois et quatre personnes sont également proposées, selon les disponibilités.','twin'),
('Une chambre pour les couples','Les chambres avec lit double offrent un espace pour une escapade à deux. Indiquez le type de chambre souhaité lors de votre demande de réservation.','double'),
('Douche et toilettes','Les installations sanitaires comprennent douche, toilettes et lavabo. Retrouvez ici une photo réelle de la salle d’eau du gîte.','bathroom'),
('La terrasse face à la Cathédrale','Installez-vous sur la terrasse couverte, autour des tables en bois, et profitez de la vue sur le mont Imsfrane. Un espace pour se retrouver entre deux découvertes.','terrace'),
('Les espaces extérieurs','Le gîte dispose d’un espace pour les tentes, du Wi-Fi et d’un parking gratuit. Pour un séjour sous tente, contactez-nous afin de préciser les conditions et le tarif.','garden')],
'packages':'Choisissez votre formule','unit':'par personne','night':'par personne / nuit','included':'Nuitée + dîner + petit-déjeuner','choose':'Choisir cette formule','packageNames':['Nuitée & demi-pension','Séjour avec tous les repas','Week-end du vendredi au dimanche'],
'packageTexts':['Une nuit au gîte, le dîner et le petit-déjeuner du lendemain.','Petit-déjeuner, déjeuner, dîner, nuitée et petit-déjeuner du lendemain.','Vendredi : arrivée, dîner et nuitée. Samedi : petit-déjeuner, déjeuner, dîner et nuitée. Dimanche : petit-déjeuner et déjeuner, puis départ.'],
'request':'Sur demande','note':'Tarifs par personne. Le prix du week-end reste à confirmer. Disponibilité et type de chambre à confirmer avant la réservation.','book':'Réserver sur WhatsApp','bookingTitle':'Préparons votre séjour','bookingText':'Choisissez votre formule et indiquez votre date d’arrivée et le nombre de voyageurs. Votre demande sera adressée directement à Farid sur WhatsApp.','fields':['Programme','Date d’arrivée','Nombre de personnes','Type de chambre (facultatif)'],'roomTypes':['Sans préférence','Deux lits individuels','Lit double · couple','Trois personnes','Quatre personnes'],'confirm':'La demande ne confirme pas automatiquement la réservation. Nous vous répondrons avec les disponibilités.','discover':'Découvrir','message':'Bonjour, je souhaite réserver au Gîte Atlas Cathédrale.'},
'en': {
'name':'Gîte Atlas Cathédrale','tag':'A STOPOVER FACING IMSFRANE','intro':'Take time to stay overlooking the Imsfrane Cathedral. Twin, double, triple and four-person rooms, a mountain-facing terrace and outdoor spaces: choose your Atlas stay.',
'nav':['The gîte','Rooms and spaces','Stay packages','Booking'],'about':'Your stay among the Atlas landscapes','amenities':['Wi-Fi','Free parking','Space for tents','Imsfrane mountain views'],
'rooms':[
('Twin rooms for shared journeys','Rooms with two single beds welcome travellers who want to share a room with separate beds. Rooms for three and four guests are also offered, subject to availability.','twin'),
('A room for couples','Double-bed rooms offer a space for a getaway together. Tell us your preferred room type when requesting your booking.','double'),
('Shower and toilet','Bathroom facilities include a shower, toilet and washbasin. This is a real photo of a bathroom at the gîte.','bathroom'),
('A terrace facing the Cathedral','Sit around the wooden tables on the covered terrace and enjoy the view of Mount Imsfrane. A space to spend time together between outings.','terrace'),
('Outdoor spaces','The gîte offers space for tents, Wi-Fi and free parking. For a stay in a tent, contact us to confirm arrangements and pricing.','garden')],
'packages':'Choose your stay','unit':'per person','night':'per person / night','included':'Overnight stay + dinner + breakfast','choose':'Choose this package','packageNames':['Overnight & half board','Stay with all meals','Friday to Sunday weekend'],
'packageTexts':['One night at the gîte, dinner and breakfast the next morning.','Breakfast, lunch, dinner, an overnight stay and breakfast the next morning.','Friday: arrival, dinner and overnight stay. Saturday: breakfast, lunch, dinner and overnight stay. Sunday: breakfast and lunch, then departure.'],
'request':'On request','note':'Prices per person. Weekend price to be confirmed. Availability and room type must be confirmed before booking.','book':'Book on WhatsApp','bookingTitle':'Plan your stay','bookingText':'Choose your package, arrival date and number of guests. Your request goes directly to Farid on WhatsApp.','fields':['Package','Arrival date','Number of guests','Room type (optional)'],'roomTypes':['No preference','Two single beds','Double bed · couple','Three guests','Four guests'],'confirm':'Sending a request does not automatically confirm a booking. We will reply with availability.','discover':'Discover','message':'Hello, I would like to book at Gîte Atlas Cathédrale.'},
'es': {
'name':'Gîte Atlas Cathédrale','tag':'UNA ESTANCIA FRENTE A IMSFRANE','intro':'Disfruta de una estancia frente a la Catedral de Imsfrane. Habitaciones con dos camas, cama doble, para tres o cuatro personas, terraza con vistas a la montaña y espacios exteriores: elige tu estancia en el Atlas.',
'nav':['El alojamiento','Habitaciones y espacios','Nuestras opciones','Reserva'],'about':'Tu estancia entre los paisajes del Atlas','amenities':['Wi-Fi','Aparcamiento gratuito','Espacio para tiendas','Vistas al monte Imsfrane'],
'rooms':[
('Habitaciones con dos camas','Las habitaciones con dos camas individuales permiten compartir una habitación manteniendo camas separadas. También hay habitaciones para tres y cuatro personas, según disponibilidad.','twin'),
('Una habitación para parejas','Las habitaciones con cama doble ofrecen un espacio para una escapada en pareja. Indica el tipo de habitación que prefieres al solicitar tu reserva.','double'),
('Ducha y aseo','Las instalaciones sanitarias incluyen ducha, aseo y lavabo. Aquí se muestra una foto real de un baño del alojamiento.','bathroom'),
('La terraza frente a la Catedral','Siéntate alrededor de las mesas de madera en la terraza cubierta y disfruta de las vistas al monte Imsfrane. Un espacio para compartir momentos entre excursiones.','terrace'),
('Los espacios exteriores','El alojamiento dispone de espacio para tiendas, Wi-Fi y aparcamiento gratuito. Para una estancia en tienda, contáctanos para confirmar las condiciones y el precio.','garden')],
'packages':'Elige tu estancia','unit':'por persona','night':'por persona / noche','included':'Noche + cena + desayuno','choose':'Elegir esta opción','packageNames':['Noche y media pensión','Estancia con todas las comidas','Fin de semana de viernes a domingo'],
'packageTexts':['Una noche en el alojamiento, cena y desayuno del día siguiente.','Desayuno, almuerzo, cena, una noche y desayuno del día siguiente.','Viernes: llegada, cena y noche. Sábado: desayuno, almuerzo, cena y noche. Domingo: desayuno y almuerzo, y salida.'],
'request':'Bajo consulta','note':'Precios por persona. Precio del fin de semana pendiente de confirmación. Disponibilidad y tipo de habitación a confirmar antes de reservar.','book':'Reservar por WhatsApp','bookingTitle':'Prepara tu estancia','bookingText':'Elige la opción, la fecha de llegada y el número de viajeros. Tu solicitud llegará directamente a Farid por WhatsApp.','fields':['Programa','Fecha de llegada','Número de personas','Tipo de habitación (opcional)'],'roomTypes':['Sin preferencia','Dos camas individuales','Cama doble · pareja','Tres personas','Cuatro personas'],'confirm':'La solicitud no confirma automáticamente la reserva. Te responderemos con la disponibilidad.','discover':'Descubrir','message':'Hola, quiero reservar en Gîte Atlas Cathédrale.'},
'ar': {
'name':'نزل أطلس كاتدرال','tag':'إقامة بإطلالة على مسفران','intro':'استمتع بإقامة أمام جبل مسفران. غرف بسريرين منفردين أو بسرير مزدوج، وغرف لثلاثة أو أربعة أشخاص، وشرفة مطلة على الجبل وفضاءات خارجية: اختر إقامتك في الأطلس.',
'nav':['النزل','الغرف والمرافق','برامج الإقامة','الحجز'],'about':'إقامتك وسط مناظر الأطلس','amenities':['واي فاي','موقف سيارات مجاني','فضاء للخيام','إطلالة على جبل مسفران'],
'rooms':[
('غرف بسريرين منفردين','غرف بسريرين منفردين للمسافرين الراغبين في مشاركة الغرفة مع الاستفادة من سرير مستقل لكل شخص. تتوفر أيضاً غرف لثلاثة وأربعة أشخاص، حسب التوفر.','twin'),
('غرف بسرير مزدوج','توفر الغرف ذات السرير المزدوج مساحة لإقامة الأزواج. حدّد نوع الغرفة الذي تفضّله عند إرسال طلب الحجز.','double'),
('الدش والمرحاض','تشمل المرافق الصحية دشاً ومرحاضاً وحوض غسل. هذه صورة حقيقية لإحدى غرف الاستحمام في النزل.','bathroom'),
('الشرفة المطلة على مسفران','اجلس حول الطاولات الخشبية في الشرفة المغطاة واستمتع بالإطلالة على جبل مسفران. فضاء للقاء والاستراحة بين الجولات.','terrace'),
('الفضاءات الخارجية','يتوفر النزل على فضاء للخيام وخدمة واي فاي وموقف سيارات مجاني. للإقامة في خيمة، تواصل معنا لتأكيد الشروط والثمن.','garden')],
'packages':'اختر برنامج إقامتك','unit':'للشخص','night':'للشخص / ليلة','included':'المبيت + العشاء + فطور الصباح','choose':'اختر هذا البرنامج','packageNames':['المبيت والعشاء والفطور','إقامة مع جميع الوجبات','نهاية الأسبوع من الجمعة إلى الأحد'],
'packageTexts':['ليلة في النزل مع العشاء وفطور صباح اليوم التالي.','الفطور والغداء والعشاء والمبيت وفطور صباح اليوم التالي.','الجمعة: الوصول والعشاء والمبيت. السبت: الفطور والغداء والعشاء والمبيت. الأحد: الفطور والغداء ثم المغادرة.'],
'request':'الثمن عند الطلب','note':'الأثمنة للشخص الواحد. ثمن نهاية الأسبوع قيد التأكيد. يجب تأكيد التوفر ونوع الغرفة قبل الحجز.','book':'احجز عبر واتساب','bookingTitle':'لنخطّط لإقامتك','bookingText':'اختر البرنامج وحدّد تاريخ الوصول وعدد الأشخاص. سيُوجَّه طلبك مباشرة إلى فريد عبر واتساب.','fields':['البرنامج','تاريخ الوصول','عدد الأشخاص','نوع الغرفة (اختياري)'],'roomTypes':['دون تفضيل','سريران منفردان','سرير مزدوج · للأزواج','ثلاثة أشخاص','أربعة أشخاص'],'confirm':'إرسال الطلب لا يؤكد الحجز تلقائياً. سنرد عليك بشأن التوفر.','discover':'اكتشف النزل','message':'مرحباً، أود الحجز في نزل أطلس كاتدرال (Gîte Atlas Cathédrale).'}
}

def build(root):
    base='/Imsfrane-demo/'
    shutil.copytree(Path(__file__).parent/'gite-assets',root/'images/gite-atlas',dirs_exist_ok=True)
    src=base+'images/gite-atlas/'
    for lang,d in DATA.items():
        template=(root/f'apartment-content-{lang}.html').read_text()
        head=template.split('<body>')[0]
        head=re.sub(r'<title\b[^>]*>.*?</title>',f'<title>{d["name"]} | Imsfrane</title>',head)
        head=head.replace('</head>','''<style>.hero h1{font-size:clamp(54px,6.4vw,92px)}.gite-price{font:600 40px/1.2 var(--serif);color:#a94f30;margin:20px 0}.step .btn{margin-top:20px;white-space:normal;text-align:center}.gite-form{display:grid;gap:18px}.gite-form label{display:grid;gap:8px;font-size:13px;font-weight:700}.gite-form input,.gite-form select{width:100%;min-width:0;padding:14px;border:1px solid #a6aca9;background:white;color:#163037;font:inherit;border-radius:5px}.gite-form button{cursor:pointer;white-space:normal}.booking-grid>*{min-width:0}.apt-amenities .chip{background:#eee9df;color:#163037;padding:10px 14px;border-radius:20px;font-size:13px}.step{display:flex;flex-direction:column}.step .btn{margin-top:auto}.step p{margin-bottom:24px}.hero-stat strong{font-size:30px}.hero-stat small{line-height:1.6}.gite-note{font-size:12px;line-height:1.8;opacity:.85}[dir=rtl] input[type=date]{direction:ltr}@media(max-width:650px){.hero h1{font-size:58px}.hero-bottom{grid-template-columns:1fr}.hero-stat strong{font-size:28px}.gite-price{font-size:34px}.quicknav-grid{grid-template-columns:1fr 1fr!important}}</style></head>''')
        def img(name,alt,lazy=True):
            return f'<img src="{src}{name}.webp" alt="{escape(alt,quote=True)}" width="1152" height="1536" '+('loading="lazy"' if lazy else 'fetchpriority="high"')+'>'
        rooms=''
        for i,(title,body,photo) in enumerate(d['rooms'],1):
            rooms+=f'<section class="room-section"><div class="container room-row"><div class="room-copy"><div class="kicker">{i:02} · {d["name"]}</div><h2 class="heading">{title}</h2><p>{body}</p></div><div class="room-visual"><a href="{src}{photo}.webp" target="_blank" rel="noopener">{img(photo,title)}</a></div></div></section>'
        prices=['250 DH','350 DH',d['request']]
        cards=''
        for i,(title,body,price) in enumerate(zip(d['packageNames'],d['packageTexts'],prices)):
            cards+=f'<article class="step"><div class="step-index">{i+1:02}</div><h3>{title}</h3><div class="gite-price">{price}</div><small>{d["unit"]}</small><p>{body}</p><a class="btn btn-dark" href="#booking" data-package="{i}">{d["choose"]} ↓</a></article>'
        options=''.join(f'<option value="{i}">{escape(n)} · {prices[i]}</option>' for i,n in enumerate(d['packageNames']))
        room_options=''.join(f'<option>{escape(n)}</option>' for n in d['roomTypes'])
        chips=''.join(f'<span class="chip">✓ {x}</span>' for x in d['amenities'])
        quick=''.join(f'<a href="#{id}"><span>{i:02}</span><strong>{label}</strong></a>' for i,(id,label) in enumerate(zip(['gite','rooms','programme','booking'],d['nav']),1))
        f=d['fields']
        hero_title='نزل أطلس' if lang=='ar' else 'Gîte Atlas'
        hero_em='كاتدرال' if lang=='ar' else 'Cathédrale'
        body=f'''<body><main>
<section class="hero"><div class="hero-main"><div class="hero-copy"><div class="topline">{d['tag']}</div><h1>{hero_title}<br><em>{hero_em}</em></h1><p class="hero-summary">{d['intro']}</p><div class="hero-acts"><a class="btn btn-gold" href="#booking">{d['book']} ↗</a><a class="btn btn-line-light" href="#programme">{d['nav'][2]} ↓</a></div><div class="hero-bottom"><div class="hero-stat"><strong>250 DH</strong><small>{d['night']}<br>{d['included']}</small></div></div></div><div class="hero-media"><div class="shot main">{img('exterior',d['name'],False)}</div><div class="shot">{img('terrace',d['rooms'][3][0],False)}</div><div class="shot">{img('double',d['rooms'][1][0],False)}</div><div class="hero-badge"><span>IMSFRANE · ATLAS</span><b>{d['amenities'][3]}</b></div></div></div></section>
<nav class="quicknav"><div class="container quicknav-grid">{quick}</div></nav>
<section class="section" id="gite"><div class="container"><div class="kicker">{d['name']}</div><h2 class="heading">{d['about']}</h2><p class="lead" style="max-width:740px;margin-top:24px">{d['intro']}</p><div class="apt-amenities">{chips}</div></div></section>
<div id="rooms">{rooms}</div>
<section class="section" id="programme"><div class="container"><div class="section-header"><h2 class="heading">{d['packages']}</h2></div><div class="steps-grid apt-steps">{cards}</div><p class="apt-note">{d['note']}</p></div></section>
<section class="section booking-section" id="booking"><div class="container booking-grid"><div class="booking-copy"><div class="kicker">{d['name']}</div><h2 class="heading">{d['bookingTitle']}</h2><p>{d['bookingText']}</p><p class="gite-note">{d['confirm']}</p></div><form id="giteBooking" class="booking-form gite-form" action="https://wa.me/212667772551" method="get" target="_blank"><label for="package">{f[0]}<select id="package" required>{options}</select></label><label for="arrival">{f[1]}<input id="arrival" type="date" required></label><label for="guests">{f[2]}<input id="guests" type="number" min="1" step="1" required value="2" inputmode="numeric"></label><label for="roomType">{f[3]}<select id="roomType">{room_options}</select></label><input type="hidden" name="text" id="message"><button class="btn btn-gold" type="submit">{d['book']} ↗</button></form></div></section>
</main>'''
        config=json.dumps({'message':d['message'],'labels':f,'programmes':[n+' · '+prices[i]+' / '+d['unit'] for i,n in enumerate(d['packageNames'])]},ensure_ascii=False)
        script='''<script>(function(){
const cfg=CONFIG;
const form=document.getElementById('giteBooking'),date=document.getElementById('arrival'),plan=document.getElementById('package');
const now=new Date();date.min=[now.getFullYear(),String(now.getMonth()+1).padStart(2,'0'),String(now.getDate()).padStart(2,'0')].join('-');
document.querySelectorAll('[data-package]').forEach(a=>a.addEventListener('click',()=>{plan.value=a.dataset.package;}));
form.addEventListener('submit',function(e){
if(!form.reportValidity()){e.preventDefault();return;}
const message=cfg.message+'\\n'+cfg.labels[0]+': '+cfg.programmes[Number(plan.value)]+'\\n'+cfg.labels[1]+': '+date.value+'\\n'+cfg.labels[2]+': '+document.getElementById('guests').value+'\\n'+cfg.labels[3]+': '+document.getElementById('roomType').value;
document.getElementById('message').value=message;
});
})();</script></body></html>'''.replace('CONFIG',config)
        (root/f'gite-content-{lang}.html').write_text(head+body+script)
        outer=(root/lang/'hebergement/index.html').read_text()
        outer=outer.replace('apartmentExperienceFrame','giteExperienceFrame').replace(f'apartment-content-{lang}.html?v=rooms3',f'gite-content-{lang}.html?v=atlas1')
        outer=re.sub(r'<title\b[^>]*>.*?</title>',f'<title>{d["name"]} | Imsfrane Cathédrale</title>',outer,flags=re.S)
        outer=re.sub(r'(<iframe[^>]*title=")[^"]*',lambda m:m[1]+d['name'],outer)
        outer=re.sub(r'<meta\b[^>]*(?:property="og:|name="twitter:|name="description")[^>]*>','',outer)
        outer=re.sub(r'<link\b[^>]*(?:rel="canonical"|rel="alternate"|rel="preload")[^>]*>','',outer)
        outer=re.sub(r'(<div class="atnav-langmini-panel".*?</div>)',lambda m:m[0].replace('/hebergement/','/gite-atlas/'),outer,flags=re.S)
        (root/lang/'gite-atlas/index.html').write_text(outer)
        chooser=root/lang/'hebergements/index.html'
        listing=chooser.read_text()
        card=f'<article class="stay-card"><img src="{src}exterior.webp" alt="{d["name"]}" loading="lazy"><div class="stay-card-body"><span class="stay-eyebrow">02 · GÎTE ATLAS</span><h2>{d["name"]}</h2><p><strong>250 DH</strong> · {d["night"]}</p><p>{d["included"]}</p><a class="stay-button" href="{base}{lang}/gite-atlas/">{d["discover"]} ↗</a></div></article>'
        listing=re.sub(r'<article class="stay-card">(?:(?!</article>).)*?/gite-atlas/(?:(?!</article>).)*?</article>',lambda _:card,listing,flags=re.S)
        chooser.write_text(listing)

        # Put the auberge beside the existing apartment card on each homepage.
        home=root/lang/'index.html'
        html=home.read_text()
        html=re.sub(r'<article class="hp-activity-card hp-gite-atlas">.*?</article>','',html,flags=re.S)
        url=f'{base}{lang}/gite-atlas/'
        card=f'''<article class="hp-activity-card hp-gite-atlas"><a class="hp-activity-image" href="{url}" aria-label="{d['name']}"><img src="{src}exterior.webp" alt="{d['name']}" width="1152" height="1536" loading="lazy" decoding="async"></a><div class="hp-activity-body"><div class="hp-activity-location"><i class="fa-solid fa-location-dot" aria-hidden="true"></i><span>{d['amenities'][3]}</span></div><h3>{d['name']}</h3><p>{d['included']}</p><div class="hp-activity-bottom"><strong>250 DH / {d['night']}</strong><a href="{url}" aria-label="{d['discover']} · {d['name']}"><span>{d['discover']}</span><i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a></div></div></article>'''
        html,count=re.subn(r'<article class="hp-activity-card hp-hebergement">.*?</article>',lambda m:m[0]+card,html,count=1,flags=re.S)
        assert count==1, f'Missing apartment homepage card: {home}'
        home.write_text(html)

    print('Built Gite Atlas in FR/EN/ES/AR with real photos and WhatsApp booking.')

if __name__=='__main__':
    import sys
    build(Path(sys.argv[1] if len(sys.argv)>1 else 'public'))
