from pathlib import Path
from bs4 import BeautifulSoup
import re
import html

PAGES=('hebergement','programme','booking','contact','memories','guide','store','blog')
def build_page(path):
    source=path.read_text(encoding='utf-8')
    soup=BeautifulSoup(source,'html.parser')
    main=soup.find('main')
    if not main:
        raise ValueError('Missing main: '+str(path))
    original_sections=main.find_all('section')
    # Select outermost sections so nested cards aren't duplicated.
    sections=[s for s in original_sections if s.find_parent('section') is None]
    if not sections:
        sections=[main]
    all_images=[]
    for im in main.find_all('img'):
        src=im.get('src','')
        if src and 'logo' not in src.lower() and src not in all_images:
            all_images.append(src)
    title_node=main.find('h1')
    title=title_node.get_text(' ',strip=True) if title_node else path.stem.title()
    hero_photo=all_images[0] if all_images else '../images/25.webp'
    lang=path.parent.name
    explore='Découvrir' if lang=='fr' else 'Explore'
    eyebrow='Imsfrane Cathédrale · Haut Atlas'
    blocks=[]
    for index,sec in enumerate(sections):
        heading=sec.find(['h2','h3'])
        name=heading.get_text(' ',strip=True) if heading else ''
        # Preserve original content hierarchy as readable sections, without legacy layout.
        paragraphs=[]
        seen=set()
        for tag in sec.find_all(['p','li'],recursive=True):
            if tag.find_parent(['p','li']) is not None:
                continue
            content=tag.get_text(' ',strip=True)
            if not content or content in seen or len(content)>1200:
                continue
            seen.add(content)
            paragraphs.append('<p>'+html.escape(content)+'</p>')
        # Keep short meaningful headings, prices, and labels that weren't paragraphs.
        details=[]
        for tag in sec.find_all(['h3','h4','strong'],recursive=True):
            value=tag.get_text(' ',strip=True)
            if 2<len(value)<150 and value!=name and value not in seen:
                seen.add(value)
                details.append('<span>'+html.escape(value)+'</span>')
        images=[]
        for im in sec.find_all('img'):
            src=im.get('src','')
            if src and 'logo' not in src.lower() and src not in images:
                images.append(src)
        links=[]
        for a in sec.find_all('a',href=True):
            label=a.get_text(' ',strip=True)
            href=a['href']
            if label and len(label)<95 and not href.startswith(('javascript:','#')) and (label,href) not in links:
                links.append((label,href))
        # Keep interactive booking/contact forms intact, including field names.
        forms=[str(f) for f in sec.find_all('form') if not f.find_parent('form')]
        # Section is rebuilt from actual source copy, images and original links.
        if not (name or paragraphs or images or links or forms or details):
            continue
        photo=images[0] if images else ''
        more=images[1:9]
        media=('<div class="demo-rebuild-photo"><img loading="lazy" src="'+html.escape(photo,quote=True)+'" alt="'+html.escape(name or title)+'"></div>') if photo else ''
        gallery=('<div class="demo-rebuild-gallery">'+''.join('<img loading="lazy" src="'+html.escape(i,quote=True)+'" alt="'+html.escape(name or title)+'">' for i in more)+'</div>') if more else ''
        buttons='<div class="demo-rebuild-actions">'+''.join('<a href="'+html.escape(h,quote=True)+'">'+html.escape(t)+' ↗</a>' for t,h in links[:8])+'</div>' if links else ''
        detail='<div class="demo-rebuild-tags">'+''.join(details[:24])+'</div>' if details else ''
        body='<div class="demo-rebuild-copy">'+('<h2>'+html.escape(name)+'</h2>' if name else '')+''.join(paragraphs[:100])+detail+buttons+''.join(forms)+'</div>'
        blocks.append('<section class="demo-rebuild-section'+(' demo-rebuild-alt' if index%2 else '')+'" id="demo-section-'+str(index)+'"><div class="demo-rebuild-inner">'+media+body+'</div>'+gallery+'</section>')
    hero='<section class="demo-editorial-hero"><div class="demo-editorial-copy"><span class="demo-editorial-eyebrow">'+eyebrow+'</span><h1>'+html.escape(title)+'</h1><a class="demo-editorial-link" href="#demo-section-0">'+explore+' ↓</a></div><div class="demo-editorial-photo"><img src="'+html.escape(hero_photo,quote=True)+'" alt="'+html.escape(title)+'"></div></section>'
    new_main='<main class="demo-rebuilt-page" id="mainContent">'+hero+''.join(blocks)+'</main>'
    source=re.sub(r'<main[^>]*>.*?</main>',lambda _:new_main,source,count=1,flags=re.S|re.I)
    path.write_text(source,encoding='utf-8')

def run(root):
    for lang in ('fr','en'):
        for page in PAGES:
            build_page(root/lang/(page+'.html'))
if __name__=='__main__':
    run(Path('public'))
