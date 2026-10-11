"""Real Chrome checks on published Imsfrane Demo in FR/EN/AR/ES.

Only reads the Demo GitHub Pages site. Does not access or modify imsfrane.com.
This complements qa_arabic_browser.py, which decodes the actual Arabic fonts.
"""
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import json

ROOT = "https://imsfraneinfo.github.io/Imsfrane-demo/"
LANGS = ("fr", "en", "ar", "es")
PAGES = ("index.html", "rafting.html", "camping.html", "blog.html", "booking.html")
OUT = Path("four-language-browser-diagnostics")
OUT.mkdir(exist_ok=True)

opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--disable-background-networking")
opts.add_argument("--hide-scrollbars")
opts.page_load_strategy = "eager"
results = []
with webdriver.Chrome(options=opts) as browser:
    browser.set_page_load_timeout(55)
    browser.set_script_timeout(35)
    for screen, width, height in (("mobile", 390, 844), ("desktop", 1366, 900)):
        browser.set_window_size(width, height)
        for page in PAGES:
            baseline = None
            for lang in LANGS:
                url = ROOT + lang + "/" + page + "?four-language-browser-qa=1"
                try:
                    browser.get(url)
                    WebDriverWait(browser, 35).until(
                        lambda d: d.execute_script(
                            "return document.readyState !== 'loading' && "
                            "!!document.querySelector('main') && "
                            "document.body.getAttribute('data-lang') === arguments[0]",
                            lang,
                        )
                    )
                    state = browser.execute_script("""
                        const root=document.documentElement,main=document.querySelector('main');
                        const menu=[...document.querySelectorAll('.atnav-langmini')];
                        const links=[...document.querySelectorAll('.atnav-langmini-panel a[lang]')]
                          .map(a=>({lang:a.lang,href:a.getAttribute('href')}));
                        return {
                          lang:root.lang,dir:root.dir,
                          mainDirection:getComputedStyle(main).direction,
                          menuCount:menu.length,links:links,
                          activityCount:document.querySelectorAll('.atnav-submenu-link').length,
                          sections:main.querySelectorAll('section').length,
                          images:[...main.querySelectorAll('img[src]')]
                            .map(img=>img.getAttribute('src')),
                          forms:main.querySelectorAll('form').length,
                          width:root.clientWidth,scrollWidth:root.scrollWidth,
                          script:[...document.scripts].map(s=>s.getAttribute('src')||'')
                            .filter(s=>s.includes('/js/core')),
                          arabicCss:!!document.querySelector('link[href*="arabic-pro.css"]')
                        };
                    """)
                    expected_dir = "rtl" if lang == "ar" else "ltr"
                    expected_core = "core-multilingual-v2.js" if lang in ("ar", "es") else "core.min.js"
                    assert (state["lang"], state["dir"]) == (lang, expected_dir), state
                    assert state["mainDirection"] == expected_dir, state
                    assert state["menuCount"] == 1 and state["activityCount"] == 6, state
                    assert len(state["links"]) == 4, state
                    assert {link["lang"] for link in state["links"]} == set(LANGS), state
                    for link in state["links"]:
                        assert link["href"] == "../" + link["lang"] + "/" + page, state
                    assert len(state["script"]) == 1 and expected_core in state["script"][0], state
                    assert state["arabicCss"] == (lang == "ar"), state
                    fingerprint = (state["sections"], state["images"], state["forms"])
                    if lang == "fr":
                        baseline = fingerprint
                    else:
                        assert fingerprint == baseline, (
                            "Page sections, image sources or forms differ from original FR design",
                            screen, page, lang
                        )
                    if page == "index.html":
                        browser.save_screenshot(str(OUT / (screen + "-" + lang + "-home.png")))
                    record = {
                        "viewport": screen, "page": page, "language": lang,
                        "direction": state["dir"], "mainDirection": state["mainDirection"],
                        "sections": state["sections"], "images": len(state["images"]),
                        "forms": state["forms"], "width": state["width"],
                        "scrollWidth": state["scrollWidth"],
                        "core": state["script"][0]
                    }
                    print("CHROME FOUR LANGUAGES", json.dumps(record, ensure_ascii=False), flush=True)
                    results.append(record)
                except Exception:
                    browser.save_screenshot(str(OUT / (screen + "-" + lang + "-" + page + "-FAIL.png")))
                    raise
(OUT / "results.json").write_text(
    json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
)
assert len(results) == 2 * len(PAGES) * len(LANGS), len(results)
print("PASS", len(results), "actual Chrome page/language/viewport checks", flush=True)
