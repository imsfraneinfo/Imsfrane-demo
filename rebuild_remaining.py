from pathlib import Path
from bs4 import BeautifulSoup
import re
import html

PAGES=('hebergement','programme','booking','contact','memories','guide','store','blog')

def crop_contact_photo(root):
    # Contact only: use the lower portion of the original HD rafting photo.
    # Do not change the shared brand logo, hero frame, or other site images.
    from PIL import Image
    source=root/'images'/'25.webp'
    destination=root/'images'/'contact-rafting-bottom.webp'
    if not source.is_file():
        raise FileNotFoundError('Original HD Contact photo is missing: '+str(source))
    with Image.open(source) as photo:
        width,height=photo.size
        if width<800 or height<1000:
            raise RuntimeError('Unexpected source Contact photo dimensions: '+str(photo.size))
        lower_part=photo.crop((0,round(height*0.39),width,height))
        lower_part.save(destination,format='WEBP',quality=91,method=6)
    if not destination.is_file():
        raise RuntimeError('Could not export cropped Contact rafting photo')

def image_key(src):
    # Treat responsive variants of one photograph as the same image.
    name=src.split('/')[-1].split('?')[0].lower()
    return re.sub(r'-(?:480|680|768|800|1024|1200)(?=\\.)', '', name)

def build_page(path, used_heroes):
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
    # Prefer the page's own original photograph, not an image already used
    # as the hero of another page. Never inject an unrelated fallback photo.
    hero_photo=next((im for im in all_images if image_key(im) not in used_heroes), all_images[0] if all_images else '')
    if hero_photo:
        used_heroes.add(image_key(hero_photo))
    used_images={image_key(hero_photo)} if hero_photo else set()
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
        # A photograph appears at most once per page, including its hero.
        # Preserve every distinct original image, including full galleries.
        unique=[]
        for img in images:
            key=image_key(img)
            if key not in used_images:
                used_images.add(key)
                unique.append(img)
        photo=unique[0] if unique else ''
        more=unique[1:]
        media=('<div class="demo-rebuild-photo"><img loading="lazy" src="'+html.escape(photo,quote=True)+'" alt="'+html.escape(name or title)+'"></div>') if photo else ''
        gallery=('<div class="demo-rebuild-gallery">'+''.join('<img loading="lazy" src="'+html.escape(i,quote=True)+'" alt="'+html.escape(name or title)+'">' for i in more)+'</div>') if more else ''
        buttons='<div class="demo-rebuild-actions">'+''.join('<a href="'+html.escape(h,quote=True)+'">'+html.escape(t)+' ↗</a>' for t,h in links[:8])+'</div>' if links else ''
        detail='<div class="demo-rebuild-tags">'+''.join(details[:24])+'</div>' if details else ''
        body='<div class="demo-rebuild-copy">'+('<h2>'+html.escape(name)+'</h2>' if name else '')+''.join(paragraphs[:100])+detail+buttons+''.join(forms)+'</div>'
        blocks.append('<section class="demo-rebuild-section'+(' demo-rebuild-alt' if index%2 else '')+'" id="demo-section-'+str(index)+'"><div class="demo-rebuild-inner">'+media+body+'</div>'+gallery+'</section>')
    hero_picture=hero_photo
    if path.stem=='contact':
        if image_key(hero_photo)!='25.webp':
            raise RuntimeError('Unexpected Contact hero source: '+hero_photo)
        hero_picture='../images/contact-rafting-bottom.webp'
    hero='<section class="demo-editorial-hero"><div class="demo-editorial-copy"><span class="demo-editorial-eyebrow">'+eyebrow+'</span><h1>'+html.escape(title)+'</h1><a class="demo-editorial-link" href="#demo-section-0">'+explore+' ↓</a></div><div class="demo-editorial-photo"><img src="'+html.escape(hero_picture,quote=True)+'" alt="'+html.escape(title)+'"></div></section>'
    new_main='<main class="demo-rebuilt-page" id="mainContent">'+hero+''.join(blocks)+'</main>'
    source=re.sub(r'<main[^>]*>.*?</main>',lambda _:new_main,source,count=1,flags=re.S|re.I)
    path.write_text(source,encoding='utf-8')

def run(root):
    crop_contact_photo(root)
    for lang in ('fr','en'):
        used_heroes=set()
        for page in PAGES:
            build_page(root/lang/(page+'.html'), used_heroes)
if __name__=='__main__':
    run(Path('public'))
