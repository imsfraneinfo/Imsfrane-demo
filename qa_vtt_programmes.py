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
        browser.get(ROOT + 'fr/vtt/?v=five-programmes-20261021')
        if browser.find_elements('css selector', 'main[data-vtt-version="five-programmes-20261021"]'):
            break
        assert time.monotonic() < deadline, 'The new VTT page was not deployed'
        time.sleep(5)
    for width, height in ((390,844), (1366,900)):
        browser.set_window_size(width, height)
        for lang, d in DATA.items():
            browser.get(ROOT + lang + '/vtt/?v=five-programmes-20261021')
            WebDriverWait(browser,30).until(lambda b: b.find_elements('css selector','main.vt-page'))
            state = browser.execute_script('''const m=document.querySelector('main.vt-page');return {lang:document.documentElement.lang,dir:getComputedStyle(m).direction,width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,h1:m.querySelectorAll('h1').length,images:m.querySelectorAll('img').length,text:m.innerText};''')
            assert state['lang'] == lang and state['h1'] == 1 and state['images'] == 10, state
            assert state['dir'] == ('rtl' if lang=='ar' else 'ltr'), state
            assert state['scroll'] <= state['width']+2, state
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
                browser.execute_script('arguments[0].scrollIntoView({block:"center"})',summary)
                summary.click()
                for step in p['steps']:
                    assert step in card.text
                if i == 1:
                    assert '150' in card.find_element('css selector','.vt-price').text
                else:
                    assert d['quote'] in card.text
            images = browser.find_elements('css selector','main.vt-page img')
            for img in images:
                browser.execute_script('arguments[0].scrollIntoView({block:"center"})',img)
                WebDriverWait(browser,30).until(lambda b: b.execute_script('return arguments[0].complete && arguments[0].naturalWidth>0',img))
            browser.execute_script('window.scrollTo(0,0)')
            browser.save_screenshot(str(OUT/f'vtt-{lang}-{width}-hero.png'))
            browser.execute_script('document.querySelector("#vtt-programmes").scrollIntoView()')
            browser.save_screenshot(str(OUT/f'vtt-{lang}-{width}-programmes.png'))
            print('VTT PASS',lang,width,'five programmes; rental 150; four individual WhatsApp requests; ten loaded photos',flush=True)
print('PASS: five VTT programmes in four languages, mobile and desktop')
