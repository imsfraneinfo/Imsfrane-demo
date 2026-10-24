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
 if base in ('25d366','22c55e','16a34a','15803d','4caf50','28a745'):return base+alpha
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
 css=re.sub(r'\b(rgba?)\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(,\s*[.\d]+\s*)?\)',rgba,css)
 # Foreground text needs a darker copper/muted tone on sand than decorative
 # borders do. Keep pale text intact; dark sections receive explicit overrides.
 def foreground(m):
  token=m[2];code=token[1:]
  if len(code)==3:code=''.join(v*2 for v in code)
  if len(code)!=6:return m[0]
  h,l,sat=colorsys.rgb_to_hls(*rgb(code));degree=h*360
  if 8<=degree<=30 and .32<l<.70:return m[1]+'#995035'
  if .36<l<.68 and sat<.36:return m[1]+'#4c6269'
  return m[0]
 css=re.sub(r'((?<![\w-])color\s*:\s*)(#[0-9a-fA-F]{3,8})\b',foreground,css)
 # Gold variables are also used for primary action surfaces in older layouts.
 def button_surface(m):
  text=m[0]
  if re.search(r'background(?:-color)?\s*:\s*(?:#[cC]46[aA]45|var\(--[\w-]*(?:gold|accent)[\w-]*\))\s*[;!}]',text):
   text=text[:-1]+';background:#a94f30;color:#fff!important;}'
  return text
 return re.sub(r'[^{}]+\{[^{}]*\}',button_surface,css)

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
main :is(.btn-gold,.hp-button-gold,.hp-button-primary,.hp-btn-primary,.quad-r-gold,.camp-btn:not(.ghost),.wo-btn),.team-about .team-contact a{background:#a94f30!important;border-color:#a94f30!important;color:#fff!important}
main :is(.btn-gold,.hp-button-gold,.hp-button-primary,.hp-btn-primary,.quad-r-gold,.camp-btn:not(.ghost),.wo-btn):hover,.team-about .team-contact a:hover{background:#8d3e25!important;border-color:#8d3e25!important}
.hp-home .hp-kicker,.team-about .chapter,.team-about .tag{color:#995035}
.team-about .company-block .chapter{color:#e6bda8}
.team-about .person-info{border-top-color:#c46a45}.team-about .person-info p{color:#995035}
.team-about .person-card,.hp-home .hp-activity{box-shadow:0 8px 24px #123e480d}
main :is(a,button,input,select,textarea):focus-visible{outline-color:#a94f30}
.floating-whatsapp{background:#087b3c!important;color:#fff!important}\n::selection{background:#dba287;color:#10333c}
.quad-r-hero .quad-r-copy h1{color:#fff!important}
.quad-r-hero .quad-r-copy h1 em{color:#e3ad92!important}
:is(.pricebox,.cta,.end) :is(h1,h2,h3,p){color:#fff!important}
:is(.quad-r-hero,.vt-hero,.camp-hero,.bp-hero,.ky-hero,.hp-hero,.pricebox,.cta,.end,.ky-season,.company-block) :is(.eyebrow,.kicker,.camp-ey,.ky-eyebrow,.gp-section-label,.pw-eyebrow,.chapter,.tag){color:#e6bda8!important}
main :is(.btn:not(.alt):not(.ghost):not(.btn-line):not(.btn-outline),.pw-btn-primary),.demo-rebuild-actions a,.demo-rebuild-form button{background:#a94f30!important;color:#fff!important;border-color:#a94f30!important}
:is(.hp-kicker,.camp-ey,.ky-eyebrow,.gp-section-label,.pw-eyebrow,.journal-kicker,.memories-kicker){color:#995035}
.ky-season .ky-eyebrow,.end .kicker{color:#e6bda8!important}
.eyebrow{color:#995035!important}
.page-randonnee .hero :is(.eyebrow,em),.page-randonnee .hero .stats strong{color:#e6bda8!important}
.camp-page .camp-hero h1 em,.camp-cta .camp-ey,.demo-editorial-hero .demo-editorial-eyebrow,.hp-season-inner .hp-kicker{color:#e6bda8!important}
.pricebox .amount,.ims-privacy-link{color:#e6bda8!important}
body.page-randonnee main.rando .hero .eyebrow,body.page-randonnee main.rando .hero .stats strong{color:#e6bda8!important}
body.atnav-ready .footer-bottom .ims-privacy-link{color:#e6bda8!important}
.weekend-program .pw-eyebrow{color:#995035!important}
.weekend-program .pw-hero .pw-eyebrow,.weekend-program .pw-price-card .pw-eyebrow{color:#e6bda8!important}
.kayak-page .ky-final .ky-eyebrow,.ib-bivouac .ib-copy .ib-kicker{color:#e6bda8!important}
#imsfrane-booking .bp-note{color:#4c6269!important}
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
  # The source CSS filenames are stable. Bust them when preview colours change,
  # including embedded activity pages, so phones do not mix two identities.
  def bust_css(m):
   url=m[2]
   if url.startswith(('https:','http:','//')):return m[0]
   url=re.sub(r'([?&])identity=[^&]*',r'\1',url).rstrip('?&')
   return m[1]+url+('&' if '?' in url else '?')+'identity=contrast7'+m[3]
  s=re.sub(r'(\bhref=["\'])([^"\']+\.css(?:\?[^"\']*)?)(["\'])',bust_css,s)
  def bust_frame(m):
   url=m[2]
   if url.startswith(('https:','http:','//')):return m[0]
   url=re.sub(r'([?&])identity=[^&]*',r'\1',url).rstrip('?&')
   return m[1]+url+('&' if '?' in url else '?')+'identity=contrast7'+m[3]
  s=re.sub(r'(<iframe\b[^>]*\bsrc=["\'])([^"\']+)(["\'])',bust_frame,s,flags=re.I)
  if '</head>' in s:
   s=s.replace('</head>','<link rel="stylesheet" href="/Imsfrane-demo/visual-identity.css?v=contrast7"></head>',1)
   p.write_text(s);pages+=1
 (root/'visual-identity.css').write_text(OVERRIDES)
 print(f'Ahansal & Atlas: {pages} pages, {changes}/{cssfiles} brand stylesheets; images and scripts unchanged.')

if __name__=='__main__':build()
