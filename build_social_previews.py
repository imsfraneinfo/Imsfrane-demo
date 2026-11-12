"""Give each public localized page a share image with an absolute HTTPS URL."""
from html import escape, unescape
from pathlib import Path
import re
from urllib.parse import urlsplit

from PIL import Image, ImageOps


PAGE_PHOTOS = {
    'gite-atlas': 'images/gite-atlas/exterior.webp',
    'hebergement': 'images/apartment/living-room.webp',
    'hebergements': 'images/gite-atlas/terrace.webp',
    'kayak': 'images/kayak/kayak-group.webp',
    'jetski': 'images/jetski-lake.webp',
    'jet-ski': 'images/jetski-lake.webp',
}
HOME_PHOTO = 'images/social/imsfrane-home-1200x630.jpg'
META = re.compile(r'<meta\b[^>]*>', re.I)
ATTR = re.compile(r'''([\w:-]+)\s*=\s*(["'])(.*?)\2''', re.S)


def attrs(tag):
    return {key.lower(): unescape(value) for key, _, value in ATTR.findall(tag)}


def build(root, site_url):
    prefix = urlsplit(site_url).path.rstrip('/')
    converted = {}
    count = 0
    for lang in ('fr', 'en', 'es', 'ar'):
        for page in sorted((root / lang).rglob('index.html')):
            html = page.read_text()
            head, close, body = html.partition('</head>')
            if not close:
                continue
            tags = [attrs(tag) for tag in META.findall(head)]
            if any(tag.get('http-equiv', '').lower() == 'refresh' for tag in tags):
                continue
            meta = {tag.get('property', tag.get('name')): tag.get('content', '') for tag in tags}
            route = page.parent.relative_to(root / lang).as_posix()
            source = PAGE_PHOTOS.get(route)
            if source is None:
                source = urlsplit(meta.get('og:image', '')).path.removeprefix(prefix).lstrip('/')
                if not source or not (root / source).is_file():
                    source = HOME_PHOTO
            assert (root / source).is_file(), (page, source)
            if source not in converted:
                with Image.open(root / source) as image:
                    if image.format == 'JPEG' and image.size == (1200, 630):
                        converted[source] = source
                    else:
                        relative = Path(source).with_suffix('').as_posix().replace('/', '-')
                        output = f'images/social/share-{relative}-1200x630.jpg'
                        cover = ImageOps.fit(image.convert('RGB'), (1200, 630), Image.Resampling.LANCZOS)
                        cover.save(root / output, 'JPEG', quality=84, optimize=True)
                        converted[source] = output
            title = meta.get('og:title') or unescape(re.search(r'<title\b[^>]*>(.*?)</title>', head, re.S)[1])
            description = meta.get('og:description') or meta.get('description')
            image_url = f'{site_url}/{converted[source]}'
            page_url = f'{site_url}/{page.parent.relative_to(root).as_posix()}/'
            og = {
                'og:type': meta.get('og:type') or 'website',
                'og:title': title, 'og:description': description,
                'og:url': page_url, 'og:site_name': 'Imsfrane Cathédrale',
                'og:image': image_url, 'og:image:secure_url': image_url,
                'og:image:type': 'image/jpeg', 'og:image:width': '1200',
                'og:image:height': '630', 'og:image:alt': title,
            }
            twitter = {
                'twitter:card': 'summary_large_image', 'twitter:title': title,
                'twitter:description': description, 'twitter:image': image_url,
                'twitter:image:alt': title,
            }
            def remove_old(tag):
                data = attrs(tag[0])
                key = data.get('property', data.get('name', ''))
                return '' if key in og or key in twitter else tag[0]
            head = META.sub(remove_old, head)
            new = [
                f'<meta {attr}="{key}" content="{escape(value, quote=True)}">'
                for attr, values in [('property', og), ('name', twitter)]
                for key, value in values.items() if value
            ]
            page.write_text(head + '\n'.join(new) + '\n' + close + body)
            count += 1
    print(f'Prepared social previews for {count} localized pages using {len(converted)} images.')
