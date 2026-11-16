"""Keep published offers and their booking links consistent in each language."""
from copy import deepcopy
import json
import shutil
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("public")
LOCALES = {
    "fr": ("Demander une réservation", "Voir les autres activités", "Demander sur WhatsApp",
           "150 DH / vélo", " / personne", "Rafting à Imsfrane", "Gîte Atlas Cathédrale",
           "12 km · env. 2 h", "30 km · env. 4 h", "50 km · 2 jours",
           "Bivouac, repas et retour à Msfrane inclus.", "Dîner et petit-déjeuner inclus.",
           "Équipement et briefing inclus.", "Choisir la demi-pension"),
    "en": ("Request a booking", "See more activities", "Ask on WhatsApp",
           "150 DH / bike", " / person", "Rafting in Imsfrane", "Gîte Atlas Cathédrale",
           "12 km · approx. 2 hr", "30 km · approx. 4 hr", "50 km · 2 days",
           "Bivouac, meals and return to Msfrane included.", "Dinner and breakfast included.",
           "Equipment and briefing included.", "Choose half board"),
    "es": ("Solicitar una reserva", "Ver más actividades", "Consultar por WhatsApp",
           "150 DH / bicicleta", " / persona", "Rafting en Imsfrane", "Gîte Atlas Cathédrale",
           "12 km · unas 2 h", "30 km · unas 4 h", "50 km · 2 días",
           "Vivac, comidas y regreso a Msfrane incluidos.", "Cena y desayuno incluidos.",
           "Equipo y sesión informativa incluidos.", "Elegir media pensión"),
    "ar": ("طلب الحجز", "عرض المزيد من الأنشطة", "استفسر عبر واتساب",
           "150 درهمًا للدراجة", " للشخص", "التجديف في إمسفران", "نزل أطلس كاتدرال",
           "12 كم · نحو ساعتين", "30 كم · نحو 4 ساعات", "50 كم · يومان",
           "يشمل المبيت في المخيم والوجبات والعودة إلى مسفران.", "يشمل العشاء والفطور.",
           "تشمل الجولة المعدات وشرح تعليمات السلامة.", "اختر الإقامة مع العشاء والفطور"),
}


def read(path):
    return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")


def save(path, page):
    path.write_text(str(page), encoding="utf-8")


def link(page, href, label):
    tag = page.new_tag("a", href=href)
    tag.string = label
    return tag


def booking_link(base, choice):
    kind = "stay" if choice in {"house", "gite250", "gite350", "weekend"} else "activity"
    return f"{base}booking/?{kind}={choice}"


def price(amount, lang):
    return f"{amount:,}".replace(",", "\u00a0") + (" درهم" if lang == "ar" else " DH")


def home(path, lang, words):
    page = read(path)
    grid = page.select_one(".hp-activity-grid")
    if not grid:
        return
    grid.select_one(".hp-vtt strong").string = words[3]
    tent_rental = {"fr": "Location de tentes", "en": "Tent rental",
                   "es": "Alquiler de tiendas", "ar": "كراء الخيام"}
    grid.select_one(".hp-camping h3").string = tent_rental[lang]
    for card in grid.select(".hp-activity-card"):
        button = card.select_one(".hp-activity-bottom a")
        if button and "wa.me/" in button.get("href", ""):
            button.clear()
            button.string = words[2]
            button["aria-label"] = f'{words[2]} · {card.h3.get_text(strip=True)}'
    secondary = ["tubing", "jetski", "4x4", "passage", "zrkan", "anergui", "almou", "ahidous"]
    more = page.new_tag("details", attrs={"class": "ims-more"})
    summary = page.new_tag("summary")
    summary.string = words[1]
    more.append(summary)
    extra = page.new_tag("div", attrs={"class": "hp-activity-grid"})
    for slug in secondary:
        card = grid.select_one(f".hp-{slug}")
        if card:
            extra.append(card.extract())
    more.append(extra)
    grid.insert_after(more)
    reviews = page.select_one(".hp-google-reviews")
    duplicate = page.select_one(".hp-reviews")
    if duplicate:
        duplicate.decompose()
    if reviews:
        more.insert_after(reviews.extract())
        mark = reviews.select_one(".hp-google-mark")
        if mark:
            mark.clear()
            mark.attrs.pop("aria-hidden", None)
            mark.append(page.new_tag("img", src="/Imsfrane-demo/review-assets/google-maps.svg",
                                     alt="Google Maps", translate="no"))
        page.head.append(page.new_tag("link", rel="stylesheet",
                             href="/Imsfrane-demo/review-assets/reviews.css?v=1"))
        hero_reviews = deepcopy(reviews)
        hero_reviews["id"] = "google-reviews-under-hero"
        title = hero_reviews.select_one("[id]")
        if title:
            title["id"] += "-under-hero"
            hero_reviews["aria-labelledby"] = title["id"]
        page.select_one(".hp-hero").insert_after(hero_reviews)
        script = page.select_one("script[src*='google-reviews-live.js']")
        script["src"] = script["src"].split("?")[0] + "?v=maps-cards1"
    page.head.append(BeautifulSoup(
        "<style>.ims-more{margin-block:1.5rem}.ims-more summary{cursor:pointer;font-weight:700;padding:12px 0}"
        ".ims-more .hp-activity-grid{margin-top:1rem}.hp-home .hp-google-reviews{margin-block:1.5rem}</style>",
        "html.parser"))
    save(path, page)


