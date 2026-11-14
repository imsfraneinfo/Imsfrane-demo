"""Apply Arabic copy corrections to the final rendered demo."""
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import json
import re

from bs4 import BeautifulSoup, NavigableString


PRODUCTS = {
    "honey": ("عسل طبيعي من الأطلس", "الكمية رهن التأكيد"),
    "oil": ("زيت الزيتون البلدي", "الحجم رهن التأكيد"),
    "thyme": ("الزعتر الجبلي البري", "للكيلوغرام"),
}


SOURCE = Path(__file__).resolve().parent
NAME = 'التجديف في واد ملول وواد أحنصال'
COPY = dict(line.split('|', 1) for line in (SOURCE / 'arabic-demo-copy.txt').read_text().splitlines() if line)
COPY.update({'Rafting': NAME, 'EN': 'الإنجليزية', 'ES': 'الإسبانية', 'FR': 'الفرنسية', 'AR': 'العربية',
             'English': 'الإنجليزية', 'Español': 'الإسبانية', 'Français': 'الفرنسية'})
TERMS = {
    'Logo Imsfrane Cathédrale': 'شعار مسفران كاتدرال',
    'Imsfrane Cathédrale': 'مسفران كاتدرال', 'Imsfrane': 'مسفران', 'Msfrane': 'مسفران',
    'Gîte Atlas Cathédrale': 'نزل أطلس كاتدرال', 'Gîte Atlas': 'نزل أطلس',
    'WhatsApp': 'واتساب', 'Google Maps': 'خرائط غوغل', 'Google AdSense': 'غوغل أدسنس', 'Google': 'غوغل',
    'Facebook': 'فيسبوك', 'Instagram': 'إنستغرام', 'TikTok': 'تيك توك', 'Supabase': 'سوبابيس',
    'Ichou Adventures': 'إيشو أدفنتشرز', 'Tilouguite': 'تيلوكيت', 'Oued Ahansal': 'واد أحنصال',
    'Oued Melloul': 'واد ملول', 'Ahansal': 'أحنصال', 'Melloul': 'ملول', 'Atlas': 'الأطلس',
    'DH': 'درهم', 'MAD': 'درهم', 'km': 'كم', 'KM': 'كم', 'GPS': 'نظام تحديد المواقع', 'IP': 'بروتوكول الإنترنت',
    'CMP': '', 'Quad': 'دراجة رباعية', 'VTT': 'الدراجات الجبلية', 'Rafting': 'التجديف',
    'رافتينغ': 'تجديف', 'روندوني': 'مشي جبلي', 'فريد العيدي': 'فريد لايدي',
    'D+': 'صعودًا',
}
TERM_PATTERN = re.compile(r'(?<![\w@/-])(?:' + '|'.join(re.escape(s) for s in sorted(TERMS, key=len, reverse=True) if s.isascii() or re.search('[A-Za-z]',s)) + r')(?![\w@/-]|\.[A-Za-z])', re.I)
TERMS_LOWER = {k.lower():v for k,v in TERMS.items()}
FOREIGN = re.compile(r'[A-Za-zÀ-ÿ]{2,}')
NUMBERED = {
    'Agrandir la photo': 'تكبير الصورة', 'Voir la photo': 'عرض الصورة',
    'Camping à Imsfrane —': 'صورة التخييم في مسفران',
    'Imsfrane hiking —': 'صورة المشي الجبلي في مسفران',
    'Photo': 'صورة', 'Image': 'صورة',
}
SKIP = {'script', 'style', 'code', 'pre'}


