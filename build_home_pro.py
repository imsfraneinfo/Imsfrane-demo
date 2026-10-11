"""Build premium bilingual Demo homepage, without modifying the real site or its brand/logo."""
from pathlib import Path
from html import escape
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
 "metrics":[("1 868 m","Sommet d’Imsfrane"),("6","Expériences à découvrir"),("Mars – juin","Rafting : saison habituelle"),("100 %","Contact direct avec l’équipe locale")],
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
   ("hebergement","Hébergement","Prolongez l’expérience dans un cadre local et accueillant.","Tarif sur demande","Maison, chambres et séjour","hebergement.html","bab2-800.webp","Hébergement local aux environs d’Imsfrane")
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
 "metrics":[("1,868 m","Imsfrane summit"),("6","Experiences to explore"),("Mar – Jun","Usual rafting season"),("100%","Direct contact with local guides")],
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
   ("hebergement","Accommodation","Stay a little longer in welcoming local surroundings.","Price on request","House, rooms and stays","hebergement.html","bab2-800.webp","Local accommodation around Imsfrane")
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
    heroPicture=img("21.webp",t["heroAlt"],'class="hp-hero-image" fetchpriority="high" decoding="async" width="1200" height="1600" sizes="(max-width: 780px) 100vw, 50vw"',srcset="../images/21-800.webp 800w, ../images/21.webp 1200w")
    hero=f'''<section class="hp-hero" aria-labelledby="hp-h1"><div class="hp-hero-inner">
      <div class="hp-hero-content"><span class="hp-eyebrow"><i class="fa-solid fa-location-dot" aria-hidden="true"></i> {e(t["eyebrow"])}</span>
        <h1 id="hp-h1">{t["heroMain"]}<span>{e(t["heroSub"])}</span></h1>
        <p>{e(t["heroText"])}</p>
        <div class="hp-hero-buttons"><a class="hp-button hp-button-gold" href="#activities"><i class="fa-solid fa-compass" aria-hidden="true"></i> {e(t["heroPrimary"])} <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>
          <a class="hp-button hp-button-outline" href="booking.html"><i class="fa-regular fa-calendar-check" aria-hidden="true"></i> {e(t["heroBook"])}</a>
        </div>
        <div class="hp-hero-foot"><span class="hp-hero-dot"></span>{e(t["heroTag"])}</div>
      </div>
      <div class="hp-hero-visual">{heroPicture}
        <div class="hp-hero-picture-note"><span>{e(t["heroPhotoKicker"])}</span><strong>{e(t["heroPhotoLabel"])}</strong></div>
        <div class="hp-hero-altitude"><i class="fa-solid fa-mountain-sun" aria-hidden="true"></i><strong>1 868 m</strong><span>Jebel Imsfrane</span></div>
      </div>
    </div><a class="hp-scroll" href="#about">{e(t["scroll"])} <i class="fa-solid fa-arrow-down" aria-hidden="true"></i></a></section>'''
    facts='<div class="hp-facts"><div class="hp-facts-inner">'+''.join('<div><strong>'+e(a)+'</strong><span>'+e(b)+'</span></div>' for a,b in t["metrics"])+'</div></div>'
    about=f'''<section class="hp-about hp-container" id="about">
      <div class="hp-about-lead">{titleBlock(t["introEyebrow"],t["introTitle"])}</div>
      <div class="hp-about-right"><p>{e(t["introText"])}</p>
      <a href="guide.html" class="hp-plain-link">{e(t["introMore"])} <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
    </section>'''
    cards=[]
    for slug,name,desc,price,note,link,picture,alt in t["activities"]:
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
    return '<main id="mainContent" class="hp-home">'+hero+facts+about+activities+destiny+programs+why+seasonal+memories+links+end+'</main>'

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
        # Keep original header and footer HTML, including the exact brand logo files and attributes.
        if re.findall(logos_re,updated,flags=re.I)!=original_logos:
            raise RuntimeError("Original brand logo changed: refusing Demo homepage update")
        if updated.count('class="hp-activity-card')!=6:
            raise RuntimeError("Six linked experiences were not generated")
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
