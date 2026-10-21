"""Check the consolidation and ad placement without requiring a browser."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from xml.etree import ElementTree as ET
import re
import sys
from build_adsense_readiness import KEEP, LANGS

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.tags=[];self.feed(text)
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag,dict(attrs)))

def check(root):
    root=Path(root); count=0; redirects=0
    for lang in LANGS:
        for slug in KEEP:
            p=root/lang/slug/'index.html'; text=p.read_text();doc=Page(text)
            assert not any(t=='meta' and a.get('http-equiv','').lower()=='refresh' for t,a in doc.tags),p
            assert any(t=='main' for t,a in doc.tags),p
        for p in (root/lang).glob('blog-*/index.html'):
            if p.parent.name in KEEP:continue
            text=p.read_text();doc=Page(text)
            assert 'noindex,follow' in text,p
            assert 'adsbygoogle' not in text,p
            target=next(a['href'] for t,a in doc.tags if t=='link' and a.get('rel')=='canonical')
            path=urlsplit(target).path
            # The QA also accepts the published demo prefix.
            path=path.removeprefix('/Imsfrane-demo')
            assert path.split('/')[2] in KEEP,(p,path)
            assert (root/path.lstrip('/')/'index.html').exists(),path
            redirects+=1
        text=(root/lang/'about/index.html').read_text()
        assert 'IMSFRANE_LOCAL_CONTACT' in text,lang
        assert 'Farid Laydi' in text or 'فريد العايدي' in text,lang
        for p in (root/lang).rglob('*.html'):
            text=p.read_text();doc=Page(text)
            if any(t=='meta' and a.get('http-equiv','').lower()=='refresh' for t,a in doc.tags):continue
            assert 'ca-pub-3106160668387388' not in text,p
            if '</footer>' in text: assert 'ims-privacy-link' in text,p
            for tag,a in doc.tags:
                for attr in ('href','src','poster'):
                    u=urlsplit(a.get(attr,''))
                    if not u.path or u.netloc or u.scheme:continue
                    path=unquote(u.path).removeprefix('/Imsfrane-demo')
                    dest=root/path.lstrip('/') if path.startswith('/') else p.parent/path
                    assert dest.exists(),(p,attr,path)
            count+=1
    for name in ['404.html','members.html','members-preview.html']:
        text=(root/name).read_text()
        assert 'adsbygoogle' not in text,name
        assert 'noindex,follow' in text,name
    for p in (root/'404.html',):
        assert not re.search(r'(?:href|src)=["\'](?:css|images|en|fr)/',p.read_text()),p
    entries=list(ET.parse(root/'sitemap.xml').getroot())
    for entry in entries:
        loc=next(e.text for e in entry if e.tag.endswith('}loc'))
        path=urlsplit(loc).path.removeprefix('/Imsfrane-demo')
        assert (root/path.lstrip('/')/'index.html').exists(),path
        if '/blog-' in path: assert path.split('/')[2] in KEEP,path
    assert (root/'ads.txt').read_text().strip()=='google.com, pub-5598024978912334, DIRECT, f08c47fec0942fa0'
    print(f'PASS: {count} content/utility pages; {redirects} consolidated articles; {len(entries)} sitemap URLs; four languages; no broken local HTML links/assets.')

if __name__=='__main__':check(sys.argv[1] if len(sys.argv)>1 else 'public')
