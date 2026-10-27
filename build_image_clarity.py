"""Demo-only responsive source upgrades. Preserve framing, content and originals."""
from pathlib import Path
from PIL import Image
import re, json

ROOT=Path('public')
BASE='/Imsfrane-demo/'
def attr(tag,key):
    m=re.search(r'(?<![\w-])'+re.escape(key)+r'=["\']([^"\']*)["\']',tag)
    return m[1] if m else ''
def put(tag,key,value):
    pattern=r'(?<![\w-])'+re.escape(key)+r'=["\'][^"\']*["\']'
    if re.search(pattern,tag):return re.sub(pattern,lambda m:key+'="'+value+'"',tag)
    return tag.rstrip('>')+' '+key+'="'+value+'">'
def build(root=ROOT):
    cache={}; changes=[]
    def dimensions(path):
        if path not in cache:
            with Image.open(path) as im:cache[path]=im.size
        return cache[path]
    def local(url):
        return root/url.split('?')[0].removeprefix(BASE).lstrip('/')
    def candidate(url):
        p=local(url)
        if not p.is_file() or 'images' not in p.parts:return None
        stem=re.sub(r'-v\d+$','',p.stem)
        stem=re.sub(r'(?:-(?:480|640|680|720|768|800|960|1200))+$','',stem)
        choices=[root/'images'/(stem+'.webp')]
        if stem=='kayak-group':choices.insert(0,root/'images/kayak/kayak-group.webp')
        if stem=='IMG_9129':choices.insert(0,root/'images/rafting-new/IMG_9129.webp')
        for q in choices:
            if q.is_file() and q!=p:
                w,h=dimensions(p);nw,nh=dimensions(q)
                # Only same-aspect variants of the same named photograph.
                if nw>w and abs(w/h-nw/nh)<.015:return q
        return None
    # Rebuild the mobile hero from the larger source, with moderate compression.
    # Desktop keeps its existing source selection and download budget.
    folder=root/'images/clarity';folder.mkdir(parents=True,exist_ok=True)
    with Image.open(root/'images/21.webp') as original:
        for w in (640,800,960,1200):
            sized=original.resize((w,round(original.height*w/original.width)),Image.Resampling.LANCZOS)
            sized.save(folder/f'hero-{w}.avif','AVIF',quality=65,speed=6)
    hero=BASE+'images/clarity/'
    hero_set=', '.join(hero+f'hero-{w}.avif '+str(w)+'w' for w in (640,800,960,1200))
    for p in root.rglob('*.html'):
        if 'admin' in p.parts:continue
        text=p.read_text();before=text
        def upgrade(m):
            tag=m[0];src=attr(tag,'data-src') or attr(tag,'src')
            if not src or 'logo' in src or src.startswith(('http:','https:','data:')):return tag
            q=candidate(src)
            if not q:return tag
            large=BASE+str(q.relative_to(root));w,h=dimensions(q)
            key='data-srcset' if attr(tag,'data-src') else 'srcset'
            current=attr(tag,key)
            oldw=dimensions(local(src))[0]
            current=current or src+' '+str(oldw)+'w'
            if large not in current:current+=', '+large+' '+str(w)+'w'
            tag=put(tag,key,current)
            if not attr(tag,'sizes'):
                # Native auto sizes uses the actual card width for lazy images.
                lazy=attr(tag,'loading')=='lazy'
                tag=put(tag,'sizes',('auto, ' if lazy else '')+'(max-width: 700px) 100vw, 60vw')
            changes.append({'page':str(p.relative_to(root)),'small':src,'large':large,'width_before':oldw,'width_after':w})
            return tag
        text=re.sub(r'<img\b[^>]*>',upgrade,text)
        # Mobile first hero had a fixed 720px source overriding all larger options.
        def hero_tag(m):
            tag=m[0]
            if 'hero-mobile-57d7ab58f87a.avif' not in tag:return tag
            if tag.startswith('<source'):
                tag=put(tag,'srcset',hero_set);tag=put(tag,'sizes','100vw')
            elif tag.startswith('<link') and attr(tag,'as')=='image':
                tag=put(tag,'href',hero+'hero-1200.avif');tag=put(tag,'imagesrcset',hero_set);tag=put(tag,'imagesizes','100vw')
            elif tag.startswith('<img'):
                tag=put(tag,'src',hero+'hero-1200.avif')
            return tag
        text=re.sub(r'<(?:source|link|img)\b[^>]*>',hero_tag,text)
        text=re.sub(r'(src=["\'][^"\']*images/team/farid-laydi\.webp)(["\'])',r'\1?v=clarity1\2',text)
        if text!=before:p.write_text(text)
    (root/'image-clarity-report.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2))
    print(f'Upgraded {len(changes)} image references; original files and crop styles unchanged.')
if __name__=='__main__':build()