def translate(value):
    text = ' '.join(value.split())
    if not text:
        return value
    if text in COPY:
        return COPY[text]
    if text.startswith(('Souvenir Imsfrane Cathédrale —', 'ذكرى مصورة من مسفران ·')):
        return 'ذكرى مصورة من مسفران'
    for prefix, label in NUMBERED.items():
        if re.fullmatch(re.escape(prefix) + r'\s+\d+', text):
            return f'{label} {text.split()[-1]}'
    if ' · ' in text and text.split(' · ', 1)[0] in ('Randonnée', 'Camping', 'Itinéraires', 'Rafting', 'VTT'):
        label, suffix = text.split(' · ', 1)
        return f'{COPY[label]} · {translate(suffix)}'
    text = re.sub(r'التجديف في المياه البيضاء(?: بوادي أحنصال)?', NAME, text)
    for old, new in (('رافتينغ','تجديف'),('الروندوني','المشي الجبلي'),('روندوني','مشي جبلي'),('فريد العيدي','فريد لايدي'),
                     ('فاش','عندما'),('كيفاش توصل لمسفران','كيف تصل إلى مسفران'),('نفس المسارات الرئيسية ديال','المسارات الرئيسية نفسها الخاصة بـ'),
                     ('عناوين IP','عناوين بروتوكول الإنترنت'), ('تقنية غوغل AdSense','تقنية غوغل أدسنس'), ('باش تشوفها كاملة','لعرضها كاملة'), ('باش تعرف الثمن ديالك','لمعرفة السعر الإجمالي'), ('ثلاثة مسارات ديال الالتجديف بالكاياك','ثلاثة مسارات للتجديف بالكاياك')):
        text = text.replace(old,new)
    text = TERM_PATTERN.sub(lambda m: TERMS_LOWER[m[0].lower()],text)
    if text in COPY:
        return COPY[text]
    text = re.sub(r'(?<=\d)\s+m\b',' مترًا',text)
    text = re.sub(r'(?<=\d)\s*(?:km|KM)\b',' كم',text)
    text = re.sub(r'\(\s*\)', '', text)
    return text if text != ' '.join(value.split()) else value


def with_spaces(original, translation):
    if original == translation:
        return original
    return re.match(r'\s*', original)[0] + translation.strip() + re.search(r'\s*$', original)[0]


DISPLAY_KEYS = {'name', 'title', 'description', 'headline', 'alt', 'label', 'valid', 'heading', 'text', 'caption', 'single', 'count', 'empty', 'added', 'removed', 'note', 'products', 'i18n', 'items', 'itemListElement', '@graph'}


def translate_payload(data):
    if isinstance(data, list):
        return [translate_payload(item) for item in data]
    if isinstance(data, dict):
        return {key: translate_payload(value) if key in DISPLAY_KEYS else value for key, value in data.items()}
    if isinstance(data, str) and not urlsplit(data).scheme and not data.startswith(('/', '#')):
        return translate(data)
    return data


def localize(source, page):
    doc = BeautifulSoup(source, 'html.parser')
    if not doc.html:
        raise ValueError(page)
    doc.html['lang'], doc.html['dir'] = 'ar', 'rtl'
    for node in list(doc.find_all(string=True)):
        if type(node) is NavigableString and node.parent.name not in SKIP:
            translated = translate(str(node))
            if translated != str(node):
                node.replace_with(with_spaces(str(node), translated))
    for tag in doc.find_all(True):
        for attr in ('aria-label', 'alt', 'title', 'placeholder', 'data-title', 'data-description', 'data-label'):
            if isinstance(tag.get(attr), str):
                tag[attr] = translate(tag[attr])
        if tag.name == 'iframe':
            tag['title'] = translate(tag.get('title') or 'المحتوى التفصيلي')
        if tag.name == 'input' and tag.get('type') in ('submit','reset','button') and tag.get('value'):
            tag['value'] = translate(tag['value'])
        if tag.name == 'a':
            url = tag.get('href','')
            if url == '/Imsfrane-demo/members.html':
                tag['href'] = '/Imsfrane-demo/members.html?lang=ar'
            if url.startswith('https://wa.me/') and '?' in url:
                split = urlsplit(url)
                params = [(k, translate(v)) for k,v in parse_qsl(split.query,keep_blank_values=True)]
                tag['href'] = urlunsplit(split._replace(query=urlencode(params)))
        if tag.name == 'script' and tag.get('type') in ('application/json','application/ld+json') and tag.string:
            try:
                data = json.loads(tag.string)
            except ValueError:
                continue
            data = translate_payload(data)
            if tag.get('id') == 'spCatalog':
                for product in data['products']:
                    product['nameAr'], product['unitAr'] = PRODUCTS[product['id']]
            tag.string = json.dumps(data,ensure_ascii=False).replace('</','<\\/')
    title = doc.title.get_text(' ',strip=True) if doc.title else 'مسفران كاتدرال'
    if doc.title and FOREIGN.search(title):
        heading = doc.find('h1')
        title = heading.get_text(' ', strip=True) if heading and not FOREIGN.search(heading.get_text()) else 'مسفران كاتدرال'
        doc.title.string = title
    if doc.find('main'):
        for link in doc.find_all('a', href=True):
            if urlsplit(link['href']).path.rstrip('/') in ('/Imsfrane-demo/ar/rafting','/Imsfrane-demo/ar/rafting.html'):
                for node in list(link.find_all(string=True)):
                    if node.strip() == 'التجديف':
                        node.replace_with(with_spaces(str(node), NAME))
    if page.name in ('rafting.html','rafting-programmes-ar.html','rafting-content-ar.html') or page.parent.name == 'rafting':
        title = NAME + ' | مسفران كاتدرال'
        if doc.title:
            doc.title.string = title
        h1 = doc.find('h1')
        if h1:
            h1.string = NAME
    if page.name in ('article.html', 'blog-post.html'):
        legacy = doc.find('script', src=lambda value: value and 'cms-blog-post.js' in value)
        if legacy:
            legacy.decompose()
        article = doc.find(id='cmsArticle')
        if article:
            link = doc.new_tag('a', href='/Imsfrane-demo/ar/blog/')
            link.string = 'عرض المقالات'
            if not article.find('a', href='/Imsfrane-demo/ar/blog/'):
                article.clear()
                article.append(link)
    main = doc.find('main') or doc.body
    intro = next((p.get_text(' ',strip=True) for p in main.find_all('p') if len(p.get_text(' ',strip=True)) >= 35 and not FOREIGN.search(p.get_text(' ',strip=True))), title) if main else title
    for meta in doc.find_all('meta'):
        key = meta.get('name',meta.get('property',''))
        if key in ('description','og:title','og:description','og:image:alt','og:site_name','twitter:title','twitter:description','twitter:image:alt'):
            value = translate(meta.get('content',''))
            if FOREIGN.search(value) or (key.endswith(':title') and title.startswith(NAME)):
                value = intro if key.endswith('description') else title
            meta['content'] = value
    for script in doc.find_all('script', src=True):
        src = script['src']
        if not src.startswith(('https:', 'http:', '//')) and 'arabic-review=' not in src:
            script['src'] = src + ('&' if '?' in src else '?') + 'arabic-review=1'
    return doc


