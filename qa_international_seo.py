"""Check search metadata, preview isolation and usable visitor information."""
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from build_international_seo import META
from build_legacy_redirects import REDIRECTS

ROOT = 'https://imsfraneinfo.github.io/Imsfrane-demo/'
OUT = Path('international-search-diagnostics')
OUT.mkdir(exist_ok=True)
opts = Options()
for flag in ('--headless=new','--no-sandbox','--disable-dev-shm-usage'):
    opts.add_argument(flag)
with webdriver.Chrome(options=opts) as b:
    b.set_page_load_timeout(55)
    deadline = time.monotonic()+180
    while True:
        b.get(ROOT+'en/vtt/?international-check='+str(time.time_ns()))
        if b.find_elements('css selector','html[data-international-seo="20261021"]'):
            break
        assert time.monotonic()<deadline, 'New demo build has not appeared'
        time.sleep(5)
    for source,target in REDIRECTS.items():
        b.get(ROOT+source+'?legacy-check='+str(time.time_ns()))
        expected=ROOT+urlparse(target).path.lstrip('/')
        WebDriverWait(b,20).until(lambda browser: browser.current_url.startswith(expected))
        assert b.find_elements('css selector','main'), (source,b.current_url)
        assert 'Page not found' not in b.title, (source,b.title)
        if '#activities' in target:
            assert b.find_elements('id','activities')
        print('LEGACY PASS',source,'->',target,flush=True)
    for lang, pages in META.items():
        for page, (title, description) in pages.items():
            b.get(ROOT+lang+'/'+page+'/?international-check='+str(time.time_ns()))
            assert b.title == title, (lang,page,b.title)
            assert b.find_element('css selector','meta[name="description"]').get_attribute('content') == description
            assert b.find_element('css selector','meta[name="robots"]').get_attribute('content') == 'noindex,follow'
            canonical = b.find_element('css selector','link[rel="canonical"]').get_attribute('href')
            assert canonical == ROOT+lang+'/'+page+'/', canonical
            for alt in ('fr','en','ar','es','x-default'):
                assert len(b.find_elements('css selector','link[hreflang="'+alt+'"]')) == 1, (lang,page,alt)
            print('METADATA PASS',lang,page,flush=True)
    for width,height in ((390,844),(1366,900)):
        b.set_window_size(width,height)
        for page in META['en']:
            b.get(ROOT+'en/'+page+'/?international-check='+str(time.time_ns()))
            planning = b.find_element('id','international-trip-planning')
            assert len(planning.find_elements('css selector','details')) == 3
            for summary in planning.find_elements('css selector','summary'):
                b.execute_script('arguments[0].scrollIntoView({block:"center",behavior:"instant"})',summary)
                summary.click()
            assert all(p.is_displayed() for p in planning.find_elements('css selector','p'))
            link = planning.find_element('css selector','a[href*="wa.me"]')
            url = urlparse(link.get_attribute('href'))
            assert url.netloc=='wa.me' and url.path=='/212667772551'
            assert 'Imsfrane' in parse_qs(url.query)['text'][0]
            assert b.execute_script('return document.documentElement.scrollWidth<=document.documentElement.clientWidth+2'), (page,width)
            if page == 'vtt':
                assert '150 MAD per bike' in planning.text
                assert len(b.find_elements('css selector','main article')) == 5
            if page == 'rafting':
                assert len(b.find_elements('id','raftingExperienceFrame')) == 1
            b.execute_script('arguments[0].scrollIntoView({block:"start",behavior:"instant"})',planning)
            b.save_screenshot(str(OUT/(page+'-'+str(width)+'.png')))
            print('PLANNING PASS',page,width,flush=True)
print('PASS: 16 activity metadata checks; four English visitor sections on mobile and desktop',flush=True)
