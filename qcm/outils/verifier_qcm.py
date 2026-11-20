#!/usr/bin/env python3
"""Vérifie les QCM Pronote : sources JSON, XML produits, exécution du code, doublons.

Usage (depuis la racine du dépôt) :
  python3 -I qcm/outils/verifier_qcm.py            # tous les quiz
  python3 -I qcm/outils/verifier_qcm.py --sans-execution

Contrôles :
  - XML bien formé, catégorie Pronote, balises obligatoires de chaque type
    (name, questiontext format="html" en CDATA, externallink, usecase, defaultgrade, single,
    shuffleanswers, answer + feedback) ; XML à jour par rapport à la source ;
  - QCU : 4 options, une seule juste (100), options toutes différentes, aucun gras ;
  - un feedback d'au moins 40 caractères pour chaque option, au tutoiement, sans formule sèche ;
  - objectif affiché au début, nom « [Thème] … » ;
  - position de la bonne réponse : équilibrée (A à D), sans série de 3, sans période ;
    la bonne réponse n'est nettement la plus longue que dans 40 % des QCU au plus (erreur), et pas la
    plus longue dans plus de 40 % des QCU (avertissement) ;
  - impression : une règle @media print fait passer le code et les consoles à la ligne, avec un retrait
    pour la suite (contrôle des pages en PDF A4 : outil coupe_impression.py du Gardien, avec Playwright) ;
  - aperçus : l'aperçu élève (<id>.html) ne marque jamais la bonne réponse, ne montre aucun retour et garde
    l'ordre du XML ; le corrigé (<id>-corrige.html) écrit « Bonne réponse : X » pour chaque QCU ;
  - coloration : tout bloc de code est coloré, chaque couleur a un contraste ≥ 7:1 sur son fond, et la
    coloration se lit aussi en noir et blanc (gras, souligné, italique) ;
  - exécution : chaque vérification Python (python3 -I) et SQL (SQLite en mémoire) donne le résultat annoncé ;
  - consoles : tout message d'erreur est coloré, son type en gras ; une console SQL affiche le vrai message de SQLite ;
  - ordre : les listes déroulantes d'un texte à trous ne placent pas la bonne réponse selon le numéro du trou,
    et un appariement ne range pas ses paires dans l'ordre de la solution ;
  - le nom et l'objectif d'une question ne contiennent pas un mot de la seule bonne option (avertissement) ;
  - caractères invisibles ou de contrôle refusés ;
  - doublons : deux questions (énoncé + code) identiques (erreur) ou presque (à relire), dans un quiz ou entre deux quiz.
Code de sortie 1 en cas d'erreur.

Auteur : Babash - NSI Tani Malandi. Licence MIT."""
import argparse
import difflib
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qcm_commun as C  # noqa: E402
import construire_qcm as B  # noqa: E402

ERREURS = []
AVERTISSEMENTS = []
SECHES = re.compile(r'^\s*(Faux|Absurde|Grosse erreur|Erreur grave|Incorrect|Inapproprié|Mauvaise pratique)\b', re.I)
VOUS = re.compile(r'\b(vous|votre|vos)\b', re.I)


VIDES = set("le la les l de des du d un une et à a en au aux ou est pas par sur ne n se s ce c qui que qu y il "
            "elle on son sa ses pour dans avec ils mais si plus sans tout tous être avoir".split())


def mots(t):
    t = t.lower().replace(chr(0x2019), "'")
    return {m for m in re.findall(r"==|!=|<=|>=|[0-9a-zà-öø-ÿ_²³ⁿ]+", t) if m not in VIDES}


def indices_de_reponse(q):
    """Les mots de la seule bonne option (absents des distracteurs et de l'énoncé) que le nom ou
    l'objectif affiché contient : ils donneraient la réponse avant la question."""
    if q.get('type', 'qcu') != 'qcu' or not any(o.get('juste') for o in q.get('options', [])):
        return set()
    juste = [o for o in q['options'] if o.get('juste')][0]
    autres = set().union(*(mots(o['texte']) for o in q['options'] if not o.get('juste')))
    contexte = mots(' '.join(q.get('enonce', []) + q.get('question', []) + q.get('code', []) + q.get('console', [])))
    # le nom entier, thème entre crochets compris : « [Super-utilisateur] … » compte aussi
    return (mots(juste['texte']) - autres - contexte) & (mots(q.get('nom', '')) | mots(q.get('objectif', '')))


