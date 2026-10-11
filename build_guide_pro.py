"""Build the Demo-only bilingual text-first practical guide, leaving the brand intact."""
from pathlib import Path
from html import escape
import re

WHATSAPP="212667772551"
MAP_BASE="https://www.google.com/maps/search/?api=1&amp;query="
T={
"fr":{
 "eyebrow":"GUIDE PRATIQUE · HAUT ATLAS · MAROC",
 "title":"Préparer votre voyage <em>à Imsfrane.</em>",
 "lede":"Accès routier, itinéraires de randonnée, saisons, transport, camping et conseils de terrain. Toutes les informations essentielles au même endroit, sans photos inutiles.",
 "map":"Localiser Imsfrane","contact":"Parler à un guide local","facts":[("1 868 m","Sommet du Jebel Imsfrane"),("≈ 10 km","Depuis Tilouguite"),("Mars – juin","Période habituelle du rafting"),("Azilal","Province · Haut Atlas")],
 "aside":"Dans ce guide","nav":[("location","Imsfrane en bref"),("access","Comment venir"),("transport","Transport local"),("hikes","Randonnées & trajets"),("places","Lieux à découvrir"),("activities","Activités & tarifs"),("seasons","Quand venir"),("stay","Où dormir"),("packing","Que prévoir"),("safety","Sécurité & respect"),("faq","Questions fréquentes")],
 "topNotice":"À retenir","topNoticeText":"Le dernier tronçon est une route de montagne. Vérifiez la météo et l’état de la route, surtout après la pluie ou en hiver. Confirmez votre point de rendez-vous avant de partir.",
 "sectionLabel":"INFORMATIONS DE TERRAIN",
 "locationTitle":"Où se trouve Imsfrane ?",
 "locationLead":"Imsfrane (ou Msfrane) se situe dans la commune de Tilouguite, province d’Azilal, au cœur du Haut Atlas central. La montagne est surnommée « Cathédrale » en raison de sa silhouette rocheuse : il ne s’agit pas d’un lieu religieux.",
 "locationCards":[("Situation","Commune de Tilouguite · Province d’Azilal · Maroc."),("Repères","Jebel Imsfrane, vallées boisées, Oued Ahansal et paysages de montagne."),("Le bon réflexe","Cherchez d’abord Tilouguite, puis faites confirmer l’emplacement exact de votre activité ou hébergement.")],
 "accessTitle":"Comment venir à Imsfrane ?",
 "accessLead":"Voici les trajets routiers utilisés pour rejoindre la région. Les durées varient selon le véhicule, les arrêts, les travaux et les conditions de la montagne.",
 "routes":[
   ("01","Depuis Beni Mellal","Beni Mellal","Ouaouizeght","Tilouguite","Imsfrane","L’itinéraire de référence pour arriver depuis Beni Mellal. Prévoir une marge sur les portions de montagne."),
   ("02","Depuis Azilal","Azilal","Ouaouizeght","Tilouguite","Imsfrane","Une option d’accès depuis Azilal par Ouaouizeght et Tilouguite."),
   ("03","Depuis Marrakech ou Casablanca","Votre ville","Beni Mellal / Azilal","Ouaouizeght","Tilouguite → Imsfrane","Planifiez l’itinéraire GPS complet et vérifiez votre correspondance : ne comptez pas sur un trajet direct garanti.")
 ],
 "driveNotice":"La distance Tilouguite–Imsfrane est d’environ 10 km selon le point de départ. Il n’existe pas de durée universelle fiable sur ce tronçon : prévoyez une marge et privilégiez les déplacements de jour.",
 "openTilouguite":"Localiser Tilouguite","openImsfrane":"Rechercher Imsfrane",
 "transportTitle":"Transports et arrivée sur place",
 "transportLead":"Voiture personnelle, taxi partagé ou transfert convenu à l’avance : adaptez votre arrivée à l’heure de départ de l’activité.",
 "transportCards":[
   ("Voiture / location","Téléchargez votre trajet hors ligne. Faites le plein avant les zones isolées et ne prévoyez pas d’arrivée tardive sans repérage."),
   ("Grands taxis","Renseignez-vous pour les liaisons Beni Mellal → Ouaouizeght → Tilouguite. Les départs, correspondances et tarifs changent ; confirmez-les localement."),
   ("Transfert privé","Indiquez votre ville de départ, la date, le nombre de voyageurs et les bagages. Le transport est chiffré sur demande."),
   ("Point de rendez-vous","Le lieu exact peut être différent pour le rafting, la randonnée et l’hébergement. Demandez le point GPS avant de prendre la route.")
 ],
 "hikesTitle":"Randonnées guidées et trajets pédestres",
 "hikesLead":"Trois formules locales pour explorer les paysages autour de Msfrane. Durées indicatives : rythme du groupe, météo et état des chemins peuvent les modifier.",
 "hikes":[
   ("01","Sommet de Jebel Imsfrane","4–5 h","Moyenne","+668 m de dénivelé","300 MAD / groupe","Montée vers le sommet à environ 1 868 m, passages raides et pauses panoramiques. Chaussures de marche et eau indispensables.","randonnee.html"),
   ("02","Gorges et cascades de l’Ahansal","3–4 h","Facile","≈ 8 km","200 MAD / groupe","Marche le long des paysages de l’Ahansal, avec découverte des gorges et points d’intérêt selon le parcours convenu.","randonnee.html"),
   ("03","Le Grand Tour","8–10 h","Soutenu","≈ 24 km","400 MAD / groupe","Grande journée combinant l’exploration de la montagne et des gorges. À réserver aux personnes habituées à la marche longue.","randonnee.html")
 ],
 "difficulty":"Difficulté","more":"Découvrir la randonnée","hikeFoot":"Prix indiqués par groupe pour la prestation guidée. Transport, nourriture et autres services ne sont pas automatiquement inclus ; confirmer la composition du groupe avec le guide.",
 "placesTitle":"Autres lieux à découvrir autour d’Imsfrane",
 "placesLead":"Des idées de sorties à organiser selon l’accessibilité, le débit des cours d’eau et la disponibilité de guides locaux.",
 "places":[
   ("Gorges de l’Ahansal","Couloirs rocheux et passages proches de la rivière. Évitez tout franchissement risqué lorsque l’eau monte."),
   ("Cascades d’Oukhodene","Excursion à préparer avec un accompagnateur local ; l’accès pédestre et les conditions saisonnières sont à vérifier."),
   ("Oued Ahansal et Oued Melloul","Cours d’eau importants pour les activités de rivière : ne présumez jamais de la navigabilité ou de la sécurité."),
   ("Bin El Ouidane & Zaouiat Ahansal","Destinations régionales pour prolonger votre séjour ; demandez les trajets adaptés à votre programme.")
 ],
 "activityTitle":"Activités, saisons et tarifs indicatifs",
 "activityLead":"Un aperçu pour préparer un budget. Les dates, conditions, capacités et prix définitifs sont à confirmer directement avant toute réservation.",
 "activityRows":[
   ("Rafting · 12 km","400 MAD / personne","Mars à juin, parfois juillet si le niveau le permet","rafting.html"),
   ("Rafting · 30 km","800 MAD / personne","Selon les conditions de la rivière et du groupe","rafting.html"),
   ("VTT · sortie guidée","100 MAD / personne","Jusqu’à 2 h, selon disponibilités","vtt.html"),
   ("VTT · location journée","150 MAD / personne","Vélo à confirmer selon disponibilité","vtt.html"),
   ("Quad · solo","250 MAD / quad","Parcours d’environ 1 h ; une personne","quad.html"),
   ("Quad · duo","300 MAD / quad","Parcours d’environ 1 h ; deux personnes","quad.html"),
   ("Randonnée · sommet","300 MAD / groupe","Voir itinéraire ci-dessus","randonnee.html")
 ],
 "tableActivity":"Activité","tablePrice":"Tarif affiché","tableNote":"À savoir","view":"Voir",
 "seasonTitle":"Quelle est la meilleure période ?",
 "seasonLead":"Les saisons en montagne sont très variables d’une année à l’autre. Le rafting dépend du débit réel, et les randonnées dépendent des conditions du sentier.",
 "seasons":[
   ("Mars – juin","Rafting en saison habituelle","Débit à confirmer pour chaque descente. Randonnées à adapter à la météo."),
   ("Juillet – août","Randonnées tôt le matin · VTT · quad","Rafting parfois possible en juillet, jamais garanti. Prévoir la chaleur en journée."),
   ("Septembre – novembre","Randonnées · nature · VTT","Jours qui raccourcissent ; vérifier les conditions des chemins et de la route."),
   ("Décembre – février","Séjour montagne selon conditions","Froid, intempéries et routes potentiellement difficiles. Contact préalable indispensable.")
 ],
 "stayTitle":"Camping et hébergement",
 "stayLead":"Les tarifs de tentes ci-dessous sont pour une tente complète et une nuit, et non pour chaque occupant.",
 "tents":[("1 place","60 MAD / nuit"),("2 places","120 MAD / nuit"),("3 places","150 MAD / nuit"),("4 places","200 MAD / nuit")],
 "tentSize":"Capacité de la tente","tentPrice":"Prix par tente et par nuit",
 "stayMore":"Pour les chambres, la maison et les transferts, demandez un devis selon le nombre de personnes et les dates.","seeCamping":"Voir le camping","seeRooms":"Voir l’hébergement",
 "packingTitle":"Checklist avant de partir",
 "packingLead":"À adapter à la météo, à la durée du trajet et à votre activité.",
 "packGroups":[
  ("Pour la route",["Carte téléchargée hors connexion","Téléphone chargé et batterie externe","Carburant suffisant et espèces en MAD","Adresse et contact du point de rendez-vous"]),
  ("Pour la randonnée",["Chaussures de marche avec adhérence","Eau, encas et protection solaire","Couche chaude / veste imperméable","Lampe frontale et petite trousse de secours"]),
  ("Pour le camping et la rivière",["Vêtements de rechange et affaires chaudes","Sac étanche pour objets sensibles","Médicaments personnels","Briefing et équipement de sécurité fournis/confirmés par l’organisateur"])
 ],
 "safetyTitle":"Sécurité, réseau et tourisme responsable",
 "safetyLead":"Quelques précautions qui rendent votre sortie plus agréable et protègent les paysages.",
 "safetyList":[
   ("Météo & rivière","Orages, crues et débit peuvent modifier ou annuler un départ. Ne vous engagez jamais dans un canyon ou une rivière sans information récente."),
   ("Réseau & orientation","La couverture mobile peut être irrégulière. Gardez une carte hors connexion et indiquez votre programme à quelqu’un."),
   ("Randonnée & quad","Respectez les itinéraires choisis, les consignes du guide, votre niveau et la tranquillité des villages."),
   ("Respect des lieux","Emportez vos déchets, ne prélevez pas de plantes et demandez l’autorisation avant de photographier les habitants.")
 ],
 "faqTitle":"Questions fréquentes",
 "faq":[
   ("Peut-on venir sans voiture ?","C’est possible en organisant les trajets avec des taxis ou un transfert privé. Confirmez en amont les correspondances jusqu’à Tilouguite et le dernier trajet vers Imsfrane."),
   ("Le rafting fonctionne-t-il toute l’année ?","Non. La période habituelle s’étend de mars à juin, parfois juillet si le débit et la sécurité le permettent. Aucune sortie n’est garantie sans accord du guide."),
   ("Les tarifs comprennent-ils le transport ?","Pas systématiquement. Les prestations sont présentées selon leur unité (groupe, personne, quad ou tente/nuit). Demandez le détail et le prix total avant de confirmer."),
   ("Peut-on débuter la randonnée depuis l’hébergement ?","Un départ depuis votre hébergement peut être organisé selon son emplacement et le circuit retenu. Convenez du point de rencontre avant le jour J."),
   ("Les tentes sont-elles facturées par personne ?","Non : 60, 120, 150 ou 200 MAD correspondent au prix d’une tente complète par nuit, selon sa capacité."),
   ("Comment réserver ou demander un itinéraire personnalisé ?","Indiquez vos dates, le nombre de voyageurs, votre ville de départ et vos activités souhaitées via le formulaire ou WhatsApp. Notre équipe confirme la disponibilité.")
 ],
 "ctaTitle":"Un séjour plus simple avec un guide local.",
 "ctaText":"Envoyez vos dates, votre point de départ et le nombre de participants. Nous vous aidons à préparer l’itinéraire, choisir une randonnée et vérifier les activités de saison.",
 "book":"Préparer une réservation","wa":"Écrire sur WhatsApp","warning":"Les informations de cette page sont indicatives. Vérifiez météo, itinéraires, tarifs et disponibilités avant le déplacement."
},
"en":{
 "eyebrow":"PRACTICAL TRAVEL GUIDE · HIGH ATLAS · MOROCCO",
 "title":"Plan your visit <em>to Imsfrane.</em>",
 "lede":"Road access, hiking itineraries, seasons, local transport, camping and essential travel advice — all in one practical, photo-free guide.",
 "map":"Find Imsfrane on Maps","contact":"Ask a local guide","facts":[("1,868 m","Jebel Imsfrane summit"),("≈ 10 km","From Tilouguite"),("Mar – Jun","Usual rafting season"),("Azilal","Province · High Atlas")],
 "aside":"Guide contents","nav":[("location","Imsfrane at a glance"),("access","Getting here"),("transport","Local transport"),("hikes","Hiking routes"),("places","Nearby places"),("activities","Activities & prices"),("seasons","When to visit"),("stay","Camping & stays"),("packing","What to pack"),("safety","Safety & local respect"),("faq","Frequently asked questions")],
 "topNotice":"Good to know","topNoticeText":"The final leg is a mountain road. Check the weather and road conditions, particularly after rain or in winter. Confirm your exact meeting point before setting off.",
 "sectionLabel":"LOCAL TRAVEL INFORMATION",
 "locationTitle":"Where is Imsfrane?",
 "locationLead":"Imsfrane (also known as Msfrane) is in Tilouguite commune, Azilal province, in Morocco’s Central High Atlas. The mountain is nicknamed “Cathedral” for its rock silhouette; the name does not indicate a religious site.",
 "locationCards":[("Location","Tilouguite commune · Azilal province · Morocco."),("Landmarks","Jebel Imsfrane, forested valleys, Oued Ahansal and mountain scenery."),("Best tip","Search for Tilouguite first, then confirm the exact activity or accommodation meeting point.")],
 "accessTitle":"How to reach Imsfrane",
 "accessLead":"These are the main road approaches to the area. Driving times depend on the vehicle, stops, roadworks and mountain weather.",
 "routes":[
   ("01","From Beni Mellal","Beni Mellal","Ouaouizeght","Tilouguite","Imsfrane","The usual approach from Beni Mellal. Allow additional time on mountain sections."),
   ("02","From Azilal","Azilal","Ouaouizeght","Tilouguite","Imsfrane","An approach from Azilal via Ouaouizeght and Tilouguite."),
   ("03","From Marrakech or Casablanca","Your city","Beni Mellal / Azilal","Ouaouizeght","Tilouguite → Imsfrane","Plan the full GPS journey and connections: do not assume a guaranteed direct service.")
 ],
 "driveNotice":"Tilouguite is approximately 10 km from Imsfrane, depending on your starting point. Journey time varies considerably; leave extra time and prefer daylight travel.",
 "openTilouguite":"Find Tilouguite","openImsfrane":"Search Imsfrane",
 "transportTitle":"Local travel and getting around",
 "transportLead":"Own vehicle, shared taxi or prearranged transfer: plan your arrival around the activity start time.",
 "transportCards":[
   ("Driving / rental car","Download the route offline, fuel up before remote stretches and avoid late arrival without prior route knowledge."),
   ("Shared grand taxis","Ask locally about Beni Mellal → Ouaouizeght → Tilouguite connections. Schedules, onward rides and fares change."),
   ("Private transfer","Share your starting city, date, number of travellers and luggage. A separate transport quote can be prepared."),
   ("Meeting point","Rafting, hiking and accommodation may all have different meeting points. Ask for the GPS location before travelling.")
 ],
 "hikesTitle":"Guided hikes and walking itineraries",
 "hikesLead":"Three locally offered routes around Msfrane. Times vary with group pace, weather and trail conditions.",
 "hikes":[
   ("01","Jebel Imsfrane summit","4–5 h","Moderate","+668 m ascent","300 MAD / group","A summit hike to around 1,868 m, with steep sections and mountain viewpoints. Sturdy shoes and water are essential.","randonnee.html"),
   ("02","Ahansal gorges & waterfalls","3–4 h","Easy","≈ 8 km","200 MAD / group","A walk through the Ahansal landscape, including gorge scenery and local points of interest along the agreed route.","randonnee.html"),
   ("03","The Grand Tour","8–10 h","Strenuous","≈ 24 km","400 MAD / group","A full-day combination of mountain and gorge exploration. Best for walkers comfortable with long-distance hiking.","randonnee.html")
 ],
 "difficulty":"Difficulty","more":"Explore the hikes","hikeFoot":"Prices listed are per guided group. Transfers, meals and extras are not automatically included; confirm group size and inclusions with your guide.",
 "placesTitle":"More places near Imsfrane",
 "placesLead":"Ideas for visits depending on access, river conditions and local guide availability.",
 "places":[
   ("Ahansal gorges","Rock corridors and riverside paths. Avoid unsafe crossings when the river rises."),
   ("Oukhodene waterfalls","A visit to organise with a local guide; walking access and seasonal conditions must be checked."),
   ("Oued Ahansal & Oued Melloul","Important waterways for river activities. Never assume a river is safe to enter or navigate."),
   ("Bin El Ouidane & Zaouiat Ahansal","Regional destinations for longer trips; ask about suitable access roads and itineraries.")
 ],
 "activityTitle":"Activities, seasons and indicative prices",
 "activityLead":"A reference for budgeting. Dates, conditions, capacities and final prices must be confirmed directly before booking.",
 "activityRows":[
   ("Rafting · 12 km","400 MAD / person","Usually March–June; sometimes July when water levels permit","rafting.html"),
   ("Rafting · 30 km","800 MAD / person","Subject to river and group conditions","rafting.html"),
   ("Guided mountain biking","100 MAD / person","Up to 2 hours, subject to availability","vtt.html"),
   ("Full-day mountain bike rental","150 MAD / person","Bike availability to be confirmed","vtt.html"),
   ("Solo quad","250 MAD / quad","About 1 hour; one rider","quad.html"),
   ("Shared quad","300 MAD / quad","About 1 hour; two riders","quad.html"),
   ("Summit hiking","300 MAD / group","See walking itineraries above","randonnee.html")
 ],
 "tableActivity":"Activity","tablePrice":"Listed rate","tableNote":"Notes","view":"Details",
 "seasonTitle":"When is the best time to visit?",
 "seasonLead":"Mountain weather varies widely from year to year. Rafting depends on actual river levels; hiking depends on safe trail conditions.",
 "seasons":[
   ("March – June","Usual rafting season","River levels need checking before every trip. Adapt hikes to the weather."),
   ("July – August","Early hikes · MTB · quad","Rafting is sometimes possible in July but never guaranteed. Expect warm daytime conditions."),
   ("September – November","Hiking · nature · biking","Shorter days; check trail and road conditions."),
   ("December – February","Mountain visits when conditions allow","Cold, possible severe weather and difficult roads: check ahead.")
 ],
 "stayTitle":"Camping and local accommodation",
 "stayLead":"Tent prices below are per whole tent per night, not per occupant.",
 "tents":[("1 berth","60 MAD / night"),("2 berths","120 MAD / night"),("3 berths","150 MAD / night"),("4 berths","200 MAD / night")],
 "tentSize":"Tent capacity","tentPrice":"Price per tent per night",
 "stayMore":"For rooms, houses and transfers, ask for a quote with your dates and group size.","seeCamping":"See camping","seeRooms":"See accommodation",
 "packingTitle":"Your travel checklist",
 "packingLead":"Adjust these essentials to your activity, trip length and weather.",
 "packGroups":[
  ("On the road",["Downloaded offline route","Charged phone and power bank","Enough fuel and cash in MAD","Meeting point address and contact"]),
  ("For hiking",["Grippy walking shoes","Water, snacks and sun protection","Warm layer / waterproof jacket","Headlamp and basic first-aid kit"]),
  ("For camping and river trips",["Spare and warm clothing","Dry bag for valuables","Personal medication","Safety equipment and briefing arranged/confirmed with the organiser"])
 ],
 "safetyTitle":"Safety, phone coverage and responsible travel",
 "safetyLead":"A few precautions help make your trip safer and protect the local environment.",
 "safetyList":[
   ("Weather & river","Storms, flash floods and water levels may change or cancel departures. Never enter a gorge or river without recent local advice."),
   ("Signal & navigation","Mobile coverage may be patchy. Keep offline maps and share your plan with someone."),
   ("Hiking & quads","Stay on agreed trails, follow guide instructions and respect your abilities and local villages."),
   ("Respect nature","Take litter home, avoid picking wild plants and ask before photographing residents.")
 ],
 "faqTitle":"Frequently asked questions",
 "faq":[
   ("Can I travel without my own car?","Yes, with taxis or a prearranged transfer. Confirm transport connections to Tilouguite and the final journey to Imsfrane before leaving."),
   ("Is rafting available year-round?","No. The usual period is March through June, occasionally July if the river and safety conditions allow. Departures are never guaranteed without your guide’s confirmation."),
   ("Does the listed price include transport?","Not necessarily. Rates are displayed per group, person, quad or tent/night. Ask for the complete inclusions and total before confirming."),
   ("Can a hike start at my accommodation?","Sometimes. This can be arranged depending on where you stay and the selected walk. Agree on the meeting point beforehand."),
   ("Are tent prices per person?","No. Prices of 60, 120, 150 and 200 MAD are for a full tent per night, depending on its capacity."),
   ("How do I book a custom itinerary?","Send your dates, group size, starting city and preferred activities through the booking form or WhatsApp. The team will confirm availability.")
 ],
 "ctaTitle":"Make your Atlas trip easier with a local guide.",
 "ctaText":"Share your dates, start location and group size. We can help choose the right walking route and check seasonal activities.",
 "book":"Start a booking request","wa":"Message on WhatsApp","warning":"Information is indicative. Check the weather, routes, prices and availability before travel."
}
}

