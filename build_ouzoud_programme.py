"""Add the Ouzoud day trip to the four localized demo programme pages."""
import json
from html import escape
from pathlib import Path
from shutil import copytree
from urllib.parse import urlencode, urlsplit

from bs4 import BeautifulSoup

SOURCE = Path(__file__).resolve().parent
SLUG = "ouzoud"
def render(data, prefix, programme, whatsapp):
    assets = prefix + "ouzoud-assets/"
    e = escape
    stage_photos = ("viewpoint", "boat", "basin", "macaque")

    def photo(name, label, eager=False):
        width, height = 760, 1013
        priority = 'fetchpriority="high"' if eager else 'loading="lazy"'
        return (f'<img src="{assets}{name}.webp" width="{width}" height="{height}" '
                f'alt="{e(label)}" {priority} decoding="async">')

    stages = []
    for (title, body), name, label in zip(data["stages"], stage_photos, data["stage_photos"], strict=True):
        if name == "macaque":
            photos = "".join(
                f'<img src="{assets}{file}.jpg" width="{width}" height="1536" '
                f'alt="{e(caption)}" loading="lazy" decoding="async">'
                for (file, width), caption in zip(
                    (("macaque-young", 898), ("macaque-adult", 888)), data["macaque_photos"], strict=True
                )
            )
            photo_class = "pair oz-macaque-pair"
        else:
            photos = photo(name, label)
            photo_class = "single"
        stages.append(
            f'<section class="rp-twelve-step"><div class="container">'
            f'<h2 class="heading">{e(title)}</h2>'
            f'<div class="rp-step-photos {photo_class}">{photos}</div>'
            f'<div class="rp-step-copy"><p>{e(body)}</p></div></div></section>'
        )
    hero_photos = "".join(
        f'<div class="shot{" main" if index == 0 else ""}">{photo(name, label, index == 0)}</div>'
        for index, (name, label) in enumerate((
            ("falls", data["photos"][1]), ("viewpoint", data["stage_photos"][0]),
            ("boat", data["stage_photos"][1]),
        ))
    )
    gallery = "".join(photo(name, data["photos"][1]) for name in ("walk", "falls", "terraces"))
    button = (f'<a class="btn btn-gold" href="{e(whatsapp)}" target="_blank" rel="noopener noreferrer">'
              f'{e(data["ask"])}</a>')
    return f"""
    <main>
      <section class="hero">
        <div class="hero-main">
          <div class="hero-copy">
            <div class="topline"><a href="{programme}" target="_parent">{e(data["back"])}</a></div>
            <h1>{e(data["title"])}</h1>
            <p class="hero-summary">{e(data["intro"])}</p>
            <div class="hero-acts">{button}</div>
          </div>
          <div class="hero-media">{hero_photos}</div>
        </div>
      </section>
      <section class="section rp-section-note"><div class="container">
        <h2 class="heading">{e(data["schedule"])}</h2><p>{e(data["meet"])}</p>
      </div></section>
      {''.join(stages)}
      <section class="rp-gallery"><div class="container">
        <h2 class="heading">{e(data["gallery"])}</h2>
        <div class="rp-gallery-grid">{gallery}</div>
      </div></section>
      <section class="section booking-section"><div class="container">{button}</div></section>
    </main>"""


