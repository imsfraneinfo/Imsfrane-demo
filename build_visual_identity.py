"""Apply the Ahansal & Atlas identity to generated demo pages only.

Brand colours in styles are transformed; photographs, logos, content and scripts
are left intact. This final build step is deliberately reversible.
"""
from pathlib import Path
import colorsys,re,json

ROOT=Path('public')
HEX=re.compile(r'(?<![\w/\-])#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})\b')
EXACT={'123e48':'123e48','c46a45':'c46a45','a94f30':'a94f30','f6f1e8':'f6f1e8',
 'c6a43f':'c46a45','9e832b':'a94f30','d7b66e':'dba287','d7b865':'c46a45',
 '19382f':'123e48','193b30':'123e48','143c30':'123e48','173d31':'123e48',
 'f7f5ef':'f6f1e8','f5f3ec':'f6f1e8','f8f6ef':'f6f1e8','fbfaf6':'fffdf9',
 '09291e':'10333c','0d2926':'10333c','12473c':'185260','e5b946':'c46a45'}

def rgb(hexcode):return tuple(int(hexcode[i:i+2],16)/255 for i in (0,2,4))
def ashex(values):return ''.join(f'{max(0,min(255,round(v*255))):02x}' for v in values)
def recolour(code):
 # Expand shorthand; preserve opacity exactly.
 if len(code) in (3,4):code=''.join(v*2 for v in code)
 base,alpha=code[:6].lower(),code[6:]
 if base in EXACT:return EXACT[base]+alpha
 r,g,b=rgb(base);h,l,s=colorsys.rgb_to_hls(r,g,b);deg=h*360
 if 30<=deg<=65 and s>=.22 and .16<l<.94:
  # Old brass/gold -> copper; keep pale tints and readable dark accents.
  return ashex(colorsys.hls_to_rgb(18/360,l,min(s,.57)))+alpha
 if 80<=deg<=180 and .08<=s<=.88 and l<.68:
  # Forest tones and their text/shadows -> petroleum blue.
  return ashex(colorsys.hls_to_rgb(192/360,l,min(.60,max(.14,s))))+alpha
 if 45<=deg<=180 and .78<l<.99 and s<.48:
  # Sage/cream surfaces -> warm sand.
  return ashex(colorsys.hls_to_rgb(39/360,l,min(.42,max(.16,s))))+alpha
 return base+alpha

def transform(css):
 css=HEX.sub(lambda m:'#'+recolour(m[1]),css)
 def rgba(m):
  r,g,b=map(int,m.group(2,3,4));alpha=m[5] or ''
  original=f'{r:02x}{g:02x}{b:02x}';changed=recolour(original)
  if original==changed:return m[0]
  values=[int(changed[i:i+2],16) for i in (0,2,4)]
  return m[1]+'('+','.join(map(str,values))+alpha+')'
 return re.sub(r'\b(rgba?)\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(,\s*[.\d]+\s*)?\)',rgba,css)

OVERRIDES='''
/* Ahansal & Atlas — demo palette */
:root{--primary:#123e48;--primary-color:#123e48;--dark:#10333c;--gold:#c46a45;--accent:#c46a45;--accent-color:#c46a45;--light:#f6f1e8;--identity-petrol:#123e48;--identity-copper:#c46a45;--identity-paper:#f6f1e8}
body{background-color:#f6f1e8;color:#193a42}
body.atnav-ready #siteHeader{background:#10333cf2!important;border-bottom-color:#c46a4555!important}
body.atnav-ready #siteHeader .brand-content small{color:#e3b79f!important}
.hp-home{--hp-night:#10333c;--hp-forest:#185260;--hp-gold:#dba287;--hp-cream:#f6f1e8;--hp-ink:#123e48;--hp-border:#e1d8cc}
html:not([lang=ar]) main :is(h1,h2){font-family:'Cormorant Garamond',Georgia,serif}
html[lang=ar] main :is(h1,h2,h3){font-family:inherit}
main :is(.btn,.hp-button,.hp-btn,.wo-btn,.camp-btn,.quad-r-btn,.vt-button,.bp-button){border-radius:11px}
main :is(.hp-button-gold,.hp-button-primary,.hp-btn-primary,.quad-r-gold,.camp-btn:not(.ghost),.wo-btn),.team-about .team-contact a{background:#a94f30!important;border-color:#a94f30!important;color:#fff!important}
main :is(.hp-button-gold,.hp-button-primary,.hp-btn-primary,.quad-r-gold,.camp-btn:not(.ghost),.wo-btn):hover,.team-about .team-contact a:hover{background:#8d3e25!important;border-color:#8d3e25!important}
.hp-home .hp-kicker,.team-about .chapter,.team-about .tag{color:#995035}
.team-about .company-block .chapter{color:#e6bda8}
.team-about .person-info{border-top-color:#c46a45}.team-about .person-info p{color:#995035}
.team-about .person-card,.hp-home .hp-activity{box-shadow:0 8px 24px #123e480d}
main :is(a,button,input,select,textarea):focus-visible{outline-color:#a94f30}
::selection{background:#dba287;color:#10333c}
'''

def build(root=ROOT):
 cssfiles=0;pages=0;changes=0
 for p in root.rglob('*.css'):
  if any(x in p.name.lower() for x in ('bootstrap','fontawesome','font-awesome','animate','swiper','all.min')):continue
  if p.name=='visual-identity.css':continue
  s=p.read_text();t=transform(s)
  if t!=s:p.write_text(t);changes+=1
  cssfiles+=1
 for p in root.rglob('*.html'):
  if any(x in p.parts for x in ('admin',)):continue
  s=p.read_text()
  # Restrict recolouring to actual CSS, never page text, JS or image bytes.
  s=re.sub(r'(<style\b[^>]*>)(.*?)(</style>)',lambda m:m[1]+transform(m[2])+m[3],s,flags=re.S|re.I)
  s=re.sub(r'(\bstyle=)(["\'])(.*?)\2',lambda m:m[1]+m[2]+transform(m[3])+m[2],s,flags=re.S|re.I)
  s=re.sub(r'<link[^>]*href=["\'][^"\']*visual-identity.css[^"\']*["\'][^>]*>','',s)
  if '</head>' in s:
   s=s.replace('</head>','<link rel="stylesheet" href="/Imsfrane-demo/visual-identity.css?v=ahansal1"></head>',1)
   p.write_text(s);pages+=1
 (root/'visual-identity.css').write_text(OVERRIDES)
 print(f'Ahansal & Atlas: {pages} pages, {changes}/{cssfiles} brand stylesheets; images and scripts unchanged.')

if __name__=='__main__':build()
