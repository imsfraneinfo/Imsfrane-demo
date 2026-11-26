"""Keep apartment and tent listings aligned with the direct booking form."""
import json
from pathlib import Path
from urllib.parse import urlencode

from booking_transport import read, save
from build_weekend_offers import SLUGS

COPY = {
    "fr": (
        "4 personnes : 2 dans la chambre double et 2 sur les banquettes du salon.",
        "Jusqu’à 7 personnes : 4 dans les chambres et 3 sur les banquettes du salon.",
        "Les voyageurs apportent leurs draps et leurs serviettes.",
        "Appartements entiers : 300 DH ou 250 DH par nuit · 4 ou 7 personnes selon l’appartement",
        "Demander sur WhatsApp",
        "Bonjour, je souhaite louer une tente à Imsfrane.",
        "Arrivée :\nNombre de nuits :",
        "Rafting sur l’Oued Ahansal à Imsfrane : parcours de 12, 30 et 50 km, tarifs et réservation avec une équipe locale.",
        "Séjour au Gîte Atlas Cathédrale à Imsfrane : chambres avec douche et WC privés, demi-pension ou pension complète.",
    ),
    "en": (
        "4 guests: 2 in the double bedroom and 2 on the living-room couches.",
        "Up to 7 guests: 4 in the bedrooms and 3 on the living-room couches.",
        "Guests bring their own bed sheets and towels.",
        "Entire apartments: 300 or 250 MAD per night · 4 or 7 guests depending on the apartment",
        "Ask on WhatsApp",
        "Hello, I’d like to rent a tent in Imsfrane.",
        "Arrival date:\nNumber of nights:",
        "Raft the Ahansal River at Imsfrane. Compare 12, 30 and 50 km routes, check prices and book with a local team.",
        "Stay at Gîte Atlas Cathédrale in Imsfrane. Rooms have their own shower and toilet. Half board and full board are available.",
    ),
    "es": (
        "4 personas: 2 en la habitación doble y 2 en los sofás del salón.",
        "Hasta 7 personas: 4 en los dormitorios y 3 en los sofás del salón.",
        "Los huéspedes deben traer sus propias sábanas y toallas.",
        "Apartamentos completos: 300 o 250 MAD por noche · 4 o 7 personas según el apartamento",
        "Consultar por WhatsApp",
        "Hola, me gustaría alquilar una tienda en Imsfrane.",
        "Fecha de llegada:\nNúmero de noches:",
        "Rafting en el río Ahansal, en Imsfrane. Consulta los recorridos de 12, 30 y 50 km, los precios y cómo reservar.",
        "Alójate en el Gîte Atlas Cathédrale de Imsfrane, con ducha y aseo privados en cada habitación, media pensión o pensión completa.",
    ),
    "ar": (
        "تتسع لأربعة أشخاص: شخصان في غرفة النوم المزدوجة وشخصان على أرائك الصالون.",
        "تتسع لسبعة أشخاص: أربعة في غرفتي النوم وثلاثة على أرائك الصالون.",
        "يُحضر الضيوف أغطية الأسرّة والمناشف الخاصة بهم.",
        "شقتان للكراء الكامل: 300 أو 250 درهمًا لليلة · أربعة أو سبعة أشخاص حسب الشقة",
        "استفسر عبر واتساب",
        "مرحبًا، أود استئجار خيمة في إمسفران.",
        "تاريخ الوصول:\nعدد الليالي:",
        "التجديف في وادي أحنصال بإمسفران: رحلات بطول 12 و30 و50 كيلومترًا، مع الأسعار والحجز لدى فريق محلي.",
        "الإقامة في نزل أطلس كاتدرال بإمسفران، مع دش ومرحاض خاصين بكل غرفة وخيارات الإقامة مع الوجبات.",
    ),
}


OFFERS = {
    "fr": ("Louer une tente", "Programme de 4 jours au départ de Marrakech",
           "4 000 DH par personne · 4 participants minimum", "Choisir la demi-pension",
           "350 DH par personne et par nuit · Pension complète", "Choisir la pension complète"),
    "en": ("Rent a tent", "4-day programme from Marrakech",
           "4,000 MAD per person · Minimum 4 participants", "Choose half board",
           "350 MAD per person per night · Full board", "Choose full board"),
    "es": ("Alquilar una tienda", "Programa de 4 días desde Marrakech",
           "4.000 MAD por persona · Mínimo 4 participantes", "Elegir media pensión",
           "350 MAD por persona y noche · Pensión completa", "Elegir pensión completa"),
    "ar": ("استئجار خيمة", "برنامج أربعة أيام انطلاقًا من مراكش",
           "4,000 درهم للشخص · أربعة مشاركين على الأقل", "اختر الإقامة مع العشاء والفطور",
           "350 درهمًا للشخص في الليلة · إقامة مع جميع الوجبات", "اختر الإقامة مع جميع الوجبات"),
}