def booking(path, lang):
    words = LOCALES[lang]
    page = read(path)
    if not page.select_one("#bookingNew"):
        return
    for selector in ("#bookingWords", "#bookingServices", "script[src*='booking-new.js']"):
        for duplicate in page.select(selector)[1:]:
            duplicate.decompose()
    data = page.select_one("#bookingServices")
    services = json.loads(data.string)
    amounts = {"raft30": 800, "raft50": 2500, "vtt": 150}
    for service in services:
        if service["id"] not in amounts:
            continue
        service["price"] = amounts[service["id"]]
        label = page.select_one(f'input[data-service][value="{service["id"]}"]').parent
        small = label.select_one("small")
        if service["id"] == "vtt":
            small.string = LOCALES[lang][3]
        elif service["id"] == "raft30":
            small.string = price(800, lang) + LOCALES[lang][4]
        elif small.string:
            small.string = re.sub(r"(?:1[\s,.]?500|2[\s,.]?500)", "2\u00a0500", small.string, count=1)
    quote = page.select_one('input[value="raft4"]').parent.select_one("small")
    quote.string = price(4000, lang) + words[4] + " · " + quote.get_text(strip=True)
    data.string = json.dumps(services, ensure_ascii=False)
    script = page.select_one("script[src*='booking-new.js']")
    script["src"] = script["src"].split("?")[0] + "?v=journey1"
    save(path, page)


def add_overview(path, base, lang, words, service):
    page = read(path)
    main = page.select_one("#mainContent") or page.select_one("main")
    if not main:
        return
    frame = main.select_one("iframe")
    area = page.new_tag("section", attrs={"class": "ims-booking-overview"})
    if service in {"rafting", "gite250"}:
        title = page.new_tag("h1")
        title.string = words[5 if service == "rafting" else 6]
        area.append(title)
    if service == "rafting":
        options = [("raft12", words[7], 400, words[12]), ("raft30", words[8], 800, words[12]),
                   ("raft50", words[9], 2500, words[10])]
    elif service == "gite250":
        per_night = {"fr": " / nuit", "en": " / night", "es": " / noche", "ar": " في الليلة"}
        options = [(service, "", 250, words[11])]
    elif service in {"raft12", "raft30", "raft50"}:
        options = {
            "raft12": [(service, words[7], 400, words[12])],
            "raft30": [(service, words[8], 800, words[12])],
            "raft50": [(service, words[9], 2500, words[10])],
        }[service]
    else:
        options = [(service, "", None, "")]
    for choice, duration, amount, included in options:
        row = page.new_tag("p")
        if amount:
            cost = price(amount, lang) + words[4]
            if service == "gite250":
                cost += per_night[lang]
            row.append(f"{duration} · {cost} · {included} " if duration else f"{cost} · {included} ")
        row.append(link(page, booking_link(base, choice), words[13] if service == "gite250" else words[0]))
        area.append(row)
    page.head.append(BeautifulSoup(
        "<style>.ims-booking-overview{width:min(1100px,calc(100% - 32px));margin:24px auto;"
        "padding:16px 20px;border:1px solid #dce5dc;border-radius:12px;background:#f5f8f4;color:#173525}"
        ".ims-booking-overview h1{font-size:clamp(1.35rem,4vw,2rem);margin:0 0 12px;color:inherit}"
        ".ims-booking-overview p{margin:8px 0}.ims-booking-overview a{color:inherit;"
        "font-weight:700;text-decoration:underline;text-underline-offset:3px;display:inline-block}</style>",
        "html.parser"))
    if frame:
        frame.insert_before(area)
    elif service == "vtt":
        rental = main.select_one(".vt-rental-copy")
        if rental:
            rental.append(link(page, booking_link(base, service), words[0]))
        hero = main.select_one(".quad-r-btn.quad-r-gold")
        if hero:
            hero["href"] = booking_link(base, service)
            hero.attrs.pop("target", None)
            hero.attrs.pop("rel", None)
            hero.string = words[0]
    else:
        main.append(area)
    save(path, page)


def fix_rafting_frames(lang):
    path = ROOT / f"rafting-programmes-{lang}.html"
    page = read(path)
    routes = page.select(".rp-card .rp-price")
    if len(routes) != 4:
        raise ValueError(f"Expected four rafting offers in {path}")
    for card, amount in zip(routes[:3], (400, 800, 2500)):
        card.string = price(amount, lang) + LOCALES[lang][4]
    save(path, page)
    detail = ROOT / f"rafting-50-km-2-jours-{lang}.html"
    page = read(detail)
    for entry in page.select(".rp-price"):
        entry.string = price(2500, lang) + LOCALES[lang][4]
    quote = {"fr": "Prix sur demande", "en": "Price on request",
             "es": "Precio bajo consulta", "ar": "السعر عند الطلب"}[lang]
    for script in page.select("script"):
        if script.string and quote in script.string:
            script.string = script.string.replace(quote, price(2500, lang) + LOCALES[lang][4])
    save(detail, page)


