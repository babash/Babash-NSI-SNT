#!/usr/bin/env python3
"""Construit les QCM Pronote (XML Moodle) et leurs aperçus HTML à partir des sources JSON.

Usage (depuis la racine du dépôt) :
  python3 -I qcm/outils/construire_qcm.py                     # tous les quiz
  python3 -I qcm/outils/construire_qcm.py --livrables DOSSIER # écrit aussi les notes de cadrage et l'avant/après

Les sources sont dans qcm/sources/<niveau>/<id>.json ; les sorties dans qcm/<niveau>/ : <id>.xml (à importer),
<id>.html (aperçu élève, sans aucune marque de la bonne réponse) et <id>-corrige.html (corrigé enseignant·e).
La bonne réponse de chaque QCU est placée par une suite équilibrée et sans motif, tirée de l'identifiant
du quiz : la sortie est la même à chaque construction.

Auteur : Babash - NSI Tani Malandi. Licence MIT."""
import argparse
import html
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qcm_commun as C  # noqa: E402

DEPOT = 'https://github.com/babash/Babash-NSI-SNT'
NIVEAUX = {'snt': 'Seconde, SNT', 'nsi-premiere': 'Première NSI', 'nsi-terminale': 'Terminale NSI', 'transversal': 'Transversal'}


def cdata(t):
    assert ']]>' not in t
    return f'<![CDATA[{t}]]>'


def fractions_qcm(n):
    base = 100 // n
    reste = 100 - base * n
    return [base + (1 if i < reste else 0) for i in range(n)]


def listes_des_trous(q):
    """Les listes déroulantes d'un texte à trous, dans l'ordre où elles apparaissent."""
    return [m.group(1).split('|') for l in q.get('lignes', []) for m in re.finditer(r'\[\[(.+?)\]\]', l)
            if any(p.startswith('*') for p in m.group(1).split('|'))]


def ordres_trous(q):
    """Pour chaque liste déroulante, l'ordre des choix : un mélange stable (même sortie à chaque
    construction), tel que la place de la bonne réponse ne suive pas le numéro du trou."""
    listes = listes_des_trous(q)
    for essai in range(5000):
        rnd = random.Random(f'{q["id"]}|{essai}|' + '|'.join(q.get('lignes', [])))
        ordres = []
        for choix in listes:
            c = list(choix)
            rnd.shuffle(c)
            ordres.append(c)
        pos = [[p.startswith('*') for p in c].index(True) for c in ordres]
        if not C.motif_trous(pos):
            return ordres
    raise RuntimeError(f'{q["id"]} : aucun ordre sans motif pour les listes déroulantes')


def paires_melangees(q):
    """Les paires d'un appariement dans un ordre mélangé et stable : jamais l'ordre de la solution
    (réponses rangées), pour que ni Pronote ni l'aperçu ne la montrent."""
    paires = list(q['paires'])
    for essai in range(5000):
        rnd = random.Random(f'{q["id"]}|{essai}|' + '|'.join(g for g, _ in paires))
        p = list(paires)
        rnd.shuffle(p)
        if not C.dans_l_ordre([d for _, d in p]) and (len(p) < 3 or p != paires):
            return p
    return paires


def trous_vers_cloze(segment, ordres):
    """[[a|b]] : réponse courte (variantes) ; [[*juste|faux|faux]] : liste déroulante (ordre mélangé)."""
    def remplace(m):
        contenu = m.group(1)
        morceaux = contenu.split('|')
        if any(p.startswith('*') for p in morceaux):
            parts = []
            for p in next(ordres):
                if p.startswith('*'):
                    parts.append(f'%100%{p[1:]}#')
                else:
                    parts.append(f'%0%{p}#')
            return '{:MULTICHOICE:' + '~'.join(parts) + '}'
        return '{:SHORTANSWER:' + '~'.join(f'%100%{p}#' for p in morceaux) + '}'
    return re.sub(r'\[\[(.+?)\]\]', remplace, segment)