def err(quiz, q, msg):
    ERREURS.append(f'{quiz}{" " + q if q else ""} : {msg}')


def avert(quiz, q, msg):
    AVERTISSEMENTS.append(f'{quiz}{" " + q if q else ""} : {msg}')


def caracteres(quiz, chemin):
    with open(chemin, encoding='utf-8') as f:
        t = f.read()
    for i, c in enumerate(t):
        if c in '\n\t':
            continue
        if unicodedata.category(c) in ('Cc', 'Cf', 'Zl', 'Zp') or c == chr(0xAD):
            err(quiz, None, f'caractère invisible U+{ord(c):04X} dans {os.path.basename(chemin)} (position {i})')
    if chr(92) + 'u' in t:
        err(quiz, None, f'séquence « barre oblique inverse + u » dans {os.path.basename(chemin)}')


# ---------------------------------------------------------------- exécution
def executer_python(code):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'extrait.py')
        with open(p, 'w', encoding='utf-8') as f:
            f.write(code)
        r = subprocess.run([sys.executable, '-I', p], capture_output=True, text=True, timeout=10, cwd=d)
    derniere = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ''
    return r.stdout.rstrip('\n'), derniere


def base_sql(quiz, q):
    c = sqlite3.connect(':memory:', isolation_level=None)
    if q.get('cles_etrangeres') or quiz.get('cles_etrangeres'):
        c.execute('PRAGMA foreign_keys = ON')
    c.executescript('\n'.join(quiz.get('schema_sql', []) + q.get('schema_sql', [])))
    return c


def verifier_execution(quiz, q):
    qid = q['id']
    v = q.get('verifications', [])
    if (q.get('code') or q.get('type') == 'trous') and not v and not q.get('note_verification'):
        err(quiz['id'], qid, 'du code sans vérification ni note_verification')
    for k, ver in enumerate(v, 1):
        lab = f'vérification {k}' + (f' ({ver["option"]})' if ver.get('option') else '')
        if 'sql' in ver:
            c = base_sql(quiz, q)
            try:
                for avant in ver.get('avant', []):
                    c.execute(avant)
                cur = c.execute(ver['sql'])
                res = [list(r) for r in cur.fetchall()]
                if 'apres' in ver:
                    res = [list(r) for r in c.execute(ver['apres']).fetchall()]
                if 'erreur_sql' in ver:
                    err(quiz['id'], qid, f'{lab} : erreur SQL attendue « {ver["erreur_sql"]} », obtenu {res}')
                elif 'resultat' in ver and res != ver['resultat']:
                    err(quiz['id'], qid, f'{lab} : attendu {ver["resultat"]}, obtenu {res}')
                elif 'different_de' in ver:
                    autre = [list(r) for r in base_sql(quiz, q).execute(ver['different_de']).fetchall()]
                    if autre == res:
                        err(quiz['id'], qid, f'{lab} : les deux requêtes donnent le même résultat {res}')
            except sqlite3.Error as e:
                if 'erreur_sql' not in ver or ver['erreur_sql'] not in str(e):
                    err(quiz['id'], qid, f'{lab} : erreur SQL inattendue : {e}')
            continue
        lignes = list(quiz.get('prelude_python', []))
        if ver.get('reprendre_code', True) and q.get('code') and q.get('langage', 'python') == 'python':
            lignes += q['code']
        lignes += ver.get('code', [])
        code = '\n'.join(lignes) + '\n'
        sortie, derniere = executer_python(code)
        if 'message' in ver:
            if derniere != ver['message']:
                err(quiz['id'], qid, f'{lab} : message attendu « {ver["message"]} », obtenu « {derniere} »')
        elif 'erreur' in ver:
            if not derniere.startswith(ver['erreur']):
                err(quiz['id'], qid, f'{lab} : erreur attendue {ver["erreur"]}, obtenu « {derniere or sortie} »')
        else:
            if derniere:
                err(quiz['id'], qid, f'{lab} : erreur inattendue « {derniere} »')
            elif sortie != ver.get('sortie', ''):
                err(quiz['id'], qid, f'{lab} : sortie attendue {ver.get("sortie")!r}, obtenue {sortie!r}')


