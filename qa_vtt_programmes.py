"""Exercise the actual published MTB programmes on mobile and desktop."""
import json
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

ROOT = 'https://imsfraneinfo.github.io/Imsfrane-demo/'
DATA = json.loads(Path('vtt-programmes.json').read_text(encoding='utf-8'))
OUT = Path('four-language-browser-diagnostics')
OUT.mkdir(exist_ok=True)
opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
with webdriver.Chrome(options=opts) as browser:
    browser.set_page_load_timeout(55)
    deadline = time.monotonic() + 180
    while True:
        browser.get(ROOT + 'fr/vtt/?v=restored-hero-20261021&check=' + str(time.time_ns()))
        if browser.find_elements('css selector', 'main[data-vtt-version="arabic-fonts-20261021"]'):
            break
        if time.monotonic() >= deadline:
            browser.save_screenshot(str(OUT/'vtt-wait-failure.png'))
            raise AssertionError({'url': browser.current_url, 'title': browser.title, 'body': browser.find_element('tag name','body').text[:700]})
        time.sleep(5)
    for width, height in ((390,844), (1366,900)):
        browser.set_window_size(width, height)
        for lang, d in DATA.items():
            browser.get(ROOT + lang + '/vtt/?v=restored-hero-20261021&check=' + str(time.time_ns()))
            WebDriverWait(browser,30).until(lambda b: b.find_elements('css selector','main.vt-page'))
            state = browser.execute_script('''const m=document.querySelector('main.vt-page');return {lang:document.documentElement.lang,dir:getComputedStyle(m).direction,width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,h1:m.querySelectorAll('h1').length,images:m.querySelectorAll('img').length,text:m.innerText};''')
            assert state['lang'] == lang and state['h1'] == 1 and state['images'] == 12, state
            assert len(browser.find_elements('css selector','.quad-r-hero .quad-r-media img')) == 3
            taghia_image = browser.find_element('css selector','#vtt-programme-4 .vt-card-photo img')
            assert browser.execute_script('return getComputedStyle(arguments[0]).objectPosition',taghia_image) == '50% 100%'
            assert state['dir'] == ('rtl' if lang=='ar' else 'ltr'), state
            assert state['scroll'] <= state['width']+2, state
            if lang == 'ar':
                fonts = browser.execute_async_script('''const done=arguments[arguments.length-1];document.fonts.ready.then(()=>done({loaded:[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family),bad:[...document.querySelectorAll('body *')].filter(e=>!["STYLE","SCRIPT"].includes(e.tagName)&&[...e.childNodes].some(n=>n.nodeType===3&&/[\\u0600-\\u06ff]/.test(n.textContent))).filter(e=>!getComputedStyle(e).fontFamily.includes('Imsfrane')).map(e=>e.outerHTML.slice(0,160)),right:getComputedStyle(document.querySelector('.quad-r-badge')).right}));''')
                assert any('Alexandria' in f for f in fonts['loaded']), fonts
                assert any('Tajawal' in f for f in fonts['loaded']), fonts
                assert not fonts['bad'], fonts
                assert fonts['right'] != 'auto', fonts
            assert '100 DH' not in state['text'] and '100 MAD' not in state['text'], state
            for i, p in enumerate(d['programs'],1):
                card = browser.find_element('id',f'vtt-programme-{i}')
                assert p['name'] in card.text
                link = card.find_element('css selector','a.vt-button')
                href = urlparse(link.get_attribute('href'))
                assert href.netloc == 'wa.me' and href.path == '/212667772551'
                message = parse_qs(href.query)['text'][0]
                assert p['name'] in message
                summary = card.find_element('css selector','summary')
                browser.execute_script('arguments[0].scrollIntoView({block:"center",behavior:"instant"})',summary)
                summary.click()
                for step in p['steps']:
                    assert step in card.text
                if i == 1:
                    assert '150' in card.find_element('css selector','.vt-price').text
                else:
                    assert d['quote'] in card.text
            images = browser.find_elements('css selector','main.vt-page img')
            for img in images:
                browser.execute_script('arguments[0].scrollIntoView({block:"center",behavior:"instant"})',img)
                WebDriverWait(browser,30).until(lambda b: b.execute_script('return arguments[0].complete && arguments[0].naturalWidth>0',img))
            browser.execute_script('window.scrollTo({top:0,behavior:"instant"})')
            browser.save_screenshot(str(OUT/f'vtt-{lang}-{width}-hero.png'))
            browser.execute_script('document.querySelector("#vtt-programmes").scrollIntoView({behavior:"instant"})')
            browser.save_screenshot(str(OUT/f'vtt-{lang}-{width}-programmes.png'))
            print('VTT PASS',lang,width,'original hero restored; Taghia crop at bottom; five programmes; rental 150; WhatsApp verified',flush=True)
print('PASS: five VTT programmes in four languages, mobile and desktop')
