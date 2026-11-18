"""Add the Ouzoud day trip to the four localized demo programme pages."""
import json
from html import escape
from pathlib import Path
from shutil import copytree
from urllib.parse import urlencode, urlsplit

from bs4 import BeautifulSoup

SOURCE = Path(__file__).resolve().parent
SLUG = "ouzoud-tanaghmelt"
TIMES = ("09:30", "10:00", "11:30", "13:00", "14:30", "16:30")
CREDITS = (
    ("Anas Souir", "شلالات_أوزود_الساحرة.jpg", "4.0"),
    ("Mohamed Bourazza", "Cascades_d%27ouzoud.jpg", "4.0"),
    ("Arnaud 25", "Cascades_d%27Ouzoud_023.JPG", "3.0"),
)


def render(data, prefix, programme, whatsapp):
    assets = prefix + "ouzoud-assets/"
    e = escape
    stages = "".join(
        f'<li><time datetime="{time}" dir="ltr">{time}</time>'
        f'<div><h3>{e(title)}</h3><p>{e(body)}</p></div></li>'
        for time, (title, body) in zip(TIMES, data["stages"], strict=True)
    )
    gallery = "".join(
        f'<figure><img src="{assets}{name}.webp" width="{width}" height="{height}" '
        f'alt="{e(label)}" loading="lazy" decoding="async"><figcaption>{e(label)}</figcaption></figure>'
        for (name, width, height), label in zip(
            (("falls", 640, 853), ("olives", 720, 540)), data["photos"][1:], strict=True
        )
    )
    credits = " · ".join(
        f'<a href="https://commons.wikimedia.org/wiki/File:{e(file)}">{e(author)}</a> '
        f'(<a href="https://creativecommons.org/licenses/by-sa/{version}/">CC BY-SA {version}</a>)'
        for author, file, version in CREDITS
    )
    button = (
        f'<a class="oz-button" href="{e(whatsapp)}" target="_blank" rel="noopener noreferrer">'
        f'{e(data["ask"])}</a>'
    )
    return f'''
    <main id="mainContent" class="oz-main">
      <picture class="oz-hero">
        <source media="(max-width: 700px)" srcset="{assets}hero-mobile.webp" width="780" height="522">
        <img src="{assets}hero.webp" width="1600" height="1071" alt="{e(data["photos"][0])}" fetchpriority="high">
      </picture>
      <div class="oz-wrap">
        <header class="oz-intro">
          <a class="oz-back" href="{programme}">{e(data["back"])}</a>
          <p class="oz-meta">{e(data["day"])} · <bdi dir="ltr">09:30–16:30</bdi> · {e(data["meet"])}</p>
          <h1>{e(data["title"])}</h1>
          <p>{e(data["intro"])}</p>
          {button}
        </header>
        <section class="oz-section">
          <h2>{e(data["schedule"])}</h2>
          <ol class="oz-timeline">{stages}</ol>
        </section>
        <section class="oz-section">
          <h2>{e(data["gallery"])}</h2>
          <div class="oz-gallery">{gallery}</div>
          <p class="oz-credits">{e(data["credits"])}<br>{credits}</p>
        </section>
        <div class="oz-final">{button}</div>
      </div>
    </main>'''


def build(root, prefix):
    data_by_language = json.loads((SOURCE / "ouzoud-programme.json").read_text(encoding="utf-8"))
    copytree(SOURCE / "ouzoud-assets", root / "ouzoud-assets", dirs_exist_ok=True)
    origin = "https://imsfraneinfo.github.io"
    for lang, data in data_by_language.items():
        programme = f"{prefix}{lang}/programme/"
        detail = f"{programme}{SLUG}/"
        source = root / lang / "programme/index.html"
        listing = BeautifulSoup(source.read_text(encoding="utf-8"), "html.parser")
        listing.head.append(listing.new_tag("link", rel="stylesheet", href=prefix + "ouzoud-assets/programme.css"))
        page = BeautifulSoup(str(listing), "html.parser")
        phone = next(a["href"].split("?")[0] for a in listing.select('a[href^="https://wa.me/"]'))
        message = f'{data["title"]}\n{data["date"]}: …\n{data["guests"]}: …'
        whatsapp = phone + "?" + urlencode({"text": message})
        page.main.replace_with(BeautifulSoup(render(data, prefix, programme, whatsapp), "html.parser"))
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
            "og:image": origin + prefix + "ouzoud-assets/hero.webp",
            "twitter:image": origin + prefix + "ouzoud-assets/hero.webp", "og:url": origin + detail,
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

        e = escape
        card = f'''
        <section class="wk-wrap oz-programme-list">
          <article class="oz-card">
            <a href="{detail}" class="oz-card-image" aria-label="{e(data["title"])}">
              <img src="{prefix}ouzoud-assets/hero-mobile.webp" width="780" height="522" alt="{e(data["photos"][0])}" loading="lazy" decoding="async">
            </a>
            <div class="oz-card-body">
              <p class="oz-meta">{e(data["day"])} · <bdi dir="ltr">09:30–16:30</bdi></p>
              <h2><a href="{detail}">{e(data["title"])}</a></h2>
              <p>{e(data["intro"])}</p>
              <a class="oz-button" href="{detail}">{e(data["open"])}</a>
            </div>
          </article>
        </section>'''
        listing.main.select_one(".wk-hero").insert_after(BeautifulSoup(card, "html.parser"))
        source.write_text(str(listing), encoding="utf-8")
