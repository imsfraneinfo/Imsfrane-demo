"""Demo-only team section; portraits and names supplied by the team."""
from pathlib import Path
import base64, re, html

BASE='/Imsfrane-demo/'
PEOPLE=[('farid-laydi','Farid Laydi','فريد العيدي'),('hamid-laydi','Hamid Laydi','حميد العيدي'),('ayoub-laydi','Ayoub Laydi','أيوب العيدي'),('abdelaziz-allam','Abdelaziz Allam','عبد العزيز علام'),('hassan-allam','Hassan Allam','حسن علام')]
COPY={
 'fr':dict(kicker='LES VISAGES DERRIÈRE L’AVENTURE',title='Notre équipe, l’esprit d’aventure.',intro='Nous partageons la même passion pour la nature et l’aventure. Randonnée en montagne, rafting ou VTT : notre équipe vous accompagne sur le terrain et prépare chaque séjour ensemble, du premier échange à l’accueil, en passant par le campement et les repas. Un travail collectif pour vous faire découvrir Imsfrane au plus près de ses habitants.',founder='Fondateur',manager='Responsable',company='Une aventure portée par une équipe locale et par Ichou Adventures, la société fondée par Farid Laydi.',see='Rencontrer notre équipe',skills=['Randonnée','Rafting','VTT']),
 'en':dict(kicker='THE PEOPLE BEHIND THE ADVENTURE',title='Our team, the spirit of adventure.',intro='We share a passion for nature and adventure. Whether hiking in the mountains, rafting or mountain biking, our team guides you outdoors and prepares each stay together, from the first conversation to welcoming you, setting up camp and preparing meals. We work as one team to help you discover Imsfrane and meet its people.',founder='Founder',manager='Manager',company='An adventure brought to life by a local team and Ichou Adventures, the company founded by Farid Laydi.',see='Meet our team',skills=['Hiking','Rafting','Mountain biking']),
 'es':dict(kicker='LAS PERSONAS DETRÁS DE LA AVENTURA',title='Nuestro equipo, el espíritu de aventura.',intro='Compartimos la pasión por la naturaleza y la aventura. Senderismo, rafting o BTT: nuestro equipo os acompaña y prepara cada estancia en conjunto, desde el primer contacto hasta la bienvenida, el campamento y las comidas. Trabajamos unidos para descubrir Imsfrane de cerca y conocer a su gente.',founder='Fundador',manager='Responsable',company='Una aventura impulsada por un equipo local e Ichou Adventures, la empresa fundada por Farid Laydi.',see='Conoce al equipo',skills=['Senderismo','Rafting','BTT']),
 'ar':dict(kicker='الناس وراء المغامرة',title='فريقنا، روح المغامرة.',intro='حنا فريق كيجمعنا شغف الطبيعة والمغامرة، وكنرافقو الزوار فالروندوني الجبلية، الرافتينغ وجولات VTT. كنتقاسمو تنظيم الرحلات واستقبال الضيوف وتجهيز المخيم والوجبات، وكنخدمو بروح واحدة باش تكون كل تجربة منظّمة، دافئة وقريبة من أهل المنطقة.',founder='المؤسس',manager='مسيّر',company='مبادرة بروح فريق محلي، إلى جانب شركة Ichou Adventures اللي أسّسها فريد العيدي.',see='تعرّف على فريقنا',skills=['الروندوني الجبلية','الرافتينغ','الدراجات الجبلية'])
}
CSS='''
.aboutx .team-section{padding:65px 0 70px;background:#f5f3ec;scroll-margin-top:90px}.aboutx .team-heading{max-width:820px;margin-bottom:30px}.aboutx .team-heading .tag{font-size:10px;letter-spacing:.14em;color:#927633}.aboutx .team-heading h2{font-size:clamp(35px,4.3vw,54px);margin:12px 0 20px;color:#19382f}.aboutx .team-heading p{font-size:14px;line-height:1.95;color:#536356;margin:0}.aboutx .team-skills{display:flex;gap:9px;flex-wrap:wrap;margin:24px 0 0;padding:0;list-style:none}.aboutx .team-skills li{padding:7px 14px;border:1px solid #d7ddce;border-radius:30px;font-size:11px;color:#3a5542;background:#fbfaf6}.aboutx .people-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:28px 24px}.aboutx .person-card{grid-column:span 2;min-width:0;background:#fff;border:1px solid #e1e3d9;border-radius:14px;overflow:hidden;box-shadow:0 8px 25px #19382f06}.aboutx .person-card:nth-child(4){grid-column:2/span 2}.aboutx .person-card:nth-child(5){grid-column:4/span 2}.aboutx .person-portrait{aspect-ratio:4/5;overflow:hidden;background:#dbe6e7}.aboutx .person-portrait img{display:block;width:100%;height:100%;object-fit:cover;object-position:center 37%;transition:transform .35s ease}.aboutx .person-card:first-child img{object-position:36% 40%}.aboutx .person-info{padding:21px 22px 23px;border-top:3px solid #c6a43f}.aboutx .person-info h3{font-family:Montserrat,Arial,sans-serif;font-size:18px;line-height:1.4;letter-spacing:-.025em;color:#19382f;margin:0 0 6px}.aboutx .person-info p{font-size:12px;color:#7f692f;margin:0;line-height:1.6}.aboutx .team-company{font-size:12px;line-height:1.9;color:#61705f;margin:27px 0 0;text-align:center}.aboutx .hero{min-height:500px}.aboutx .hero h1{font-size:clamp(52px,6vw,85px)}html[dir=rtl] .aboutx .person-info h3{font-family:inherit;letter-spacing:0}html[dir=rtl] .aboutx .team-heading h2{font-family:inherit;font-size:clamp(30px,4vw,43px);line-height:1.6}html[dir=rtl] .aboutx .team-heading .tag{letter-spacing:0}
@media(max-width:700px){.aboutx .team-section{padding:38px 0 44px}.aboutx .team-heading{margin-bottom:24px}.aboutx .team-heading h2{font-size:36px}.aboutx .team-heading p{font-size:13px;line-height:1.95}.aboutx .people-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:15px 12px}.aboutx .person-card,.aboutx .person-card:nth-child(4),.aboutx .person-card:nth-child(5){grid-column:auto}.aboutx .person-card:last-child{grid-column:1/-1;width:calc((100% - 12px)/2);justify-self:center}.aboutx .person-info{padding:14px 11px 16px}.aboutx .person-info h3{font-size:14px;min-height:40px;display:flex;align-items:center}.aboutx .person-info p{font-size:11px}.aboutx .team-company{text-align:start;font-size:11px}.aboutx .hero{min-height:0}}
@media(prefers-reduced-motion:reduce){.aboutx .person-portrait img{transition:none}}
'''