def ligne_a_trous(ligne, langage, pour_apercu, ordres):
    sortie = []
    pos = 0
    for m in re.finditer(r'\[\[(.+?)\]\]', ligne):
        sortie.append(C.colorer_ligne(ligne[pos:m.start()], langage))
        morceaux = m.group(1).split('|')
        liste = any(p.startswith('*') for p in morceaux)
        if liste and pour_apercu:
            morceaux = next(ordres)
        if pour_apercu == 'eleve':
            # Ce que voit l'élève : un champ vide, ou une liste déroulante dans l'ordre du fichier, sans marque.
            if liste:
                choix = ''.join(f'<option>{html.escape(p.lstrip("*"))}</option>' for p in morceaux)
                sortie.append(f'<select class="trou" disabled aria-label="liste de choix"><option>…</option>{choix}</select>')
            else:
                sortie.append('<span class="trou vide" aria-label="champ à remplir">&#160;&#160;&#160;&#160;&#160;&#160;</span>')
        elif pour_apercu:
            bonnes = [p.lstrip('*') for p in morceaux if p.startswith('*')] or morceaux
            sortie.append(f'<span class="trou">{html.escape(" ou ".join(bonnes) if not liste else bonnes[0])}</span>')
        else:
            sortie.append(trous_vers_cloze(m.group(0), ordres))
        pos = m.end()
    sortie.append(C.colorer_ligne(ligne[pos:], langage))
    return ''.join(sortie)


def texte_question(q, pour_apercu=False):
    morceaux = ['<div style="font-family: Arial, Helvetica, sans-serif; font-size: 14px;">']
    morceaux.append(f'<p style="color: {C.TEXTE_OBJECTIF};"><strong>Objectif :</strong> {C.texte_html(q["objectif"])}</p>')
    for p in q.get('enonce', []):
        morceaux.append(f'<p>{C.texte_html(p)}</p>')
    if q.get('code'):
        morceaux.append(C.bloc_code(q['code'], q.get('langage', 'python')))
    if q.get('console'):
        morceaux.append('<p>Console :</p>')
        morceaux.append(C.bloc_console(q['console']))
    if q.get('type') == 'trous':
        ordres = iter(ordres_trous(q))
        lignes = [ligne_a_trous(l, q.get('langage', 'texte'), pour_apercu, ordres) for l in q['lignes']]
        if q.get('langage', 'texte') in ('python', 'sql', 'bash'):
            morceaux.append(f'<div style="{C.STYLE_BLOC}">' + C.lignes_en_blocs(lignes) + '</div>')
        else:
            morceaux.append('<p>' + '<br>'.join(lignes) + '</p>')
    for p in q.get('question', []):
        morceaux.append(f'<p>{C.texte_html(p)}</p>')
    morceaux.append('</div>')
    return ''.join(morceaux)


def xml_question(q, lettre):
    t = q.get('type', 'qcu')
    typ = {'qcu': 'multichoice', 'qcm': 'multichoice', 'appariement': 'matching', 'numerique': 'numerical',
           'reponse_courte': 'shortanswer', 'trous': 'cloze'}[t]
    x = [f'\t<question type="{typ}">',
         f'\t\t<name>\n\t\t\t<text>{cdata(q["nom"])}</text>\n\t\t</name>',
         f'\t\t<questiontext format="html">\n\t\t\t<text>{cdata(texte_question(q))}</text>\n\t\t</questiontext>',
         '\t\t<externallink/>']
    usecase = '1' if (t == 'reponse_courte' and q.get('casse')) else ('0' if t in ('reponse_courte', 'numerique') else '1')
    x.append(f'\t\t<usecase>{usecase}</usecase>')
    x.append(f'\t\t<defaultgrade>{q.get("points", 1)}</defaultgrade>')

    def reponse(fraction, texte, fb, extra=''):
        return (f'\t\t<answer fraction="{fraction}" format="plain_text">\n\t\t\t<text>{cdata(C.texte_brut(texte))}</text>{extra}\n'
                f'\t\t\t<feedback>\n\t\t\t\t<text>{cdata(C.texte_brut(fb))}</text>\n\t\t\t</feedback>\n\t\t</answer>')
    if t == 'qcu':
        x.append('\t\t<single>true</single>')
        x.append('\t\t<shuffleanswers>false</shuffleanswers>')
        for o in C.ordonner_options(q, lettre):
            x.append(reponse(100 if o.get('juste') else 0, o['texte'], o['feedback']))
    elif t == 'qcm':
        x.append('\t\t<single>false</single>')
        x.append('\t\t<shuffleanswers>false</shuffleanswers>')
        justes = [o for o in q['options'] if o.get('juste')]
        fr = iter(fractions_qcm(len(justes)))
        for o in q['options']:
            x.append(reponse(next(fr) if o.get('juste') else 0, o['texte'], o['feedback']))
    elif t == 'appariement':
        for g, d in paires_melangees(q):
            x.append(f'\t\t<subquestion>\n\t\t\t<text>{cdata(C.texte_brut(g))}</text>\n'
                     f'\t\t\t<answer>\n\t\t\t\t<text>{cdata(C.texte_brut(d))}</text>\n\t\t\t</answer>\n\t\t</subquestion>')
        x.append('\t\t<shuffleanswers>true</shuffleanswers>')
    elif t == 'numerique':
        x.append(reponse(100, str(q['reponse']), q['feedback'],
                         f'\n\t\t\t<tolerance>{q.get("tolerance", 0)}</tolerance>'))
    elif t == 'reponse_courte':
        for r in q['reponses']:
            x.append(reponse(100, r, q['feedback']))
    x.append('\t</question>')
    return '\n'.join(x)


