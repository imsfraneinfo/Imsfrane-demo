from pathlib import Path
from html import escape
import json
import re

CATALOG = json.loads(Path("booking-prices.json").read_text(encoding="utf-8"))
WORDS = {
"fr":{
"kicker":"RÉSERVATION DIRECTE · HAUT ATLAS","hero":"Composez votre <em>aventure.</em>",
"intro":"Choisissez vos activités, le nombre de personnes et les dates : le prix estimé se calcule immédiatement.",
"tags":["Demande sans paiement","Calcul instantané","Confirmation humaine"],
"steps":["Expériences","Votre séjour","Récapitulatif"],
"eyebrow1":"ÉTAPE 01 · VOS ENVIES","pick":"Choisissez vos expériences",
"pickhelp":"Cochez les activités souhaitées avec une croix ×. Indiquez le nombre de personnes : le total s’actualise automatiquement. Pour les tentes et les quads, précisez les quantités.",
"filters":{"all":"Tout voir","rafting":"Rafting","camping":"Tentes","hiking":"Randonnée","vtt":"VTT","quad":"Quad","stay":"Séjour"},
"units":{"person":"par personne","tentNight":"par tente / nuit","group":"par groupe","vehicle":"par quad"},
"season":"Le rafting est généralement proposé de mars à juin, parfois en juillet si le débit le permet. La sécurité et la disponibilité sont à confirmer.",
"eyebrow2":"ÉTAPE 02 · VOS INFORMATIONS","details":"Les détails de votre séjour",
"detailshelp":"Une demande complète facilite la réponse de notre équipe. Aucune réservation n'est confirmée avant notre accord.",
"name":"Nom complet","phone":"WhatsApp / téléphone","email":"E-mail","opt":"facultatif","country":"Pays",
"start":"Date souhaitée","end":"Départ du camping","endhelp":"Pour les tentes, indiquez la date de départ afin de calculer les nuits.",
"travelers":"Nombre de voyageurs","countHint":"Les tarifs par personne sont multipliés automatiquement par ce nombre.","quantity":"Quantité","selected":"Sélectionner","language":"Langue souhaitée","place":"Lieu de départ ou hébergement",
"placehint":"Ex. Tilouguite, Imsfrane, Béni Mellal","extra":"Services supplémentaires (sur devis)",
"notes":"Informations ou demandes particulières","noteshint":"Horaires, enfants, besoins particuliers, questions…",
"disclaimer":"Le total comprend uniquement les prestations tarifées ci-dessus. Transport, chambres et services sur devis ne sont pas inclus. L'envoi sur WhatsApp n'est pas une réservation confirmée.",
"summaryeyebrow":"VOTRE SÉLECTION","summary":"Votre récapitulatif","summaryempty":"Choisissez des activités pour afficher le détail du prix.","total":"Total estimé",
"pending":"Disponibilité, tarif définitif et conditions confirmés par notre équipe. Aucun paiement demandé ici.",
"send":"Envoyer sur WhatsApp","copy":"Copier le récapitulatif",
"trust":["Aucun paiement en ligne","Contact direct avec votre guide","Confirmation après vérification"]
},
"en":{
"kicker":"DIRECT REQUEST · HIGH ATLAS","hero":"Build your <em>adventure.</em>",
"intro":"Choose activities, the number of participants and your travel dates to see a clear, instant price estimate.",
"tags":["No online payment","Instant estimate","Personally confirmed"],
"steps":["Experiences","Your trip","Summary"],
"eyebrow1":"STEP 01 · YOUR ADVENTURE","pick":"Choose your experiences",
"pickhelp":"Tick × the activities you want and enter the number of travelers: the total updates automatically. For tents and quads, choose quantities.",
"filters":{"all":"All","rafting":"Rafting","camping":"Tents","hiking":"Hiking","vtt":"Mountain biking","quad":"Quad","stay":"3-day stay"},
"units":{"person":"per person","tentNight":"per tent / night","group":"per group","vehicle":"per quad"},
"season":"Rafting is generally offered from March to June, sometimes July if river levels permit. Safety and availability must be confirmed.",
"eyebrow2":"STEP 02 · YOUR DETAILS","details":"Your trip details",
"detailshelp":"Providing your trip details helps our team reply. No booking is confirmed until we agree.",
"name":"Full name","phone":"WhatsApp / phone","email":"Email","opt":"optional","country":"Country",
"start":"Preferred date","end":"Camping check-out","endhelp":"For tents, enter your check-out date to calculate nights.",
"travelers":"Number of travelers","countHint":"Per-person prices automatically use this number.","quantity":"Quantity","selected":"Select","language":"Preferred language","place":"Departure point or accommodation",
"placehint":"e.g. Tilouguite, Imsfrane, Beni Mellal","extra":"Additional services (quote required)",
"notes":"Special requests","noteshint":"Timing, children, accessibility, questions…",
"disclaimer":"The estimate includes only the priced services above. Transfers, rooms and quote-only services are excluded. Sending a WhatsApp message does not confirm a booking.",
"summaryeyebrow":"YOUR SELECTION","summary":"Booking summary","summaryempty":"Select an experience to see its price breakdown.","total":"Estimated total",
"pending":"Final price, conditions and availability will be confirmed by our team. No payment is taken here.",
"send":"Send via WhatsApp","copy":"Copy summary",
"trust":["No online payment","Direct contact with your guide","Confirmed after checking"]
}
}
ICONS = {"rafting":"≈","camping":"⌂","hiking":"△","vtt":"◉","quad":"✦","stay":"✺"}