def build(root=Path('public')):
 target=root/'images'/'team';target.mkdir(parents=True,exist_ok=True)
 for slug,_,_ in PEOPLE:
  payload=Path('team-portraits',slug+'.webp.b64').read_text().strip()
  (target/(slug+'.webp')).write_bytes(base64.b64decode(payload,validate=True))
 (root/'about-team.css').write_text(CSS)
 for lang,c in COPY.items():
  path=root/lang/'about'/'index.html';source=path.read_text()
  cards=[]
  for n,(slug,latin,arabic) in enumerate(PEOPLE):
   name=arabic if lang=='ar' else latin;role=c['founder'] if n==0 else c['manager']
   cards.append(f'<article class="person-card"><div class="person-portrait"><img src="{BASE}images/team/{slug}.webp" alt="{html.escape(name)}" width="720" height="960" loading="lazy" decoding="async"></div><div class="person-info"><h3>{name}</h3><p>{role}</p></div></article>')
  section=f'''<section class="team-section" id="our-team" aria-labelledby="team-title"><div class="wrap"><div class="team-heading"><div class="tag">{c['kicker']}</div><h2 id="team-title">{c['title']}</h2><p>{c['intro']}</p><ul class="team-skills">{''.join('<li>'+s+'</li>' for s in c['skills'])}</ul></div><div class="people-grid">{''.join(cards)}</div><p class="team-company">{c['company']}</p></div></section>'''
  # Replace only the former anonymous team gallery, preserve the rest of About.
  sections=list(re.finditer(r'<section\b[^>]*>.*?</section>',source,re.S))
  old=next((m for m in sections if 'class="team-grid"' in m[0] or 'id="our-team"' in m[0]),None)
  assert old,f'Team section not found: {lang}'
  source=source[:old.start()]+section+source[old.end():]
  source=re.sub(r'(<a\b[^>]*href=")#story("[^>]*>).*?</a>',lambda m:m[1]+'#our-team'+m[2]+c['see']+'</a>',source,count=1,flags=re.S)
  source=source.replace('</head>',f'<link rel="stylesheet" href="{BASE}about-team.css?v=team1"></head>',1)
  path.write_text(source)
 print('Built equal-sized cards for 5 team members × 4 languages.')

if __name__=='__main__':build()
