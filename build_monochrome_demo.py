"""Prepare the shared Atlas identity and navigation links on the demo."""
from pathlib import Path
import re


CSS_COLOR = re.compile(
    r"""(?P<protected>/\*.*?\*/|\burl\([^)]*\)|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')"""
    r"|(?<![\w/\-])#(?P<hex>[\da-f]{8}|[\da-f]{6}|[\da-f]{4}|[\da-f]{3})(?![\w-])"
    r"|\b(?P<rgb>rgba?)\(\s*(?P<r>\d+)\s*,\s*(?P<g>\d+)\s*,\s*(?P<b>\d+)(?P<alpha>\s*,[^)]*)?\s*\)",
    re.I | re.S,
)
INLINE_STYLE = re.compile(r'(<style\b[^>]*>)(.*?)(</style>)', re.I | re.S)
STYLE_ATTRIBUTE = re.compile(r"""(\sstyle\s*=\s*)(["'])(.*?)\2""", re.I | re.S)
CSS_LINK = re.compile(r"""(<link\b[^>]*\bhref=["'])([^"'?#]+\.css(?:\?[^"']*)?)(["'])""", re.I)
MENU_BRAND = re.compile(r'<div class="atnav-drawer-brand">(.*?)</div>', re.S)




BASELINE = """
html body { background-color: #fff; color: #151515; }

body.atnav-ready #siteHeader,
body.atnav-ready .atnav-article-header,
#atnavDrawer,
body.atnav-ready .atnav-langmini-panel {
  background: #fff !important;
  border-color: #d5d5d5 !important;
  color: #151515 !important;
}
#ims-footer,
.site-footer {
  background: #111 !important;
  border-color: #333 !important;
}
body.atnav-ready #siteHeader .brand-content strong,
body.atnav-ready .atnav-article-brand,
body.atnav-ready #siteHeader .atnav-desktop a,
body.atnav-ready .atnav-langmini-panel a,
#atnavDrawer :is(.atnav-drawer-brand strong, .atnav-intro-title, .atnav-item, .atnav-submenu a, .atnav-languages a) {
  color: #151515 !important;
}
body.atnav-ready #siteHeader .brand-content small,
#atnavDrawer :is(.atnav-drawer-brand small, .atnav-label, .atnav-mark, .atnav-item-icon, .atnav-subicon, .atnav-chevron) {
  color: #464646 !important;
}
#atnavDrawer :is(.atnav-drawer-top, .atnav-label-separated, .atnav-actions) {
  border-color: #dedede;
}
body.atnav-ready :is(.atnav-open, .atnav-langmini-trigger, .ims-member-entry),
#atnavDrawer :is(.atnav-close, .atnav-whatsapp, .atnav-languages a) {
  background: #fff !important;
  border-color: #b5b5b5 !important;
  color: #151515 !important;
}
body.atnav-ready :is(.atnav-open, .atnav-langmini-trigger, .ims-member-entry):hover,
body.atnav-ready .atnav-langmini-trigger[aria-expanded="true"],
body.atnav-ready .atnav-langmini-panel a:is(:hover, :focus-visible, [aria-current="page"]),
#atnavDrawer :is(.atnav-close, .atnav-whatsapp):hover {
  background: #eee !important;
  color: #151515 !important;
}
body.atnav-ready #siteHeader .header-book-button,
body.atnav-ready .atnav-article-book,
#atnavDrawer .atnav-book {
  background: #171717 !important;
  border-color: #171717 !important;
  color: #fff !important;
}
body.atnav-ready #siteHeader .atnav-desktop a:is(:hover, [aria-current="page"]),
#atnavDrawer :is(.atnav-item, .atnav-submenu a):is(:hover, [aria-current="page"]),
#atnavDrawer .atnav-drawer-brand:hover strong {
  text-decoration: underline;
  text-underline-offset: .25em;
}
#atnavDrawer .atnav-drawer-brand:focus-visible {
  outline: 2px solid #333;
  outline-offset: 5px;
}
#ims-footer .fp-cta {
  background: #fff !important;
  border-color: #fff !important;
  color: #111 !important;
}
#ims-footer .fp-cta:hover { background: #dedede !important; }

/* Give labels over busy photographs an opaque reading surface. */
html body main.rando .mosaic .stamp,
html body .hp-home .hp-activity-grid > .hp-activity-card > .hp-activity-image > .hp-photo-tag,
html body .hp-home .hp-destination-label,
html body .hero-badge {
  background: #fff !important;
  color: #151515 !important;
  border-color: #dedede !important;
  text-shadow: none;
}
html body :is(.hp-destination-label, .hero .hero-badge) { border-radius: 4px; }
html body .hp-destination-label { padding: .45em .7em; }
html body .hero-badge :is(b, span, strong) { color: #151515 !important; }
::selection { background: #191919; color: #fff; }
"""