# ---------------------------------------------------------------- source
def verifier_source(quiz, executer):
    for champ in ('id', 'titre', 'niveau', 'programme', 'notions', 'objectifs', 'sources', 'questions'):
        if champ not in quiz:
            err(quiz.get('id', '?'), None, f'champ « {champ} » absent')
    if quiz.get('auteur') != 'Babash - NSI Tani Malandi':
        err(quiz['id'], None, 'auteur absent ou différent de « Babash - NSI Tani Malandi »')
    ids = [q['id'] for q in quiz['questions']]
    if len(set(ids)) != len(ids):
        err(quiz['id'], None, 'identifiants de question en double')
    n = len(quiz['questions'])
    if not 15 <= n <= 21:
        avert(quiz['id'], None, f'{n} questions (15 à 20 visées)')
    longues = 0
    nb_qcu = 0
    plus_longues = 0
    for q in quiz['questions']:
        qid = q['id']
        t = q.get('type', 'qcu')
        if not re.match(r'^\[[^\]]+\] \S', q.get('nom', '')):
            err(quiz['id'], qid, 'nom absent ou pas au format « [Thème] … »')
        if len(q.get('objectif', '')) < 15:
            err(quiz['id'], qid, 'objectif absent ou trop court')
        indices = indices_de_reponse(q)
        if indices:
            avert(quiz['id'], qid, f'le nom ou l\'objectif contient un mot de la seule bonne option : {", ".join(sorted(indices))}')
        for ligne in q.get('console', []):
            if ' error' in ligne.lower() or 'Error' in ligne:
                if not C.RE_ERREUR.match(ligne):
                    err(quiz['id'], qid, f'console : message d\'erreur non reconnu, donc non coloré : « {ligne} »')
        if q.get('console') and q.get('langage') == 'sql' and executer:
            try:
                base_sql(quiz, q).execute(' '.join(q['code']))
                err(quiz['id'], qid, 'console SQL : la requête ne provoque aucune erreur')
            except sqlite3.Error as e:
                if not q['console'][-1].endswith(str(e)):
                    err(quiz['id'], qid, f'console SQL : SQLite répond « {e} », la console affiche « {q["console"][-1]} »')
        textes = ' '.join(q.get('enonce', []) + q.get('question', []))
        if VOUS.search(textes):
            err(quiz['id'], qid, 'énoncé au vouvoiement (forme impersonnelle attendue)')
        if t in ('qcu', 'qcm'):
            opts = q['options']
            justes = [o for o in opts if o.get('juste')]
            if t == 'qcu':
                nb_qcu += 1
                if len(opts) != 4:
                    err(quiz['id'], qid, f'{len(opts)} options (4 attendues)')
                if len(justes) != 1:
                    err(quiz['id'], qid, f'{len(justes)} réponses justes (1 attendue)')
                if justes:
                    L = sorted((len(C.texte_brut(o['texte'])), bool(o.get('juste'))) for o in opts)
                    if L[-1][1] and L[-1][0] > 1.25 * L[-2][0] and L[-1][0] - L[-2][0] > 8:
                        longues += 1
                    if L[-1][1] and L[-1][0] > L[-2][0]:
                        plus_longues += 1
            elif len(justes) < 2:
                err(quiz['id'], qid, 'choix multiple avec moins de 2 réponses justes (faire un QCU)')
            vus = [re.sub(r'\s+', ' ', C.texte_brut(o['texte']).strip()) for o in opts]
            if len(set(vus)) != len(vus):
                err(quiz['id'], qid, 'options identiques')
            for i, o in enumerate(opts):
                fb = C.texte_brut(o.get('feedback', ''))
                if len(fb) < 40:
                    err(quiz['id'], qid, f'option {i + 1} : feedback absent ou de moins de 40 caractères')
                if VOUS.search(fb):
                    err(quiz['id'], qid, f'option {i + 1} : feedback au vouvoiement')
                if SECHES.search(fb):
                    err(quiz['id'], qid, f'option {i + 1} : feedback qui commence sèchement')
                if '**' in o['texte']:
                    err(quiz['id'], qid, f'option {i + 1} : gras dans une option')
        elif t == 'appariement':
            if len(q.get('paires', [])) < 3:
                err(quiz['id'], qid, 'appariement de moins de 3 paires')
            if len(q.get('feedback', '')) < 40:
                err(quiz['id'], qid, 'explication absente ou trop courte')
        elif t in ('numerique', 'reponse_courte', 'trous'):
            if len(q.get('feedback', '')) < 40:
                err(quiz['id'], qid, 'feedback absent ou trop court')
            if VOUS.search(q.get('feedback', '')):
                err(quiz['id'], qid, 'feedback au vouvoiement')
            if t == 'reponse_courte':
                if not q.get('reponses'):
                    err(quiz['id'], qid, 'aucune réponse acceptée')
                if any(len(r.split()) > 3 and not re.fullmatch(r'[0-9A-Fa-f ]+', r) for r in q['reponses']):
                    err(quiz['id'], qid, 'réponse courte de plus de 3 mots')
            if t == 'trous' and not any('[[' in l for l in q.get('lignes', [])):
                err(quiz['id'], qid, 'texte à trous sans trou')
        else:
            err(quiz['id'], qid, f'type inconnu « {t} »')
        if executer:
            verifier_execution(quiz, q)
    if nb_qcu and longues / nb_qcu > 0.4:
        err(quiz['id'], None, f'la bonne réponse est nettement la plus longue dans {longues}/{nb_qcu} QCU (40 % au plus)')
    elif longues:
        avert(quiz['id'], None, f'bonne réponse nettement la plus longue dans {longues}/{nb_qcu} QCU')
    if nb_qcu and plus_longues / nb_qcu > 0.4:
        avert(quiz['id'], None, f'bonne réponse la plus longue dans plus de 40 % des questions ({plus_longues}/{nb_qcu} QCU)')


