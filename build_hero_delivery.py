"""Prioritize the visible hero photos in the generated website."""
from io import BytesIO
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup
from PIL import Image


def image_path(root, url):
    parsed = urlsplit(url)
    if parsed.netloc or parsed.scheme or not parsed.path.startswith('/'):
        return None
    path = unquote(parsed.path).removeprefix('/Imsfrane-demo/').lstrip('/')
    return root / path


def compress_image(path, format, quality, max_size=None):
    original_size = path.stat().st_size
    with Image.open(path) as image:
        if max_size:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        compressed = BytesIO()
        image.save(compressed, format, quality=quality, icc_profile=image.info.get('icc_profile'))
    if compressed.tell() < original_size:
        print(f'{path.name}: {original_size} → {compressed.tell()} bytes')
        path.write_bytes(compressed.getvalue())


def compress_hero_images(root):
    for path in (root / 'images/clarity').glob('hero-*.avif'):
        compress_image(path, 'AVIF', quality=62)
    for filename in ('rando-IMG_6167.webp', 'rando-IMG_7453.webp', 'rando-IMG_6269.webp'):
        path = root / 'images' / filename
        if path.is_file():
            compress_image(path, 'WEBP', quality=81, max_size=(1080, 1440))


SLIDER_LABELS = {
    'ar': ('الصورة السابقة', 'الصورة التالية'),
    'en': ('Previous photo', 'Next photo'),
    'es': ('Foto anterior', 'Foto siguiente'),
    'fr': ('Photo précédente', 'Photo suivante'),
}
SLIDER_STYLE = """
<style id="hp-slider-counter-style">
.hp-home .hp-slider-controls:has(.hp-slide-count) {
  gap: 0;
  padding: 3px;
  border-radius: 12px;
  background: #09291df2;
  border-color: #f8f6ef4d;
}
.hp-home .hp-slider-controls:has(.hp-slide-count) .hp-slide-arrow {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: transparent;
  border: 0;
}
.hp-home .hp-slider-controls:has(.hp-slide-count) .hp-slide-arrow:hover {
  background: #ffffff20;
}
.hp-home .hp-slide-count {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  gap: .4em;
  min-width: 66px;
  padding-inline: .4em;
  color: #f8f6ef;
  font: 700 12px/1 system-ui, sans-serif;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.hp-home .hp-slide-count-current { color: #e5b946; }
</style>
"""


def replace_slider_dots(source, soup):
    dots = re.compile(r"""<div\b[^>]*class=["']hp-slide-dots["'][^>]*>.*?</div>""", re.S)
    count = len(soup.select('.hp-slide-track .hp-slide'))
    if not count or not dots.search(source):
        return source
    status = (
        '<span class="hp-slide-count" dir="ltr">'
        '<span class="hp-slide-count-current">01</span>'
        f'<span>/</span><span>{count:02d}</span></span>'
    )
    source = dots.sub(status, source, count=1)
    for arrow, label in zip(soup.select('.hp-slider-controls .hp-slide-arrow'),
                            SLIDER_LABELS.get(soup.html.get('lang'), SLIDER_LABELS['fr'])):
        direction = arrow['data-slide-dir']
        button = re.compile(r'<button\b(?=[^>]*data-slide-dir="'
                            + re.escape(direction) + r'")[^>]*>')
        source = button.sub(lambda match: re.sub(r'aria-label="[^"]*"',
                                                 f'aria-label="{label}"',
                                                 match[0]), source, count=1)
    return source.replace('</head>', SLIDER_STYLE + '</head>', 1)


def prioritize(page, root):
    source = page.read_text(encoding='utf-8')
    if '<img' not in source and '<iframe' not in source:
        return False
    soup = BeautifulSoup(source, 'html.parser')
    if soup.select_one('.hp-hero'):
        updated = re.sub(r'(/images/clarity/hero-\d+\.avif)(?![?\w])', r'\1?hero=2', source)
        updated = re.sub(
            r'''(\bsrc=["'])([^"']*?/home-pro\.js)(?:\?[^"']*)?(["'])''',
            lambda match: f'{match[1]}{match[2]}?v=slider-counter1{match[3]}',
            updated,
        )
        updated = replace_slider_dots(updated, soup)
        if updated != source:
            page.write_text(updated, encoding='utf-8')
        return updated != source
    if not soup.head:
        return False
    hero_images = soup.select('section.hero img[src], section.rp-hero img[src], .hero-media img[src]')
    hiking = soup.select_one('main.rando .hero .mosaic') is not None
    changed = False
    for index, image in enumerate(hero_images):
        path = image_path(root, image['src'])
        if path is None or not path.is_file():
            continue
        if image.get('loading') == 'lazy':
            del image['loading']
            changed = True
        if index == 0 or hiking:
            if image.get('fetchpriority') != 'high':
                image['fetchpriority'] = 'high'
                changed = True
        elif image.get('fetchpriority') == 'high':
            del image['fetchpriority']
            changed = True
    if hiking:
        for preload in soup.select('link[rel=preload][as=image]'):
            if re.search(r'/17(?:-\d+)?\.webp$', preload.get('href', '')):
                preload.decompose()
                changed = True
    for frame in soup.select('main iframe[src], iframe#raftingProgramFrame, iframe#giteExperienceFrame'):
        embedded = image_path(root, frame['src'])
        if embedded is None or embedded.suffix != '.html' or not embedded.is_file():
            continue
        subpage = BeautifulSoup(embedded.read_text(encoding='utf-8'), 'html.parser')
        photo = subpage.select_one('section.hero .hero-media img[src], section.hero img[src]')
        if not photo or photo.has_attr('srcset') or photo.find_parent('picture'):
            continue
        photo_path = image_path(root, photo['src'])
        if photo_path is None or not photo_path.is_file():
            continue
        if frame.get('loading') == 'lazy':
            frame['loading'] = 'eager'
            changed = True
        if not any(link.get('href') == photo['src'] for link in soup.select('link[rel=preload][as=image]')):
            soup.head.insert(0, soup.new_tag('link', attrs={
                'rel': 'preload', 'as': 'image', 'href': photo['src'], 'fetchpriority': 'high',
            }))
            changed = True
        break
    if changed:
        page.write_text(str(soup), encoding='utf-8')
    return changed


def build(root):
    compress_hero_images(root)
    (root / 'home-pro.js').write_bytes(Path(__file__).with_name('home-slider.js').read_bytes())
    count = sum(prioritize(page, root) for page in root.rglob('*.html')
                if not any(part.startswith('.') or part == 'admin'
                           for part in page.relative_to(root).parts))
    print(f'Updated hero delivery on {count} pages.')


if __name__ == '__main__':
    build(Path(sys.argv[1]))