def construire_xml(quiz, positions):
    x = ['<?xml version="1.0" encoding="UTF-8"?>', '<quiz>', f'\t<!--{quiz["titre"]} : Babash - NSI Tani Malandi, CC BY-SA 4.0-->',
         '\t<question type="category">', '\t\t<category>',
         '\t\t\t<text>' + cdata(f'<infos><name>{html.escape(quiz["titre"], quote=False)}</name><answernumbering>123</answernumbering>'
                               f'<niveau>{C.NIVEAU_PRONOTE[quiz["niveau"]]}</niveau><matiere>NUMERIQUE SC.INFORM.</matiere></infos>') + '</text>',
         '\t\t</category>', '\t</question>']
    it = iter(positions)
    for q in quiz['questions']:
        x.append(xml_question(q, next(it) if C.est_qcu(q) else None))
    x.append('</quiz>')
    return '\n'.join(x) + '\n'


def positions_du_quiz(quiz):
    n = sum(1 for q in quiz['questions'] if C.est_qcu(q))
    return C.positions_equilibrees(n, quiz['id'])


# ---------------------------------------------------------------- aperçus HTML
# Deux aperçus par quiz :
#   <id>.html          aperçu « élève » : ce que l'élève voit avant de répondre, options dans l'ordre du
#                      fichier XML, sans aucune marque de la bonne réponse et sans les retours ;
#   <id>-corrige.html  corrigé enseignant·e : la bonne réponse est écrite en toutes lettres
#                      (« Bonne réponse »), pas seulement indiquée par une couleur, avec tous les retours.
CSS = """
:root{--fond:#ffffff;--texte:#1b1b1b;--doux:#4a4a4a;--carte:#f5f6f8;--bord:#d5d8de;--lien:#0b57a4;--bonne:#14532d;--bonne-fond:#eef7f0;--alerte:#7a2e00;--alerte-fond:#fff4e5}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--fond:#14161a;--texte:#e8e8e8;--doux:#b8bcc4;--carte:#1f2329;--bord:#3a3f48;--lien:#8ab8ff;--bonne:#a7e8b9;--bonne-fond:#17271c;--alerte:#ffd29a;--alerte-fond:#2e2210}}
:root[data-theme="dark"]{--fond:#14161a;--texte:#e8e8e8;--doux:#b8bcc4;--carte:#1f2329;--bord:#3a3f48;--lien:#8ab8ff;--bonne:#a7e8b9;--bonne-fond:#17271c;--alerte:#ffd29a;--alerte-fond:#2e2210}
*{box-sizing:border-box}body{margin:0;background:var(--fond);color:var(--texte);font-family:Arial,Helvetica,sans-serif;line-height:1.5}
main{max-width:860px;margin:0 auto;padding:16px}h1{font-size:1.5rem;margin:.2em 0}.meta{color:var(--doux);font-size:.95rem}
section.q{background:var(--carte);border:1px solid var(--bord);border-radius:8px;padding:12px 14px;margin:16px 0;overflow-wrap:anywhere}
section.q h2{font-size:1.05rem;margin:0 0 .4em}.type{color:var(--doux);font-size:.85rem}
.pronote>div>div[style]{overflow-x:auto;overflow-wrap:normal;word-break:normal;white-space:nowrap}
@media print{.pronote>div>div[style]{overflow:visible;white-space:pre-wrap;overflow-wrap:anywhere}}ol.opts{padding-left:1.6em}ol.opts li{margin:.5em 0;padding:4px 6px;border-radius:5px}
.fb{display:block;color:var(--doux);font-size:.92rem}
.trou{border:0;border-bottom:2px solid #8a4b2a;padding:0 3px;font:inherit;background:transparent;color:inherit}
a{color:var(--lien)}footer{color:var(--doux);font-size:.9rem;border-top:1px solid var(--bord);margin-top:24px;padding-top:10px}
.pronote{background:#ffffff;color:#1b1b1b;border-radius:6px;padding:2px 10px;margin:6px 0}
table{border-collapse:collapse}td,th{border:1px solid var(--bord);padding:3px 8px;text-align:left}ul.choix{padding-left:1.4em}
.avertissement{background:var(--alerte-fond);color:var(--alerte);border:1px solid var(--bord);border-radius:6px;padding:8px 12px}
li.bonne{background:var(--bonne-fond);border-left:4px solid var(--bonne)}.etiquette{font-weight:bold;color:var(--bonne)}.etiquette-faux{font-weight:bold;color:var(--doux)}
p.reponse{margin:.4em 0}
"""