PACKAGE_COPY = {
    "fr": ("350 DH par personne et par nuit", "par personne et par nuit",
           "Rafting de 30 km sur l’Oued Ahansal à Imsfrane : environ 4 heures, équipement et briefing inclus, 800 DH par personne.",
           "Séjour rafting de 4 jours au départ de Marrakech vers Imsfrane, à 4 000 DH par personne pour un groupe d’au moins 4 participants."),
    "en": ("350 MAD per person per night", "per person per night",
           "Raft 30 km on the Ahansal River at Imsfrane. Around 4 hours, equipment and briefing included, 800 MAD per person.",
           "A four-day rafting trip from Marrakech to Imsfrane. 4,000 MAD per person for groups of at least four."),
    "es": ("350 MAD por persona y noche", "por persona y noche",
           "Rafting de 30 km por el río Ahansal en Imsfrane. Unas 4 horas, equipo e instrucciones incluidos, 800 MAD por persona.",
           "Viaje de rafting de cuatro días desde Marrakech a Imsfrane. 4.000 MAD por persona para grupos de cuatro o más."),
    "ar": ("350 درهمًا للشخص في الليلة", "للشخص في الليلة",
           "تجديف لمسافة 30 كيلومترًا في وادي أحنصال بإمسفران، يستغرق نحو أربع ساعات ويشمل المعدات والإرشادات مقابل 800 درهم للشخص.",
           "رحلة تجديف لأربعة أيام من مراكش إلى إمسفران بسعر 4,000 درهم للشخص، للمجموعات من أربعة مشاركين فأكثر."),
}


PROGRAMME_COPY = {
    "fr": ("Autres idées de week-end", "Cascades d’Ouzoud · visite guidée",
           "300 DH par sortie · Barque facultative : 30 DH par personne, à régler séparément"),
    "en": ("More weekend trips", "Ouzoud Falls · guided visit",
           "300 MAD per outing · Optional boat ride: 30 MAD per person, paid separately"),
    "es": ("Más escapadas de fin de semana", "Cascadas de Ouzoud · visita guiada",
           "300 MAD por salida · Paseo en barca opcional: 30 MAD por persona, pago aparte"),
    "ar": ("خيارات أخرى لعطلة نهاية الأسبوع", "شلالات أوزود · زيارة مع مرشد",
           "300 درهم للجولة · جولة القارب اختيارية: 30 درهمًا للشخص تُدفع بشكل منفصل"),
}


def add_ouzoud(page, lang, services):
    _, name, details = PROGRAMME_COPY[lang]
    if not any(service["id"] == "ouzoud" for service in services):
        services.append({"id": "ouzoud", "name": name, "price": 300, "unit": "group"})
    if not page.select_one('input[value="ouzoud"]'):
        custom = page.select_one('input[value="custom"]').find_parent("label")
        label = page.new_tag("label", attrs={"class": "bk-choice"})
        label.append(page.new_tag("input", attrs={"data-service": "", "type": "checkbox", "value": "ouzoud"}))
        copy = page.new_tag("span")
        for element, text in (("strong", name), ("small", details)):
            tag = page.new_tag(element)
            tag.string = text
            copy.append(tag)
        label.append(copy)
        custom.insert_before(label)


def update_programme_navigation(root, lang, prefix):
    folder = root / lang
    for route in ("camping", "quad", "randonnee", "store"):
        path = folder / route / "index.html"
        page = read(path)
        main = page.select_one("main")
        skip = page.select_one('a[href="#mainContent"]')
        if skip and not page.select_one("#mainContent"):
            main["id"] = main.get("id", "mainContent")
            main["tabindex"] = "-1"
            skip["href"] = "#" + main["id"]
            save(path, page)

    path = folder / "programme/index.html"
    page = read(path)
    section = page.select_one("#weekend-trips")
    if section is None:
        section = page.new_tag("section", id="weekend-trips", attrs={"class": "wk-wrap oz-programme-list"})
        heading = page.new_tag("h2")
        heading.string = PROGRAMME_COPY[lang][0]
        section.append(heading)
        listing = page.new_tag("ul")
        for slug in SLUGS:
            offer = read(folder / slug / "index.html")
            link = page.new_tag("a", href=f"{prefix}{lang}/{slug}/")
            link.string = offer.select_one("main h1").get_text(" ", strip=True)
            item = page.new_tag("li")
            item.append(link)
            listing.append(item)
        section.append(listing)
        ouzoud = page.select_one(".oz-programme-list")
        if ouzoud:
            ouzoud.insert_after(section)
        else:
            page.select_one("main").append(section)
        save(path, page)


