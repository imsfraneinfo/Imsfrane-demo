"""Keep apartment and tent listings aligned with the direct booking form."""
from pathlib import Path
from urllib.parse import urlencode

from booking_transport import read, save

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
        assert code.count(before) == 1, before
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
            note = page.new_tag("p")
            note.string = f"{copy} {linens}"
            card.select_one(".rental-price").insert_after(note)
        save(path, page)

        path = folder / "hebergements/index.html"
        page = read(path)
        card = page.select_one(".stay-card-body")
        lines = card.find_all("p", recursive=False)
        lines[0].string = comparison
        lines[1].decompose()
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
        page.select_one('script[src*="booking-new.js"]')["src"] += "&rental=2"
        save(path, page)

        path = folder / "camping/index.html"
        page = read(path)
        tariffs = page.select("#camp-prices .camp-tariff")
        assert len(tariffs) >= 4, lang
        for card, price in zip(tariffs, (60, 120, 150, 200)):
            assert card.strong.get_text(strip=True).startswith(str(price)), lang
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