TYPES = {'qcu': 'QCU, une seule réponse', 'qcm': 'Choix multiple', 'appariement': 'Appariement',
         'numerique': 'Réponse numérique', 'reponse_courte': 'Réponse courte', 'trous': 'Texte à trous'}


def options_dans_l_ordre(q, lettre):
    """Les options dans l'ordre exact du fichier XML."""
    return C.ordonner_options(q, lettre) if q.get('type', 'qcu') == 'qcu' else q['options']


def bloc_eleve(q, lettre):
    e = html.escape
    t = q.get('type', 'qcu')
    b = []
    if t in ('qcu', 'qcm'):
        b.append('<ol class="opts" type="A">')
        b += [f'<li>{e(C.texte_brut(o["texte"]))}</li>' for o in options_dans_l_ordre(q, lettre)]
        b.append('</ol>')
    elif t == 'appariement':
        # Pronote propose, pour chaque élément, une liste des réponses : on les montre triées, sans les relier.
        droites = sorted({d for _, d in q['paires']}, key=lambda s: C.texte_brut(s).lower())
        b.append('<table><tr><th>Élément</th><th>Réponse à choisir</th></tr>' +
                 ''.join(f'<tr><td>{e(g)}</td><td><span class="trou vide">&#160;&#160;&#160;&#160;&#160;&#160;</span></td></tr>' for g, _ in paires_melangees(q))
                 + '</table>')
        b.append('<p>Réponses proposées :</p><ul class="choix">' + ''.join(f'<li>{e(d)}</li>' for d in droites) + '</ul>')
    elif t in ('numerique', 'reponse_courte'):
        b.append('<p>Réponse : <span class="trou vide" aria-label="champ à remplir">&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;</span></p>')
    return b


