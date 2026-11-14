"""Show three equally sized photos on the demo's Msfrane summit card."""
from html import escape
from pathlib import Path
import re
import shutil


ASSETS = Path(__file__).resolve().parent / 'summit-card-assets'
PHOTOS = ('summit-sign.webp', 'summit-trail.webp', 'summit-altitude.webp')
ALT = {
    'fr': ('Deux randonneuses au sommet de Msfrane', 'Groupe sur le sentier du sommet', 'Randonneur près du panneau à 1 868 m'),
    'en': ('Two hikers at the Msfrane summit', 'Group on the summit trail', 'Hiker beside the 1,868 m sign'),
    'es': ('Dos senderistas en la cima de Msfrane', 'Grupo en el sendero de la cima', 'Senderista junto al cartel de 1.868 m'),
    'ar': ('متنزّهتان على قمة مسفران', 'مجموعة على مسار القمة', 'متنزّه بجانب لافتة الارتفاع ١٨٦٨ مترًا'),
}
SUMMIT_IMAGE = re.compile(r'(<article class="card">\s*)<img\b[^>]*\bsrc="[^"]*/rando-IMG_7453\.webp"[^>]*>')
STYLES = """
<style>
.rando .card .summit-card-photos {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 3px;
}
.rando .card .summit-card-photos img {
  display: block;
  width: 100%;
  height: auto;
  aspect-ratio: 3 / 4;
}
</style>
"""


def build(root):
    target = root / 'images' / 'summit-card'
    target.mkdir(parents=True, exist_ok=True)
    for photo in PHOTOS:
        shutil.copyfile(ASSETS / photo, target / photo)

    for lang, labels in ALT.items():
        page = root / lang / 'randonnee' / 'index.html'
        html = page.read_text(encoding='utf-8')
        if 'class="summit-card-photos"' in html:
            continue
        images = ''.join(
            f'<img src="/Imsfrane-demo/images/summit-card/{photo}" alt="{escape(label)}" '
            'width="600" height="800" loading="lazy" decoding="async">'
            for photo, label in zip(PHOTOS, labels)
        )
        gallery = f'<div class="summit-card-photos">{images}</div>'
        updated, count = SUMMIT_IMAGE.subn(lambda match: match[1] + gallery, html)
        if count != 1:
            raise ValueError(f'Expected one summit card in {page}, found {count}')
        page.write_text(updated.replace('</head>', STYLES + '</head>', 1), encoding='utf-8')
