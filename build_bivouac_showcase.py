"""Add the new field-photo bivouac story to Demo kayak and rafting pages."""

from pathlib import Path


STYLE = r"""
<style id="imsfrane-bivouac-showcase-css">
.ib-bivouac{background:#0a2825;color:#fff;padding:88px 0;overflow:hidden;position:relative}
.ib-bivouac:before{content:"";position:absolute;width:520px;height:520px;border:1px solid rgba(220,190,112,.15);border-radius:50%;right:-260px;top:-220px}
.ib-shell{width:min(1180px,calc(100% - 40px));margin:auto;display:grid;grid-template-columns:minmax(280px,.78fr) minmax(0,1.22fr);gap:64px;align-items:center;position:relative}
.ib-copy{max-width:475px}
.ib-kicker{color:#dfbf70;font-size:10px;font-weight:800;letter-spacing:.22em;text-transform:uppercase;margin-bottom:18px}
.ib-title{color:#fff;font:600 clamp(42px,5vw,69px)/.98 "Cormorant Garamond",Georgia,serif;margin:0 0 22px;letter-spacing:-.025em}
.ib-copy>p{color:#c8d6d2;font-size:14px;line-height:1.9;margin:0 0 26px}
.ib-points{display:flex;flex-wrap:wrap;gap:9px}
.ib-points span{border:1px solid rgba(233,210,151,.35);border-radius:999px;padding:9px 13px;color:#f0dfb0;font-size:10px;font-weight:700;letter-spacing:.04em}
.ib-mosaic{display:grid;grid-template-columns:1.08fr .92fr;grid-template-rows:220px 220px;gap:12px;min-width:0}
.ib-card{position:relative;overflow:hidden;border-radius:10px;background:#173a35;min-height:0;margin:0}
.ib-card:first-child{grid-row:1/3}
.ib-card:last-child{display:none}
.ib-card img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .7s ease}
.ib-card:first-child img{object-position:center 64%}
.ib-card:hover img{transform:scale(1.025)}
.ib-card:after{content:"";position:absolute;inset:auto 0 0;height:45%;background:linear-gradient(transparent,rgba(3,18,16,.82))}
.ib-card figcaption{position:absolute;z-index:1;left:17px;right:17px;bottom:14px;color:#fff;font-size:11px;font-weight:700;line-height:1.35;text-shadow:0 1px 8px #000}
[dir="rtl"] .ib-copy{text-align:right}
[dir="rtl"] .ib-card figcaption{left:17px;right:17px;text-align:right}
@media(max-width:820px){.ib-bivouac{padding:66px 0}.ib-shell{grid-template-columns:1fr;gap:34px}.ib-copy{max-width:650px}.ib-mosaic{grid-template-rows:260px 260px}}
@media(max-width:560px){.ib-bivouac{padding:54px 0}.ib-shell{width:min(100% - 28px,1180px);gap:27px}.ib-title{font-size:46px}.ib-copy>p{font-size:13px}.ib-mosaic{grid-template-columns:1.04fr .96fr;grid-template-rows:195px 195px;gap:8px}.ib-card{border-radius:7px}.ib-card figcaption{font-size:9px;left:10px;right:10px;bottom:10px}.ib-points{gap:7px}.ib-points span{font-size:9px;padding:8px 10px}}
</style>
""".strip()