def add_hiking_links(path, base, label):
    page = read(path)
    cards = page.select("#parcours article")
    for card, service in zip(cards, ("hikeSummit", "hikeGorges", "hikeGrand")):
        card.append(link(page, booking_link(base, service), label))
    save(path, page)



def render_reviews_in_both_sections():
    path = ROOT / "google-reviews-live.js"
    script = path.read_text(encoding="utf-8")

    def replace(before, after):
        nonlocal script
        if script.count(before) != 1:
            raise ValueError(f"Google reviews source changed near {before!r}")
        script = script.replace(before, after, 1)

    replace('  const section = document.querySelector(".hp-google-reviews[data-google-place-id]");',
            '  const sections = Array.from(document.querySelectorAll(".hp-google-reviews[data-google-place-id]"));\n'
            '  const [section] = sections;')
    nodes_start = script.index('  const ratingNode')
    nodes_end = script.index('  const key', nodes_start)
    nodes = script[nodes_start:nodes_end]
    replace(nodes, '')
    replace('  if (countNode) countNode.textContent = tx.fallback;',
            '  for (const block of sections) {\n'
            '    const count = block.querySelector(".hp-review-count");\n'
            '    if (count) count.textContent = tx.fallback;\n'
            '  }')
    replace('function carousel(cards)', 'function carousel(cards, section, reviewList)')
    replace('    document.head.appendChild(style);',
            '    if (!document.getElementById("hp-review-carousel-style")) {\n'
            '      style.id = "hp-review-carousel-style";\n'
            '      document.head.appendChild(style);\n'
            '    }')
    replace('  function show(place) {',
            '  function show(place) {\n'
            '    sections.forEach(section => renderSection(place, section));\n'
            '  }\n'
            '  function renderSection(place, section) {\n'
            + ''.join('  ' + line for line in nodes.splitlines(keepends=True)).rstrip())
    replace('      const authorName = author.displayName || "Google Maps";',
            '      const authorName = author.displayName || "Google Maps";\n'
            '      const avatar = node("span", "hp-review-avatar", Array.from(authorName.trim())[0] || "G");\n'
            '      avatar.setAttribute("aria-hidden", "true");\n'
            '      header.appendChild(avatar);')
    replace('      if (r.text) card.appendChild(node("p", "hp-live-review-text", r.text));',
            '      if (r.text) {\n'
            '        const text = node("p", "hp-live-review-text", r.text);\n'
            '        text.dir = "auto";\n'
            '        if (r.text.length > 250) text.tabIndex = 0;\n'
            '        card.appendChild(text);\n'
            '      }')
    replace('    carousel(cards);', '    carousel(cards, section, reviewList);')
    replace('    observer.observe(section);', '    sections.forEach(block => observer.observe(block));')
    path.write_text(script, encoding="utf-8")

def main():
    shutil.copytree(Path(__file__).with_name("review-assets"), ROOT / "review-assets", dirs_exist_ok=True)
    render_reviews_in_both_sections()
    for lang, words in LOCALES.items():
        folder = ROOT / lang
        base = f"/Imsfrane-demo/{lang}/"
        home(folder / "index.html", lang, words)
        for path in (folder / "booking/index.html", folder / "booking.html"):
            booking(path, lang)
        fix_rafting_frames(lang)
        add_hiking_links(folder / "randonnee/index.html", base, words[0])
        destinations = {
            "rafting": "rafting", "gite-atlas": "gite250", "hebergement": "house",
            "vtt": "vtt", "quad": "quadSolo", "kayak": "kayak",
            "rafting/12-km": "raft12", "rafting/30-km": "raft30",
            "rafting/50-km-2-jours": "raft50", "rafting/4-jours-marrakech": "raft4",
        }
        for directory, service in destinations.items():
            path = folder / directory / "index.html"
            if path.is_file():
                add_overview(path, base, lang, words, service)

    js = ROOT / "booking-new.js"
    script = js.read_text(encoding="utf-8")
    marker = "});calculate();"
    assert script.count(marker) == 1
    script = script.replace(marker, """});
const selection = new URLSearchParams(location.search);
const selectedStay = selection.get('stay');
if (Array.from($('stay').options).some(option => option.value === selectedStay)) {
  $('stay').value = selectedStay;
}
const selectedActivity = selection.get('activity');
const activity = Array.from(form.querySelectorAll('[data-service]'))
  .find(input => input.value === selectedActivity);
if (activity) activity.checked = true;
calculate();""")
    js.write_text(script, encoding="utf-8")


if __name__ == "__main__":
    main()