# ---------------------------------------------------------------- XML
def verifier_xml(quiz, chemin):
    with open(chemin, encoding='utf-8') as f:
        brut = f.read()
    try:
        racine = ET.fromstring(brut)
    except ET.ParseError as e:
        err(quiz['id'], None, f'XML mal formé : {e}')
        return
    pos = B.positions_du_quiz(quiz)
    attendu = B.construire_xml(quiz, pos)
    if brut != attendu:
        err(quiz['id'], None, 'XML pas à jour : relancer construire_qcm.py')
    qs = racine.findall('question')
    if not qs or qs[0].get('type') != 'category' or '<infos><name>' not in (qs[0].findtext('category/text') or ''):
        err(quiz['id'], None, 'catégorie Pronote (infos, name, niveau, matiere) absente')
    qs = qs[1:]
    if len(qs) != len(quiz['questions']):
        err(quiz['id'], None, 'nombre de questions différent de la source')
    lettres = ''
    for q, src in zip(qs, quiz['questions']):
        qid = src['id']
        t = q.get('type')
        for tag in ('name/text', 'questiontext', 'externallink', 'usecase', 'defaultgrade'):
            if q.find(tag) is None:
                err(quiz['id'], qid, f'balise <{tag}> absente')
        if q.find('questiontext').get('format') != 'html':
            err(quiz['id'], qid, 'questiontext sans format="html"')
        qt = q.findtext('questiontext/text') or ''
        if 'Objectif :' not in qt[:400]:
            err(quiz['id'], qid, 'objectif non affiché au début')
        if (src.get('code') and C.FOND_CODE not in qt):
            err(quiz['id'], qid, 'bloc de code non coloré')
        if t == 'multichoice':
            for tag in ('single', 'shuffleanswers'):
                if q.find(tag) is None:
                    err(quiz['id'], qid, f'balise <{tag}> absente')
            ans = q.findall('answer')
            if any(a.find('feedback/text') is None for a in ans):
                err(quiz['id'], qid, 'réponse sans <feedback>')
            if q.findtext('single') == 'true':
                fr = [a.get('fraction') for a in ans]
                if fr.count('100') != 1 or any(x not in ('0', '100') for x in fr):
                    err(quiz['id'], qid, f'fractions {fr} (une à 100, les autres à 0)')
                else:
                    lettres += C.LETTRES[fr.index('100')]
            if any(re.search(r'<(b|strong)\b', a.findtext('text') or '') for a in ans):
                err(quiz['id'], qid, 'gras dans une option')
        elif t == 'shortanswer':
            if not q.findall('answer'):
                err(quiz['id'], qid, 'réponse courte sans réponse')
        elif t == 'numerical':
            if q.find('answer/tolerance') is None:
                err(quiz['id'], qid, 'réponse numérique sans tolérance')
        elif t == 'matching':
            if len(q.findall('subquestion')) < 3:
                err(quiz['id'], qid, 'appariement de moins de 3 paires')
            droites = [s.findtext('answer/text') for s in q.findall('subquestion')]
            if C.dans_l_ordre(droites):
                err(quiz['id'], qid, f'appariement dans l\'ordre de la solution : {droites}')
        elif t == 'cloze':
            if '{:' not in qt:
                err(quiz['id'], qid, 'texte à trous sans trou')
            pos = [[c.startswith('%100%') for c in m.split('~')].index(True)
                   for m in re.findall(r'\{:MULTICHOICE:([^}]*)\}', qt)]
            if C.motif_trous(pos):
                err(quiz['id'], qid, f'listes déroulantes : la bonne réponse suit le numéro du trou (places {pos})')
        for ligne in src.get('console', []):
            m = C.RE_ERREUR.match(ligne)
            if m and f'<strong>{C.echapper_code(m.group("type"))}</strong>' not in qt:
                err(quiz['id'], qid, f'console : message d\'erreur non coloré « {ligne} »')
    # positions
    if lettres:
        from collections import Counter
        c = Counter(lettres)
        n = len(lettres)
        bas, haut = n // 4 - (1 if n >= 8 else 0), -(-n // 4) + (1 if n >= 8 else 0)
        for L in C.LETTRES:
            if not bas <= c.get(L, 0) <= haut:
                err(quiz['id'], None, f'positions déséquilibrées : {lettres} ({dict(c)})')
                break
        series, periode = C.motif(lettres)
        if series:
            err(quiz['id'], None, f'série de la même lettre : {series} dans {lettres}')
        if periode:
            err(quiz['id'], None, f'motif périodique ({periode}) dans {lettres}')
    # contrastes
    fonds = {C.FOND_CODE: C.styles_de_couleur(brut) | {C.TEXTE_CODE},
             C.FOND_CONSOLE: {C.TEXTE_CONSOLE, C.ERREUR_CONSOLE}, C.FOND_CODE_EN_LIGNE: {C.TEXTE_CODE_EN_LIGNE}, '#ffffff': {C.TEXTE_OBJECTIF}}
    for fond, cols in fonds.items():
        for col in cols:
            r = C.contraste(col, fond)
            if r < C.SEUIL_CONTRASTE:
                err(quiz['id'], None, f'contraste {col} sur {fond} : {r:.2f}:1 ({C.SEUIL_CONTRASTE:.0f}:1 au moins)')
    for classe, forme in C.FORMES.items():
        if f'<span style="color: {C.COULEURS[classe]};">' in brut:
            err(quiz['id'], None, f'{classe} marqué par la couleur seule ({forme} attendu)')
    caracteres(quiz['id'], chemin)