def build(root):
    pages = sorted((root/'ar').rglob('*.html')) + sorted(root.glob('*-ar.html'))
    runtime(root)
    for page in pages:
        doc = localize(page.read_text(), page)
        page.write_text(str(doc),encoding='utf-8')
    footer = root / 'footer-pro-content-ar.json'
    content = json.loads(footer.read_text())
    doc = localize('<html><body>'+content['html']+'</body></html>', footer)
    content['html'] = doc.body.decode_contents()
    footer.write_text(json.dumps(content,ensure_ascii=False))
    validation = '<script defer src="/Imsfrane-demo/arabic-form-validation.js?v=1"></script>'
    for page in pages:
        html = page.read_text()
        if '<form' in html and validation not in html:
            page.write_text(html.replace('</body>', validation + '</body>', 1))
    (root / 'arabic-form-validation.js').write_bytes((SOURCE / 'arabic-form-validation.js').read_bytes())
    members = root / 'members.html'
    member_html = members.read_text()
    if validation not in member_html:
        members.write_text(member_html.replace('</body>', validation + '</body>', 1))
    print(f'Reviewed Arabic text on {len(pages)} demo pages and embeds')


def patch_script(root, file, replacements):
    path = root / file
    original = path.read_text()
    updated = original
    for old, new in replacements:
        if new in updated and old not in updated:
            continue
        if old not in updated:
            raise ValueError(f'Missing Arabic localization hook in {file}: {old}')
        updated = updated.replace(old, new)
    if updated != original:
        path.write_text(updated)


