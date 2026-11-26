"""Update the travel guide and booking with the approved transfer tariff."""
import json
from copy import deepcopy

from bs4 import BeautifulSoup

COPY = {
    "fr": ("Transfert aller-retour depuis Béni Mellal", "1 800 DH pour le groupe de 1 à 5 personnes",
           "Au-delà de 5 personnes : sur devis", "Comment venir à Imsfrane ?", "150 MAD / vélo",
           "Autre transport / transfert", "Camping organisé · demande de devis",
           "Votre demande sera confirmée par l’équipe après vérification des disponibilités. Aucun paiement à cette étape.",
           "Le point de rendez-vous exact vous est communiqué lors de la confirmation."),
    "en": ("Round-trip transfer from Beni Mellal", "1,800 MAD total for 1–5 travellers",
           "For 6 or more travellers, request a quote", "How to get to Imsfrane", "150 MAD / bike",
           "Other transport or transfer", "Organised camping · request a quote",
           "Our team will confirm your request once availability is checked. No payment is taken at this stage.",
           "We’ll share the exact meeting point when we confirm your request."),
    "es": ("Traslado de ida y vuelta desde Beni Melal", "1.800 MAD en total para 1 a 5 viajeros",
           "Para más de 5 viajeros, solicita presupuesto", "Cómo llegar a Imsfrane", "150 MAD / bicicleta",
           "Otro transporte o traslado", "Acampada organizada · solicitar presupuesto",
           "Nuestro equipo confirmará tu solicitud tras comprobar la disponibilidad. No se realiza ningún pago en este paso.",
           "Te indicaremos el punto de encuentro exacto al confirmar tu solicitud."),
    "ar": ("النقل ذهابًا وإيابًا من بني ملال", "1,800 درهم للمجموعة من شخص واحد إلى 5 أشخاص",
           "لأكثر من 5 أشخاص يُحدَّد السعر عند الطلب", "كيف تصل إلى إمسفران؟", "150 درهمًا للدراجة",
           "نقل آخر", "التخييم المنظّم · طلب عرض سعر",
           "يؤكّد الفريق طلبك بعد التحقق من التوفّر. لا يُطلب أي دفع في هذه المرحلة.",
           "نُطلعك على نقطة اللقاء عند تأكيد طلبك."),
}



POLICIES = {
    "fr": ("Conditions d’annulation et de report",
           "Si vous annulez plus de 5 jours avant la date prévue, nous vous remboursons intégralement. À 5 jours ou moins, les sommes versées ne sont pas remboursées, car le transport, les guides et l’équipe sont réservés à l’avance.",
           "Si la météo ou le niveau de la rivière ne permettent pas le rafting, nous proposons une autre date. Si elle ne vous convient pas, nous vous remboursons intégralement."),
    "en": ("Cancellation and rescheduling",
           "If you cancel more than 5 days before the scheduled date, you receive a full refund. If you cancel 5 days or less before the date, payments are non-refundable because transport, guides and staff are booked in advance.",
           "If weather or river levels prevent rafting, we offer another date. If it does not suit you, we refund any amount already paid in full."),
    "es": ("Cancelaciones y cambios de fecha",
           "Si cancelas con más de 5 días de antelación, te devolvemos íntegramente lo abonado. Si cancelas cuando faltan 5 días o menos, no se devuelve lo abonado, ya que el transporte, los guías y el equipo se reservan con antelación.",
           "Si el tiempo o el nivel del río impiden hacer rafting, proponemos otra fecha. Si no te conviene, te devolvemos íntegramente lo abonado."),
    "ar": ("شروط الإلغاء والتأجيل",
           "إذا ألغيت الحجز قبل الموعد بأكثر من 5 أيام، نعيد لك كامل المبلغ المدفوع. إذا ألغيت قبل الموعد بـ5 أيام أو أقل، فلا يُسترد المبلغ لأننا نحجز النقل والمرشدين والفريق مسبقًا.",
           "إذا لم يسمح الطقس أو مستوى النهر بالتجديف، نقترح موعدًا آخر. إذا لم يناسبك، نعيد لك كامل المبلغ الذي دفعته."),
}


DEPOSIT = {
    "fr": "Pour une activité, l’équipe confirme d’abord la disponibilité. Vous versez ensuite un acompte de 20 %, puis le solde de 80 % après l’activité.",
    "en": "For an activity, our team confirms availability first. You then pay a 20% deposit and the remaining 80% after the activity.",
    "es": "Para reservar una actividad, el equipo confirma primero la disponibilidad. Después pagas un anticipo del 20 % y el 80 % restante al terminar la actividad.",
    "ar": "لحجز نشاط، يؤكّد الفريق التوفّر أولًا. بعد ذلك تدفع عربونًا بنسبة 20٪، وتسدد المبلغ المتبقي بنسبة 80٪ بعد النشاط.",
}