def e(value):
    return escape(str(value), quote=True)

def render(lang):
    t=WORDS[lang]
    cards=[]
    for p in CATALOG["offers"]:
        name=e(p[lang])
        detail=e(p["detailFr" if lang=="fr" else "detailEn"])
        unit=e(t["units"][p["unit"]])
        per_person = p["unit"]=="person"
        counts = (t["travelers"] if per_person else t["quantity"])
        controls = ('<span class="bp-count-auto" data-unit="people">× <strong>2</strong></span>' if per_person else
                    '<div class="bp-stepper" role="group" aria-label="'+e(counts)+' — '+name+'">'
                    '<button type="button" data-delta="-1" data-offer="'+e(p["id"])+'" aria-label="− '+name+'" disabled>−</button>'
                    '<output aria-live="off">0</output>'
                    '<button type="button" data-delta="1" data-offer="'+e(p["id"])+'" aria-label="+ '+name+'">+</button></div>')
        cards.append(
          '<article class="bp-offer" data-id="'+e(p["id"])+'" data-category="'+e(p["category"])+'" data-selected="false">'
          '<div class="bp-offer-top"><label class="bp-select-activity" for="bp-choice-'+e(p["id"])+'">'
          '<input class="bp-choice" id="bp-choice-'+e(p["id"])+'" type="checkbox" data-offer="'+e(p["id"])+'">'
          '<span class="bp-select-label">'+e(t["selected"])+'</span></label>'
          '<span class="bp-unit">'+unit+'</span></div>'
          '<h3>'+name+'</h3><p>'+detail+'</p><div class="bp-price-row"><div class="bp-offer-price">'+f'{p["price"]:,}'.replace(","," ")+' <small>MAD</small></div>'
          '<div class="bp-quantity-control">'+controls+'</div></div></article>'
        )
    cats=["all","rafting","camping","hiking","vtt","quad","stay"]
    filters="".join('<button type="button" class="bp-filter" data-filter="'+key+'" aria-pressed="'+str(key=="all").lower()+'">'+e(t["filters"][key])+'</button>' for key in cats)
    steps="".join('<li><b>'+str(i+1)+'</b>'+e(x)+'</li>' for i,x in enumerate(t["steps"]))
    tags="".join('<span>✓ '+e(x)+'</span>' for x in t["tags"])
    extras="".join('<label class="bp-extra"><input type="checkbox" value="'+e(p["id"])+'"> '+e(p[lang])+'</label>' for p in CATALOG["requestOptions"])
    trust="".join('<div><span>✓</span>'+e(x)+'</div>' for x in t["trust"])
    optional='<span class="bp-optional">('+e(t["opt"])+')</span>'
    def field(fid,title,ftype="text",extra="",full=False):
        return '<div class="bp-field'+(' bp-full' if full else '')+'"><label for="'+fid+'">'+e(title)+' '+("" if "required" in extra else optional)+'</label><input id="'+fid+'" type="'+ftype+'" '+extra+'></div>'
    fields=[
        field("bp-name",t["name"],extra='required maxlength="90" autocomplete="name"'),
        field("bp-phone",t["phone"],ftype="tel",extra='required maxlength="28" inputmode="tel" autocomplete="tel" placeholder="+212 …"'),
        field("bp-email",t["email"],ftype="email",extra='maxlength="120" autocomplete="email"'),
        field("bp-country",t["country"],extra='maxlength="70" autocomplete="country-name"'),
        field("bp-start",t["start"],ftype="date",extra='required'),
        '<div class="bp-field" id="bp-checkout-field" hidden><label for="bp-end">'+e(t["end"])+' *</label><input id="bp-end" type="date"><small class="bp-note">'+e(t["endhelp"])+'</small></div>',

        '<div class="bp-field"><label for="bp-language">'+e(t["language"])+'</label><select id="bp-language"><option value="Français"'+(' selected' if lang=="fr" else '')+'>Français</option><option value="English"'+(' selected' if lang=="en" else '')+'>English</option><option value="العربية">العربية</option></select></div>',
        field("bp-place",t["place"],extra='maxlength="150" placeholder="'+e(t["placehint"])+'"',full=True),
        '<div class="bp-field bp-full"><label>'+e(t["extra"])+'</label><div id="bp-extras" class="bp-extras">'+extras+'</div></div>',
        '<div class="bp-field bp-full"><label for="bp-note">'+e(t["notes"])+' '+optional+'</label><textarea id="bp-note" maxlength="1500" placeholder="'+e(t["noteshint"])+'"></textarea></div>'
    ]
    main=f'''<main class="bp-main" id="mainContent">
    <div id="imsfrane-booking" data-bp-lang="{lang}">
      <section class="bp-hero" aria-labelledby="bp-title">
        <div class="bp-hero-copy"><span class="bp-kicker">{e(t["kicker"])}</span><h1 id="bp-title">{t["hero"]}</h1>
          <p>{e(t["intro"])}</p><div class="bp-hero-tags">{tags}</div>
        </div>
      </section>
      <div class="bp-wrap">
        <ol class="bp-steps" aria-label="Reservation steps">{steps}</ol>
        <div class="bp-layout">
          <div class="bp-main-col">
            <section class="bp-section" aria-labelledby="bp-select-heading">
              <div class="bp-section-heading"><div><span class="bp-heading-hint">{e(t["eyebrow1"])}</span><h2 id="bp-select-heading">{e(t["pick"])}</h2><p>{e(t["pickhelp"])}</p></div></div>
              <div class="bp-travelers-box"><label for="bp-travelers">{e(t["travelers"])} <span aria-hidden="true">*</span></label>
                <div class="bp-travelers-control"><button type="button" id="bp-people-minus" aria-label="− {e(t["travelers"])}">−</button>
                <input id="bp-travelers" type="number" form="bp-form" min="1" max="60" value="2" inputmode="numeric" required aria-describedby="bp-people-help">
                <button type="button" id="bp-people-plus" aria-label="+ {e(t["travelers"])}">+</button></div>
                <p id="bp-people-help">{e(t["countHint"])}</p></div>
              <div id="bp-filters" class="bp-filters" role="group" aria-label="{e(t["pick"])}">{filters}</div>
              <div id="bp-offers" class="bp-offers">{"".join(cards)}</div>
              <p class="bp-alert" id="bp-season-tip" hidden>{e(t["season"])}</p>
            </section>
            <section class="bp-section" id="bp-trip-details" aria-labelledby="bp-details-heading">
              <div class="bp-section-heading"><div><span class="bp-heading-hint">{e(t["eyebrow2"])}</span><h2 id="bp-details-heading">{e(t["details"])}</h2><p>{e(t["detailshelp"])}</p></div></div>
              <div class="bp-panel">
                <form id="bp-form" novalidate><div class="bp-form-grid">{"".join(fields)}</div>
                  <p class="bp-note">{e(t["disclaimer"])}</p>
                  <p class="bp-validation" id="bp-validation" role="alert" aria-live="polite"></p>
                </form>
              </div>
            </section>
          </div>
          <aside class="bp-side" aria-labelledby="bp-summary-heading">
            <section class="bp-summary">
              <div class="bp-summary-head"><span>{e(t["summaryeyebrow"])}</span><h2 id="bp-summary-heading">{e(t["summary"])}</h2></div>
              <div class="bp-summary-items" id="bp-summary-items" aria-live="polite"><p class="bp-summary-empty">{e(t["summaryempty"])}</p></div>
              <div class="bp-summary-total"><div class="bp-sum-top"><span>{e(t["total"])}</span><strong id="bp-total">0 MAD</strong></div>
                <p>{e(t["pending"])}</p>
                <button class="bp-send" id="bp-send" type="submit" form="bp-form">✉ {e(t["send"])} ↗</button>
                <button class="bp-copy" id="bp-copy" type="button">{e(t["copy"])}</button>
              </div>
            </section>
            <div class="bp-trust">{trust}</div>
            <div class="bp-instructions"><b>Imsfrane Cathédrale.</b> {e(t["disclaimer"])}</div>
          </aside>
        </div>
      </div>
    </div>
    <noscript><div style="text-align:center;padding:25px"><a href="https://wa.me/212667772551">WhatsApp · +212 667 772 551</a></div></noscript>
  </main>'''
    return main