# ---------------------------------------------------------------- aperçus
MARQUES = re.compile(r'class="[^"]*\b(juste|bonne|marque|etiquette)\b|Bonnes? réponses? :|Réponses? (attendues?|acceptées)|Juste ·|Distracteur|Retour :', re.I)


def verifier_apercus(quiz, eleve, corrige):
    """L'aperçu élève ne montre jamais la bonne réponse ; le corrigé l'écrit en toutes lettres."""
    with open(eleve, encoding='utf-8') as f:
        h = f.read()
    m = MARQUES.search(h)
    if m:
        err(quiz['id'], None, f'aperçu élève : la bonne réponse est signalée (« {m.group(0)} »)')
    lettres = iter(B.positions_du_quiz(quiz))
    with open(corrige, encoding='utf-8') as f:
        c = f.read()
    for nom, page in (('aperçu élève', h), ('corrigé', c)):
        # à l'impression, le code et les consoles passent à la ligne au lieu d'être coupés
        if not re.search(r'@media print\{[^}]*\{[^}]*white-space:pre-wrap', page):
            err(quiz['id'], None, f'{nom} : pas de règle d\'impression qui fait passer le code à la ligne')
        if 'white-space:nowrap' in page and page.count('text-indent: -') == 0 and quiz_a_du_code(quiz):
            err(quiz['id'], None, f'{nom} : lignes de code sans retrait pour la suite')
    if 'Corrigé enseignant·e' not in c or 'noindex' not in c:
        err(quiz['id'], None, 'corrigé : titre « Corrigé enseignant·e » ou balise noindex absents')
    for q in quiz['questions']:
        t = q.get('type', 'qcu')
        lettre = next(lettres) if C.est_qcu(q) else None
        for o in q.get('options', []):
            fb = html_texte(o['feedback'])
            if fb in h:
                err(quiz['id'], q['id'], 'aperçu élève : un retour (feedback) est affiché')
                break
        if t == 'qcu':
            if q['id'] not in c or f'<span class="etiquette">Bonne réponse :</span> {lettre}</p>' not in c:
                err(quiz['id'], q['id'], f'corrigé : « Bonne réponse : {lettre} » absent')
        if t in ('qcu', 'qcm'):
            ordre = [html_texte(o['texte']) for o in B.options_dans_l_ordre(q, lettre)]
            pos = [h.find(f'<li>{x}</li>', h.find(f'id="{q["id"]}"')) for x in ordre]
            if -1 in pos or pos != sorted(pos):
                err(quiz['id'], q['id'], "aperçu élève : options absentes ou pas dans l'ordre du XML")


