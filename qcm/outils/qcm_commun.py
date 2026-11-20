"""Fonctions communes aux outils des QCM Pronote : lecture des sources, coloration du code,
mise en forme du texte, contrastes, placement de la bonne réponse.

Auteur : Babash - NSI Tani Malandi. Licence MIT (code des outils)."""
import html
import json
import os
import random
import re

RACINE_QCM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER_SOURCES = os.path.join(RACINE_QCM, 'sources')
NIVEAUX = ('snt', 'nsi-premiere', 'nsi-terminale', 'transversal')
NIVEAU_PRONOTE = {'snt': '2NDE', 'nsi-premiere': '1ERE', 'nsi-terminale': 'TERMINALE', 'transversal': ''}
LETTRES = 'ABCD'

# ---------------------------------------------------------------- couleurs
# Décision de l'enseignant du 20/11/2026 (code affiché) : fond clair, coloration qui se lit aussi
# en noir et blanc (mots-clés en gras, fonctions soulignées, chaînes en italique, commentaires gris),
# contrastes d'au moins 7:1, indentation très visible (un filet par niveau sur une bande grise),
# consoles compactes (une ligne de console par ligne de texte).
SEUIL_CONTRASTE = 7.0
FOND_CODE = '#f7f7f7'
TEXTE_CODE = '#1b1b1b'
COULEURS = {
    'motcle': '#00309c',     # def, class, True, False, None
    'controle': '#6a0f8e',   # if, for, return…
    'fonction': '#5c3c00',   # fonctions natives, commandes
    'nombre': '#0a4f24',
    'chaine': '#8a1c00',
    'commentaire': '#474747',
    'option': '#00507a',     # options d'une commande (-r, -a)
    'classe': '#004d47',
}
# ce qui ne passe pas par la couleur (lisible en noir et blanc)
FORMES = {
    'motcle': 'font-weight: bold;',
    'controle': 'font-weight: bold;',
    'fonction': 'text-decoration: underline;',
    'chaine': 'font-style: italic;',
    'commentaire': 'font-style: italic;',
    'classe': 'font-weight: bold;',
}
FOND_INDENT = '#e8e8e8'
FILET_INDENT = '#6e6e6e'
FOND_CONSOLE = '#1b1b1b'
TEXTE_CONSOLE = '#f0f0f0'
# message d'erreur d'une console : en couleur, et son type en gras (lisible aussi en noir et blanc)
ERREUR_CONSOLE = '#ffb4a8'
RE_ERREUR = re.compile(r'^(?P<type>[A-Za-z_.]*(?:Error|Exception|Warning)|Parse error|Error)(?P<reste>:.*)?$')
FOND_CODE_EN_LIGNE = '#f0f0f0'
TEXTE_CODE_EN_LIGNE = '#8b0f0f'
TEXTE_OBJECTIF = '#3b3b3b'
POLICE_CODE = "font-family: 'Courier New', Courier, monospace; font-size: 14px;"
STYLE_BLOC = (f"background-color: {FOND_CODE}; color: {TEXTE_CODE}; border: 1px solid #8a8a8a; "
              f"padding: 6px 10px; {POLICE_CODE} line-height: 1.45; border-radius: 4px;")
STYLE_CONSOLE = (f"background-color: {FOND_CONSOLE}; color: {TEXTE_CONSOLE}; padding: 2px 8px; "
                 f"{POLICE_CODE} line-height: 1.35; border-radius: 3px;")
STYLE_EN_LIGNE = (f"font-family: 'Courier New', Courier, monospace; background-color: {FOND_CODE_EN_LIGNE}; "
                  f"color: {TEXTE_CODE_EN_LIGNE}; padding: 1px 4px; border-radius: 3px;")
# une ligne de code ou de console par bloc : si elle passe à la ligne (impression, écran étroit),
# la suite est en retrait.
STYLE_LIGNE = 'padding-left: 3ch; text-indent: -3ch;'


def lignes_en_blocs(lignes):
    return ''.join(f'<div style="{STYLE_LIGNE}">{l or "&nbsp;"}</div>' for l in lignes)


STYLE_INDENT = f"border-left: 2px solid {FILET_INDENT}; background-color: {FOND_INDENT};"


