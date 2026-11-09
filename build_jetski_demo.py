"""Add a localized Jet Ski detail page to the demo mirror."""
from pathlib import Path
import re
from urllib.parse import quote

from bs4 import BeautifulSoup

ROOT = Path("public")
BASE = "/Imsfrane-demo/"
COPY = {
    "fr": (
        "Jet Ski au lac de Bin El Ouidane", "15 min · 300 MAD", "Retour à l’accueil",
        "Une session de jet ski au milieu des montagnes du Haut Atlas.",
        "Comment se déroule la session ?",
        "Retrouvez notre partenaire local au bord du lac. Enfilez votre gilet de sauvetage et écoutez les consignes avant de partir pour 15 minutes sur l’eau.",
        "Rendez-vous directement au lac de Bin El Ouidane. Le point de rencontre et le créneau sont confirmés par WhatsApp.",
        "Réserver sur WhatsApp", "Bonjour, je souhaite réserver une session de jet ski de 15 minutes à Bin El Ouidane.",
    ),
    "en": (
        "Jet Ski on Lake Bin El Ouidane", "15 min · 300 MAD", "Back to home",
        "A jet ski session surrounded by the mountains of the High Atlas.",
        "What to expect",
        "Meet our local partner by the lake. Put on your life jacket and listen to the briefing before heading out for 15 minutes on the water.",
        "Meet directly at Lake Bin El Ouidane. We confirm the meeting point and time on WhatsApp.",
        "Book on WhatsApp", "Hello, I’d like to book a 15-minute jet ski session at Bin El Ouidane.",
    ),
    "es": (
        "Moto de agua en el lago de Bin El Ouidane", "15 min · 300 MAD", "Volver al inicio",
        "Una sesión en moto de agua rodeada de las montañas del Alto Atlas.",
        "Cómo se desarrolla la sesión",
        "Reúnete con nuestro colaborador local junto al lago. Ponte el chaleco salvavidas y escucha las indicaciones antes de salir 15 minutos al agua.",
        "El punto de encuentro está en el lago de Bin El Ouidane. Confirmamos el lugar exacto y la hora por WhatsApp.",
        "Reservar por WhatsApp", "Hola, me gustaría reservar una sesión de moto de agua de 15 minutos en Bin El Ouidane.",
    ),
    "ar": (
        "الدراجات المائية في بحيرة بين الويدان", "<bdi>15</bdi> دقيقة · <bdi>300</bdi> درهم", "العودة إلى الرئيسية",
        "جولة بالدراجة المائية وسط جبال الأطلس الكبير.",
        "كيف تجري الجولة؟",
        "التقِ بشريكنا المحلي على ضفاف البحيرة، وارتدِ سترة النجاة واستمع إلى التعليمات قبل الانطلاق في جولة تستغرق 15 دقيقة على الماء.",
        "اللقاء مباشرةً عند بحيرة بين الويدان. نؤكد نقطة الالتقاء والموعد عبر واتساب.",
        "احجز عبر واتساب", "مرحبًا، أود حجز جولة بالدراجة المائية لمدة 15 دقيقة في بحيرة بين الويدان.",
    ),
}


def build():
    for lang, (title, price, back, intro, heading, session, meeting, booking, message) in COPY.items():
        home_url = f"{BASE}{lang}/"
        detail_url = home_url + "jet-ski/"
        home_path = ROOT / lang / "index.html"
        source = home_path.read_text()
        card = re.search(r'<article\b[^>]*\bhp-jetski\b[^>]*>.*?</article>', source, re.S)
        assert card, f"Jet Ski card missing: {home_path}"
        linked_card, links = re.subn(r'href="https://wa\.me/[^"]+"', f'href="{detail_url}"', card[0])
        assert links == 2, f"Unexpected Jet Ski links: {home_path}"
        linked_card = re.sub(r"<strong>.*?</strong>", f"<strong>{price}</strong>", linked_card, count=1)
        if lang == "ar":
            linked_card = linked_card.replace('aria-label="Jet Ski"', 'aria-label="الدراجات المائية"')

        page = BeautifulSoup(source, "html.parser")
        for element in page.select('link[rel="canonical"], link[rel="alternate"], link[as="image"], meta[property^="og:"], meta[name^="twitter:"], script[type="application/ld+json"]'):
            element.decompose()
        page.title.string = f"{title} | Imsfrane Cathédrale"
        page.select_one('meta[name="description"]')["content"] = intro
        for link in page.select(".atnav-langmini a[href]"):
            for locale in COPY:
                if link["href"].rstrip("/") == f"{BASE}{locale}":
                    link["href"] = f"{BASE}{locale}/jet-ski/"

        style = page.new_tag("style")
        style.string = """
.jet-detail { padding-block: clamp(28px, 5vw, 64px); }
.jet-detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: clamp(22px, 5vw, 64px); align-items: center; }
.jet-detail h1 { font-size: clamp(38px, 5.5vw, 76px); margin-block: 18px; }
.jet-detail h2 { font-size: clamp(26px, 3vw, 40px); margin-block: 24px 10px; }
.jet-detail-price { display: block; font-size: 1.25rem; margin-block: 14px; }
.jet-detail img { display: block; width: 100%; height: auto; aspect-ratio: 4/5; object-fit: cover; border-radius: 18px; }
.jet-detail-back { display: inline-block; margin-block-end: 24px; }
[dir="rtl"] .jet-detail :is(h1,h2) { font-family: Alexandria, Tajawal, sans-serif; letter-spacing: normal; }
@media (max-width: 740px) { .jet-detail-grid { grid-template-columns: 1fr; } .jet-detail img { max-height: 440px; } }
"""
        page.head.append(style)
        main = f"""
<main class="hp-home jet-detail" id="mainContent" dir="{'rtl' if lang == 'ar' else 'ltr'}">
  <div class="hp-container">
    <a class="jet-detail-back" href="{home_url}">{back}</a>
    <div class="jet-detail-grid">
      <div>
        <h1>{title}</h1>
        <p>{intro}</p>
        <strong class="jet-detail-price">{price}</strong>
        <h2>{heading}</h2>
        <p>{session}</p>
        <p>{meeting}</p>
        <a class="hp-button hp-button-dark" href="https://wa.me/212667772551?text={quote(message)}">{booking}</a>
      </div>
      <img src="{BASE}images/optimized/jetski-lake-800.avif" alt="{title}" width="800" height="1066" fetchpriority="high">
    </div>
  </div>
</main>"""
        page.main.replace_with(BeautifulSoup(main, "html.parser").main)
        detail_path = ROOT / lang / "jet-ski" / "index.html"
        detail_path.parent.mkdir(exist_ok=True)
        detail_path.write_text(str(page))
        home_path.write_text(source[:card.start()] + linked_card + source[card.end():])


if __name__ == "__main__":
    build()