def quiz_a_du_code(quiz):
    return any(q.get('code') or q.get('console') for q in quiz['questions'])


def html_texte(t):
    import html as H
    return H.escape(C.texte_brut(t))


# ---------------------------------------------------------------- doublons
def cle(q):
    t = ' '.join(q.get('enonce', []) + q.get('question', []) + q.get('code', []) + q.get('lignes', []))
    return re.sub(r'\s+', ' ', t.lower()).strip()


def verifier_doublons(tous):
    items = [(quiz['id'], q['id'], cle(q)) for quiz in tous for q in quiz['questions']]
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i][2], items[j][2]
            if len(a) < 30 or abs(len(a) - len(b)) > 0.2 * max(len(a), len(b)):
                continue
            r = difflib.SequenceMatcher(None, a, b).ratio()
            if a == b:
                err(f'{items[i][0]} {items[i][1]}', None, f'doublon exact de {items[j][0]} {items[j][1]}')
            elif r >= 0.9:
                avert(f'{items[i][0]} {items[i][1]}', None, f'très proche de {items[j][0]} {items[j][1]} ({r:.2f})')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sans-execution', action='store_true')
    a = ap.parse_args()
    tous = C.lire_sources()
    if not tous:
        print('aucune source')
        return 1
    for quiz in tous:
        caracteres(quiz['id'], quiz['_chemin'])
        verifier_source(quiz, not a.sans_execution)
        x = os.path.join(C.RACINE_QCM, quiz['niveau'], quiz['id'] + '.xml')
        h = os.path.join(C.RACINE_QCM, quiz['niveau'], quiz['id'] + '.html')
        k = os.path.join(C.RACINE_QCM, quiz['niveau'], quiz['id'] + '-corrige.html')
        if not all(os.path.exists(f) for f in (x, h, k)):
            err(quiz['id'], None, 'XML, aperçu élève ou corrigé absent : lancer construire_qcm.py')
            continue
        verifier_xml(quiz, x)
        for f, attendu in ((h, B.apercu_html(quiz, B.positions_du_quiz(quiz))),
                           (k, B.apercu_html(quiz, B.positions_du_quiz(quiz), corrige=True))):
            with open(f, encoding='utf-8') as g:
                if g.read() != attendu:
                    err(quiz['id'], None, f'{os.path.basename(f)} pas à jour : relancer construire_qcm.py')
            caracteres(quiz['id'], f)
        verifier_apercus(quiz, h, k)
    verifier_doublons(tous)
    nq = sum(len(q['questions']) for q in tous)
    nv = sum(len(x.get('verifications', [])) for q in tous for x in q['questions'])
    for m in AVERTISSEMENTS:
        print('  à relire :', m)
    for m in ERREURS:
        print('ERREUR', m)
    print(f'{len(tous)} quiz, {nq} questions, {nv} vérifications par exécution'
          + ('' if not a.sans_execution else ' (non lancées)') + f' : {len(ERREURS)} erreur(s), {len(AVERTISSEMENTS)} point(s) à relire.')
    return 1 if ERREURS else 0


if __name__ == '__main__':
    sys.exit(main())
