"""Recover the 23 historical URLs reported as 404 in Search Console."""
from pathlib import Path
from html import escape
from urllib.parse import urlsplit
import json

PAGES = ('camping','hebergement','blog','quad','programme','memories',
         'booking','vtt','rafting','contact','guide','randonnee','store')
ROOT_PAGES = ('blog','guide','vtt','hebergement','contact','quad','rafting','randonnee','camping')
REDIRECTS = {f'pages/{page}.html': f'/fr/{page}/' for page in PAGES}
REDIRECTS.update({f'{page}.html': f'/fr/{page}/' for page in ROOT_PAGES})
REDIRECTS['activities.html'] = '/fr/#activities'

def build(root):
    root = Path(root)
    for source, target in REDIRECTS.items():
        url = urlsplit(target)
        destination = root / url.path.lstrip('/') / 'index.html'
        assert destination.is_file(), f'Missing redirect destination: {target}'
        if url.fragment:
            assert f'id="{url.fragment}"' in destination.read_text(encoding='utf-8'), target
        path = root / source
        if path.exists():
            old = path.read_text(encoding='utf-8')
            assert 'IMSFRANE_LEGACY_RECOVERY' in old, f'Refusing to replace an existing page: {source}'
        path.parent.mkdir(parents=True, exist_ok=True)
        # Pages hosting cannot issue per-path HTTP 301s. Immediate meta refresh
        # plus a matching canonical consolidates each old URL onto its real page.
        # Build the JavaScript path without an embedded fragment, so a query
        # string always comes before the fragment.
        script = 'location.replace(' + json.dumps(url.path) + '+location.search+(location.hash||' + json.dumps('#'+url.fragment if url.fragment else '') + '));'
        content = ('<!doctype html>\n<!-- IMSFRANE_LEGACY_RECOVERY -->\n'
                   '<html lang="fr"><head><meta charset="utf-8">'
                   '<meta name="viewport" content="width=device-width,initial-scale=1">'
                   '<title>Page déplacée | Imsfrane Cathédrale</title>'
                   '<meta http-equiv="refresh" content="0;url=' + escape(target, quote=True) + '">'
                   '<link rel="canonical" href="https://imsfrane.com' + escape(url.path, quote=True) + '">'
                   '<script>' + script + '</script></head><body>'
                   '<p>Cette page a changé d’adresse. <a href="' + escape(target, quote=True) + '">Ouvrir la page actuelle</a>.</p>'
                   '</body></html>\n')
        path.write_text(content, encoding='utf-8')
    print(f'Recovered {len(REDIRECTS)} legacy URLs with immediate redirects')

if __name__ == '__main__':
    import sys
    build(sys.argv[1] if len(sys.argv)>1 else 'public')