def bloc_corrige(q, lettre):
    e = html.escape
    t = q.get('type', 'qcu')
    b = []
    if t in ('qcu', 'qcm'):
        opts = options_dans_l_ordre(q, lettre)
        bonnes = ['ABCDEFGHIJKL'[i] for i, o in enumerate(opts) if o.get('juste')]
        b.append(f'<p class="reponse"><span class="etiquette">{"Bonne réponse" if len(bonnes) == 1 else "Bonnes réponses"} :</span> {", ".join(bonnes)}</p>')
        b.append('<ol class="opts" type="A">')
        for o in opts:
            if o.get('juste'):
                b.append(f'<li class="bonne"><span class="etiquette">Bonne réponse : </span>{e(C.texte_brut(o["texte"]))}'
                         f'<span class="fb">Retour : {e(C.texte_brut(o["feedback"]))}</span></li>')
            else:
                b.append(f'<li><span class="etiquette-faux">Distracteur : </span>{e(C.texte_brut(o["texte"]))}'
                         f'<span class="fb">Retour : {e(C.texte_brut(o["feedback"]))}</span></li>')
        b.append('</ol>')
    elif t == 'appariement':
        b.append('<table><tr><th>Élément</th><th>Association attendue</th></tr>' +
                 ''.join(f'<tr><td>{e(g)}</td><td>{e(d)}</td></tr>' for g, d in paires_melangees(q)) + '</table>')
    elif t == 'numerique':
        b.append(f'<p class="reponse"><span class="etiquette">Réponse attendue :</span> {e(str(q["reponse"]))} (tolérance {q.get("tolerance", 0)})</p>')
    elif t == 'reponse_courte':
        b.append(f'<p class="reponse"><span class="etiquette">Réponses acceptées :</span> {e(" ; ".join(q["reponses"]))}'
                 f' ({"casse respectée" if q.get("casse") else "majuscules indifférentes"})</p>')
    elif t == 'trous':
        b.append('<p class="reponse"><span class="etiquette">Réponses attendues :</span> écrites dans les trous ci-dessus.</p>')
    if t not in ('qcu', 'qcm') and q.get('feedback'):
        b.append(f'<p class="fb">Retour : {e(q["feedback"])}</p>')
    return b