def e(x):
    return escape(str(x),quote=True)

def para(text):
    return "<p>"+e(text)+"</p>"

def heading(tag,title,desc=""):
    return '<div class="gp-heading"><span class="gp-section-label">IMSFRANE · HAUT ATLAS</span><'+tag+'>'+e(title)+'</'+tag+'>'+('<p>'+e(desc)+'</p>' if desc else '')+'</div>'

def card(title,body):
    return '<article class="gp-card"><h3>'+e(title)+'</h3>'+para(body)+'</article>'

def section(key,title,desc,body):
    return '<section class="gp-section" id="'+key+'">'+heading("h2",title,desc)+body+'</section>'

def render(lang):
    t=T[lang]
    wha="https://wa.me/"+WHATSAPP
    mapI=MAP_BASE+"Imsfrane%20Cath%C3%A9drale%20Tilouguite"
    mapT=MAP_BASE+"Tilouguite%20Azilal%20Morocco"
    factHTML="".join('<div class="gp-fact"><strong>'+e(a)+'</strong><span>'+e(b)+'</span></div>' for a,b in t["facts"])
    nav="".join('<a href="#'+id+'"><span>'+str(i+1).zfill(2)+'</span>'+e(name)+'</a>' for i,(id,name) in enumerate(t["nav"]))
    locationCards='<div class="gp-three">'+''.join(card(a,b) for a,b in t["locationCards"])+'</div>'
    locations=section("location",t["locationTitle"],t["locationLead"],locationCards)
    routeCards=[]
    for number,title,a,b,c,d,desc in t["routes"]:
        line='<div class="gp-journey">'+''.join('<span>'+e(stop)+'</span>' for stop in (a,b,c,d))+'</div>'
        routeCards.append('<article class="gp-route"><div class="gp-route-top"><span class="gp-route-number">'+number+'</span><h3>'+e(title)+'</h3></div>'+line+para(desc)+'</article>')
    access=section("access",t["accessTitle"],t["accessLead"],
        '<div class="gp-routes">'+''.join(routeCards)+'</div><div class="gp-info gp-info-gold"><i class="fa-solid fa-circle-info" aria-hidden="true"></i>'+para(t["driveNotice"])+'</div>'
        '<div class="gp-inline-actions"><a href="'+mapT+'" target="_blank" rel="noopener noreferrer"><i class="fa-solid fa-location-dot" aria-hidden="true"></i> '+e(t["openTilouguite"])+'</a><a href="'+mapI+'" target="_blank" rel="noopener noreferrer"><i class="fa-solid fa-map-location-dot" aria-hidden="true"></i> '+e(t["openImsfrane"])+'</a></div>')
    transport=section("transport",t["transportTitle"],t["transportLead"],'<div class="gp-two">'+''.join(card(a,b) for a,b in t["transportCards"])+'</div>')
    hikeCards=[]
    for n,title,duration,level,detail,price,about,link in t["hikes"]:
        hikeCards.append('<article class="gp-hike"><div class="gp-hike-head"><span class="gp-hike-index">'+e(n)+'</span><h3>'+e(title)+'</h3><strong>'+e(price)+'</strong></div><div class="gp-hike-facts"><span><i class="fa-regular fa-clock" aria-hidden="true"></i> '+e(duration)+'</span><span><i class="fa-solid fa-gauge" aria-hidden="true"></i> '+e(level)+'</span><span><i class="fa-solid fa-person-hiking" aria-hidden="true"></i> '+e(detail)+'</span></div>'+para(about)+'<a class="gp-text-link" href="'+e(link)+'">'+e(t["more"])+' <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a></article>')
    hikes=section("hikes",t["hikesTitle"],t["hikesLead"],'<div class="gp-hikes">'+''.join(hikeCards)+'</div><p class="gp-fine">'+e(t["hikeFoot"])+'</p>')
    places=section("places",t["placesTitle"],t["placesLead"],'<div class="gp-two">'+''.join(card(a,b) for a,b in t["places"])+'</div>')
    rows="".join('<tr><th scope="row">'+e(name)+'</th><td><strong>'+e(price)+'</strong></td><td>'+e(note)+'</td><td><a href="'+e(link)+'" aria-label="'+e(t["view"]+" : "+name)+'">'+e(t["view"])+' ↗</a></td></tr>' for name,price,note,link in t["activityRows"])
    activityTable='<div class="gp-table-scroll"><table><thead><tr><th>'+e(t["tableActivity"])+'</th><th>'+e(t["tablePrice"])+'</th><th>'+e(t["tableNote"])+'</th><th></th></tr></thead><tbody>'+rows+'</tbody></table></div>'
    activities=section("activities",t["activityTitle"],t["activityLead"],activityTable)
    seasonCards="".join('<article class="gp-season"><div class="gp-season-period">'+e(a)+'</div><div><h3>'+e(b)+'</h3>'+para(c)+'</div></article>' for a,b,c in t["seasons"])
    seasons=section("seasons",t["seasonTitle"],t["seasonLead"],'<div class="gp-seasons">'+seasonCards+'</div>')
    tentsRows="".join('<tr><th scope="row">'+e(size)+'</th><td><strong>'+e(price)+'</strong></td></tr>' for size,price in t["tents"])
    stay=section("stay",t["stayTitle"],t["stayLead"],'<div class="gp-table-scroll gp-table-narrow"><table><thead><tr><th>'+e(t["tentSize"])+'</th><th>'+e(t["tentPrice"])+'</th></tr></thead><tbody>'+tentsRows+'</tbody></table></div>'+para(t["stayMore"])+'<div class="gp-inline-actions"><a href="camping.html">'+e(t["seeCamping"])+' ↗</a><a href="hebergement.html">'+e(t["seeRooms"])+' ↗</a></div>')
    packingCards=[]
    for name,items in t["packGroups"]:
        packingCards.append('<article class="gp-checklist"><h3>'+e(name)+'</h3><ul>'+''.join('<li><i class="fa-regular fa-square-check" aria-hidden="true"></i>'+e(item)+'</li>' for item in items)+'</ul></article>')
    packing=section("packing",t["packingTitle"],t["packingLead"],'<div class="gp-three gp-checklists">'+''.join(packingCards)+'</div>')
    safety=section("safety",t["safetyTitle"],t["safetyLead"],'<div class="gp-two">'+''.join(card(a,b) for a,b in t["safetyList"])+'</div>')
    faqHTML="".join('<details class="gp-faq"><summary>'+e(q)+'<i class="fa-solid fa-plus" aria-hidden="true"></i></summary><div>'+para(answer)+'</div></details>' for q,answer in t["faq"])
    faqs=section("faq",t["faqTitle"],"",'<div class="gp-faqs">'+faqHTML+'</div>')
    return f'''<main id="mainContent" class="gp-main"><div id="imsfrane-guide">
      <section class="gp-hero">
        <div class="gp-hero-inner"><div class="gp-hero-copy">
          <span class="gp-eyebrow"><i class="fa-solid fa-compass" aria-hidden="true"></i> {e(t["eyebrow"])}</span>
          <h1>{t["title"]}</h1>{para(t["lede"])}
          <div class="gp-hero-actions">
            <a class="gp-hero-primary" href="#access"><i class="fa-solid fa-route" aria-hidden="true"></i> {e(t["nav"][1][1])}</a>
            <a class="gp-hero-secondary" href="{mapI}" target="_blank" rel="noopener noreferrer"><i class="fa-solid fa-map-location-dot" aria-hidden="true"></i> {e(t["map"])}</a>
          </div>
        </div><aside class="gp-hero-aside"><span>{e(t["topNotice"])}</span><p>{e(t["topNoticeText"])}</p><a href="{wha}" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-whatsapp" aria-hidden="true"></i> {e(t["contact"])} ↗</a></aside></div>
      </section>
      <div class="gp-facts">{factHTML}</div>
      <div class="gp-layout">
        <aside class="gp-side"><nav class="gp-side-inner" aria-label="{e(t["aside"])}"><div class="gp-side-heading"><i class="fa-solid fa-list-ul" aria-hidden="true"></i> {e(t["aside"])}</div>{nav}</nav></aside>
        <div class="gp-body">{locations+access+transport+hikes+places+activities+seasons+stay+packing+safety+faqs}
          <section class="gp-last"><span class="gp-section-label">IMSFRANE CATHÉDRALE</span><h2>{e(t["ctaTitle"])}</h2><p>{e(t["ctaText"])}</p><div><a href="booking.html"><i class="fa-regular fa-calendar-check" aria-hidden="true"></i> {e(t["book"])} ↗</a><a href="{wha}" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-whatsapp" aria-hidden="true"></i> {e(t["wa"])} ↗</a></div></section>
          <p class="gp-disclaimer"><i class="fa-solid fa-circle-info" aria-hidden="true"></i> {e(t["warning"])}</p>
        </div>
      </div>
    </div></main>'''

