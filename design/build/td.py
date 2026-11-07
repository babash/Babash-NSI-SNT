"""Met un TD de POO à la charte : retire les polices embarquées et la feuille
de style intégrée, relie charte.css + fiche.css, harmonise barre d'outils,
couleurs des schémas et ajoute le runner du bloc titre. Texte inchangé."""
import re, sys
sys.path.insert(0, '/tmp/design/equipage')
from runners import RUNNERS, portrait
R = {r['id']: r for r in RUNNERS}

src, dst, runner = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding='utf-8').read()

# 1. En-tête : feuilles de style communes à la place du <style> intégré (polices comprises)
s = re.sub(r'<style>.*?</style>', '<link rel="stylesheet" href="../../assets/charte.css">\n'
           '<link rel="stylesheet" href="../../assets/fiche.css">\n'
           '<script src="../../assets/fiche.js" defer></script>', s, count=1, flags=re.S)
s = s.replace('<body>', '<body class="niv-tle dense">', 1)

# 2. Barre d'outils standard
m = re.search(r'<div class="toolbar">(.*?)</div>', s, re.S)
back = re.search(r'<a class="back"[^>]*>.*?</a>', m.group(1), re.S).group(0)
proj = ('<button type="button" data-action="projeter" aria-pressed="false"><svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="3" width="20" height="14"/><path d="M8 21h8M12 17v4"/></svg> <span class="libelle">Projeter</span></button>')
impr = re.search(r'<button[^>]*onclick="window.print\(\)"[^>]*>(.*?)</button>', m.group(1), re.S).group(1)
aide = re.search(r'<span>(Format A4.*?)</span>', m.group(1), re.S).group(1)
s = s.replace(m.group(0), '<nav class="toolbar" aria-label="Outils">%s%s<button type="button" class="principal" data-action="imprimer">%s</button><span class="aide">%s</span></nav>'
              % (back, proj, impr, aide), 1)

# 3. Anciennes variables et couleurs codées en dur → jetons de la charte
for a, b in [('var(--cours-bg)', 'var(--essentiel-fond)'), ('var(--cours)', 'var(--essentiel)'),
             ('var(--hint-bg)', 'var(--pouce-fond)'), ('var(--hint)', 'var(--pouce)'),
             ('var(--ink-2)', 'var(--encre-2)'), ('var(--ink)', 'var(--encre)'),
             ('#1b2230', '#0B1020'), ('#c7ccd4', '#C9D0DC'), ('#f3f6fa', '#F1F3F7'), ('#7b8390', '#586276')]:
    s = s.replace(a, b)

# 4. Runner guide : au début de la frise du bloc titre
r = R[runner]
art = portrait(r, 'trait', uid=runner + '-td', badge=True)
guide = '<div class="tb-guide">%s<span><b>%s</b></span></div>' % (art, r['nom'])
s = re.sub(r'(<ol class="frise">.*?</ol>)', lambda m: '<div class="tb-piste">%s%s</div>' % (guide, m.group(1)), s, count=1, flags=re.S)
open(dst, 'w', encoding='utf-8').write(s)
print(dst, len(s))
