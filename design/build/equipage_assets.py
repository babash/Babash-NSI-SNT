"""Écrit les portraits de l'équipage (SVG) et assets/equipage.js pour le site."""
import json, sys
sys.path.insert(0, '/tmp/design/equipage')
from runners import RUNNERS, PROFILS, portrait
D = '/home/claude/babash-nsi-snt/assets/equipage/'
for r in RUNNERS:
    for mode in ('nuit', 'trait'):
        svg = portrait(r, mode, uid=r['id'] + '-' + mode)
        open(D + f"{r['id']}-{mode}.svg", 'w').write(svg)
GENRE = {'f': 'elle', 'm': 'il', 'n': None}
data = [dict(id=r['id'], nom=r['nom'], profil=PROFILS[r['profil']]['nom'], glyphe=PROFILS[r['profil']]['glyphe'], neon=PROFILS[r['profil']]['neon'],
             encre=PROFILS[r['profil']]['encre'], specialite=r['specialite'], capacite=r['capacite'],
             replique=r['replique'], stats=r['stats']) for r in RUNNERS]
profils = {k: dict(nom=v['nom'], devise=v['devise'], neon=v['neon'], encre=v['encre']) for k, v in PROFILS.items()}
js = open('/tmp/design/build/equipage.tpl.js').read().replace('/*DONNEES*/[]', json.dumps(data, ensure_ascii=False, indent=1)).replace('/*PROFILS*/{}', json.dumps(profils, ensure_ascii=False))
open('/home/claude/babash-nsi-snt/assets/equipage.js', 'w').write(js)
print(len(data), 'runners')
