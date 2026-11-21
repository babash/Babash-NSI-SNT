def svg(P, E, W, H, label, courbes=None, r=14, taille=12, noms=None):
    courbes = courbes or {}
    o = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{label}" '
         f'style="display:block;max-width:100%;height:auto;margin:.4rem auto;color:var(--td-encre)">']
    o.append('<g fill="none" stroke="currentColor" stroke-width="1.8">')
    for e in E:
        a, b = e.split('-')
        if e in courbes:
            (c1x, c1y), (c2x, c2y) = courbes[e]
            o.append(f'<path d="M{P[a][0]},{P[a][1]} C{c1x},{c1y} {c2x},{c2y} {P[b][0]},{P[b][1]}"/>')
        else:
            o.append(f'<line x1="{P[a][0]}" y1="{P[a][1]}" x2="{P[b][0]}" y2="{P[b][1]}"/>')
    o.append('</g>')
    o.append('<g stroke="currentColor" stroke-width="1.8" style="fill:var(--td-panneau)">')
    for v, (x, y) in P.items():
        o.append(f'<circle cx="{x}" cy="{y}" r="{r}"/>')
    o.append('</g>')
    o.append(f'<g fill="currentColor" font-family="Atkinson Hyperlegible, Arial, sans-serif" font-size="{taille}" font-weight="700" text-anchor="middle">')
    for v, (x, y) in P.items():
        o.append(f'<text x="{x}" y="{y + taille * 0.36:.0f}">{(noms or {}).get(v, v)}</text>')
    o.append('</g></svg>')
    return '\n'.join(o)

amis = svg({'Y': (165, 118), 'J': (165, 30), 'G': (72, 58), 'M': (88, 140), 'A': (128, 192), 'N': (232, 192), 'E': (270, 110), 'L': (262, 30)},
           'G-J G-Y G-M J-Y J-E J-L Y-E Y-N Y-M Y-A E-N M-A G-N'.split(), 300, 235,
           "Graphe des amitiés : G relié à J, Y, N et M ; J relié à G, Y, E et L ; Y relié à G, J, E, N, M et A ; E relié à J, Y et N ; N relié à G, Y et E ; M relié à G, Y et A ; A relié à Y et M ; L relié à J.",
           courbes={'G-N': ((0, 140), (80, 290))})
villes = svg({'Ni': (35, 198), 'Av': (150, 22), 'Ax': (318, 107), 'Ar': (237, 228), 'Mp': (78, 227), 'Mr': (177, 195), 'To': (179, 61), 'Nc': (202, 104), 'Di': (244, 128)},
             'Ar-Ax Ar-Mp Ar-Mr Ar-Ni Av-Ax Av-Mr Av-Ni Ax-Di Ax-Mr Ax-Nc Ax-To Di-Nc Mr-Nc Mr-To Nc-To Mp-Ni'.split(), 340, 250,
             "Graphe G, non pondéré, de 9 villes. Ar est relié à Ax, Mp, Mr et Ni ; Av à Ax, Mr et Ni ; Ax à Ar, Av, Di, Mr, Nc et To ; Di à Ax et Nc ; Mp à Ar et Ni ; Mr à Ar, Av, Ax, Nc et To ; Nc à Ax, Di, Mr et To ; Ni à Ar, Av et Mp ; To à Ax, Mr et Nc.",
             r=16, taille=13)
if __name__ == '__main__':
    import sys
    print({'amis': amis, 'villes': villes}[sys.argv[1]])