def apercu_html(quiz, positions, corrige=False):
    e = html.escape
    it = iter(positions)
    corps = []
    for i, q in enumerate(quiz['questions'], 1):
        t = q.get('type', 'qcu')
        lettre = next(it) if C.est_qcu(q) else None
        bloc = [f'<section class="q" id="{e(q["id"])}"><h2>{i}. {e(q["nom"])}</h2>',
                f'<p class="type">{e(TYPES[t])}</p>',
                '<div class="pronote">' + texte_question(q, pour_apercu='corrige' if corrige else 'eleve') + '</div>']
        bloc += bloc_corrige(q, lettre) if corrige else bloc_eleve(q, lettre)
        bloc.append('</section>')
        corps.append('\n'.join(bloc))
    ident = e(quiz['id'])
    if corrige:
        titre = f'Corrigé enseignant·e : {quiz["titre"]}'
        tete = (f'<p class="avertissement"><strong>Corrigé enseignant·e.</strong> Cette page donne les bonnes réponses et tous les retours. '
                f'Elle sert à relire le quiz ; elle ne se donne pas aux élèves. L\'aperçu sans réponses : <a href="{ident}.html">{ident}.html</a>.</p>')
        robots = '<meta name="robots" content="noindex">\n'
    else:
        titre = quiz['titre']
        tete = ('<p class="meta">Les questions et les options telles que l\'élève les voit, dans l\'ordre du fichier, '
                'sans les réponses ni les retours.</p>')
        robots = ''
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{robots}<title>{e(titre)}</title>
<style>{CSS}</style>
</head>
<body>
<main>
<p class="meta">{"Corrigé" if corrige else "Aperçu"} d'un QCM Pronote · {e(NIVEAUX[quiz['niveau']])}</p>
<h1>{e(titre)}</h1>
<p class="meta">{len(quiz['questions'])} questions · fichier à importer dans Pronote : <a href="{ident}.xml">{ident}.xml</a></p>
{tete}
{''.join(corps)}
<footer>Babash - NSI Tani Malandi · CC BY-SA 4.0 · <a href="{DEPOT}">Code source sur GitHub</a></footer>
</main>
</body>
</html>
"""


# ---------------------------------------------------------------- livrables
def note_cadrage(quiz):
    from collections import Counter
    themes = Counter(re.match(r'\[([^\]]+)\]', q['nom']).group(1) for q in quiz['questions'])
    types = Counter(q.get('type', 'qcu') for q in quiz['questions'])
    lignes = [f'# Note de cadrage : {quiz["titre"]}', '',
              f'Validée par délégation de l\'enseignant (chef d\'orchestre, 20/11/2026). Fichier : `qcm/{quiz["niveau"]}/{quiz["id"]}.xml`.', '',
              '| Champ | Contenu |', '|---|---|',
              f'| Niveau | {quiz["niveau_affiche"]} : {quiz.get("justification_niveau", "")} |',
              f'| Programme (BO 2019) | {"<br>".join(quiz["programme"])} |',
              f'| Notions du référentiel | {", ".join("`" + n + "`" for n in quiz["notions"])} |',
              f'| Questions | {len(quiz["questions"])} : ' + ', '.join(f'{v} {k}' for k, v in types.items()) + ' |',
              f'| Contexte | {quiz.get("contexte", "")} |',
              f'| Sources | {"<br>".join(quiz["sources"])} |', '',
              '## Objectifs', ''] + [f'- {o}' for o in quiz['objectifs']] + ['', '## Répartition et progression', '']
    lignes += [f'- {k} : {v} question(s)' for k, v in themes.items()]
    if quiz.get('progression'):
        lignes += ['', quiz['progression']]
    lignes += ['', '## Les questions', '', '| # | Nom | Type | Origine |', '|---|---|---|---|']
    for i, q in enumerate(quiz['questions'], 1):
        lignes.append(f'| {i} | {q["nom"].replace("|", "/")} | {q.get("type", "qcu")} | {q.get("origine", "nouvelle")} |')
    return '\n'.join(lignes) + '\n'


def avant_apres(quiz):
    l = [f'## {quiz["titre"]} (`qcm/{quiz["niveau"]}/{quiz["id"]}.xml`)', '']
    l.append('Sources : ' + ' ; '.join(quiz['sources']) + '.')
    l.append('')
    fonds = [q for q in quiz['questions'] if q.get('fond')]
    l.append(f'### Corrections de fond ({len(fonds)})')
    l.append('')
    if fonds:
        l += ['| Question | Origine | Avant | Après | Raison |', '|---|---|---|---|---|']
        for q in fonds:
            for f in (q['fond'] if isinstance(q['fond'], list) else [q['fond']]):
                l.append(f'| {q["nom"].replace("|", "/")} | {q.get("origine", "")} | {f["avant"].replace("|", "/")} | {f["apres"].replace("|", "/")} | {f["raison"].replace("|", "/")} |')
    else:
        l.append('Aucune.')
    l += ['', '### Changements de forme', ''] + [f'- {x}' for x in quiz.get('forme', [])]
    l += ['', '### Questions retirées ou déplacées', '']
    if quiz.get('retirees'):
        l += ['| Origine | Raison |', '|---|---|'] + [f'| {r["origine"]} | {r["raison"]} |' for r in quiz['retirees']]
    else:
        l.append('Aucune.')
    return '\n'.join(l) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--livrables')
    a = ap.parse_args()
    tous = C.lire_sources()
    for quiz in tous:
        assert quiz['niveau'] == quiz['_niveau_dossier'], quiz['id']
        quiz['niveau_affiche'] = NIVEAUX[quiz['niveau']]
        pos = positions_du_quiz(quiz)
        d = os.path.join(C.RACINE_QCM, quiz['niveau'])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, quiz['id'] + '.xml'), 'w', encoding='utf-8') as f:
            f.write(construire_xml(quiz, pos))
        with open(os.path.join(d, quiz['id'] + '.html'), 'w', encoding='utf-8') as f:
            f.write(apercu_html(quiz, pos))
        with open(os.path.join(d, quiz['id'] + '-corrige.html'), 'w', encoding='utf-8') as f:
            f.write(apercu_html(quiz, pos, corrige=True))
        print(f'{quiz["niveau"]}/{quiz["id"]} : {len(quiz["questions"])} questions, positions {pos}')
    if a.livrables:
        os.makedirs(a.livrables, exist_ok=True)
        for quiz in tous:
            with open(os.path.join(a.livrables, f'cadrage-{quiz["id"]}.md'), 'w', encoding='utf-8') as f:
                f.write(note_cadrage(quiz))
        with open(os.path.join(a.livrables, 'avant-apres-qcm.md'), 'w', encoding='utf-8') as f:
            f.write('# Avant/après des QCM Pronote révisés (T111)\n\nAtelier des quiz. Généré par `qcm/outils/construire_qcm.py --livrables`. '
                    'Les corrections de fond ont été validées en bloc par délégation de l\'enseignant (20/11/2026).\n\n')
            for quiz in tous:
                f.write(avant_apres(quiz) + '\n')


if __name__ == '__main__':
    main()