def build(root):
    for lang in ("fr","en"):
        page=root/lang/"guide.html"
        original=page.read_text(encoding="utf-8")
        logo_regex=r'<img\b[^>]*data-cms-image="guide-i(?:1|15)"[^>]*>'
        source_logos=re.findall(logo_regex,original,flags=re.I)
        if len(source_logos)!=2:
            raise RuntimeError('Guide source branding not found, refusing update')
        output,n=re.subn(r"<main\b[^>]*>[\s\S]*?</main>",lambda m:render(lang),original,count=1,flags=re.I)
        if n!=1:
            raise RuntimeError('Guide main element missing')
        output=output.replace("</head>",'<link rel="stylesheet" href="../guide-pro.css"></head>',1)
        output=re.sub(r'<link\b[^>]*\bas="image"[^>]*>', '',output,flags=re.I)
        if re.findall(logo_regex,output,flags=re.I)!=source_logos:
            raise RuntimeError('Original Imsfrane header/footer logo changed. Aborting guide update')
        main=re.search(r'<main\b[^>]*>[\s\S]*?</main>',output,flags=re.I).group(0)
        if re.search(r'<img\b|<picture\b|<video\b',main,flags=re.I):
            raise RuntimeError('Images and media are forbidden in Guide page content')
        page.write_text(output,encoding="utf-8")

if __name__=="__main__":
    build(Path("public"))