def build(root):
    config=json.dumps(CATALOG,ensure_ascii=False).replace("</","<\\/")
    for lang in ("fr","en"):
        path=root/lang/"booking.html"
        original=path.read_text(encoding="utf-8")
        replacement=render(lang)
        original,n=re.subn(r"<main\b[^>]*>.*?</main>",lambda m:replacement,original,count=1,flags=re.S|re.I)
        if n!=1:
            raise RuntimeError("Booking main missing: "+str(path))
        original=original.replace("</head>",'<link rel="stylesheet" href="../booking-pro.css"></head>',1)
        original=original.replace("</body>",'<script type="application/json" id="bpCatalog">'+config+'</script><script defer src="../booking-pro.js"></script></body>',1)
        # No photos anywhere on the Booking pages, including shared header and footer.
        # Keep the site's textual wordmark and navigation intact.
        original=re.sub(r'<img\\b[^>]*>', '', original, flags=re.I)
        original=re.sub(r'<link\\b[^>]*\\bas=(["\\'])image\\1[^>]*>', '', original, flags=re.I)
        original=original.replace('<script defer="" src="../js/pages/booking.min.js"></script>','')
        original=original.replace('<script defer src="../js/pages/booking.min.js"></script>','')
        original=original.replace('Choisissez votre activité, la date et le nombre de participants, puis envoyez votre demande par WhatsApp.','Créez votre séjour à Imsfrane et calculez le tarif du rafting, des tentes, du VTT, du quad et des randonnées.')
        original=original.replace('Choose your activity, date and group size, then send your booking request directly by WhatsApp.','Build your Imsfrane adventure and calculate transparent rafting, camping, mountain biking, quad and hiking prices.')
        path.write_text(original,encoding="utf-8")

if __name__=="__main__":
    build(Path("public"))
