"""Build the demo desktop navigation from the translated mobile links."""
from html import escape
from pathlib import Path
import re
import shutil

from bs4 import BeautifulSoup


SOURCE = Path(__file__).resolve().parent


def menu_link(link):
    current = ' aria-current="page"' if link.get('aria-current') == 'page' else ''
    return f'<a href="{escape(link["href"])}"{current}>{escape(link.get_text(" ", strip=True))}</a>'


def dropdown(label, links):
    items = ''.join(menu_link(link) for link in links)
    return (f'<details class="atnav-desktop-group" name="desktop-navigation">'
            f'<summary>{escape(label)}</summary><div class="atnav-desktop-panel">{items}</div></details>')


def desktop_menu(drawer):
    home = drawer.select_one('nav > a.atnav-item')
    activities = drawer.select_one('#atnavActivities')
    accommodation = drawer.select_one('#atnavAccommodation')
    trip_links, info_links = drawer.select('.atnav-secondary')
    programme = trip_links.select_one('a')
    guide = info_links.select_one('a[href$="/guide/"], a[href$="guide.html"]')
    contact = info_links.select_one('a[href$="/contact/"], a[href$="contact.html"]')
    more = [link for link in info_links.select('a') if link is not guide and link is not contact]
    more_label = info_links.find_previous_sibling(class_='atnav-label').get_text(' ', strip=True)
    book = drawer.select_one('.atnav-book')
    groups = [menu_link(home)]
    for toggle in (activities, accommodation):
        links = drawer.find(id=toggle['aria-controls']).select('a')
        groups.append(dropdown(toggle.get_text(' ', strip=True), links))
    groups.extend((menu_link(programme), menu_link(guide), dropdown(more_label, more), menu_link(contact)))
    groups.append(f'<span class="atnav-desktop-book">{menu_link(book)}</span>')
    return f'<nav class="atnav-desktop atnav-desktop-demo" aria-label="{escape(drawer["aria-label"])}">{"".join(groups)}</nav>'


def build(root):
    for asset in ('fullscreen-menu.css', 'demo-desktop-menu.js'):
        shutil.copyfile(SOURCE / asset, root / asset)
    for page in root.rglob('*.html'):
        html = page.read_text(encoding='utf-8')
        if 'id="atnavDrawer"' not in html or 'atnav-desktop-demo' in html:
            continue
        soup = BeautifulSoup(html, 'html.parser')
        drawer = soup.find(id='atnavDrawer')
        activity_list = drawer.select_one('#atnavActivityList ul')
        if not activity_list.select_one('a[href*="kayak"]'):
            rafting = activity_list.select_one('a[href*="rafting"]')
            kayak = soup.new_tag('a', href=rafting['href'].replace('rafting', 'kayak'))
            kayak.string = 'كاياك' if soup.html.get('lang') == 'ar' else 'Kayak'
            if page.parent.name == 'kayak' or page.name == 'kayak.html':
                kayak['aria-current'] = 'page'
            rafting.insert_after(kayak)
        menu = desktop_menu(drawer)
        html, replaced = re.subn(r'<nav\b[^>]*class="atnav-desktop"[^>]*>.*?</nav>', lambda _: menu, html, count=1, flags=re.S)
        if not replaced:
            html = html.replace('<div class="atnav-article-actions">', menu + '<div class="atnav-article-actions">', 1)
        if 'atnav-desktop-demo' not in html:
            raise ValueError(f'Missing desktop menu insertion point in {page}')
        html = html.replace('</head>', '<link rel="stylesheet" href="/Imsfrane-demo/fullscreen-menu.css?v=3">\n</head>', 1)
        html = html.replace('</body>', '<script defer src="/Imsfrane-demo/demo-desktop-menu.js?v=3"></script>\n</body>', 1)
        page.write_text(html, encoding='utf-8')
