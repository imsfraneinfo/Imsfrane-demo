"""Deploy the approved booking design to the localized demo booking routes only."""
from pathlib import Path
import re
import sys

def build(root: Path):
    template = (Path(__file__).resolve().parent / 'booking-premium.html').read_text(encoding='utf-8')
    # Keep the existing navigation URLs working, including /fr/booking/ and /fr/booking.html.
    for lang in ('fr', 'en', 'es', 'ar'):
        html = template.replace('<html lang="fr">', f'<html lang="{lang}" dir="{"rtl" if lang == "ar" else "ltr"}">', 1)
        html = html.replace('let lang=new URLSearchParams(location.search).get("lang")||"fr";',
                            f'let lang=new URLSearchParams(location.search).get("lang")||"{lang}";', 1)
        html = html.replace('<option value="'+lang+'">', '<option value="'+lang+'">')
        destination = root / lang / 'booking' / 'index.html'
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(html, encoding='utf-8')
        (root / lang / 'booking.html').write_text(html, encoding='utf-8')
    (root / 'booking-premium.html').write_text(template, encoding='utf-8')
    print('Premium booking applied to FR/EN/ES/AR demo booking URLs; official site untouched.')

if __name__ == '__main__':
    build(Path(sys.argv[1] if len(sys.argv) > 1 else 'public'))
