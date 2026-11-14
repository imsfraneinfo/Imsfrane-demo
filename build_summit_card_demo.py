"""Show equally sized photos on the demo's hiking cards."""
from html import escape
from pathlib import Path
import re
import shutil


SOURCE = Path(__file__).resolve().parent
PHOTOS = ('summit-sign.webp', 'summit-trail.webp', 'summit-altitude.webp')
SUMMIT_ALT = {
    'fr': ('Deux randonneuses au sommet de Msfrane', 'Groupe sur le sentier du sommet', 'Randonneur près du panneau à 1 868 m'),
    'en': ('Two hikers at the Msfrane summit', 'Group on the summit trail', 'Hiker beside the 1,868 m sign'),
    'es': ('Dos senderistas en la cima de Msfrane', 'Grupo en el sendero de la cima', 'Senderista junto al cartel de 1.868 m'),
    'ar': ('متنزّهتان على قمة مسفران', 'مجموعة على مسار القمة', 'متنزّه بجانب لافتة الارتفاع ١٨٦٨ مترًا'),
}
GORGES_PHOTOS = ('waterfall.webp', 'river-gorge.webp', 'narrow-gorge.webp')
GORGES_ALT = {
    'fr': ('Cascade et bassin naturel', 'L’Oued Ahansal au pied des falaises', 'Passage étroit des gorges de l’Ahansal'),
    'en': ('Waterfall and natural pool', 'The Ahansal River below the cliffs', 'Narrow passage in the Ahansal gorges'),
    'es': ('Cascada y poza natural', 'El río Ahansal al pie de los acantilados', 'Paso estrecho de las gargantas del Ahansal'),
    'ar': ('شلال وبركة طبيعية', 'واد أحنصال عند سفح الجروف', 'ممر ضيق في مضايق أحنصال'),
}
CARDS = (
    ('summit-card', 'rando-IMG_7453.webp', PHOTOS, SUMMIT_ALT),
    ('gorges-card', 'rando-IMG_6269.webp', GORGES_PHOTOS, GORGES_ALT),
)
STYLES = """
<style>
.rando .card .hiking-card-photos {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 3px;
}
.rando .card .hiking-card-photos img {
  display: block;
  width: 100%;
  height: auto;
  aspect-ratio: 3 / 4;
}
</style>
"""


def build(root):
    for card, _, photos, _ in CARDS:
        target = root / 'images' / card
        target.mkdir(parents=True, exist_ok=True)
        for photo in photos:
            shutil.copyfile(SOURCE / f'{card}-assets' / photo, target / photo)

    for lang in SUMMIT_ALT:
        page = root / lang / 'randonnee' / 'index.html'
        html = page.read_text(encoding='utf-8')
        updated = html
        for card, original, photos, labels in CARDS:
            if f'{card}-photos hiking-card-photos' in updated:
                continue
            images = ''.join(
                f'<img src="/Imsfrane-demo/images/{card}/{photo}" alt="{escape(label)}" '
                'width="600" height="800" loading="lazy" decoding="async">'
                for photo, label in zip(photos, labels[lang])
            )
            gallery = f'<div class="{card}-photos hiking-card-photos">{images}</div>'
            pattern = rf'(<article class="card">\s*)<img\b[^>]*\bsrc="[^"]*/{re.escape(original)}"[^>]*>'
            updated, count = re.subn(pattern, lambda match: match[1] + gallery, updated)
            if count != 1:
                raise ValueError(f'Expected one {card} in {page}, found {count}')
        if updated != html:
            page.write_text(updated.replace('</head>', STYLES + '</head>', 1), encoding='utf-8')