def add_policy(page, container, lang):
    if container is None:
        return
    title, cancellation, rafting = POLICIES[lang]
    section = page.select_one(".booking-cancellation-policy")
    if section:
        section.find_all("p", recursive=False)[1].string = rafting
        return
    section = page.new_tag("div", attrs={"class": "booking-cancellation-policy"})
    heading = page.new_tag("strong")
    heading.string = title
    section.append(heading)
    for copy in (cancellation, rafting):
        paragraph = page.new_tag("p")
        paragraph.string = copy
        section.append(paragraph)
    actions = container.select_one(".enquiry-actions")
    if actions:
        actions.insert_before(section)
    else:
        container.append(section)


def read(path):
    return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")


def save(path, page):
    path.write_text(str(page), encoding="utf-8")


def guide(path, words, booking_url):
    page = read(path)
    for row in page.select("main tr"):
        cells = row.find_all("td", recursive=False)
        if not cells or "/vtt" not in str(row):
            continue
        text = cells[0].get_text(strip=True)
        if text.startswith("100"):
            row.decompose()
        elif text.startswith("150"):
            cells[0].string = words[4]
    transport = page.select_one("#transport")
    if not transport.select_one(".beni-mellal-fare"):
        note = page.new_tag("p", attrs={"class": "beni-mellal-fare"})
        strong = page.new_tag("strong")
        strong.string = words[0] + " · " + words[1]
        note.append(strong)
        note.append(" " + words[2] + ". ")
        link = page.new_tag("a", href=booking_url + "?activity=transportBeniMellal")
        link.string = words[0]
        note.append(link)
        transport.find("h2").parent.append(note)
    save(path, page)


def booking(path, words, guide_url, lang):
    page = read(path)
    services_node = page.select_one("#bookingServices")
    if not services_node:
        return
    summary = page.select_one(".bk-summary")
    add_policy(page, summary, lang)
    quote = summary.select_one("#quoteNote")
    if quote and not summary.select_one(".booking-deposit-note"):
        deposit = page.new_tag("p", attrs={"class": "booking-deposit-note"})
        deposit.string = DEPOSIT[lang]
        quote.find_next_sibling("p").insert_after(deposit)
    services = json.loads(services_node.string)
    position = next(i for i, service in enumerate(services) if service["id"] == "transport")
    if any(service["id"] == "transportBeniMellal" for service in services):
        save(path, page)
        return
    services[position]["name"] = words[5]
    services.insert(position, {
        "id": "transportBeniMellal", "name": words[0], "price": 1800, "unit": "group", "maxGuests": 5,
    })
    next(s for s in services if s["id"] == "camping")["name"] = words[6]
    services_node.string = json.dumps(services, ensure_ascii=False)

    other = page.select_one('input[data-service][value="transport"]').parent
    transfer = deepcopy(other)
    transfer.input["value"] = "transportBeniMellal"
    transfer.strong.string = words[0]
    transfer.small.string = words[1] + " · " + words[2]
    other.strong.string = words[5]
    other.insert_before(transfer)
    page.select_one('input[data-service][value="camping"]').parent.strong.string = words[6]

    arrival = page.select_one("#arrival")
    travel = page.new_tag("a", href=guide_url + "#transport")
    travel.string = words[3]
    arrival.insert_after(travel)
    quote = page.select_one("#quoteNote")
    confirmation = quote.find_next_sibling("p")
    if confirmation and confirmation.find("button") is None:
        confirmation.string = words[7]
    script = page.select_one("script[src*='booking-new.js']")
    script["src"] = script["src"].split("?")[0] + "?v=transfer1"
    save(path, page)


def update_site(root, prefix):
    for lang, words in COPY.items():
        folder = root / lang
        base = f"{prefix}{lang}/"
        guide(folder / "guide/index.html", words, base + "booking/")
        for name in ("booking/index.html", "booking.html"):
            booking(folder / name, words, base + "guide/", lang)
        for name in ("rafting", "gite-atlas"):
            path = folder / name / "index.html"
            page = read(path)
            overview = page.select_one(".ims-booking-overview")
            if overview and not overview.select_one(".ims-meeting-note"):
                note = page.new_tag("p", attrs={"class": "ims-meeting-note"})
                note.string = words[8]
                overview.append(note)
            if name == "rafting":
                add_policy(page, overview, lang)
            if overview or name == "rafting":
                save(path, page)

    path = root / "booking-new.js"
    script = path.read_text(encoding="utf-8")
    if "a.maxGuests" in script:
        return
    old = "add(a.name,a.price===null?null:a.price*qty,a.price===null?t[30]:a.price+' × '+qty);"
    new = """const needsQuote = a.price === null || (a.maxGuests && people > a.maxGuests);
   add(a.name, needsQuote ? null : a.price * qty, needsQuote ? t[30] : a.price + ' × ' + qty);"""
    assert script.count(old) == 1
    path.write_text(script.replace(old, new), encoding="utf-8")