def luminance(hexa):
    hexa = hexa.lstrip('#')
    if len(hexa) == 3:
        hexa = ''.join(c * 2 for c in hexa)
    r, g, b = (int(hexa[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contraste(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# ---------------------------------------------------------------- coloration
PY_MOTCLE = {'def', 'class', 'True', 'False', 'None', 'lambda', 'global', 'nonlocal', 'self'}
PY_CONTROLE = {'if', 'elif', 'else', 'for', 'while', 'in', 'not', 'and', 'or', 'return', 'import', 'from',
               'as', 'pass', 'break', 'continue', 'try', 'except', 'finally', 'raise', 'with', 'is', 'del', 'assert'}
PY_NATIVES = {'print', 'len', 'range', 'int', 'str', 'float', 'list', 'dict', 'tuple', 'set', 'input', 'type',
              'enumerate', 'sorted', 'sum', 'min', 'max', 'abs', 'round', 'bin', 'hex', 'ord', 'chr', 'isinstance'}
SQL_MOTCLE = {'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN', 'IS', 'NULL', 'ORDER', 'BY',
              'ASC', 'DESC', 'JOIN', 'INNER', 'ON', 'AS', 'DISTINCT', 'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET',
              'DELETE', 'DROP', 'TABLE', 'CREATE', 'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'LIMIT', 'GROUP',
              'HAVING', 'INTEGER', 'TEXT', 'REAL', 'UNIQUE', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'PRAGMA'}

JETON_PY = re.compile(r'(?P<commentaire>#.*)'
                      r'|(?P<chaine>[fFrRbB]?("""|\'\'\'|"|\')(?:\\.|(?!\3).)*(?:\3)?)'
                      r'|(?P<nombre>\b\d+(?:\.\d+)?\b)'
                      r'|(?P<id>[A-Za-z_À-ſ][\wÀ-ſ]*)'
                      r'|(?P<autre>.)')
JETON_SQL = re.compile(r"(?P<commentaire>--.*)|(?P<chaine>'(?:''|[^'])*'?)|(?P<nombre>\b\d+(?:\.\d+)?\b)"
                       r"|(?P<id>[A-Za-z_À-ſ][\wÀ-ſ]*)|(?P<autre>.)")


def _span(classe, texte):
    forme = FORMES.get(classe, '')
    return f'<span style="color: {COULEURS[classe]};{" " + forme if forme else ""}">{texte}</span>'


def indentation(ligne):
    """Sépare l'indentation (4 espaces ou une tabulation par niveau) du reste de la ligne,
    et la dessine : un filet par niveau, sur une bande grise."""
    m = re.match(r'[ \t]*', ligne)
    blanc = m.group(0).replace('\t', ' ' * 4)
    niveaux, reste = divmod(len(blanc), 4)
    dessin = ''.join(f'<span style="{STYLE_INDENT}">{"&nbsp;" * 3}</span>&nbsp;' for _ in range(niveaux))
    return dessin + '&nbsp;' * reste, ligne[m.end():]


def echapper_code(texte):
    """Échappe et garde les espaces (insécables) pour que l'indentation reste visible."""
    t = html.escape(texte, quote=False)
    return t.replace(' ', '&nbsp;').replace('\t', '&nbsp;' * 4)


def colorer_ligne(ligne, langage):
    if langage in ('python', 'sql', 'bash') and ligne[:1] in (' ', '\t'):
        debut, reste = indentation(ligne)
        return debut + colorer_ligne(reste, langage)
    if langage == 'python':
        sortie, prec = [], ''
        for m in JETON_PY.finditer(ligne):
            k, v = m.lastgroup, m.group(0)
            if k == 'id':
                if v in PY_MOTCLE:
                    sortie.append(_span('motcle', echapper_code(v)))
                elif v in PY_CONTROLE:
                    sortie.append(_span('controle', echapper_code(v)))
                elif v in PY_NATIVES or prec in ('def',):
                    sortie.append(_span('fonction', echapper_code(v)))
                elif prec == 'class':
                    sortie.append(_span('classe', echapper_code(v)))
                else:
                    sortie.append(echapper_code(v))
                prec = v
            elif k in ('commentaire', 'chaine', 'nombre'):
                sortie.append(_span(k, echapper_code(v)))
            else:
                sortie.append(echapper_code(v))
                if not v.isspace():
                    prec = v
        return ''.join(sortie)
    if langage == 'sql':
        sortie = []
        for m in JETON_SQL.finditer(ligne):
            k, v = m.lastgroup, m.group(0)
            if k == 'id' and v.upper() in SQL_MOTCLE:
                sortie.append(_span('motcle', echapper_code(v)))
            elif k in ('commentaire', 'chaine', 'nombre'):
                sortie.append(_span(k, echapper_code(v)))
            else:
                sortie.append(echapper_code(v))
        return ''.join(sortie)
    if langage == 'bash':
        mots = re.split(r'(\s+)', ligne)
        sortie, premier = [], True
        for mot in mots:
            if not mot:
                continue
            if mot.isspace():
                sortie.append(echapper_code(mot))
            elif mot.startswith('$') and premier:
                sortie.append(_span('commentaire', echapper_code(mot)))
            elif premier:
                sortie.append(_span('fonction', echapper_code(mot)))
                premier = False
            elif mot.startswith('-'):
                sortie.append(_span('option', echapper_code(mot)))
            elif mot.startswith('#'):
                sortie.append(_span('commentaire', echapper_code(mot)))
            else:
                sortie.append(echapper_code(mot))
        return ''.join(sortie)
    return echapper_code(ligne)


def bloc_code(lignes, langage):
    corps = lignes_en_blocs(colorer_ligne(l, langage) for l in lignes)
    return f'<div style="{STYLE_BLOC}">{corps}</div>'


def ligne_console(ligne):
    """Une ligne de console ; un message d'erreur est coloré, avec son type en gras."""
    m = RE_ERREUR.match(ligne)
    if not m:
        return echapper_code(ligne)
    return (f'<span style="color: {ERREUR_CONSOLE};"><strong>{echapper_code(m.group("type"))}</strong>'
            f'{echapper_code(m.group("reste") or "")}</span>')


def bloc_console(lignes):
    corps = lignes_en_blocs(ligne_console(l) for l in lignes)
    return f'<div style="{STYLE_CONSOLE}">{corps}</div>'


def styles_de_couleur(brut):
    """Les couleurs de texte utilisées dans les spans de coloration d'un XML."""
    return set(re.findall(r'<span style="color: (#[0-9a-fA-F]{6});', brut)) - {ERREUR_CONSOLE}


# ---------------------------------------------------------------- texte
def texte_html(t):
    """`code` → code en ligne ; **gras** → gras. Le reste est échappé."""
    t = html.escape(t, quote=False)
    t = re.sub(r'`([^`]+)`', lambda m: f'<code style="{STYLE_EN_LIGNE}">{m.group(1)}</code>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    return t


def texte_brut(t):
    """Pour les options et les feedbacks (format plain_text) : on retire les marques."""
    return re.sub(r'\*\*([^*]+)\*\*', r'\1', t.replace('`', ''))


# ---------------------------------------------------------------- sources
def lire_sources(dossier=DOSSIER_SOURCES):
    quiz = []
    for niveau in NIVEAUX:
        d = os.path.join(dossier, niveau)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith('.json'):
                chemin = os.path.join(d, f)
                with open(chemin, encoding='utf-8') as fh:
                    q = json.load(fh)
                q['_chemin'] = chemin
                q['_niveau_dossier'] = niveau
                quiz.append(q)
    return quiz


def est_qcu(q):
    return q.get('type', 'qcu') == 'qcu'


# ---------------------------------------------------------------- positions
def motif(pos):
    """Renvoie (séries de 3 lettres identiques ou plus, période détectée ou None)."""
    series = [m.group(0) for m in re.finditer(r'(.)\1{2,}', pos)]
    periode = None
    for k in (2, 3, 4, 5):
        if len(pos) >= 2 * k + 2:
            same = sum(1 for i in range(k, len(pos)) if pos[i] == pos[i - k])
            if same / (len(pos) - k) >= 0.6:
                periode = k
                break
    return series, periode


def positions_equilibrees(n, graine):
    """Une suite de n lettres A-D, équilibrée, sans série de 3, sans période, déterminée par la graine."""
    if n == 0:
        return ''
    rnd = random.Random(graine)
    base = [LETTRES[i % 4] for i in range(n)]
    for _ in range(20000):
        rnd.shuffle(base)
        s = ''.join(base)
        series, periode = motif(s)
        if not series and periode is None:
            return s
    raise RuntimeError('aucune suite trouvée')


def motif_trous(pos):
    """Vrai si la place de la bonne réponse suit le numéro du trou (même place partout, même décalage,
    ou ordre inverse)."""
    n = len(pos)
    if n >= 2 and len(set(pos)) == 1:
        return True
    if n >= 2 and len({p - k for k, p in enumerate(pos)}) == 1:
        return True
    return n >= 3 and len({p + k for k, p in enumerate(pos)}) == 1


def dans_l_ordre(valeurs):
    """Vrai si les valeurs sont rangées (croissant ou décroissant), en nombres si elles le sont toutes."""
    try:
        cles = [float(v) for v in valeurs]
    except ValueError:
        cles = [str(v).casefold() for v in valeurs]
    return len(cles) >= 3 and (cles == sorted(cles) or cles == sorted(cles, reverse=True))


def ordonner_options(question, lettre):
    """Place la bonne réponse à la lettre voulue ; les distracteurs gardent leur ordre."""
    opts = question['options']
    juste = [o for o in opts if o.get('juste')]
    autres = [o for o in opts if not o.get('juste')]
    i = LETTRES.index(lettre)
    return autres[:i] + juste + autres[i:]
