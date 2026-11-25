#!/usr/bin/env python3
"""Essais des outils des TD (T123c) : ils doivent voir une fuite, et ne rien voir sur une feuille saine.

Usage (à la racine du dépôt) : python3 -I charte/tester-outils.py

1. imprimer-td.py sur le gabarit : « PDF vierge : oui ».
2. Témoins de fuite (pages temporaires, effacées ensuite, à côté de la page d'origine) : la page avec une règle
   d'impression qui affiche les corrections, puis une qui affiche les sorties attendues, puis une qui affiche les
   coups de pouce. imprimer-td.py doit répondre « NON » et nommer la fuite. Pages : le gabarit, et le témoin du
   Gardien 25 (« La casse du siècle », corrections forcées à l'impression : 18 corrections imprimées).
3. verifier-td.py sur le gabarit : « tout est juste ».
4. numeroter-feuilles.py --tout --verifier : il passe sur tout le dépôt, sans « Problème ».
5. Corrections partielles (T123d) : verifier-td.py pose une correction qui ne donne qu'une fonction ou une méthode
   sur le code de départ, comme l'élève : la fonction à sa place, la méthode dans sa classe. Les 10 cas des TD type
   bac (charte/essais/corrections-partielles.json) passent leurs tests cachés, et le départ seul ne les passe pas ;
   plus 4 cas écrits ici (méthode nouvelle, fonction nouvelle avant les instructions, correction en retrait, classe).
6. Correction posée qui échoue (T123e) : une page témoin (effacée ensuite) dont la correction partielle est fausse ;
   verifier-td.py doit la refuser et rapporter l'échec de la correction POSÉE (« posée sur le code de départ »,
   l'assertion des tests cachés), et non d'abord le NameError de la correction seule.
7. Réponses à l'étroit sur papier (T123e) : imprimer-td.py ne signale aucune réponse à l'étroit dans un tableau ni
   sur une rangée sur les pages des tableaux (le gabarit, « Décimal et binaire » de SNT, les conditions) ; et le
   signale sur un témoin dont les cases « Réponse » sont réduites à 15 mm.
8. Mise en page déclarée (T140) :
   - la page d'exemple charte/gabarit-td/mise-en-page.html : « PDF vierge : oui » et « tout est juste » ;
   - l'ordre de lecture : sur papier, dans des colonnes (td-colonnes), les numéros descendent la première colonne puis
     la deuxième ; dans une grille (td-grille-reponses) ou un côte à côte, ils vont de gauche à droite puis vers le
     bas ; sur téléphone (320 px), une seule colonne dans l'ordre de la page ; au clavier (Tab), les champs viennent
     dans l'ordre des numéros ;
   - verifier-td.py refuse un témoin mal écrit (trois blocs dans un côte à côte, proportion inconnue, ligne de code
     trop longue pour sa colonne, console trop large, genre d'encadré inconnu) ;
   - imprimer-td.py signale les défauts de page d'un témoin (titre orphelin, consigne séparée de sa réponse, dernière
     page presque vide) et n'en signale aucun sur un modèle soigné (charte/exemples-mise-en-page/conversions) ;
   - une « courte » plus longue qu'une ligne pleine a deux lignes d'écriture (GHOST q7 et q8 : plus de réponse à
     l'étroit).
Code de sortie : 0 si tout est conforme.
"""
import functools
import importlib.util
import json
import http.server
import os
import subprocess
import sys
import threading

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
PAGES = ['charte/gabarit-td/index.html', 'nsi-premiere/fichiers/algorithmes-gloutons-premiere/casse-du-siecle/index.html']
FUITES = {
    'corrections': ('.td .td-q .td-correction, .td .td-q .td-correction *', 'correction'),
    'attendus': ('.td .td-q pre.td-attendu', 'attendu'),
    'coups de pouce': ('.td .td-q .td-aide', 'aide'),
}


