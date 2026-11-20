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
FOND_CODE = '#1e1e1e'
TEXTE_CODE = '#d4d4d4'
COULEURS = {
    'motcle': '#569cd6',     # def, class, True, False, None
    'controle': '#c586c0',   # if, for, return…
    'fonction': '#dcdcaa',   # fonctions natives, commandes
    'nombre': '#b5cea8',
    'chaine': '#ce9178',
    'commentaire': '#6a9955',
    'option': '#9cdcfe',     # options d'une commande (-r, -a)
    'classe': '#4ec9b0',
}
FOND_CONSOLE = '#2d0000'
TEXTE_CONSOLE = '#f38ba8'
FOND_CODE_EN_LIGNE = '#f3f3f3'
TEXTE_CODE_EN_LIGNE = '#a31515'
TEXTE_OBJECTIF = '#3b3b3b'
STYLE_BLOC = (f"background-color: {FOND_CODE}; color: {TEXTE_CODE}; padding: 10px; "
              "font-family: 'Courier New', Courier, monospace; font-size: 14px; border-radius: 5px; line-height: 1.4;")
STYLE_CONSOLE = (f"background-color: {FOND_CONSOLE}; color: {TEXTE_CONSOLE}; padding: 10px; "
                 "font-family: 'Courier New', Courier, monospace; font-size: 14px; border-radius: 5px;")
STYLE_EN_LIGNE = (f"font-family: 'Courier New', Courier, monospace; background-color: {FOND_CODE_EN_LIGNE}; "
                  f"color: {TEXTE_CODE_EN_LIGNE}; padding: 1px 4px; border-radius: 3px;")


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
    return f'<span style="color: {COULEURS[classe]};">{texte}</span>'


def echapper_code(texte):
    """Échappe et garde les espaces (insécables) pour que l'indentation reste visible."""
    t = html.escape(texte, quote=False)
    return t.replace(' ', '&nbsp;').replace('\t', '&nbsp;' * 4)


def colorer_ligne(ligne, langage):
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
    corps = '<br>'.join(colorer_ligne(l, langage) for l in lignes)
    return f'<div style="{STYLE_BLOC}">{corps}</div>'


def bloc_console(lignes):
    corps = '<br>'.join(echapper_code(l) for l in lignes)
    return f'<div style="{STYLE_CONSOLE}">{corps}</div>'


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


def ordonner_options(question, lettre):
    """Place la bonne réponse à la lettre voulue ; les distracteurs gardent leur ordre."""
    opts = question['options']
    juste = [o for o in opts if o.get('juste')]
    autres = [o for o in opts if not o.get('juste')]
    i = LETTRES.index(lettre)
    return autres[:i] + juste + autres[i:]
