from pathlib import Path
import re,html
from bs4 import BeautifulSoup

NEW_IMAGES=["F6408B73-5136-4406-A2B0-2BB77695EDC9.jpeg","IMG_0017.webp","IMG_0021.webp","IMG_0026.webp","IMG_0037.webp","IMG_0162.webp","IMG_0179.webp","IMG_0270.webp","IMG_0284.webp","IMG_0296.webp","IMG_0305.webp","IMG_0310.webp","IMG_1005.jpeg","IMG_1880.webp","IMG_1893.webp","IMG_2012.webp","IMG_2060.webp","IMG_2089.webp","IMG_2101.webp","IMG_2604.webp","IMG_2606.webp","IMG_2629.webp","IMG_2634.webp","IMG_2667.webp","IMG_4771.jpeg","IMG_4772.jpeg","IMG_4842.jpeg","IMG_4866.jpeg","IMG_5306.jpeg","IMG_5536.jpeg","IMG_5545.jpeg","IMG_6449.jpeg","IMG_6505.jpeg","IMG_6626.webp","IMG_7076.webp","IMG_7394.webp","IMG_7410.webp","IMG_7886.webp","IMG_7987.jpeg","IMG_7990.jpeg","IMG_8792.webp","IMG_8810.webp","IMG_9066.webp","IMG_9087.webp","IMG_9104.jpeg","IMG_9108.jpeg","IMG_9129.webp","IMG_9182.webp","IMG_9296.webp","IMG_9763.webp","IMG_9939.webp","about-team-01.webp","about-team-02.webp","about-team-03.webp","about-team-05.webp","about-team-06.webp","about-team-07.webp","rando-IMG_2855.webp","rando-IMG_2878.webp","rando-IMG_4503.webp","rando-IMG_4507.webp","rando-IMG_6167.webp","rando-IMG_6269.webp","rando-IMG_6274.webp","rando-IMG_7432.webp","rando-IMG_7447.webp","rando-IMG_7453.webp","rando-IMG_7634.webp","rando-IMG_7660.webp"]
ARCHIVE_IMAGES=["24.webp","22-800.webp","19-800.webp","IMG_5134-800.webp","4x4-800.webp","vtt-800.webp","quad-800.webp","babmsfrane-800.webp","25-800.webp"]

def build(root):
    for lang in ('fr','en'):
        path=root/lang/'memories.html'
        page=path.read_text(encoding='utf-8')
        soup=BeautifulSoup(page,'html.parser')
        main=soup.find('main')
        if not main: raise RuntimeError('Missing memories main')
        french=lang=='fr'
        title='Nos souvenirs, vos aventures' if french else 'Our memories, your adventures'
        intro=('Des moments authentiques dans le Haut Atlas : rafting, randonnée, VTT, quad, camping et rencontres. Découvrez toutes nos photos récentes et nos archives.' if french else 'Real moments in the High Atlas: rafting, hiking, mountain biking, quad, camping and local encounters. Explore our latest photos and our archives.')
        latest='Nos nouvelles photos' if french else 'Our latest photos'
        archives='Les souvenirs du site' if french else 'Photos from our original website'
        sublatest='Une collection de nos dernières aventures et de notre équipe.' if french else 'A collection of our latest adventures and team moments.'
        subold='Les images déjà présentes sur Imsfrane Cathédrale, réunies ici.' if french else 'The images already on Imsfrane Cathédrale, together in one place.'
        seen=set()
        def gallery(images,kind):
            cards=[]
            for name in images:
                key=re.sub(r'-(?:480|680|768|800|1024|1200)(?=\\.)','',name.lower())
                if key in seen: continue
                seen.add(key)
                src='../images/'+name
                alt=('Souvenir Imsfrane Cathédrale — ' if french else 'Imsfrane Cathédrale memory — ')+name.rsplit('.',1)[0].replace('_',' ')
                cards.append('<a class="memory-tile" href="'+html.escape(src,quote=True)+'" target="_blank" rel="noopener" aria-label="'+html.escape(alt,quote=True)+'"><img src="'+html.escape(src,quote=True)+'" alt="'+html.escape(alt,quote=True)+'" loading="lazy" decoding="async"><span class="memory-zoom" aria-hidden="true">↗</span></a>')
            return '<div class="memory-grid memory-'+kind+'">'+''.join(cards)+'</div>'
        heroimg='../images/'+NEW_IMAGES[0]
        body='<main class="memories-showcase" id="mainContent"><section class="memories-intro"><span class="memories-kicker">IMSFRANE CATHÉDRALE · HAUT ATLAS</span><h1>'+title+'</h1><p>'+intro+'</p><a href="#recent-photos" class="memories-scroll">'+('Voir les photos' if french else 'View photos')+' ↓</a></section>'
        body+='<section class="memories-gallery-section" id="recent-photos"><div class="memories-heading"><span class="memories-kicker">01 / COLLECTION</span><h2>'+latest+'</h2><p>'+sublatest+'</p></div>'+gallery(NEW_IMAGES,'new')+'</section>'
        body+='<section class="memories-gallery-section memories-archive" id="archive-photos"><div class="memories-heading"><span class="memories-kicker">02 / ARCHIVES</span><h2>'+archives+'</h2><p>'+subold+'</p></div>'+gallery(ARCHIVE_IMAGES,'old')+'</section></main>'
        page=re.sub(r'<main[^>]*>.*?</main>',lambda m:body,page,count=1,flags=re.S|re.I)
        style=Path('memories-gallery.css').read_text(encoding='utf-8')
        page=page.replace('</head>','<style id="memories-showcase-style">'+style+'</style></head>',1)
        path.write_text(page,encoding='utf-8')

if __name__=='__main__':build(Path('public'))