def runtime(root):
    patch_script(root, 'booking-new.js', [
        ("const services=JSON.parse", "const arabic = document.documentElement.lang === 'ar';\nconst currency = arabic ? ' درهم' : ' DH';\nconst services=JSON.parse"),
        ("+' DH'", "+currency"),
        ("['IMSFRANE · '+t[6]", "[(arabic ? 'مسفران · ' : 'IMSFRANE · ')+t[6]"),
    ])
    patch_script(root, 'google-reviews-live.js', [
        ('تقييماً على Google','تقييمًا على غوغل'),
        ('شاهد التقييمات على Google','شاهد التقييمات على غوغل'),
        ('تقييمات Google Maps','تقييمات خرائط غوغل'),
    ])
    patch_script(root, 'js/core-multilingual-v2.js', [
        ('" : "Close navigation menu"', '" : language === "ar" ? "إغلاق قائمة التنقل" : "Close navigation menu"'),
        ('" : "Back to top"', '" : language === "ar" ? "العودة إلى أعلى الصفحة" : "Back to top"'),
        ('" : "Previous image"', '" : language === "ar" ? "الصورة السابقة" : "Previous image"'),
        ('" : "Next image"', '" : language === "ar" ? "الصورة التالية" : "Next image"'),
        ('getPageLanguage() === "fr" ? "Image" : "Image"', 'getPageLanguage() === "ar" ? "صورة" : "Image"'),
    ])
    patch_script(root, 'navigation-pro.js', [
        ('المتابعة باستخدام Google','المتابعة باستخدام غوغل'),
    ])
    patch_script(root, 'website-enquiry.js', [
        ("const message=()=>['IMSFRANE',", "const message=()=>[language==='ar'?'مسفران':'IMSFRANE',"),
    ])
    patch_script(root, 'store-pro.js', [
        ('var language=(document.documentElement.lang||"fr").toLowerCase().startsWith("en")?"en":"fr";',
         'var pageLanguage=(document.documentElement.lang||"fr").toLowerCase().slice(0,2); var language=pageLanguage==="ar"||pageLanguage==="en"?pageLanguage:"fr";'),
        ('var i18n=language==="fr"?{', '''var i18n=language==="ar"?{
 count:"منتجات",single:"منتج",cartEmpty:"سلة التسوق فارغة.",qty:"الكمية",remove:"إزالة",
 added:"أُضيف المنتج إلى السلة",removed:"أُزيل المنتج من السلة",messageTitle:"طلب شراء من متجر مسفران",
 confirmation:"يرجى تأكيد التوفر والكميات والتعبئة والسعر النهائي والتوصيل."
}:language==="fr"?{'''),
        ('+" MAD"', '+(language==="ar"?" درهم":" MAD")'),
        ('function nameOf(p){return p[language==="fr"?"nameFr":"nameEn"]}',
         'function nameOf(p){return p[language==="ar"?"nameAr":language==="en"?"nameEn":"nameFr"]}'),
        ('function unitOf(p){return p[language==="fr"?"unitFr":"unitEn"]}',
         'function unitOf(p){return p[language==="ar"?"unitAr":language==="en"?"unitEn":"unitFr"]}'),
        ('picture.src="../images/"+p.image', 'picture.src="/Imsfrane-demo/images/"+p.image'),
        ('"*TOTAL "+(language==="fr"?"INDICATIF":"ESTIMATE")', '(language==="ar"?"*المجموع التقريبي":"*TOTAL "+(language==="fr"?"INDICATIF":"ESTIMATE"))'),
    ])
    patch_script(root, 'members.html', [
        ('document.title=localized().heading+" | Imsfrane Cathédrale"', 'document.title=localized().heading+(lang==="ar"?" | مسفران كاتدرال":" | Imsfrane Cathédrale")'),
        ('document.querySelector(".ims-site-brand").href="/Imsfrane-demo/"+lang+"/Imsfrane-demo/index.html";',
         '''const brand=document.querySelector(".ims-site-brand");brand.href=route;
brand.querySelector("strong").textContent=brand.querySelector("img").alt=lang==="ar"?"مسفران كاتدرال":"Imsfrane Cathédrale";
const languageLabels={ar:"العربية",fr:"الفرنسية",en:"الإنجليزية",es:"الإسبانية"};
const nativeLabels={ar:"العربية",fr:"Français",en:"English",es:"Español"};
for(const select of [$("language"),$("imsDashLang")]){
select.setAttribute("aria-label",lang==="ar"?"اللغة":"Language");
for(const option of select.options)option.textContent=(lang==="ar"?languageLabels:nativeLabels)[option.value]||option.value;
}'''),
        ('المتابعة باستخدام Google','المتابعة باستخدام غوغل'),
        ('واش متأكد بغيتي تمسح التعليق؟','هل تريد حذف هذا التعليق؟'),
        ('msg(localized().error+(e.message||String(e)),true)', 'msg(lang==="ar"?"تعذّر إتمام العملية. تحقق من المعلومات وحاول مجددًا.":localized().error+(e.message||String(e)),true)'),
        ('msg(localized().error+error.message,true)', 'msg(lang==="ar"?"تعذّر تحميل التعليقات.":localized().error+error.message,true)'),
        ('JPG أو PNG أو WebP', 'بإحدى صيغ الصور المدعومة'),

    ])
