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
<style id="hp-slider-progress-style">
.hp-home .hp-hero-slider .hp-slider-controls {
  gap: 4px;
  padding: 2px 5px;
  border-radius: 999px;
  background: #09291de8;
  border-color: #f8f6ef55;
}
html[dir="rtl"] .hp-home .hp-hero-slider .hp-slider-controls { direction: rtl; }
.hp-home .hp-hero-slider .hp-slide-arrow {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: transparent;
  color: #fffdf7;
  border: 0;
}
.hp-home .hp-hero-slider .hp-slide-arrow:hover { background: #ffffff20; }
.hp-home .hp-slide-progress {
  display: flex;
  align-items: center;
  gap: 5px;
}
.hp-home .hp-slide-progress-segment {
  width: 12px;
  height: 3px;
  border-radius: 4px;
  background: #f8f6ef70;
  transition: width .22s ease, background-color .22s ease;
}
.hp-home .hp-slide-progress-segment.is-active {
  width: 24px;
  background: #e5b946;
}
.hp-home .hp-hero-slider .hp-slide-track {
  transform: translateX(var(--hp-drag-x, 0px));
  transition: transform .22s ease-out;
}
.hp-home .hp-hero-slider.is-dragging .hp-slide-track { transition: none; }
@media (prefers-reduced-motion: reduce) {
  .hp-home .hp-hero-slider .hp-slide-track,
  .hp-home .hp-slide-progress-segment { transition: none; }
}
</style>
"""


def replace_slider_dots(source, soup):
    dots = re.compile(r"""<div\b[^>]*class=["']hp-slide-dots["'][^>]*>.*?</div>""", re.S)
    count = len(soup.select('.hp-slide-track .hp-slide'))
    if not count or not dots.search(source):
        return source
    segments = ''.join(
        '<span class="hp-slide-progress-segment'
        + (' is-active' if index == 0 else '') + '"></span>'
        for index in range(count)
    )
    source = dots.sub(f'<span class="hp-slide-progress" aria-hidden="true">{segments}</span>',
                      source, count=1)
    lang = soup.html.get('lang', 'fr')
    labels = SLIDER_LABELS.get(lang, SLIDER_LABELS['fr'])
    rtl = soup.html.get('dir') == 'rtl'
    for direction, label in zip(('-1', '1'), labels):
        left = (direction == '-1') != rtl
        path = 'M14 6l-6 6 6 6' if left else 'M10 6l6 6-6 6'
        icon = ('<svg aria-hidden="true" width="19" height="19" viewBox="0 0 24 24" '
                'fill="none" stroke="currentColor" stroke-width="2" '
                f'stroke-linecap="round" stroke-linejoin="round"><path d="{path}"/></svg>')
        button = re.compile(r'(<button\b(?=[^>]*data-slide-dir="'
                            + direction + r'")[^>]*>).*?</button>', re.S)
        source = button.sub(lambda match: re.sub(r'aria-label="[^"]*"',
                                                 f'aria-label="{label}"', match[1])
                            + icon + '</button>', source, count=1)
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
            lambda match: f'{match[1]}{match[2]}?v=slider-progress1{match[3]}',
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