def neutral_value(red, green, blue):
    value = round(0.2126 * red + 0.7152 * green + 0.0722 * blue)
    if max(red, green, blue) - min(red, green, blue) < 6:
        return value
    if min(red, green, blue) >= 220:
        return min(255, value + 7)
    if value < 85:
        return max(12, round(value * .65))
    return value


def atlas_tone(value):
    # Tint dark surfaces forest-green and light surfaces like Atlas limestone.
    if value == 0 or value == 255:
        return (value, value, value)
    if value < 128:
        strength = min(value / 24, (128 - value) / 72, 1)
        offset = (-10, 8, 1)
    else:
        strength = min((value - 128) / 50, (255 - value) / 13, 1)
        offset = (6, 3, -8)
    return tuple(max(0, min(255, round(value + delta * strength))) for delta in offset)


def transform(css):
    def replace(match):
        if match['protected']:
            return match[0]
        if match['hex']:
            original = match['hex']
            expanded = ''.join(char * 2 for char in original) if len(original) in (3, 4) else original
            channels = [int(expanded[start:start + 2], 16) for start in (0, 2, 4)]
            value = neutral_value(*channels)
            return '#' + ''.join(f'{channel:02x}' for channel in atlas_tone(value)) + expanded[6:]
        channels = [int(match[channel]) for channel in ('r', 'g', 'b')]
        value = neutral_value(*channels)
        channels = ','.join(str(channel) for channel in atlas_tone(value))
        return f"{match['rgb']}({channels}{match['alpha'] or ''})"

    return CSS_COLOR.sub(replace, css)


def version_link(match):
    url = match[2]
    if url.startswith(('https:', 'http:', '//')):
        return match[0]
    return f"{match[1]}{url}{'&' if '?' in url else '?'}palette=atlas2{match[3]}"


def build(root: Path):
    for stylesheet in root.rglob('*.css'):
        if any(vendor in stylesheet.name.lower() for vendor in ('bootstrap', 'fontawesome', 'font-awesome', 'animate', 'swiper', 'all.min')):
            continue
        original = stylesheet.read_text(encoding='utf-8')
        updated = transform(original)
        if updated != original:
            stylesheet.write_text(updated, encoding='utf-8')

    for page in root.rglob('*.html'):
        parts = page.relative_to(root).parts
        if 'admin' in parts:
            continue
        original = page.read_text(encoding='utf-8')
        updated = INLINE_STYLE.sub(lambda m: m[1] + transform(m[2]) + m[3], original)
        updated = STYLE_ATTRIBUTE.sub(lambda m: m[1] + m[2] + transform(m[3]) + m[2], updated)
        updated = CSS_LINK.sub(version_link, updated)
        if parts[0] in ('fr', 'en', 'es', 'ar'):
            home = f'/Imsfrane-demo/{parts[0]}/'
            updated = MENU_BRAND.sub(
                lambda match: f'<a class="atnav-drawer-brand" href="{home}">{match[1]}</a>',
                updated,
            )
        if '</head>' in updated:
            updated = updated.replace('</head>', '<link rel="stylesheet" href="/Imsfrane-demo/atlas-identity.css?v=2">\n</head>', 1)
        if updated != original:
            page.write_text(updated, encoding='utf-8')

    colours = Path(__file__).with_name('atlas-identity.css').read_text(encoding='utf-8')
    (root / 'atlas-identity.css').write_text(BASELINE + '\n' + colours, encoding='utf-8')
