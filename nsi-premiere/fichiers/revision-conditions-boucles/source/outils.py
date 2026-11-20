"""Outils communs des feuilles de Première (robot, code coloré, grilles, styles), repris du générateur du contrôle sans son contenu."""
import html, io, re, sys, contextlib

COLS = "ABCDEFGH"
NL = 6

# ---------------------------------------------------------------- robot
class Ecrase(Exception):
    pass


def pos(c):
    return COLS.index(c[0]), int(c[1]) - 1


def nom(p):
    return COLS[p[0]] + str(p[1] + 1)


def lancer(code, depart, obstacles, entrees=(), nc=8, nl=6):
    """Exécute un programme ; renvoie (chemin, affichage)."""
    obs = {pos(o) for o in obstacles}
    chemin = [pos(depart)]
    compteur = [0]
    D = {"nord": (0, -1), "sud": (0, 1), "est": (1, 0), "ouest": (-1, 0)}

    def bloque(d):
        x, y = chemin[-1]
        x, y = x + D[d][0], y + D[d][1]
        return not (0 <= x < nc and 0 <= y < nl) or (x, y) in obs

    def tic():
        compteur[0] += 1
        if compteur[0] > 500:
            raise RuntimeError("boucle infinie")

    env = {}
    for d in D:
        def bouge(d=d):
            tic()
            if bloque(d):
                raise Ecrase(d)
            x, y = chemin[-1]
            chemin.append((x + D[d][0], y + D[d][1]))
        def test(d=d):
            tic()
            return bloque(d)
        env[d] = bouge
        env["obstacle" + d.capitalize()] = test
    file = list(entrees)
    env["input"] = lambda *a: file.pop(0)
    sortie = io.StringIO()
    with contextlib.redirect_stdout(sortie):
        exec(code, env)
    return chemin, sortie.getvalue().strip().split("\n") if sortie.getvalue().strip() else []


# ---------------------------------------------------------------- code
MOTS = {"if", "elif", "else", "for", "in", "while", "not", "and", "or", "def", "return", "True", "False"}
JETON = re.compile(r'("[^"\n]*")|(\d+(?:\.\d+)?)|([A-Za-zÀ-ÿ_]\w*)(\s*\()?')


def colorer(t):
    out, i = [], 0
    for m in JETON.finditer(t):
        out.append(html.escape(t[i:m.start()]))
        if m.group(1):
            out.append(f'<span class="s">{html.escape(m.group(1))}</span>')
        elif m.group(2):
            out.append(f'<span class="n">{m.group(2)}</span>')
        else:
            mot, par = m.group(3), m.group(4) or ""
            if mot in MOTS:
                out.append(f'<span class="k">{mot}</span>{par}')
            elif par:
                out.append(f'<span class="f">{mot}</span>{par}')
            else:
                out.append(mot)
        i = m.end()
    out.append(html.escape(t[i:]))
    return "".join(out)


def pre(code, corrige=False, cls="py"):
    """Les passages entre ⟦ ⟧ sont des trous (remplis dans le corrigé)."""
    parts = re.split(r"⟦(.*?)⟧", code)
    out = []
    for i, p in enumerate(parts):
        if i % 2 == 0:
            out.append(colorer(p))
        elif corrige:
            out.append(f'<span class="rep">{colorer(p)}</span>')
        else:
            w = 5.8 if len(p) <= 2 else 8.7 if len(p) <= 5 else 14.5 if len(p) <= 10 else 20.3
            out.append(f'<span class="blank" style="width:{w}ch"></span>')
    return f'<pre class="{cls}">' + "".join(out) + "</pre>"


def plein(code):
    return code.replace("⟦", "").replace("⟧", "")


# ---------------------------------------------------------------- grilles
ROBOT = ('<svg width="{t}" height="{t}" viewBox="0 0 24 24" aria-label="robot"><line x1="12" y1="2" x2="12" y2="6" stroke="#1a2a6c" stroke-width="1.6"/>'
         '<circle cx="12" cy="2.5" r="1.6" fill="#b21f1f"/><rect x="4" y="6" width="16" height="13" rx="3" fill="#1a2a6c"/>'
         '<circle cx="9" cy="11.5" r="2" fill="#fff"/><circle cx="15" cy="11.5" r="2" fill="#fff"/><rect x="8.5" y="15" width="7" height="1.6" rx=".8" fill="#fff"/>'
         '<rect x="6" y="19" width="3" height="3" fill="#1a2a6c"/><rect x="15" y="19" width="3" height="3" fill="#1a2a6c"/></svg>')
OBST = ('<svg width="{t}" height="{t}" viewBox="0 0 24 24" aria-label="obstacle"><rect x="2" y="2" width="20" height="20" rx="2" fill="#3a4152"/>'
        '<path d="M5 5L19 19M19 5L5 19" stroke="#c9ced8" stroke-width="2.2"/></svg>')