COPY = {
    "fr": {
        "kicker": "BIVOUAC AU BORD DE L’EAU",
        "title": "La rivière le jour.<br>Le camp le soir.",
        "kayak": "Pour les expéditions de plusieurs jours, l’aventure continue après la navigation : bivouac installé, repas préparés au bord de l’Ahansal et soirée partagée sous les montagnes.",
        "rafting": "Dans l’expédition de deux jours, le bivouac fait pleinement partie de l’expérience : un camp au bord de l’Ahansal, des repas locaux et une soirée partagée avant de reprendre la rivière.",
        "points": ["Tentes installées", "Repas locaux", "Organisation sur mesure"],
        "labels": ["Nuit en bivouac", "Repas au bord de l’Ahansal", "Camp de groupe", "Dîner partagé"],
        "alts": ["Bivouac de nuit sous les montagnes", "Préparation d’un repas au bord de l’Ahansal", "Camp de groupe dans l’Atlas", "Dîner collectif au bivouac"],
    },
    "en": {
        "kicker": "RIVERSIDE BIVOUAC",
        "title": "The river by day.<br>The camp by night.",
        "kayak": "On multi-day expeditions, the adventure continues after paddling: a prepared bivouac, meals by the Ahansal and an evening together beneath the mountains.",
        "rafting": "On the two-day expedition, the bivouac is part of the experience: a camp beside the Ahansal, local meals and an evening together before returning to the river.",
        "points": ["Tents prepared", "Local meals", "Tailored logistics"],
        "labels": ["Night at camp", "Meal beside the Ahansal", "Group camp", "Dinner together"],
        "alts": ["Night bivouac beneath the mountains", "Preparing a meal beside the Ahansal", "Group camp in the Atlas", "Shared dinner at the bivouac"],
    },
    "es": {
        "kicker": "VIVAC JUNTO AL RÍO",
        "title": "El río de día.<br>El campamento de noche.",
        "kayak": "En las expediciones de varios días, la aventura continúa después de remar: vivac preparado, comidas junto al Ahansal y una velada compartida bajo las montañas.",
        "rafting": "En la expedición de dos días, el vivac forma parte de la experiencia: campamento junto al Ahansal, comidas locales y una velada compartida antes de volver al río.",
        "points": ["Tiendas preparadas", "Comidas locales", "Logística a medida"],
        "labels": ["Noche de vivac", "Comida junto al Ahansal", "Campamento de grupo", "Cena compartida"],
        "alts": ["Vivac nocturno bajo las montañas", "Preparación de comida junto al Ahansal", "Campamento de grupo en el Atlas", "Cena compartida en el vivac"],
    },
    "ar": {
        "kicker": "مخيم على ضفة النهر",
        "title": "النهر نهاراً.<br>والمخيم مساءً.",
        "kayak": "في رحلات الكاياك لعدة أيام، تستمر المغامرة بعد التجديف: مخيم مجهز، ووجبات على ضفة نهر أحنصال، وأمسية مشتركة بين جبال الأطلس.",
        "rafting": "في رحلة الرافتينغ ليومين، يشكل المخيم جزءاً من التجربة: إقامة على ضفة أحنصال، ووجبات محلية، وأمسية مشتركة قبل العودة إلى النهر.",
        "points": ["خيام مجهزة", "وجبات محلية", "تنظيم حسب الطلب"],
        "labels": ["ليلة في المخيم", "وجبة على ضفة أحنصال", "مخيم جماعي", "عشاء مشترك"],
        "alts": ["مخيم ليلي بين الجبال", "تحضير وجبة على ضفة نهر أحنصال", "مخيم جماعي في الأطلس", "عشاء جماعي في المخيم"],
    },
}


IMAGES = [
    ("IMG_bivouac-night.webp", 1050, 1400),
    ("IMG_bivouac-river-meal.webp", 825, 1100),
    ("IMG_bivouac-day.webp", 1100, 825),
    ("IMG_bivouac-dinner.webp", 1400, 1050),
]


def section(lang: str, kind: str) -> str:
    copy = COPY[lang]
    cards = []
    for (filename, width, height), label, alt in zip(IMAGES, copy["labels"], copy["alts"]):
        cards.append(
            f'<figure class="ib-card"><img src="/Imsfrane-demo/images/{filename}" '
            f'width="{width}" height="{height}" loading="lazy" decoding="async" alt="{alt}">'
            f'<figcaption>{label}</figcaption></figure>'
        )
    points = "".join(f"<span>{point}</span>" for point in copy["points"])
    return (
        f'\n<section class="ib-bivouac" id="bivouac-experience" aria-labelledby="ib-title-{kind}-{lang}">'
        f'<div class="ib-shell"><div class="ib-copy"><div class="ib-kicker">{copy["kicker"]}</div>'
        f'<h2 class="ib-title" id="ib-title-{kind}-{lang}">{copy["title"]}</h2>'
        f'<p>{copy[kind]}</p><div class="ib-points">{points}</div></div>'
        f'<div class="ib-mosaic">{"".join(cards)}</div></div></section>\n'
    )


def patch_page(path: Path, lang: str, kind: str, marker: str) -> None:
    html = path.read_text(encoding="utf-8")
    if "imsfrane-bivouac-showcase-css" in html:
        return
    if "</head>" not in html or marker not in html:
        raise RuntimeError(f"Required marker missing in {path}")
    html = html.replace("</head>", STYLE + "\n</head>", 1)
    html = html.replace(marker, section(lang, kind) + marker, 1)
    path.write_text(html, encoding="utf-8")


def build(root: Path) -> None:
    for lang in ("fr", "en", "es", "ar"):
        kayak = root / lang / "kayak" / "index.html"
        patch_page(kayak, lang, "kayak", '<section class="ky-section ky-gallery-section"')

    rafting_pages = {
        "fr": root / "rafting-content.html",
        "en": root / "rafting-content-en.html",
        "es": root / "rafting-content-es.html",
        "ar": root / "rafting-content-ar.html",
    }
    for lang, path in rafting_pages.items():
        patch_page(path, lang, "rafting", '<section aria-labelledby="gallery-title"')

    print("Bivouac showcase installed on 4 kayak and 4 rafting experiences")


if __name__ == "__main__":
    build(Path("public"))
