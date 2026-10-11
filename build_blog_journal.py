from pathlib import Path
from bs4 import BeautifulSoup
import html,re,json
import xml.etree.ElementTree as ET

def build(root):
    for lang in ('fr','en'):
        path=root/lang/'blog.html'
        original=path.read_text(encoding='utf-8')
        soup=BeautifulSoup(original,'html.parser')
        main=soup.find('main')
        if main is None: raise RuntimeError('Blog main missing')
        fr=lang=='fr'
        cards=[]
        seen=set()
        for card in main.select('article.blog-card'):
            a=card.select_one('h2 a[href]')
            img=card.find('img')
            if not a or not img: continue
            href=a.get('href','')
            if href in seen: continue
            seen.add(href)
            title=a.get_text(' ',strip=True)
            desc=card.select_one('.blog-card-content p')
            desc=desc.get_text(' ',strip=True) if desc else ''
            meta=[e.get_text(' ',strip=True) for e in card.select('.blog-meta span.editable')]
            category=meta[1] if len(meta)>1 else ('Nature' if fr else 'Nature')
            date=meta[0] if meta else ''
            cards.append(dict(href=href,title=title,description=desc,image=img.get('src',''),category=category,date=date))
        # Preserve existing editorial cards, and discover further published article
        # pages already present in the original site. Never invent an article.
        for article in sorted((root/lang).glob('blog-*.html')):
            if article.name in ('blog-post.html',) or article.name in seen: continue
            page=BeautifulSoup(article.read_text(encoding='utf-8'),'html.parser')
            title_node=page.select_one('main h1') or page.find('h1')
            if not title_node: continue
            title=title_node.get_text(' ',strip=True)
            meta_desc=page.find('meta',attrs={'name':'description'})
            desc=meta_desc.get('content','') if meta_desc else ''
            image_node=page.select_one('main img') or page.find('meta',attrs={'property':'og:image'})
            image=image_node.get('src','') if image_node and image_node.name=='img' else (image_node.get('content','') if image_node else '')
            if image.startswith('https://imsfrane.com/'):
                image='../'+image.split('https://imsfrane.com/',1)[1].lstrip('/')
            cards.append(dict(href=article.name,title=title,description=desc,image=image,category=('Découverte' if fr else 'Discover'),date=''))
            seen.add(article.name)
        # Two stories must not share the same photo in the magazine index.
        # Keep their original article URLs untouched; hide duplicate thumbnails
        # where a more detailed guide is already featured with that photograph.
        distinct=[]
        seen_photos=set()
        for card in cards:
            image_key=re.sub(r'-(?:480|680|768|800|1024|1200)(?=\.[^.]+$)','',card['image'].split('?',1)[0].lower())
            if image_key and image_key in seen_photos: continue
            if image_key: seen_photos.add(image_key)
            source=card['image'].split('?',1)[0]
            if source.startswith('/Imsfrane-demo/images/'):
                photo=root/'images'/source.split('/images/',1)[1]
            elif source.startswith('../images/'):
                photo=root/'images'/source.split('../images/',1)[1]
            else:
                photo=None
            if photo is not None and not photo.is_file():
                raise RuntimeError('Missing indexed blog photograph: '+str(photo))
            distinct.append(card)
        cards=distinct
        # Featured lead is the first original article, with its own photo.
        labels=dict(kicker='LE JOURNAL DE L’ATLAS' if fr else 'THE ATLAS JOURNAL',title='Histoires du Haut Atlas' if fr else 'Stories from the High Atlas',intro='Des récits authentiques sur Imsfrane, les rivières, les montagnes et la vie locale.' if fr else 'Authentic stories of Imsfrane, its rivers, mountains and local life.',search='Rechercher un article, un lieu, un thème…' if fr else 'Search stories, places, topics…',all='Tous' if fr else 'All',featured='À la une' if fr else 'Featured story',latest='Tous les articles' if fr else 'All stories',read='Lire l’article' if fr else 'Read story',none='Aucun article ne correspond à votre recherche.' if fr else 'No stories match your search.',more='Afficher plus' if fr else 'Show more',count='articles' if fr else 'stories',explore='Explorez nos récits' if fr else 'Explore our stories')
        def esc(s):return html.escape(str(s or ''),quote=True)
        def card_html(c,index):
            src=esc(c['image'])
            image='<img src="'+src+'" alt="'+esc(c['title'])+'" loading="lazy" decoding="async">' if src else ''
            text=esc(c['description'])
            return '<article class="journal-card" data-title="'+esc(c['title'])+'" data-description="'+text+'" data-category="'+esc(c['category'])+'" data-date="'+esc(c['date'])+'"><a class="journal-card-image" href="'+esc(c['href'])+'">'+image+'</a><div class="journal-card-body"><span class="journal-card-category">'+esc(c['category'])+'</span><h3><a href="'+esc(c['href'])+'">'+esc(c['title'])+'</a></h3><p>'+text+'</p><div class="journal-card-foot"><span>'+esc(c['date'])+'</span><a href="'+esc(c['href'])+'">'+labels['read']+' →</a></div></div></article>'
        featured=cards[0] if cards else None
        categories=[]
        for c in cards:
            if c['category'] not in categories:categories.append(c['category'])
        hero_image='../images/IMG_5131.webp'
        hero='<section class="journal-hero"><img class="journal-hero-bg" src="'+hero_image+'" alt="Imsfrane Atlas" fetchpriority="high"><div class="journal-hero-overlay"></div><div class="journal-hero-content"><span class="journal-kicker">'+labels['kicker']+'</span><h1>'+labels['title']+'</h1><p>'+labels['intro']+'</p><a href="#journal-articles">'+labels['explore']+' ↓</a></div></section>'
        lead=''
        if featured:
            lead='<section class="journal-featured"><div class="journal-featured-copy"><span class="journal-kicker">'+labels['featured']+'</span><h2><a href="'+esc(featured['href'])+'">'+esc(featured['title'])+'</a></h2><p>'+esc(featured['description'])+'</p><a class="journal-primary-link" href="'+esc(featured['href'])+'">'+labels['read']+' ↗</a></div><a class="journal-featured-photo" href="'+esc(featured['href'])+'"><img src="'+esc(featured['image'])+'" alt="'+esc(featured['title'])+'" loading="lazy"></a></section>'
        buttons='<button type="button" class="journal-filter active" data-category="all">'+labels['all']+'</button>'+''.join('<button type="button" class="journal-filter" data-category="'+esc(c)+'">'+esc(c)+'</button>' for c in categories)
        filters='<section class="journal-index" id="journal-articles"><div class="journal-index-heading"><span class="journal-kicker">'+labels['kicker']+'</span><h2>'+labels['latest']+'</h2><span class="journal-count" id="journal-count">'+str(len(cards))+' '+labels['count']+'</span></div><div class="journal-controls"><label class="journal-search-label"><span class="journal-search-icon" aria-hidden="true">⌕</span><input id="journal-search" type="search" autocomplete="off" placeholder="'+labels['search']+'" aria-label="'+labels['search']+'"></label><div class="journal-filters" role="group" aria-label="Categories">'+buttons+'</div></div><div class="journal-grid" id="journal-grid">'+''.join(card_html(c,i) for i,c in enumerate(cards))+'</div><p class="journal-no-results" id="journal-empty" hidden>'+labels['none']+'</p><button type="button" class="journal-more" id="journal-more">'+labels['more']+' ↓</button></section>'
        newmain='<main class="journal-page" id="mainContent">'+hero+lead+filters+'</main>'
        original=re.sub(r'<main[^>]*>.*?</main>',lambda m:newmain,original,count=1,flags=re.S|re.I)
        css=Path('blog-journal.css').read_text(encoding='utf-8')
        js=Path('blog-journal.js').read_text(encoding='utf-8')
        # Add the Arabic article index to the translated blog landing pages.
        arabic_hreflang='<link rel="alternate" hreflang="ar" href="https://imsfraneinfo.github.io/Imsfrane-demo/ar/blog.html">'
        original=original.replace('</head>',arabic_hreflang+'<style id="journal-v2">'+css+'</style></head>',1)
        original=original.replace('</body>','<script>'+js+'</script></body>',1)
        path.write_text(original,encoding='utf-8')
    # Demo-only sitemap: never publish new blog URLs into the live site's map.
    sitemap=root/'sitemap.xml'
    if sitemap.exists():
        sitemap_ns='http://www.sitemaps.org/schemas/sitemap/0.9'
        xhtml_ns='http://www.w3.org/1999/xhtml'
        ET.register_namespace('',sitemap_ns)
        ET.register_namespace('xhtml',xhtml_ns)
        xml=ET.parse(sitemap)
        urls=xml.getroot()
        base='https://imsfraneinfo.github.io/Imsfrane-demo/'
        for node in urls.iter():
            if node.tag.endswith('}loc') and node.text and 'https://imsfrane.com/' in node.text:
                node.text=node.text.replace('https://imsfrane.com/',base)
            if node.tag.endswith('}link') and 'href' in node.attrib:
                node.set('href',node.attrib['href'].replace('https://imsfrane.com/',base))
        existing={el.text for el in urls.findall('.//{'+sitemap_ns+'}loc')}
        slugs=['blog.html']+['blog-guide-'+t['slug']+'.html' for t in json.loads(Path('blog_new_topics.json').read_text(encoding='utf-8'))]
        for slug in slugs:
            for lang in ('fr','en','ar'):
                target=root/lang/slug
                if not target.exists(): raise RuntimeError('Missing indexed page: '+str(target))
                url=base+lang+'/'+slug
                if url in existing: continue
                entry=ET.SubElement(urls,'{'+sitemap_ns+'}url')
                ET.SubElement(entry,'{'+sitemap_ns+'}loc').text=url
                for alternate in ('fr','en','ar'):
                    ET.SubElement(entry,'{'+xhtml_ns+'}link',{'rel':'alternate','hreflang':alternate,'href':base+alternate+'/'+slug})
                ET.SubElement(entry,'{'+xhtml_ns+'}link',{'rel':'alternate','hreflang':'x-default','href':base+'fr/'+slug})
                existing.add(url)
        xml.write(sitemap,encoding='utf-8',xml_declaration=True)
        (root/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /Imsfrane-demo/admin/\n\nSitemap: '+base+'sitemap.xml\n',encoding='utf-8')

if __name__=='__main__':build(Path('public'))