CIBLE = ('<svg width="{t}" height="{t}" viewBox="0 0 24 24" aria-label="arrivée"><path d="M12 2l2.9 6.6 7.1.7-5.4 4.8 1.6 7-6.2-3.7-6.2 3.7 1.6-7L2 9.3l7.1-.7z" '
         'fill="#fff" stroke="#b21f1f" stroke-width="2"/></svg>')


def grille(depart, obstacles, cell=5.2, cible=None, chemin=None, nc=8, nl=6):
    t = round(cell * 2.9)
    obs = {pos(o) for o in obstacles}
    vus = set(chemin or [])
    fin = chemin[-1] if chemin else None
    s = [f'<table class="rgrid" style="--cell:{cell}mm"><tr><th></th>' + "".join(f"<th>{c}</th>" for c in COLS[:nc]) + "</tr>"]
    for y in range(nl):
        s.append(f"<tr><th>{y + 1}</th>")
        for x in range(nc):
            cl = ' class="fin"' if (x, y) == fin else ' class="vu"' if (x, y) in vus else ""
            c = ""
            if (x, y) in obs:
                c = OBST.format(t=t)
            elif (x, y) == pos(depart):
                c = ROBOT.format(t=t)
            elif cible and (x, y) == pos(cible):
                c = CIBLE.format(t=t)
            s.append(f"<td{cl}>{c}</td>")
        s.append("</tr>")
    s.append("</table>")
    return "".join(s)



# ---------------------------------------------------------------- pages
def lignes(n):
    return '<div class="lines">' + "<i></i>" * n + "</div>"



PLUS = """
h2 { display: flex; align-items: center; gap: 4px; }
h2 .pts { margin-left: auto; font-size: .78em; font-weight: 500; text-transform: none; color: var(--muted); }
h2 .exo-num { flex: none; }
.et { color: var(--secondary); font-weight: 700; }
.bar { font-size: .95em; padding: 3px 9px; margin: 0 0 5px; }
.ident span.small { flex: .5; }
.q { grid-template-columns: 13mm 64mm 1fr; }
.q .lines i { height: 7.2mm; }
.e2 { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; }
.q3.e { grid-template-columns: 11mm 1fr; row-gap: 2px; padding: 4px 8px 5px; }
.q3.e > div:last-child { grid-column: 1 / -1; }
.q3.e pre { margin: 0; font-size: 8pt; }
.q3.e .cap { font-style: italic; margin-top: 2px; }
.q3.e .lines i { height: 7mm; }
.ex5 > .item.w5 { grid-column: span 5; }
.p2 pre.fill { line-height: 2.2; }
.p2 .q3.e .lines i { height: 7.4mm; }
.p2 .ex5 { gap: 6px; }
.r8 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.rr { border: 1.5px solid var(--border); border-radius: 4px; padding: 9px 8px; display: grid; grid-template-columns: 1fr auto; column-gap: 8px; align-items: start; }
.rr .rc { min-width: 0; }
.rr .rc pre { margin: 2px 0 0; font-size: 7.4pt; line-height: 1.36; }
.rr .ans { margin-top: 3px; } .rr .ans span { height: 6mm; min-width: 12mm; }
.pb { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; margin-top: 6px; }
.pi { border: 1.5px solid var(--border); border-radius: 4px; padding: 6px 9px 8px; }
.pi .pp { color: var(--muted); font-size: .92em; }
.pi .lines i { height: 8.4mm; }
.pi.large { grid-column: 1 / -1; }
.pz.avec { display: grid; grid-template-columns: auto 1fr; column-gap: 14px; align-items: end; margin-top: 4px; }
.pz.avec .pg { display: flex; gap: 9px; }
.gn { text-align: center; font-size: 7.6pt; font-weight: 700; color: var(--muted); }
pre.tete { margin: 5px 0 0; font-size: 8.8pt; }
.pi .pl .lines i { padding-left: 0; }
.pi:not(.large) .lines { margin-left: 9mm; }
.rep, .rep-t { color: #0b5cad; font-weight: 600; }
.rep { background: #e8f1fb; border-radius: 2px; padding: 0 2px; }
.rep-t { margin: 0; font-weight: 500; }
pre.fixe { border-left-color: #0b5cad; background: #e8f1fb; margin: 0 0 2px; }
.sol pre { border-left-color: #0b5cad; background: #e8f1fb; font-size: 8.6pt; }
.rgrid td.vu { background: #cfe3f7; } .rgrid td.fin { background: #0b5cad; }
"""

STYLE = ""

LICENCE = "https://creativecommons.org/licenses/by-sa/4.0/deed.fr"
DEPOT = "https://github.com/babash/Babash-NSI-SNT/tree/main/nsi-premiere/fichiers/"


def credit(dossier):
    """Auteur, licence et lien vers le code source (pied de chaque page)."""
    return ('<span class="credit">Babash - NSI Tani Malandi · '
            f'<a href="{LICENCE}" target="_blank" rel="license noopener">CC BY-SA 4.0</a> · '
            f'<a href="{DEPOT}{dossier}" target="_blank" rel="noopener">Code source sur GitHub</a></span>')