def build(root, prefix):
    data_by_language = json.loads((SOURCE / "ouzoud-programme.json").read_text(encoding="utf-8"))
    copytree(SOURCE / "ouzoud-assets", root / "ouzoud-assets", dirs_exist_ok=True)
    origin = "https://imsfraneinfo.github.io"
    for lang, data in data_by_language.items():
        programme = f"{prefix}{lang}/programme/"
        detail = f"{programme}{SLUG}/"
        source = root / lang / "programme/index.html"
        listing = BeautifulSoup(source.read_text(encoding="utf-8"), "html.parser")
        listing.head.append(listing.new_tag("link", rel="stylesheet", href=prefix + "ouzoud-assets/programme.css?v=ouzoud2"))
        page = BeautifulSoup(str(listing), "html.parser")
        phone = next(a["href"].split("?")[0] for a in listing.select('a[href^="https://wa.me/"]'))
        message = f'{data["title"]}\n{data["date"]}: …\n{data["guests"]}: …'
        whatsapp = phone + "?" + urlencode({"text": message})
        embed_name = f"ouzoud-{lang}.html"
        template = root / f"rafting-12-km-{lang}.html"
        embed = BeautifulSoup(template.read_text(encoding="utf-8"), "html.parser")
        embed.main.replace_with(BeautifulSoup(render(data, prefix, programme, whatsapp), "html.parser"))
        embed.title.string = data["title"]
        style = embed.new_tag("style")
        style.string = (
            ".rp-twelve-step .rp-step-photos.oz-macaque-pair"
            "{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));align-items:start}"
            ".rp-twelve-step .rp-step-photos.oz-macaque-pair img"
            "{width:100%;height:auto;aspect-ratio:auto;object-fit:contain}"
        )
        embed.head.append(style)
        for script in embed.select("script"):
            script.decompose()
        for preload in embed.select('link[rel="preload"][as="image"]'):
            preload.decompose()
        (root / embed_name).write_text(str(embed), encoding="utf-8")

        main = page.new_tag("main", id="mainContent")
        iframe = page.new_tag("iframe", id="ouzoudFrame", src=f"{prefix}{embed_name}?v=macaque-pair1",
                              title=data["title"], style="display:block;width:100%;height:1800px;border:0")
        main.append(iframe)
        page.main.replace_with(main)
        resize = page.new_tag("script")
        resize.string = """(() => {
  const frame = document.getElementById('ouzoudFrame');
  frame.addEventListener('load', () => {
    const main = frame.contentDocument.querySelector('main');
    if (!main) return;
    const fit = () => { frame.style.height = Math.ceil(main.getBoundingClientRect().height) + 'px'; };
    new ResizeObserver(fit).observe(main);
    fit();
  });
})();"""
        page.body.append(resize)
        for anchor in page.select('a[href^="https://wa.me/"], a[href^="https://api.whatsapp.com/"]'):
            anchor["href"] = whatsapp
        page.html["dir"] = "rtl" if lang == "ar" else "ltr"
        page.title.string = data["title"] + " | ICHOU ADVENTURES"
        for tag in page.select('script[type="application/ld+json"], link[rel="preload"][as="image"], link[rel="canonical"], link[hreflang], meta[property^="og:image:"], meta[name="twitter:image:alt"]'):
            tag.decompose()
        page.head.append(page.new_tag("link", rel="canonical", href=origin + detail))
        for code in data_by_language:
            translated = f"{prefix}{code}/programme/{SLUG}/"
            page.head.append(page.new_tag("link", rel="alternate", hreflang=code, href=origin + translated))
        for anchor in page.select("a[lang][href], a[hreflang][href], a[data-lang][href]"):
            href = urlsplit(anchor["href"])
            for code in data_by_language:
                if href.path == f"{prefix}{code}/programme/":
                    anchor["href"] = f"{prefix}{code}/programme/{SLUG}/"
        meta_values = {
            "description": data["intro"], "og:description": data["intro"], "twitter:description": data["intro"],
            "og:title": data["title"], "twitter:title": data["title"],
            "og:image": origin + prefix + "ouzoud-assets/falls.webp",
            "twitter:image": origin + prefix + "ouzoud-assets/falls.webp", "og:url": origin + detail,
        }
        for key, value in meta_values.items():
            attr = "property" if key.startswith("og:") else "name"
            node = page.find("meta", attrs={attr: key})
            if node is None:
                node = page.new_tag("meta", attrs={attr: key})
                page.head.append(node)
            node["content"] = value
        robots = page.find("meta", attrs={"name": "robots"})
        if robots is None:
            robots = page.new_tag("meta", attrs={"name": "robots"})
            page.head.append(robots)
        robots["content"] = "noindex,follow"
        target = source.parent / SLUG / "index.html"
        target.parent.mkdir(exist_ok=True)
        target.write_text(str(page), encoding="utf-8")
        legacy = source.parent / "ouzoud-tanaghmelt"
        legacy.mkdir(exist_ok=True)
        (legacy / "index.html").write_text(
            f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8">'
            f'<meta name="robots" content="noindex"><link rel="canonical" href="{origin}{detail}">'
            f'<meta http-equiv="refresh" content="0;url={detail}"><title>{escape(data["title"])}</title>'
            f'</head><body><a href="{detail}">{escape(data["title"])}</a></body></html>',
            encoding="utf-8",
        )

        e = escape
        card = f'''
        <section class="wk-wrap oz-programme-list">
          <article class="oz-card">
            <a href="{detail}" class="oz-card-image" aria-label="{e(data["title"])}">
              <img src="{prefix}ouzoud-assets/falls.webp" width="760" height="1013" alt="{e(data["photos"][1])}" loading="lazy" decoding="async">
            </a>
            <div class="oz-card-body">
              <p class="oz-meta">{e(data["day"])}</p>
              <h2><a href="{detail}">{e(data["title"])}</a></h2>
              <p>{e(data["intro"])}</p>
              <a class="oz-button" href="{detail}">{e(data["open"])}</a>
            </div>
          </article>
        </section>'''
        listing.main.select_one(".wk-hero").insert_after(BeautifulSoup(card, "html.parser"))
        source.write_text(str(listing), encoding="utf-8")

        home_path = root / lang / "index.html"
        home = BeautifulSoup(home_path.read_text(encoding="utf-8"), "html.parser")
        more = home.select_one("details.ims-more")
        grid = more.find_previous_sibling(class_="hp-activity-grid") if more else None
        if grid is None:
            grid = home.select_one(".hp-activity-grid")
        if grid is None:
            raise ValueError(f"Homepage activity grid missing: {home_path}")
        home_card = f"""
        <article class="hp-activity-card hp-ouzoud">
          <a class="hp-activity-image" href="{detail}" aria-label="{e(data["title"])}">
            <img src="{prefix}ouzoud-assets/falls.webp" width="760" height="1013"
                 alt="{e(data["photos"][1])}" loading="lazy" decoding="async">
          </a>
          <div class="hp-activity-body">
            <div class="hp-activity-location"><i class="fa-solid fa-location-dot" aria-hidden="true"></i>
              <span>{'أوزود' if lang == 'ar' else 'Ouzoud'}</span>
            </div>
            <h3>{e(data["title"])}</h3>
            <p>{e(data["intro"])}</p>
            <div class="hp-activity-bottom"><a href="{detail}"><span>{e(data["open"])}</span></a></div>
          </div>
        </article>"""
        grid.append(BeautifulSoup(home_card, "html.parser"))
        home_path.write_text(str(home), encoding="utf-8")