def set_metadata(page, name, content):
    for attribute, key in (("name", name), ("property", f"og:{name}"), ("name", f"twitter:{name}")):
        tag = page.select_one(f'meta[{attribute}="{key}"]')
        if tag is None:
            tag = page.new_tag("meta", attrs={attribute: key})
            page.head.append(tag)
        tag["content"] = content


def update_package_pages(root, lang):
    _, unit, rafting30, rafting4 = PACKAGE_COPY[lang]
    folder = root / lang
    assert read(folder / "index.html").select_one("#activities"), lang
    for slug in SLUGS:
        path = folder / slug / "index.html"
        page = read(path)
        back = page.select_one("a.wo-back")
        back["href"] = back["href"].split("#")[0] + "#activities"
        title = page.select_one("main h1").get_text(" ", strip=True) + " | Imsfrane Cathédrale"
        page.title.string = title
        for attribute, key in (("property", "og:title"), ("name", "twitter:title")):
            tag = page.select_one(f'meta[{attribute}="{key}"]')
            if tag:
                tag["content"] = title
        save(path, page)
    for route, description in (("30-km", rafting30), ("4-jours-marrakech", rafting4)):
        path = folder / "rafting" / route / "index.html"
        page = read(path)
        set_metadata(page, "description", description)
        save(path, page)
    path = root / f"gite-content-{lang}.html"
    page = read(path)
    offer = page.select_one('.step a[href*="stay=gite350"]').find_parent("article")
    offer.small.string = unit
    save(path, page)


def add_offers(page, root, lang):
    tent, programme, price, half, full_price, full = OFFERS[lang]
    service_data = page.select_one("#bookingServices")
    services = json.loads(service_data.string)
    service = next(service for service in services if service["id"] == "raft4")
    service.update(name=programme, price=4000, minGuests=4)
    add_ouzoud(page, lang, services)
    service_data.string = json.dumps(services, ensure_ascii=False)
    offer = page.select_one('input[value="raft4"]').parent
    offer.strong.string = programme
    offer.small.string = price
    link = page.select_one('a[href$="/camping/#camp-prices"]')
    if link is None:
        link = page.new_tag("a", href=f"/Imsfrane-demo/{lang}/camping/#camp-prices")
        note = page.new_tag("p", attrs={"class": "bk-note"})
        note.append(link)
        page.select_one("#campNote").insert_after(note)
    link.string = tent

    path = root / lang / "rafting/4-jours-marrakech/index.html"
    detail = read(path)
    action = detail.select_one('.ims-booking-overview a[href*="activity=raft4"]')
    row = action.parent
    action.extract()
    row.clear()
    row.extend([price + " · ", action])
    save(path, detail)

    path = root / lang / "gite-atlas/index.html"
    gite = read(path)
    half_link = gite.select_one('.ims-booking-overview a[href*="stay=gite250"]')
    half_link.string = half
    if not gite.select_one('.ims-booking-overview a[href*="stay=gite350"]'):
        row = gite.new_tag("p")
        action = gite.new_tag("a", href=half_link["href"].replace("stay=gite250", "stay=gite350"))
        action.string = full
        row.extend([full_price + " · ", action])
        half_link.parent.insert_after(row)
    for action in gite.select('.ims-booking-overview a[href*="stay=gite"]'):
        action["class"] = ["gite-plan-button"]
    if not gite.select_one("#gite-plan-buttons"):
        style = gite.new_tag("style", id="gite-plan-buttons")
        style.string = (
            ".ims-booking-overview .gite-plan-button{background:#173525;color:#fff;"
            "padding:8px 13px;border-radius:7px;text-decoration:none;margin-block:4px}"
        )
        gite.head.append(style)
    save(path, gite)


