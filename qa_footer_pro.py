"""Check the shared footer, all local destinations and Arabic phone isolation."""
from pathlib import Path
import json,re
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
ROOT=Path('public');BASE='/Imsfrane-demo/'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.refs=[];self.phone=[];self.bdis=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a':self.refs.append(a.get('href',''))
  if tag=='bdi' and 'fp-ltr' in a.get('class','').split():self.bdis.append(a)
def check():
 report=json.loads((ROOT/'footer-build-report.json').read_text());bylang={};count=0
 for name in report['pages']:
  p=ROOT/name;source=p.read_text();fs=re.findall(r'<footer\b.*?</footer\s*>',source,re.S|re.I)
  assert len(fs)==1,(name,'duplicate footer')
  f=fs[0];assert 'id="ims-footer"' in f,name
  lang=re.search(r'\blang="(fr|en|ar|es)"',f)[1]
  if lang in bylang:assert bylang[lang]==f,(name,'footer differs')
  else:bylang[lang]=f
  assert 'مسفران كاتدرائية' not in f and 'مسفران كاتدرال' not in f,name
  assert f.count('href="tel:+212667772551"')==1,name
  assert '<bdi class="fp-contact-value fp-ltr" dir="ltr">+212 667 772 551</bdi>' in f,name
  assert f.count('class="ims-privacy-link"')==1,name
  assert source.count('footer-pro.css?v=1')==1,name
  assert source.count('footer-pro.js?v=1')==1,name
  assert json.loads((ROOT/f'footer-pro-content-{lang}.json').read_text())['html']==f,name
  parser=Links();parser.feed(f)
  for href in parser.refs:
   if not href.startswith(BASE):continue
   path=ROOT/unquote(urlsplit(href).path.removeprefix(BASE))
   assert path.is_file() or (path/'index.html').is_file(),(name,href)
  count+=1
 assert set(bylang)=={'fr','en','ar','es'}
 assert count>100
 css=(ROOT/'footer-pro.css').read_text();assert 'direction:ltr!important;unicode-bidi:isolate!important' in css
 print(f'PASS: {count} pages, 4 identical localized footer templates, all internal links exist, phone +212 667 772 551 isolated LTR.')
if __name__=='__main__':check()
