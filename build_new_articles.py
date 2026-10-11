from pathlib import Path
import json,html,re
from bs4 import BeautifulSoup

TOPICS=json.loads(Path('blog_new_topics.json').read_text(encoding='utf-8'))
RESEARCH=json.loads(Path('blog_article_research.json').read_text(encoding='utf-8'))
CATEGORY={
'rafting':('Rafting','Rafting','الرافتينغ'),
'vtt':('VTT','Mountain biking','الدراجات الجبلية'),
'hiking':('Randonnée','Hiking','المشي الجبلي'),
'camping':('Camping','Camping','التخييم'),
'access':('Itinéraires','Routes','المسالك'),
'culture':('Culture','Culture','الثقافة'),
'nature':('Nature','Nature','الطبيعة')}
EN_ADVICE={
'rafting':['Ask the local guide to confirm river level, route and meeting point shortly before your trip. Spring snowmelt often makes March to May the main season, sometimes extending into June.','Wear a fitted buoyancy aid and helmet when required, listen to the safety briefing and never enter white water without qualified supervision.','If flow or weather is unsuitable, choose a land-based activity rather than forcing a river descent.'],
'vtt':['Choose a route that matches the least experienced rider. Mountain tracks can include loose stones, steep climbs and fast-changing surfaces.','Check brakes, tyres and helmet fit before setting off. Bring drinking water, repair supplies and an offline map.','Slow down around villages, livestock and walkers. Ask a local guide about current track conditions.'],
'hiking':['Confirm the trail and weather before leaving. Distances alone do not describe the difficulty of rocky mountain terrain.','Take water, suitable footwear, warm layers and a map that works without a mobile connection.','Avoid exposed sections during storms and allow enough daylight to return safely.'],
'camping':['Ask about land access and local restrictions before setting up a tent, especially near protected areas.','Keep away from dry riverbeds and flood channels. Avoid campfires and pack out every piece of litter.','Prepare for cool nights and changing mountain weather, even when the afternoon feels warm.'],
'access':['Check current road conditions with local contacts before travelling. Mountain roads may be affected by weather or works.','Plan fuel, daylight and offline navigation, and allow time for photo stops without rushing.','Respect private tracks, villages and other road users along the way.'],
'culture':['Meet local people respectfully and ask permission before taking portraits or entering private spaces.','Support local accommodation, guides and small shops whenever possible.','Remember that everyday village life is not a tourist performance.'],
'nature':['Choose activities based on current conditions rather than relying only on a calendar date.','Protect water sources, wildlife and trails, and carry out everything you bring in.','Ask local guides which places are suitable and accessible during your visit.']}
AR_ADVICE={
'rafting':['غالباً كيبدا موسم الرافتينغ ففصل الربيع، خصوصاً من مارس حتى ماي، وقد يمتد ليونيو حسب الثلوج وصبيب الواد.','قبل أي نزول خاص التأكد من مستوى المياه والطقس والمسار مع مرشد مختص، واتباع تعليمات السلامة واستعمال التجهيزات المناسبة.','إلا ما كانتش الظروف مناسبة، الأحسن اختيار نشاط آخر بحال الروندوني أو الدراجة الجبلية.'],
'vtt':['اختار المسار حسب مستوى المجموعة، لأن بعض المسالك فيها الحجر والطلوع والهبوط.','ضروري الخوذة وفحص الفرامل والعجلات وحمل الماء ومعدات إصلاح بسيطة.','خفف السرعة قرب الدواوير والمارة والماشية واحترم المسالك المحلية.'],
'hiking':['تأكد من حالة الطقس والمسار قبل الانطلاق وخلي الوقت الكافي للرجوع قبل الظلام.','جيب الماء والصباط المناسب وملابس دافئة وخريطة يمكن استعمالها بلا أنترنت.','ما تقربش من الجروف الخطيرة وتجنب المسالك المكشوفة وقت العواصف.'],
'camping':['قبل نصب الخيمة تأكد من السماح بالتخييم فالمكان واحترم الأراضي الخاصة والمناطق المحمية.','بعد على مجاري السيول وما تشعلش النار فالأماكن الخطيرة وجمع جميع النفايات.','وجد راسك للبرد والرياح حتى إلا كان النهار سخون.'],
'access':['تأكد من حالة الطريق قبل السفر، خصوصاً بعد الأمطار أو الأشغال.','حمل خريطة بلا أنترنت وخطط للوقود والوصول قبل الليل.','احترم الساكنة والمسالك الخاصة وخلي وقت كافي للتوقف والتصوير.'],
'culture':['سول على الإذن قبل تصوير الناس واحترم خصوصية البيوت والأراضي.','شجع المرشدين والمحلات وأماكن الإقامة المحلية.','التعرف على الثقافة الأمازيغية كيبدا بالاحترام والحوار.'],
'nature':['اختار النشاط حسب الفصل والطقس الفعلي، ماشي غير حسب التاريخ.','حافظ على نظافة الماء والمسالك وما تخليش النفايات فالطبيعة.','استفسر من السكان والمرشدين على الأماكن والمسالك المناسبة.']}
def esc(x):return html.escape(str(x),quote=True)
def build(root):
    # Existing original article pages are left unchanged.
    for lang in ('fr','en','ar'):
        (root/lang).mkdir(parents=True,exist_ok=True)
        links=[]
        for topic in TOPICS:
            slug='blog-guide-'+topic['slug']+'.html'
            title=topic[lang]
            desc=topic['desc'+lang]
            cat=CATEGORY[topic['category']][{'fr':0,'en':1,'ar':2}[lang]]
            image=topic['image']
            # Some new uploads live only in the demo repository; use an existing
            # source photo if the requested asset has not been published.
            image_file=root/'images'/image.split('/')[-1]
            if not image_file.exists():
                fallback={'vtt':'IMG_9763.webp','hiking':'22-800.webp','rafting':'24-800.webp','camping':'camping-1-800.webp','access':'19-800.webp','culture':'blog-tilouguite-800.webp','nature':'24.webp'}[topic['category']]
                image='../images/'+fallback
            lead=(desc+' '+RESEARCH['details'][topic['slug']][0]) if lang=='fr' else (desc+' '+RESEARCH['enLead'][topic['category']] if lang=='en' else desc+' '+RESEARCH['arLead'][topic['category']])
            paragraphs=RESEARCH['details'][topic['slug']] if lang=='fr' else EN_ADVICE[topic['category']] if lang=='en' else AR_ADVICE[topic['category']]
            heads={'fr':['À savoir avant de partir','Préparer son expérience','Respecter la montagne'],'en':['What to know','Prepare your visit','Travel responsibly'],'ar':['معلومات مهمة','الاستعداد للخرجة','احترام الطبيعة']}
            sections=''.join('<section><h2>'+esc(heads[lang][i])+'</h2><p>'+esc(paragraphs[i])+'</p></section>' for i in range(3))
            route='../fr/blog.html' if lang=='ar' else 'blog.html'
            back='← '+('Tous les articles' if lang=='fr' else 'All articles' if lang=='en' else 'جميع المقالات')
            dirattr=' dir="rtl"' if lang=='ar' else ''
            alternates=''.join('<link rel="alternate" hreflang="'+l+'" href="https://imsfraneinfo.github.io/Imsfrane-demo/'+l+'/'+slug+'">' for l in ('fr','en','ar'))
            htmlpage='''<!doctype html><html lang="'''+lang+'"'+dirattr+'''><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+esc(title)+''' | Imsfrane Cathédrale</title><meta name="description" content="'''+esc(desc)+'''"><meta name="robots" content="index,follow"><link rel="canonical" href="https://imsfraneinfo.github.io/Imsfrane-demo/'''+lang+'/'+slug+'''">'''+alternates+'''<meta property="og:type" content="article"><meta property="og:title" content="'''+esc(title)+'''"><meta property="og:description" content="'''+esc(desc)+'''"><meta property="og:image" content="https://imsfrane.com/images/'''+esc(image.split('/')[-1])+'''"><style>'''+Path('blog-articles.css').read_text(encoding='utf-8')+'''</style></head><body><header class="article-nav"><a href="../'''+('fr' if lang=='ar' else lang)+'''/index.html">IMSFRANE <b>CATHÉDRALE</b></a><nav><a href="'''+route+'''">'''+back+'''</a> <a href="../fr/'''+slug+'''">FR</a> <a href="../en/'''+slug+'''">EN</a> <a href="../ar/'''+slug+'''">العربية</a></nav></header><main><div class="article-hero"><img src="'''+esc(image)+'''" alt="'''+esc(title)+'''"><div class="article-shade"></div><div class="article-hero-text"><span>'''+esc(cat)+''' · IMSFRANE CATHÉDRALE</span><h1>'''+esc(title)+'''</h1><p>'''+esc(desc)+'''</p></div></div><div class="article-layout"><article class="article-body"><p class="article-lead">'''+esc(lead)+'''</p>'''+sections+'''<aside class="article-note">'''+('Les conditions peuvent évoluer : vérifiez les informations locales avant le départ.' if lang=='fr' else 'Conditions can change: confirm local information before setting out.' if lang=='en' else 'الظروف يمكن تتبدل، تأكد من المعلومات المحلية قبل الانطلاق.')+'''</aside><a class="article-cta" href="../'''+('fr' if lang=='ar' else lang)+'''/contact.html">'''+('Contacter notre équipe →' if lang=='fr' else 'Contact our team →' if lang=='en' else 'تواصل مع الفريق ←')+'''</a></article></div></main><footer>© Imsfrane Cathédrale · Tilouguite · Azilal</footer></body></html>'''
            (root/lang/slug).write_text(htmlpage,encoding='utf-8')
            links.append((slug,title,desc,image,cat))
        if lang=='ar':
            items=''.join('<a class="arabic-card" href="'+esc(slug)+'"><img src="'+esc(im)+'" alt="'+esc(title)+'" loading="lazy"><span>'+esc(cat)+'</span><h2>'+esc(title)+'</h2><p>'+esc(desc)+'</p></a>' for slug,title,desc,im,cat in links)
            index='<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>مدونة مسفران | الرافتينغ والروندوني والتخييم والدراجات</title><meta name="description" content="مقالات عربية عن مسفران وتيلوكيت وواد أحنصال والرافتينغ والدراجات الجبلية والتخييم والروندوني."><style>'+Path('blog-articles.css').read_text(encoding='utf-8')+'</style></head><body><header class="article-nav"><a href="../fr/index.html">IMSFRANE CATHÉDRALE</a><nav><a href="../fr/blog.html">Français</a> <a href="../en/blog.html">English</a></nav></header><div class="arabic-intro"><span>IMSFRANE CATHÉDRALE</span><h1>مدونة مسفران</h1><p>مقالات ونصائح حول الطبيعة والمغامرات في جبال الأطلس وواد أحنصال</p></div><main class="arabic-grid">'+items+'</main><footer>© Imsfrane Cathédrale · Tilouguite · Azilal</footer></body></html>'
            (root/'ar/blog.html').write_text(index,encoding='utf-8')
if __name__=='__main__':build(Path('public'))
