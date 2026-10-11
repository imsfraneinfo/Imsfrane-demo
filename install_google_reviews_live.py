"""Attach Google's live Place reviews to Demo homepage in 4 languages.

No fabricated reviews or old fixed review count. No changes to imsfrane.com.
The browser key is injected only into GitHub Pages output and must be
restricted in Google Cloud to the Demo Pages HTTP referrer + Maps JS API.
"""
import json
import os
import re
from pathlib import Path

PLACE_ID = "ChIJGfO-zLRxow0RFtfhVkfxEmU"
OLD_ID = "ChIJGf0-zLRxow0RFtfhVkfxEmU"
LANG = {"fr":"Voir les avis Google", "en":"See Google reviews",
        "ar":"شاهد تقييمات Google", "es":"Ver reseñas en Google"}


def install(root: Path):
    key = os.getenv("GOOGLE_MAPS_BROWSER_KEY", "").strip()
    if key and not re.fullmatch(r"[A-Za-z0-9_-]{15,256}", key):
        raise RuntimeError("GOOGLE_MAPS_BROWSER_KEY is malformed")
    for code, fallback in LANG.items():
        file = root / code / "index.html"
        html = file.read_text(encoding="utf-8")
        section = re.search(r'<section\b[^>]*\bclass="hp-google-reviews"[^>]*>[\s\S]*?</section>', html)
        if not section:
            raise RuntimeError("Missing exact Google review section: " + str(file))
        old = section.group(0)
        if "data-google-place-id" in old:
            raise RuntimeError("Google review integration inserted twice: " + str(file))
        updated = re.sub(
            r'<section\b[^>]*\bclass="hp-google-reviews"[^>]*>',
            lambda m: m.group(0)[:-1] + ' data-google-place-id="' + PLACE_ID + '">',
            old, count=1)
        updated, scores = re.subn(
            r'<div class="hp-google-score">[\s\S]*?</div>',
            '<div class="hp-google-score"><strong class="hp-google-rating-number" hidden></strong>'
            '<span class="hp-google-stars" aria-hidden="true" hidden></span></div>',
            updated, count=1)
        updated, counts = re.subn(
            r'<span class="hp-review-count">[\s\S]*?</span>',
            '<span class="hp-review-count" aria-live="polite">' + fallback + '</span>',
            updated, count=1)
        if scores != 1 or counts != 1:
            raise RuntimeError("Google review summary structure changed: " + str(file))
        updated = updated.replace(
            '</section>',
            '<div class="hp-live-review-list" aria-label="Google Maps reviews" hidden></div></section>', 1)
        html = html.replace(old, updated, 1)
        html = html.replace(OLD_ID, PLACE_ID)
        if html.count('href="../google-reviews-live.css"') or html.count('src="../google-reviews-live.js"'):
            raise RuntimeError("Live reviews already installed: " + str(file))
        css = '<link rel="stylesheet" href="../google-reviews-live.css?v=20261011-debug3">'
        scripts = ''
        if key:
            # This browser key is visible to site visitors by design; protect with
            # HTTP referrer and Maps JavaScript API restrictions in Google Cloud.
            scripts = '<script>window.IMSFRANE_GOOGLE_MAPS_KEY=' + json.dumps(key) + ';</script>'
        scripts += '<script defer src="../google-reviews-live.js?v=20261011-debug3"></script>'
        html = html.replace('</head>', css + '</head>', 1)
        html = html.replace('</body>', scripts + '</body>', 1)
        file.write_text(html, encoding="utf-8")
        print('[GOOGLE REVIEWS]', code, 'configured' if key else 'awaiting restricted browser API key')
    for name in ('google-reviews-live.js', 'google-reviews-live.css'):
        src = Path(name)
        if not src.is_file():
            raise RuntimeError('Missing Demo-only reviews asset: ' + name)
        (root / name).write_bytes(src.read_bytes())


if __name__ == "__main__":
    install(Path("public"))