def build(root, rentals):
    script = root / "booking-new.js"
    code = script.read_text()
    changes = (
        ("stay==='house'?6:stay==='apartment2'?4", "stay==='house'?4:stay==='apartment2'?7"),
        ("const currency = arabic ? ' درهم' : ' DH';",
         "const currency = arabic ? ' درهم' : document.documentElement.lang === 'fr' ? ' DH' : ' MAD';"),
        (" if(!form.reportValidity())return;",
         """ const emailChannel = e.submitter?.dataset.channel === 'email';
 $('email').required = emailChannel;
 $('phone').required = !emailChannel;
 if(!form.reportValidity())return;"""),
    )
    for before, after in changes:
        if after not in code:
            assert code.count(before) == 1, before
            code = code.replace(before, after)
    if "const selectedServices" not in code:
        limits = " $('guests').max=limit;"
        assert limits in code
        code = code.replace(limits, limits + """
 const selectedServices = [...form.querySelectorAll('[data-service]:checked')]
   .map(input => services.find(service => service.id === input.value));
 const minGuests = Math.max(1, ...selectedServices.map(service => service.minGuests || 1));
 $('guests').min = minGuests;""", 1)
        before = "form.querySelectorAll('[data-service]:checked').forEach(input=>{const a=services.find(a=>a.id===input.value);"
        assert before in code
        code = code.replace(before, "selectedServices.forEach(a=>{if(people < (a.minGuests || 1) || minGuests > limit)return;")
    before = "add(t[23],nights===1?350*people:null,t[24]+(nights!==1?' · '+t[30]:''));"
    after = "add(t[23],350*people*Math.max(nights,1),'350 × '+people+' × '+Math.max(nights,1)+' '+t[33]);"
    if after not in code:
        assert code.count(before) == 1
        code = code.replace(before, after)
    script.write_text(code)

    for lang, words in COPY.items():
        first, second, linens, comparison, ask, greeting, dates, rafting, gite = words
        folder = root / lang
        path = folder / "hebergement/index.html"
        page = read(rentals / f"{lang}.html")
        cards = page.select("main .rental-card")
        assert len(cards) == 2, lang
        for card, copy in zip(cards, (first, second)):
            note = card.select_one(".rental-capacity") or page.new_tag("p", attrs={"class": "rental-capacity"})
            for old in card.find_all("p", recursive=False):
                if old is not note and old.get_text(strip=True) == f"{copy} {linens}":
                    old.decompose()
            note.string = f"{copy} {linens}"
            card.select_one(".rental-price").insert_after(note)
        save(path, page)

        path = folder / "hebergements/index.html"
        page = read(path)
        card = page.select_one(".stay-card-body")
        lines = card.find_all("p", recursive=False)
        lines[0].string = comparison
        for line in lines[1:]:
            line.decompose()
        save(path, page)

        path = folder / "booking/index.html"
        page = read(path)
        form = page.select_one("#bookingForm")
        form["novalidate"] = ""
        for field in ("email", "phone"):
            form.select_one(f"#{field}").attrs.pop("required", None)
        notes = page.select_one("#stay").find_parent("section").select(".bk-note")
        for note, capacity in zip(notes[:2], (first, second)):
            heading = note.strong.extract()
            note.clear()
            note.extend([heading, page.new_tag("br"), f"{capacity} {linens}"])
        page.select_one('script[src*="booking-new.js"]')["src"] = "/Imsfrane-demo/booking-new.js?v=offers4"
        add_offers(page, root, lang)
        rate, _, _, _ = PACKAGE_COPY[lang]
        option = page.select_one('#stay option[value="gite350"]')
        option.string = option.get_text().rsplit(" · ", 1)[0] + " · " + rate
        full_board = page.select_one("#stay").find_parent("section").select(".bk-note")[3]
        details = full_board.contents[-1].strip()
        full_board.contents[-1].replace_with(rate + " · " + details.split(" · ", 1)[-1])
        save(path, page)
        update_package_pages(root, lang)
        update_programme_navigation(root, lang, "/Imsfrane-demo/")

        path = folder / "camping/index.html"
        page = read(path)
        tariffs = page.select("#camp-prices .camp-tariff")
        assert len(tariffs) >= 4, lang
        for card, price in zip(tariffs, (60, 120, 150, 200)):
            assert card.strong.get_text(strip=True).startswith(str(price)), lang
            for old in card.select('a[href*="wa.me"]'):
                old.decompose()
            details = card.get_text(" · ", strip=True)
            query = urlencode({"text": f"{greeting}\n{details}\n{dates}"})
            action = page.new_tag("a", href=f"https://wa.me/212667772551?{query}",
                                  target="_blank", rel="noopener")
            action.string = ask
            card.append(action)
        save(path, page)

        for route, description in (("rafting", rafting), ("gite-atlas", gite)):
            path = folder / route / "index.html"
            page = read(path)
            tag = page.select_one('meta[name="description"]')
            if tag is None:
                tag = page.new_tag("meta", attrs={"name": "description"})
                page.head.append(tag)
            tag["content"] = description
            save(path, page)


if __name__ == "__main__":
    build(Path("public"), Path(".preview-rentals"))
