"""Give the three rafting photo numbers consistent, legible display type."""
from pathlib import Path
import re

STYLE = '''<style id="rafting-route-number-type">
.route-visual .num{
 font-family:"Montserrat",Arial,sans-serif!important;
 font-weight:800!important;
 font-size:clamp(56px,5.6vw,76px)!important;
 font-style:normal!important;
 font-variant-numeric:lining-nums tabular-nums;
 letter-spacing:-.055em!important;
 line-height:1!important;
 color:#fff!important;
 -webkit-text-stroke:1px rgba(7,28,35,.4);
 text-shadow:0 2px 3px rgba(7,28,35,.7),0 6px 24px rgba(7,28,35,.55);
 right:18px!important;bottom:14px!important;
 direction:ltr;white-space:nowrap;
}
html[lang="ar"] body .route-visual .num{font-family:"Montserrat",Arial,sans-serif!important;font-weight:800!important;line-height:1!important;letter-spacing:-.055em!important}
@media(max-width:650px){.route-visual .num{font-size:58px!important;right:15px!important;bottom:12px!important}}
</style>'''

def build(root):
 for lang in ('fr','en','ar','es'):
  suffix='' if lang=='fr' else '-'+lang
  path=Path(root)/('rafting-content'+suffix+'.html')
  html=path.read_text(encoding='utf-8')
  assert len(re.findall(r'<span class="num">0[123]</span>',html))==3,path
  html=re.sub(r'<style id="rafting-route-number-type">.*?</style>','',html,flags=re.S)
  html=html.replace('</head>',STYLE+'</head>',1)
  path.write_text(html,encoding='utf-8')
 print('Rafting photo numbers: Montserrat ExtraBold, four languages')

if __name__=='__main__':
 import sys
 build(sys.argv[1] if len(sys.argv)>1 else 'public')
