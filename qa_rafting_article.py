"""Check the published article, full photographs and blog discovery in Chrome."""
import json
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

ROOT = 'https://imsfraneinfo.github.io/Imsfrane-demo/'
SLUG = 'blog-rafting-50-km-bin-el-ouidane'
OUT = Path('four-language-browser-diagnostics')
OUT.mkdir(exist_ok=True)
opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
with webdriver.Chrome(options=opts) as browser:
    browser.set_page_load_timeout(55)
    # The publish workflow starts before Pages finishes deploying its branch.
    deadline = time.monotonic() + 180
    while True:
        browser.get(ROOT + 'ar/' + SLUG + '/?article-check=20261020')
        if (len(browser.find_elements('css selector', '.expedition-article>section')) == 6
                and len(browser.find_elements('css selector', '.expedition-hero img,.expedition-photo img')) == 5
                and browser.find_elements('css selector', 'a[data-article-back="static-v2"]')):
            break
        assert time.monotonic() < deadline, 'New article not deployed within three minutes'
        time.sleep(5)
    for width, height in ((390, 844), (1366, 900)):
        browser.set_window_size(width, height)
        for lang in ('fr', 'en', 'ar', 'es'):
            browser.get(ROOT + lang + '/' + SLUG + '/?article-check=20261020')
            WebDriverWait(browser, 30).until(lambda d: d.execute_script('return !!document.querySelector(".expedition-article")'))
            images = browser.find_elements('css selector', '.expedition-hero img,.expedition-photo img')
            assert len(images) == 5
            for img in images:
                browser.execute_script('arguments[0].scrollIntoView({block:"center"})', img)
                WebDriverWait(browser, 30).until(lambda d: d.execute_script('return arguments[0].complete && arguments[0].naturalWidth>0', img))
                state = browser.execute_script('''const i=arguments[0],s=getComputedStyle(i);return {fit:s.objectFit,w:i.clientWidth,h:i.clientHeight,nw:i.naturalWidth,nh:i.naturalHeight}''', img)
                assert state['fit'] == 'contain', state
                assert abs(state['w']/state['h'] - state['nw']/state['nh']) < 0.02, state
            state = browser.execute_script('''return {lang:document.documentElement.lang,dir:document.documentElement.dir,sections:document.querySelectorAll('.expedition-article>section').length,width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,links:[...document.querySelectorAll('.atnav-langmini-panel a[lang]')].map(a=>new URL(a.href).pathname),text:document.querySelector('.expedition-article').innerText,font:getComputedStyle(document.querySelector('.expedition-article')).fontFamily}''')
            assert state['lang'] == lang and state['sections'] == 6, state
            assert state['scroll'] <= state['width'] + 2, state
            assert set(state['links']) == {'/Imsfrane-demo/' + code + '/' + SLUG + '/' for code in ('fr','en','ar','es')}
            if lang == 'ar':
                assert state['dir'] == 'rtl' and 'Tajawal' in state['font'], state
                assert not any(word in state['text'] for word in ('غادي', 'ديال', 'باش', 'كتكون'))
            browser.execute_script('window.scrollTo(0,0)')
            browser.save_screenshot(str(OUT / f'article-50km-{lang}-{width}.png'))
            day_two = browser.find_element('css selector', '#expedition-5')
            assert not day_two.find_elements('css selector', 'img'), 'No misleading Imsfrane photograph on day two'
            print('ARTICLE PASS', lang, width, 'five uncropped images, six concise sections', flush=True)
            back = WebDriverWait(browser, 30).until(lambda d: d.find_element('css selector', '.ims-blog-return a'))
            assert back.get_attribute('href') == ROOT + lang + '/blog/', 'Runtime back-link points into the article directory'
            back.click()
            WebDriverWait(browser, 30).until(lambda d: d.find_elements('css selector', '.journal-card'))
            assert browser.current_url.rstrip('/') == (ROOT + lang + '/blog').rstrip('/')
            card = browser.find_element('css selector', '.journal-card a[href*="' + SLUG + '"]')
            assert card.is_displayed(), 'New article must be visible among the first cards'
            card_image = card.find_element('css selector', 'img')
            crop = browser.execute_script('return getComputedStyle(arguments[0]).objectPosition', card_image)
            assert crop == '50% 100%', crop
            featured = browser.find_element('css selector', '.journal-featured-photo img')
            assert browser.execute_script('return getComputedStyle(arguments[0]).objectPosition', featured) == '50% 100%'
    print('PASS: article and blog discovery in four languages on mobile and desktop', flush=True)
