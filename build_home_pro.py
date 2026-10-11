"""Build premium bilingual Demo homepage, without modifying the real site or its brand/logo."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import re

TXT = {
"fr":{
 "eyebrow":"EXPLORER · RESPIRER · VIVRE L’ATLAS",
 "heroMain":"Imsfrane <em>Cathédrale.</em>",
 "heroSub":"L’aventure a une autre dimension.",
 "heroText":"Au cœur du Haut Atlas marocain, découvrez des montagnes spectaculaires, l’Oued Ahansal et des expériences de plein air accompagnées par des guides locaux.",
 "heroPrimary":"Découvrir les activités","heroBook":"Préparer mon séjour",
 "heroAlt":"L’Oued Ahansal et les paysages rocheux d’Imsfrane Cathédrale",
 "heroPhotoKicker":"Haut Atlas · Maroc","heroPhotoLabel":"Entre rivière et montagne",
 "heroTag":"À Tilouguite, province d’Azilal",
 "metrics":[("1 868 m","Sommet d’Imsfrane"),("14","Activités & expériences"),("Mars – juin","Rafting : saison habituelle"),("100 %","Contact direct avec l’équipe locale")],
 "introEyebrow":"BIENVENUE DANS LE HAUT ATLAS",
 "introTitle":"Un lieu rare. <em>Des souvenirs qui restent.</em>",
 "introText":"Msfrane — aussi appelée Imsfrane Cathédrale en raison de la silhouette de sa montagne — est une destination de nature dans la commune de Tilouguite. Entre forêts, villages, gorges et rivières, chaque sortie révèle une autre facette de l’Atlas.",
 "introMore":"Découvrir la destination",
 "activitiesEyebrow":"VOS PROCHAINES EXPÉRIENCES",
 "activitiesTitle":"À chacun <em>son aventure.</em>",
 "activitiesText":"Sur l’eau, à pied ou sur les pistes : choisissez une expérience qui correspond à votre rythme, à la saison et à vos envies.",
 "activities":[
   ("rafting","Rafting","Les rapides de l’Oued Ahansal, au rythme de la rivière.","À partir de 400 MAD / personne","Mars à juin · parfois juillet","rafting.html","raft2-800.webp","Rafting guidé sur l’Oued Ahansal"),
   ("randonnee","Randonnée","Sentiers, panoramas et sommet de Jebel Imsfrane.","À partir de 200 MAD / groupe","Parcours adaptés au niveau","randonnee.html","19-800.webp","Groupe en randonnée à Imsfrane"),
   ("camping","Camping","Des nuits simples et authentiques au cœur de la nature.","À partir de 60 MAD / tente / nuit","Selon la capacité des tentes","camping.html","camping-1-800.webp","Camping à Imsfrane dans l’Atlas"),
   ("vtt","VTT","Les reliefs de montagne à découvrir sur deux roues.","À partir de 100 MAD / personne","Sortie guidée ou location","vtt.html","vtt-800.webp","VTT et pistes de montagne"),
   ("quad","Quad","Des pistes et des points de vue hors du commun.","À partir de 250 MAD / quad","Solo ou duo · env. 1 h","quad.html","quad-800.webp","Sortie en quad à Imsfrane"),
   ("hebergement","Hébergement","Prolongez l’expérience dans un cadre local et accueillant.","Tarif sur demande","Maison, chambres et séjour","hebergement.html","bab2-800.webp","Hébergement local aux environs d’Imsfrane"),
   ("tubing","Tubing","Une expérience de rivière en bouée sur l’Oued Ahansal.","300 MAD / personne","Selon le niveau de l’eau","wa:Tubing sur Oued Ahansal","tubing-800.webp","Tubing sur l’Oued Ahansal"),
   ("jetski","Jet Ski","Sensations sur le lac de Bin El Ouidane.","300 MAD · tarif à confirmer","Bin El Ouidane","wa:Jet Ski Bin El Ouidane","jetski-800.webp","Jet Ski au lac Bin El Ouidane"),
   ("4x4","Excursion 4×4","Explorez les pistes de montagne et les beaux panoramas.","Tarif sur demande","Avec organisation préalable","wa:Excursion 4x4 Imsfrane","4x4-800.webp","Excursion 4x4 dans l’Atlas"),
   ("passage","Passage Amazigh","Découvrez le passage emblématique de Taghia.","Tarif sur demande","Taghia · accès à organiser","wa:Passage Amazigh Taghia","passage-800.webp","Passage Amazigh à Taghia"),
   ("zrkan","Cascades Zrkan","Découvrez des cascades et paysages préservés.","Tarif sur demande","Conditions d’accès à vérifier","wa:Cascades Zrkan","zrkan-800.webp","Cascades Zrkan dans l’Atlas"),
   ("anergui","Visite d’Anergui","Villages et paysages authentiques du Haut Atlas.","Tarif sur demande","Excursion à organiser","wa:Visite Anergui","anergui-800.webp","Paysages autour d’Anergui"),
   ("almou","Almou Ntalmast","Découverte des paysages et pâturages de montagne.","Tarif sur demande","Selon la saison","wa:Almou Ntalmast","almo-800.webp","Paysages d’Almou Ntalmast"),
   ("ahidous","Soirée Ahidous","Découvrez la tradition musicale et festive amazighe.","800 MAD / groupe","Sur réservation","wa:Soirée Ahidous","ahidous-800.webp","Soirée Ahidous traditionnelle")
 ],
 "discover":"Découvrir","otherActivities":"Explorer toutes les possibilités",
 "seasonTip":"Le rafting est une activité saisonnière : généralement de mars à juin, parfois jusqu’en juillet selon le niveau de l’eau. Chaque descente nécessite une confirmation.",
 "destinationEyebrow":"PLUS QU’UNE DESTINATION",
 "destinationTitle":"L’Atlas, <em>dans ce qu’il a de plus vrai.</em>",
 "destinationText":"Surplombant la vallée à environ 1 868 mètres, le massif d’Imsfrane se distingue par ses parois rocheuses. Ici, les paysages alternent entre falaises, eaux vives et villages de montagne. Le nom « Cathédrale » décrit la forme du rocher : ce n’est pas un site religieux.",
 "destinationBullets":["Dans la commune de Tilouguite, province d’Azilal","Montagne, gorges et rivières à proximité","Des découvertes avec des guides qui connaissent la région"],
 "destinationCTA":"Lire le guide pratique",
 "destinationPhoto":"Le massif d’Imsfrane vu depuis les pistes de montagne",
 "programEyebrow":"NOS ITINÉRAIRES",
 "programTitle":"Des journées qui <em>valent le détour.</em>",
 "programText":"Trois propositions de randonnée guidée autour de Msfrane. Les tarifs ci-dessous s’appliquent au groupe et restent à confirmer selon le programme.",
 "programs":[
   ("01","Sommet de Msfrane","Une ascension guidée vers le sommet, avec des pauses panoramiques.","4–5 h","Niveau moyen","300 MAD","randonnee.html"),
   ("02","Gorges & cascades","Une marche à travers les paysages de l’Ahansal et ses points d’intérêt.","3–4 h","Facile · 8 km","200 MAD","randonnee.html"),
   ("03","Le Grand Tour","Le combiné montagne et gorges pour une journée riche en découvertes.","8–10 h","Soutenu · 24 km","400 MAD","randonnee.html")
 ],
 "perGroup":"par groupe","programCTA":"Voir le programme","bookNow":"Faire une demande",
 "trustEyebrow":"POURQUOI PARTIR AVEC NOUS",
 "trustTitle":"Des aventures humaines, <em>avant tout.</em>",
 "trust":[
    ("fa-solid fa-compass","Guides locaux","Un accompagnement qui valorise la connaissance des sentiers et des lieux."),
    ("fa-solid fa-mountain-sun","Paysages authentiques","Des vallées, des rivières et des montagnes loin des circuits ordinaires."),
    ("fa-solid fa-list-check","Programme sur mesure","Composez votre expérience avec des activités et des durées adaptées."),
    ("fa-brands fa-whatsapp","Contact direct","Posez vos questions et vérifiez les détails avant de réserver.")
 ],
 "seasonEyebrow":"PLANIFIER AU BON MOMENT",
 "seasonTitle":"Chaque saison a son aventure.",
 "seasonText":"Printemps : rafting si les conditions le permettent. Le reste de l’année : randonnée, VTT, quad et séjours nature selon la météo et la disponibilité.",
 "seasonCTA":"Préparer mon voyage",
 "memEyebrow":"INSTANTS PARTAGÉS",
 "memTitle":"L’aventure se raconte <em>en images.</em>",
 "memText":"Des moments vécus au bord de la rivière, sur les sentiers et autour du campement.",
 "memCTA":"Voir toutes les photos",
 "memPhotos":[("20-800.webp","Souvenirs d’un groupe de randonnée"),("29-800.webp","Camping de nuit dans l’Atlas"),("guide-800.webp","Groupe au sommet dans l’Atlas")],
 "linksEyebrow":"POUR ALLER PLUS LOIN",
 "linksTitle":"Préparez <em>votre escapade.</em>",
 "links":[
    ("fa-solid fa-map-location-dot","Guide pratique","Accès, transport, équipements et conseils de terrain.","guide.html","Consulter le guide"),
    ("fa-solid fa-book-open","Notre journal","Idées de sorties et découvertes de la région.","blog.html","Lire les articles"),
    ("fa-solid fa-basket-shopping","Boutique de l’Atlas","Miel, huile d’olive et produits naturels de la région.","store.html","Découvrir la boutique")
 ],
 "reviewsTitle":"Ils racontent leurs expériences sur Google",
 "reviewsCopy":"Consultez les avis publics des visiteurs avant de préparer votre propre aventure.",
 "reviewsCTA":"Lire les avis Google",
 "ctaEyebrow":"VOTRE PROCHAINE HISTOIRE COMMENCE ICI",
 "ctaTitle":"Prêt à découvrir <em>Imsfrane ?</em>",
 "ctaText":"Une date, quelques envies, et nous vous aidons à préparer une aventure dans le Haut Atlas. Disponibilités et conditions confirmées par l’équipe.",
 "ctaBooking":"Demander une réservation","ctaWhatsApp":"Parler sur WhatsApp",
 "scroll":"Explorer",
 "metaDesc":"Découvrez Imsfrane Cathédrale dans le Haut Atlas au Maroc : rafting saisonnier, randonnées guidées, camping, VTT, quad et hébergement à Tilouguite."
},
"en":{
 "eyebrow":"EXPLORE · BREATHE · EXPERIENCE THE ATLAS",
 "heroMain":"Imsfrane <em>Cathedral.</em>",
 "heroSub":"Adventure feels different here.",
 "heroText":"In Morocco’s High Atlas, discover dramatic mountain landscapes, the Ahansal River and outdoor adventures guided by people who know this region.",
 "heroPrimary":"Explore activities","heroBook":"Plan your stay",
 "heroAlt":"Ahansal River and the striking rock formations of Imsfrane",
 "heroPhotoKicker":"High Atlas · Morocco","heroPhotoLabel":"Where rivers meet mountains",
 "heroTag":"Tilouguite · Azilal Province",
 "metrics":[("1,868 m","Imsfrane summit"),("14","Activities & experiences"),("Mar – Jun","Usual rafting season"),("100%","Direct contact with local guides")],
 "introEyebrow":"WELCOME TO THE HIGH ATLAS",
 "introTitle":"One remarkable place. <em>Lasting memories.</em>",
 "introText":"Msfrane — also called Imsfrane Cathedral for the distinctive shape of its mountain — is a nature destination in Tilouguite commune. Among forests, villages, gorges and rivers, there’s a different side of the Atlas around every bend.",
 "introMore":"Explore the destination",
 "activitiesEyebrow":"FIND YOUR NEXT EXPERIENCE",
 "activitiesTitle":"Your kind of <em>adventure.</em>",
 "activitiesText":"On the water, on foot or on mountain tracks: choose the experience that fits your pace, the season and your interests.",
 "activities":[
   ("rafting","Rafting","Paddle the Ahansal’s rapids through mountain scenery.","From 400 MAD / person","March–June · sometimes July","rafting.html","raft2-800.webp","Guided rafting on the Ahansal River"),
   ("randonnee","Hiking","Trails, viewpoints and the summit of Jebel Imsfrane.","From 200 MAD / group","Walks for different levels","randonnee.html","19-800.webp","Guided mountain hiking at Imsfrane"),
   ("camping","Camping","Unplug for a night in nature under the Atlas sky.","From 60 MAD / tent / night","Different tent capacities","camping.html","camping-1-800.webp","Camping in the Imsfrane mountains"),
   ("vtt","Mountain biking","Discover mountain trails and valleys on two wheels.","From 100 MAD / person","Guided ride or rental","vtt.html","vtt-800.webp","Mountain biking in the High Atlas"),
   ("quad","Quad biking","Explore scenic tracks and mountain viewpoints.","From 250 MAD / quad","Solo or duo · around 1 hour","quad.html","quad-800.webp","Quad biking around Imsfrane"),
   ("hebergement","Accommodation","Stay a little longer in welcoming local surroundings.","Price on request","House, rooms and stays","hebergement.html","bab2-800.webp","Local accommodation around Imsfrane"),
   ("tubing","River tubing","Explore the Ahansal River in a river tube.","300 MAD / person","Subject to river levels","wa:Ahansal river tubing","tubing-800.webp","River tubing on the Ahansal"),
   ("jetski","Jet Ski","A watersport adventure on Bin El Ouidane Lake.","300 MAD · confirm rate","Bin El Ouidane","wa:Jet Ski Bin El Ouidane","jetski-800.webp","Jet Ski on Bin El Ouidane"),
   ("4x4","4×4 Excursion","Discover mountain trails and scenic viewpoints.","Price on request","Prearranged excursion","wa:Imsfrane 4x4 excursion","4x4-800.webp","Four-wheel-drive mountain excursion"),
   ("passage","Amazigh Passage","Explore the iconic cliffside passage of Taghia.","Price on request","Taghia · arranged access","wa:Amazigh Passage Taghia","passage-800.webp","Amazigh Passage at Taghia"),
   ("zrkan","Zrkan Waterfalls","A discovery trip to scenic mountain waterfalls.","Price on request","Access conditions to check","wa:Zrkan Waterfalls","zrkan-800.webp","Zrkan mountain waterfalls"),
   ("anergui","Explore Anergui","Local village life and High Atlas scenery.","Price on request","Excursion on request","wa:Anergui visit","anergui-800.webp","Anergui landscapes"),
   ("almou","Almou Ntalmast","Discover beautiful highland landscapes.","Price on request","Seasonal access","wa:Almou Ntalmast","almo-800.webp","Almou Ntalmast highland landscape"),
   ("ahidous","Ahidous Evening","A traditional Amazigh music and dance evening.","800 MAD / group","By arrangement","wa:Traditional Ahidous evening","ahidous-800.webp","Traditional Ahidous cultural evening")
 ],
 "discover":"Discover","otherActivities":"See more possibilities",
 "seasonTip":"Rafting is seasonal: usually March to June, occasionally July when river levels permit. Every departure requires confirmation.",
 "destinationEyebrow":"MORE THAN A DESTINATION",
 "destinationTitle":"Experience the Atlas <em>as it truly is.</em>",
 "destinationText":"Rising to around 1,868 metres, Imsfrane’s mountain stands out for its towering rock faces. Between cliffs, rushing rivers and mountain villages, there’s so much to discover. The nickname “Cathedral” refers to the shape of the rock; it is not a religious landmark.",
 "destinationBullets":["Tilouguite commune, Azilal Province","Mountain landscapes, gorges and nearby rivers","Explore with guides who know the region"],
 "destinationCTA":"Read the practical guide",
 "destinationPhoto":"The Imsfrane rock massif seen from a mountain road",
 "programEyebrow":"OUR WALKING ROUTES",
 "programTitle":"Days worth <em>remembering.</em>",
 "programText":"Three guided hiking routes around Msfrane. Prices are listed per group and are subject to confirmation of the final program.",
 "programs":[
   ("01","Msfrane summit","A guided summit hike with stops for sweeping mountain views.","4–5 hours","Moderate","300 MAD","randonnee.html"),
   ("02","Gorges & waterfalls","Follow the Ahansal scenery and discover local highlights.","3–4 hours","Easy · 8 km","200 MAD","randonnee.html"),
   ("03","The Grand Tour","Combine the mountain and the gorges in one full day.","8–10 hours","Strenuous · 24 km","400 MAD","randonnee.html")
 ],
 "perGroup":"per group","programCTA":"Explore the route","bookNow":"Request to book",
 "trustEyebrow":"WHY TRAVEL WITH US",
 "trustTitle":"Real experiences. <em>Real connections.</em>",
 "trust":[
    ("fa-solid fa-compass","Local guides","Guided experiences shaped by local knowledge of the trails and region."),
    ("fa-solid fa-mountain-sun","Authentic landscapes","Valleys, rivers and mountains away from the usual tourist circuits."),
    ("fa-solid fa-list-check","Tailored trips","Choose activities and durations that work for your group."),
    ("fa-brands fa-whatsapp","Direct contact","Ask questions and check the details before making a request.")
 ],
 "seasonEyebrow":"TIMING YOUR VISIT",
 "seasonTitle":"Every season brings a new adventure.",
 "seasonText":"Spring: rafting when river conditions allow. Other times of year: hiking, biking, quads and nature stays depending on weather and availability.",
 "seasonCTA":"Plan your visit",
 "memEyebrow":"SHARED MOMENTS",
 "memTitle":"Stories worth <em>remembering.</em>",
 "memText":"Memories from the river, the trails and evenings around camp.",
 "memCTA":"Explore the gallery",
 "memPhotos":[("20-800.webp","A hiking group in the Atlas"),("29-800.webp","Night camping in the High Atlas"),("guide-800.webp","Visitors at a High Atlas summit")],
 "linksEyebrow":"KEEP EXPLORING",
 "linksTitle":"Plan a better <em>escape.</em>",
 "links":[
    ("fa-solid fa-map-location-dot","Practical guide","Access, transport, packing lists and useful advice.","guide.html","Open the guide"),
    ("fa-solid fa-book-open","Our journal","Outdoor ideas and stories from the region.","blog.html","Read the journal"),
    ("fa-solid fa-basket-shopping","Atlas shop","Honey, olive oil and other local natural products.","store.html","Explore the shop")
 ],
 "reviewsTitle":"Read visitors’ stories on Google",
 "reviewsCopy":"Explore public visitor reviews before planning your own adventure.",
 "reviewsCTA":"Read Google reviews",
 "ctaEyebrow":"YOUR NEXT STORY STARTS HERE",
 "ctaTitle":"Ready to explore <em>Imsfrane?</em>",
 "ctaText":"Bring your dates and a few ideas. We’ll help you plan your High Atlas trip, with availability and conditions confirmed by the team.",
 "ctaBooking":"Request a booking","ctaWhatsApp":"Message on WhatsApp",
 "scroll":"Explore",
 "metaDesc":"Explore Imsfrane Cathedral in Morocco’s High Atlas: seasonal rafting, guided hiking, camping, mountain biking, quad biking and stays near Tilouguite."
}
}
GOOGLE_REVIEWS="https://www.google.com/maps/search/?api=1&amp;query=Rafting+et+Vtt+%C3%A0+Imsfrane+cath%C3%A9drale&amp;query_place_id=ChIJGf0-zLRxow0RFtfhVkfxEmU"

def e(v):return escape(str(v),quote=True)
def img(filename,alt,additional="",srcset=None):
    # The project-owned, already-published image library; unique photo per block.
    return '<img '+additional+' src="../images/'+e(filename)+'" alt="'+e(alt)+'"'+(' srcset="'+e(srcset)+'"' if srcset else '')+'>'
def titleBlock(eyebrow,headline,desc=""):
    return '<div class="hp-heading"><span class="hp-kicker">'+e(eyebrow)+'</span><h2>'+headline+'</h2>'+('<p>'+e(desc)+'</p>' if desc else '')+'</div>'
def build(lang):
    t=TXT[lang]
    slider_images=[
      ("21.webp","21-800.webp",t["heroAlt"]),
      ("24.webp","24-800.webp","Rafting on the Ahansal River"),
      ("27.webp","27-800.webp","Quad biking by the Imsfrane mountain"),
      ("29.webp","29-800.webp","An Imsfrane campsite at dusk"),
      ("31.webp","31-800.webp","Mountain biking in the Atlas")
    ]
    slides=[]
    for i,(original,thumb,alt) in enumerate(slider_images):
        attrs=('fetchpriority="high"' if i==0 else 'loading="lazy"')
        slides.append('<div class="hp-slide'+(' is-active' if i==0 else '')+'" aria-hidden="'+('false' if i==0 else 'true')+'" data-slide="'+str(i)+'">'+
                      img(original,alt,'class="hp-hero-image" decoding="async" '+attrs+' sizes="(max-width: 860px) 100vw, 47vw"',srcset="../images/"+thumb+" 800w, ../images/"+original+" 1200w")+
                      '</div>')
    slider_dots=''.join('<button type="button" class="hp-slide-dot'+(' is-active' if i==0 else '')+'" data-slide-to="'+str(i)+'" aria-label="'+e(("Afficher la photo " if lang=="fr" else "Show photo ")+str(i+1))+'" aria-current="'+('true' if i==0 else 'false')+'"></button>' for i in range(len(slides)))
    slider_control='<div class="hp-slider-controls" aria-label="'+e("Galerie photos Imsfrane" if lang=="fr" else "Imsfrane photo gallery")+'">'+\
         '<button type="button" class="hp-slide-arrow" data-slide-dir="-1" aria-label="'+e("Photo précédente" if lang=="fr" else "Previous photo")+'"><i class="fa-solid fa-chevron-left" aria-hidden="true"></i></button>'+\
         '<div class="hp-slide-dots">'+slider_dots+'</div>'+\
         '<button type="button" class="hp-slide-arrow" data-slide-dir="1" aria-label="'+e("Photo suivante" if lang=="fr" else "Next photo")+'"><i class="fa-solid fa-chevron-right" aria-hidden="true"></i></button></div>'
    hero=f'''<section class="hp-hero" aria-labelledby="hp-h1"><div class="hp-hero-inner">
      <div class="hp-hero-content"><span class="hp-eyebrow"><i class="fa-solid fa-location-dot" aria-hidden="true"></i> {e(t["eyebrow"])}</span>
        <h1 id="hp-h1">{t["heroMain"]}<span>{e(t["heroSub"])}</span></h1>
        <p>{e(t["heroText"])}</p>
        <div class="hp-hero-buttons"><a class="hp-button hp-button-gold" href="#activities"><i class="fa-solid fa-compass" aria-hidden="true"></i> {e(t["heroPrimary"])} <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>
          <a class="hp-button hp-button-outline" href="booking.html"><i class="fa-regular fa-calendar-check" aria-hidden="true"></i> {e(t["heroBook"])}</a>
        </div>
        <div class="hp-hero-foot"><span class="hp-hero-dot"></span>{e(t["heroTag"])}</div>
      </div>
      <div class="hp-hero-visual hp-hero-slider" aria-roledescription="carousel"><div class="hp-slide-track">{"".join(slides)}</div>{slider_control}
        <div class="hp-hero-picture-note"><span>{e(t["heroPhotoKicker"])}</span><strong>{e(t["heroPhotoLabel"])}</strong></div>
        <div class="hp-hero-altitude"><i class="fa-solid fa-mountain-sun" aria-hidden="true"></i><strong>1 868 m</strong><span>Jebel Imsfrane</span></div>
      </div>
    </div><a class="hp-scroll" href="#activities">{e(t["scroll"])} <i class="fa-solid fa-arrow-down" aria-hidden="true"></i></a></section>'''
    reviews=f'''<section class="hp-google-reviews" id="google-reviews" aria-labelledby="hp-reviews-title">
      <div class="hp-reviews-inner"><div class="hp-google-mark" aria-hidden="true"><i class="fa-brands fa-google"></i></div>
        <div class="hp-google-rating"><span class="hp-google-label">GOOGLE REVIEWS</span><div class="hp-google-score"><strong>{e("4,8" if lang=="fr" else "4.8")}<small>/5</small></strong><span aria-label="5 stars" class="hp-google-stars">★★★★★</span></div>
        <span class="hp-review-count">{e("23 avis affichés sur notre site" if lang=="fr" else "23 reviews listed on our site")}</span></div>
        <div class="hp-google-copy"><h2 id="hp-reviews-title">{e("Vos avis comptent." if lang=="fr" else "Your reviews matter.")}</h2>
          <p>{e("Découvrez les avis publiés sur Google par les visiteurs de nos activités à Imsfrane." if lang=="fr" else "See real Google reviews left by visitors to our Imsfrane adventures.")}</p></div>
        <a class="hp-google-link" href="{GOOGLE_REVIEWS}" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-google" aria-hidden="true"></i> {e("Lire les avis Google" if lang=="fr" else "Read Google reviews")} <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
      </div>
    </section>'''
    cards=[]
    for slug,name,desc,price,note,link,picture,alt in t["activities"]:
        if link.startswith("wa:"):
            message=("Bonjour, je souhaite avoir des informations sur " if lang=="fr" else "Hello, I would like information about ")+link[3:]+"."
            link="https://wa.me/212667772551?text="+quote(message)
        cards.append('<article class="hp-activity-card hp-'+slug+'"><a class="hp-activity-image" href="'+e(link)+'" aria-label="'+e(name)+'">'+img(picture,alt,'loading="lazy" decoding="async"')+'</a>'+
            '<div class="hp-activity-body"><span class="hp-activity-note">'+e(note)+'</span><h3>'+e(name)+'</h3><p>'+e(desc)+'</p>'+
            '<div class="hp-activity-bottom"><strong>'+e(price)+'</strong><a href="'+e(link)+'" aria-label="'+e(t["discover"]+" "+name)+'"><span>'+e(t["discover"])+'</span><i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a></div></div></article>')
    activities=f'''<section class="hp-activities" id="activities"><div class="hp-container">
      <div class="hp-section-row">{titleBlock(t["activitiesEyebrow"],t["activitiesTitle"],t["activitiesText"])}</div>
      <div class="hp-activity-grid">{"".join(cards)}</div>
      <p class="hp-season-tip"><i class="fa-solid fa-circle-info" aria-hidden="true"></i>{e(t["seasonTip"])}</p>
    </div></section>'''
    mountainImage=img("hero.webp",t["destinationPhoto"],'loading="lazy" decoding="async" width="1368" height="1824"')
    destiny=f'''<section class="hp-destination" id="destination"><div class="hp-destination-image">{mountainImage}
        <span class="hp-destination-label">IMSFRANE CATHÉDRALE · HAUT ATLAS</span></div>
        <div class="hp-destination-content">{titleBlock(t["destinationEyebrow"],t["destinationTitle"])}
        <p>{e(t["destinationText"])}</p>
        <ul>{"".join('<li><i class="fa-solid fa-check" aria-hidden="true"></i>'+e(text)+'</li>' for text in t["destinationBullets"])}</ul>
        <a href="guide.html" class="hp-button hp-button-dark">{e(t["destinationCTA"])} <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>
    </div></section>'''
    progs=[]
    for number,name,desc,duration,level,price,link in t["programs"]:
        progs.append('<article class="hp-program"><div class="hp-program-head"><span>'+e(number)+'</span><i class="fa-solid fa-arrow-up-right-dots" aria-hidden="true"></i></div>'+
          '<h3>'+e(name)+'</h3><p>'+e(desc)+'</p>'+
          '<div class="hp-program-details"><span><i class="fa-regular fa-clock" aria-hidden="true"></i>'+e(duration)+'</span><span><i class="fa-solid fa-person-hiking" aria-hidden="true"></i>'+e(level)+'</span></div>'+
          '<div class="hp-program-foot"><div><strong>'+e(price)+'</strong><small>'+e(t["perGroup"])+'</small></div><a href="'+e(link)+'">'+e(t["programCTA"])+' ↗</a></div></article>')
    programs=f'''<section class="hp-programs" id="programmes"><div class="hp-container">
      {titleBlock(t["programEyebrow"],t["programTitle"],t["programText"])}
      <div class="hp-program-grid">{"".join(progs)}</div>
      <a href="booking.html" class="hp-prog-cta">{e(t["bookNow"])} <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>
    </div></section>'''
    perks=[]
    for icon,title,desc in t["trust"]:
        perks.append('<div class="hp-trust-item"><div class="hp-trust-icon"><i class="'+e(icon)+'" aria-hidden="true"></i></div><h3>'+e(title)+'</h3><p>'+e(desc)+'</p></div>')
    why=f'''<section class="hp-trust"><div class="hp-container">{titleBlock(t["trustEyebrow"],t["trustTitle"])}
      <div class="hp-trust-grid">{"".join(perks)}</div></div></section>'''
    seasonal=f'''<section class="hp-season"><div class="hp-container hp-season-inner"><div>
      <span class="hp-kicker">{e(t["seasonEyebrow"])}</span><h2>{e(t["seasonTitle"])}</h2><p>{e(t["seasonText"])}</p>
      </div><a href="guide.html" class="hp-button hp-button-gold">{e(t["seasonCTA"])} <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>
      </div></section>'''
    memoriesPhotos=[]
    for filename,alt in t["memPhotos"]:
        memoriesPhotos.append('<a href="memories.html" aria-label="'+e(t["memCTA"])+'">'+img(filename,alt,'loading="lazy" decoding="async"')+'</a>')
    memories=f'''<section class="hp-memories hp-container"><div class="hp-memories-heading">
      {titleBlock(t["memEyebrow"],t["memTitle"],t["memText"])}
      <a href="memories.html" class="hp-plain-link">{e(t["memCTA"])} <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a></div>
      <div class="hp-memories-grid">{"".join(memoriesPhotos)}</div></section>'''
    linkCards=[]
    for icon,name,desc,href,button in t["links"]:
        linkCards.append('<a class="hp-link-card" href="'+e(href)+'"><i class="'+e(icon)+'" aria-hidden="true"></i><h3>'+e(name)+'</h3><p>'+e(desc)+'</p><span>'+e(button)+' <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span></a>')
    links=f'''<section class="hp-explore"><div class="hp-container">
      {titleBlock(t["linksEyebrow"],t["linksTitle"])}
      <div class="hp-explore-grid">{"".join(linkCards)}</div>
      <div class="hp-reviews"><div><i class="fa-brands fa-google" aria-hidden="true"></i><strong>{e(t["reviewsTitle"])}</strong><p>{e(t["reviewsCopy"])}</p></div>
      <a href="{GOOGLE_REVIEWS}" target="_blank" rel="noopener noreferrer">{e(t["reviewsCTA"])} ↗</a></div>
    </div></section>'''
    end=f'''<section class="hp-final"><div class="hp-container"><span class="hp-kicker">{e(t["ctaEyebrow"])}</span>
      <h2>{t["ctaTitle"]}</h2><p>{e(t["ctaText"])}</p>
      <div class="hp-final-buttons"><a href="booking.html" class="hp-button hp-button-gold"><i class="fa-regular fa-calendar-check" aria-hidden="true"></i> {e(t["ctaBooking"])}</a>
      <a href="https://wa.me/212667772551" class="hp-button hp-button-outline" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-whatsapp" aria-hidden="true"></i> {e(t["ctaWhatsApp"])}</a></div>
    </div></section>'''
    return '<main id="mainContent" class="hp-home">'+hero+reviews+activities+destiny+programs+why+seasonal+memories+links+end+'</main>'

def publish(root):
    for lang in ("fr","en"):
        path=root/lang/"index.html"
        source=path.read_text(encoding="utf-8")
        logos_re=r'<img\b[^>]*data-cms-image="index-i(?:1|24)"[^>]*>'
        original_logos=re.findall(logos_re,source,flags=re.I)
        if len(original_logos)!=2:raise RuntimeError("Demo original homepage logo not found")
        fresh=build(lang)
        updated,count=re.subn(r'<main\b[^>]*>[\s\S]*?</main>',lambda _:fresh,source,count=1,flags=re.I)
        if count!=1:raise RuntimeError("Homepage main not found")
        updated=updated.replace("</head>",'<link rel="stylesheet" href="../home-pro.css"></head>',1)
        updated=updated.replace("</body>",'<script defer src="../home-pro.js"></script></body>',1)
        # Keep original header and footer HTML, including the exact brand logo files and attributes.
        if re.findall(logos_re,updated,flags=re.I)!=original_logos:
            raise RuntimeError("Original brand logo changed: refusing Demo homepage update")
        if updated.count('class="hp-activity-card')!=14:
            raise RuntimeError("All 14 main-site activities were not generated")
        if updated.count('data-slide="')!=5:raise RuntimeError("Five original homepage slider images missing")
        rendered_main=re.search(r'<main\\b[^>]*>[\\s\\S]*?</main>',updated,flags=re.I).group(0)
        if 'class="hp-facts"' in rendered_main or 'class="hp-about hp-container"' in rendered_main:
            raise RuntimeError("Removed facts/about sections reappeared in homepage")
        if updated.count('class="hp-google-reviews"')!=1:raise RuntimeError("Google Reviews directly under hero missing")
        if updated.count('class="hp-program"')!=3:
            raise RuntimeError("Three programs were not generated")
        if updated.count('<h1')!=1:raise RuntimeError("Homepage H1 mismatch")
        if updated.count('<main')!=1:raise RuntimeError("Homepage main mismatch")
        # Demo-only metadata, never change canonicals or OG owned by the real website.
        if lang=="fr":
            old='Découvrez Imsfrane Cathédrale'
        path.write_text(updated,encoding="utf-8")

if __name__=="__main__":
    publish(Path("public"))