class Silencieux(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def lancer(*args):
    r = subprocess.run([sys.executable, '-I', *args], capture_output=True, text=True, cwd=RACINE)
    return r.returncode, r.stdout + r.stderr


CAS_ECRITS = [
    ('méthode nouvelle, mise dans sa classe',
     'class Pile:\n    def __init__(self):\n        self.t = []\n\np = Pile()\np.empiler(3)\nprint(p.t)\n',
     'def empiler(self, x):\n    self.t.append(x)\n', 'p2 = Pile(); p2.empiler(1); assert p2.t == [1]\n'),
    ('fonction nouvelle, avant les instructions',
     'def double(x):\n    return 2 * x\n\nprint(quadruple(3))\n',
     'def quadruple(x):\n    return double(double(x))\n', 'assert quadruple(2) == 8\n'),
    ('correction écrite en retrait, méthode remplacée à sa place',
     'class A:\n    def f(self):\n        ...\n\n    def g(self):\n        return self.f() + 1\n\nprint(A().g())\n',
     '    def f(self):\n        return 1\n', 'assert A().g() == 2\n'),
    ('classe remplacée à sa place',
     'class B:\n    ...\n\nb = B()\nprint(b.v)\n',
     'class B:\n    def __init__(self):\n        self.v = 5\n', 'assert B().v == 5\n'),
]


def essayer_corrections_partielles(noter):
    spec = importlib.util.spec_from_file_location('verifier_td', os.path.join(ICI, 'verifier-td.py'))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    cas = json.load(open(os.path.join(ICI, 'essais', 'corrections-partielles.json'), encoding='utf-8'))
    cas = [(f"{c['page']} {c['question']}", c['depart'], c['correction'], c['tests'], c['fichier'], c['preambule']) for c in cas]
    cas += [(n, d, c, t, 'mon_code.py', '') for n, d, c, t in CAS_ECRITS]
    for nom, dep, corr, tests, fichier, pre in cas:
        rc, out, err = v.lancer(v.sur_depart(dep, corr), fichier, pre=pre, tests=tests)
        rc0, _, _ = v.lancer(dep, fichier, pre=pre, tests=tests)
        noter(rc == 0 and rc0 != 0, f'correction partielle posée sur le départ : {nom}'
              + ('' if rc == 0 else ' : ' + err.strip().splitlines()[-1][:120] if err.strip() else '')
              + ('' if rc0 != 0 else ' (le départ seul passe déjà : essai sans valeur)'))


TEMOIN_POSE = '''<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Témoin</title></head><body>
<main class="td" data-td="temoin"><section class="td-q" data-type="code" id="q1" data-obligatoire>
<p class="td-consigne">Écris la méthode <code>empiler</code>.</p>
<pre class="td-depart">
class Pile:
    def __init__(self):
        self.t = []

    def empiler(self, x):
        ...
</pre>
<script type="text/x-python" class="td-tests">
_p = Pile()
_p.empiler(1)
_p.empiler(2)
assert _p.t == [1, 2], "Après empiler(1) puis empiler(2), t doit valoir [1, 2]. Il vaut : " + repr(_p.t)
</script>
<pre class="td-code" data-verifier="correction">
def empiler(self, x):
    self.t.insert(0, x)
</pre>
</section></main></body></html>
'''
PAGES_ETROIT = ['charte/gabarit-td/index.html', 'snt/fichiers/binaire-seance/activite-conversion-binaire/index.html',
                'nsi-premiere/fichiers/python-exercices-bases-premiere/exercices-conditions-2.html']


def essayer_correction_posee_fausse(noter):
    temoin = os.path.join(ICI, 'essais', '.temoin-posee.html')
    open(temoin, 'w', encoding='utf-8').write(TEMOIN_POSE)
    try:
        rc, out = lancer('charte/verifier-td.py', os.path.relpath(temoin, RACINE))
    finally:
        os.remove(temoin)
    ligne = next((l.strip() for l in out.splitlines() if 'q1' in l), '')
    # le NameError de la correction seule n'est donné qu'en second, après « la correction seule »
    nom = ligne.find('NameError')
    vu = rc != 0 and 'posée sur le code de départ' in ligne and 'Il vaut' in ligne and (nom < 0 or nom > ligne.find('la correction seule') >= 0)
    noter(vu, 'correction posée fausse : refusée, échec de la correction posée rapporté (' + ligne[:110] + ')')


def essayer_etroit(noter, base, pdf):
    for page in PAGES_ETROIT:
        if not os.path.exists(os.path.join(RACINE, page)):
            continue
        rc, out = lancer('charte/imprimer-td.py', base + page, pdf)
        moteur = [l.strip() for l in out.splitlines() if "réponse à l'étroit" in l and 'ligne pleine' not in l]
        noter(not moteur, f'{page} : aucune réponse à l\'étroit dans un tableau ni sur une rangée' + (f' ({moteur[0][:100]})' if moteur else ''))
    page = PAGES_ETROIT[1]
    source = open(os.path.join(RACINE, page), encoding='utf-8').read()
    temoin = os.path.join(os.path.dirname(os.path.join(RACINE, page)), '.temoin-etroit.html')
    regle = '<style>@media print { .td table.td-groupe .td-groupe-r { width: 15mm !important; } }</style>'
    open(temoin, 'w', encoding='utf-8').write(source.replace('</head>', regle + '</head>', 1))
    try:
        rc, out = lancer('charte/imprimer-td.py', base + os.path.relpath(temoin, RACINE).replace(os.sep, '/'), pdf)
    finally:
        os.remove(temoin)
    vus = [l for l in out.splitlines() if "réponse à l'étroit" in l]
    noter(len(vus) >= 2, f'témoin aux cases de 15 mm : {len(vus)} réponse(s) à l\'étroit signalée(s)')


TEMOIN_MEP = """<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Témoin</title></head><body>
<main class="td" data-td="temoin-mep">
<div class="td-cote-a-cote" data-proportions="5/7"><div class="td-col"></div><div class="td-col"></div><div class="td-col"></div></div>
<div class="td-cote-a-cote"><div class="td-col"><pre class="td-code">
une_variable_au_nom_bien_trop_long_pour_cette_colonne = 1</pre>
<pre class="td-sortie-exemple">
UID     PID   PPID  C  CMD           un extrait bien trop large</pre></div><div class="td-col"></div></div>
<div class="td-encadre" data-genre="astuce"><p>?</p></div>
</main></body></html>
"""
ORDRE_JS = r"""(sel) => {
  const box = document.querySelector(sel); if (!box) return null;
  const qs = [...box.querySelectorAll(':scope > .td-q, :scope > .td-col > .td-q')].filter(q => q.getClientRects().length);
  return qs.map(q => { const r = q.getBoundingClientRect(), n = q.querySelector('.td-num-papier') || q.querySelector('.td-q-num');
    return { n: parseInt(n.textContent.replace(/\D+/g, ''), 10), x: Math.round(r.left), y: Math.round(r.top) }; });
}"""


def essayer_mise_en_page(noter, base, pdf):
    from playwright.sync_api import sync_playwright
    page = 'charte/gabarit-td/mise-en-page.html'
    rc, out = lancer('charte/imprimer-td.py', base + page, pdf)
    noter(rc == 0 and 'PDF vierge : oui' in out, 'mise-en-page.html : PDF vierge')
    rc, out = lancer('charte/verifier-td.py', page)
    noter(rc == 0 and 'tout est juste' in out, 'mise-en-page.html : verifier-td.py, tout est juste')
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_page(viewport={'width': 794, 'height': 1123})
        p.goto(base + page)
        p.wait_for_selector('.td-pret', state='attached')
        p.emulate_media(media='print')
        col = p.evaluate(ORDRE_JS, '.td-colonnes')
        # colonnes de journal : trié par (colonne, hauteur), les numéros croissent
        ordre = [x['n'] for x in sorted(col, key=lambda x: (x['x'], x['y']))]
        noter(len(col) >= 2 and ordre == sorted(ordre) and len({x['x'] for x in col}) >= 2,
              f'papier, colonnes : numéros dans l\'ordre de lecture (colonne après colonne) {ordre}')
        gr = p.evaluate(ORDRE_JS, '.td-grille-reponses')
        ordre = [x["n"] for x in sorted(gr, key=lambda x: (round(x["y"] / 4), x["x"]))]
        noter(len(gr) >= 3 and ordre == sorted(ordre) and len({x['y'] for x in gr}) == 1,
              f'papier, grille : numéros de gauche à droite {ordre}')
        cc = p.evaluate(ORDRE_JS, '.td-cote-a-cote[data-proportions="3/5"]')
        noter(len(cc) == 3 and [x['n'] for x in cc] == sorted(x['n'] for x in cc), 'papier, côte à côte : les questions de la colonne dans l\'ordre')
        p.emulate_media(media='screen')
        p.set_viewport_size({'width': 320, 'height': 800})
        p.wait_for_timeout(200)
        tel = p.evaluate(ORDRE_JS, '.td-colonnes') + p.evaluate(ORDRE_JS, '.td-grille-reponses')
        noter(len({x['x'] for x in tel}) == 1 and [x['n'] for x in tel] == sorted(x['n'] for x in sorted(tel, key=lambda x: x['y'])),
              '320 px : une seule colonne, dans l\'ordre des numéros')
        deb = p.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
        noter(deb <= 0, f'320 px : aucun défilement horizontal ({deb} px)')
        # clavier : l'ordre de tabulation des champs suit l'ordre des numéros
        p.set_viewport_size({'width': 1440, 'height': 900})
        champs = p.evaluate("""() => [...document.querySelectorAll('.td-grille-reponses input.td-champ, .td-cote-a-cote input.td-champ')]
            .map(c => c.id)""")
        vus = []
        p.focus('#' + champs[0])
        for _ in range(60):
            i = p.evaluate('document.activeElement.id')
            if i in champs and i not in vus:
                vus.append(i)
            if len(vus) == len(champs):
                break
            p.keyboard.press('Tab')
        noter(vus == champs, f'clavier : les champs dans l\'ordre de la page ({len(vus)}/{len(champs)})')
        # écran large : le côte à côte sort de la colonne de lecture, sans dépasser la fenêtre
        l = p.evaluate("(() => { const r = document.querySelector('.td-cote-a-cote').getBoundingClientRect(); return [r.left, r.right, innerWidth]; })()")
        noter(l[0] >= 0 and l[1] <= l[2] and l[1] - l[0] > 800, f'1440 px : côte à côte élargi dans la fenêtre ({round(l[0])}..{round(l[1])})')
        b.close()
    # verifier-td.py : un témoin mal écrit est refusé, avec chaque raison
    temoin = os.path.join(ICI, 'essais', '.temoin-mep.html')
    open(temoin, 'w', encoding='utf-8').write(TEMOIN_MEP)
    try:
        rc, out = lancer('charte/verifier-td.py', os.path.relpath(temoin, RACINE))
    finally:
        os.remove(temoin)
    attendus = ['exactement deux blocs', 'data-proportions="5/7"', 'trop longue pour sa colonne', 'ligne 1 de la console', 'data-genre="astuce"']
    manque = [a for a in attendus if a not in out]
    noter(rc != 0 and not manque, 'verifier-td.py : témoin de mise en page mal écrite refusé' + (f' (manque : {manque})' if manque else ''))
    # imprimer-td.py : défauts de page vus dans le PDF (témoin : une règle force les sauts au mauvais endroit)
    page = 'charte/gabarit-td/mise-en-page.html'
    source = open(os.path.join(RACINE, page), encoding='utf-8').read()
    regle = ('<style>@media print { .td h2.td-partie:nth-of-type(2) { break-after: page !important; } '
             '#q4 > .td-consigne { break-after: page !important; } }</style>')
    temoin = os.path.join(RACINE, 'charte', 'gabarit-td', '.temoin-pages.html')
    open(temoin, 'w', encoding='utf-8').write(source.replace('</head>', regle + '</head>', 1))
    try:
        rc, out = lancer('charte/imprimer-td.py', base + 'charte/gabarit-td/.temoin-pages.html', pdf)
    finally:
        os.remove(temoin)
    noter('titre orphelin' in out, 'imprimer-td.py : titre orphelin vu')
    noter('sont séparées' in out, 'imprimer-td.py : consigne séparée de sa réponse vue')
    rc, out = lancer('charte/imprimer-td.py', base + 'charte/exemples-mise-en-page/conversions/index.html', pdf)
    mep = [l.strip() for l in out.splitlines() if 'mise en page' in l]
    noter(rc == 0 and not mep, 'modèle « Conversions » : aucun défaut de page' + (f' ({mep[0][:100]})' if mep else ''))
    ghost = 'nsi-premiere/fichiers/operation-ghost/fiche-eleve-ghost.html'
    if os.path.exists(os.path.join(RACINE, ghost)):
        rc, out = lancer('charte/imprimer-td.py', base + ghost, pdf)
        etroit = [l for l in out.splitlines() if "réponse à l'étroit" in l and ('q7 ' in l or 'q8 ' in l)]
        noter(rc == 0 and not etroit, 'GHOST q7 et q8 : deux lignes d\'écriture, plus de réponse à l\'étroit')


def main():
    serveur = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Silencieux, directory=RACINE))
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{serveur.server_address[1]}/'
    pdf = os.path.join(RACINE, 'charte', '.essai-outils.pdf')
    resultats = []

    def noter(ok, msg):
        resultats.append(ok)
        print(('OK    ' if ok else 'ÉCHEC ') + msg)

    rc, out = lancer('charte/imprimer-td.py', base + PAGES[0], pdf)
    noter(rc == 0 and 'PDF vierge : oui' in out, 'gabarit : PDF vierge')
    for page in PAGES:
        if not os.path.exists(os.path.join(RACINE, page)):
            continue
        source = open(os.path.join(RACINE, page), encoding='utf-8').read()
        for nom, (sel, mot) in FUITES.items():
            temoin = os.path.join(os.path.dirname(os.path.join(RACINE, page)), '.temoin-fuite.html')
            regle = '<style>@media print { ' + sel + ' { display: block !important; } }</style>'
            open(temoin, 'w', encoding='utf-8').write(source.replace('</head>', regle + '</head>', 1))
            try:
                rc, out = lancer('charte/imprimer-td.py', base + os.path.relpath(temoin, RACINE).replace(os.sep, '/'), pdf)
            finally:
                os.remove(temoin)
            vu = rc != 0 and 'PDF vierge : NON' in out and ('imprimé(s)' in out or 'texte caché imprimé' in out)
            ligne = next((l.strip() for l in out.splitlines() if 'imprimé(s)' in l or 'caché imprimé' in l), '')
            noter(vu, f'{page} : {nom} imprimés : fuite vue ({ligne[:110]})')
    rc, out = lancer('charte/verifier-td.py', 'charte/gabarit-td/index.html')
    noter(rc == 0 and 'tout est juste' in out, 'gabarit : verifier-td.py, tout est juste')
    essayer_corrections_partielles(noter)
    essayer_correction_posee_fausse(noter)
    essayer_etroit(noter, base, pdf)
    essayer_mise_en_page(noter, base, pdf)
    rc, out = lancer('charte/numeroter-feuilles.py', '--tout', '--verifier')
    noter('Problème' not in out and 'Traceback' not in out, 'numeroter-feuilles.py --tout --verifier : tout le dépôt, sans problème (' + out.strip().splitlines()[-1] + ')')
    if os.path.exists(pdf):
        os.remove(pdf)
    serveur.shutdown()
    print(f'{sum(resultats)} / {len(resultats)} essais conformes')
    sys.exit(0 if all(resultats) else 1)


if __name__ == '__main__':
    main()
