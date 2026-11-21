#!/usr/bin/env python3
"""Une page de TD en ligne laisse-t-elle passer une réponse par sa source ? (Gardien 26, T124)

Usage (depuis la copie du dépôt) :
  python3 -I .github/gardien/td_papier.py PAGE.html [PAGE.html …]

Complète charte/imprimer-td.py et le contrôle « aucune réponse dans le PDF » : ces deux outils
cherchent dans le PDF les textes CACHÉS de la page (corrections, coups de pouce, retours,
réponses attendues). Ils ne voient pas une réponse qui est devenue du texte VISIBLE par une
erreur de la source. Deux cas trouvés le 21/11/2026 (TD type bac du routage) :
  1. une balise <section class="td-q"> cassée : un attribut ajouté au milieu de la valeur d'un
     autre (data-reponse="…F-> data-support="ecran">H->J…") ferme la balise trop tôt ; la fin des
     réponses s'affiche en clair, à l'écran et dans le PDF, et l'attribut ajouté est perdu ;
  2. une variante papier (data-support="papier") qui recopie le code d'une question à compléter
     avec ses réponses ([[…]]) : sur papier, le code s'imprime tel quel, réponses comprises.
L'outil signale, pour chaque page :
  - un attribut dont la valeur contient « data-…= » (balise cassée), ou un nom d'attribut qui n'en
    est pas un (avec un guillemet, par exemple : le reste d'une valeur coupée) ;
  - du texte visible qui finit comme une balise (« "> » ou « '> ») : reste d'une balise cassée ;
  - dans une question papier, ce que le moteur imprime tel quel : [[ ]] (réponses d'une question à
    compléter), pre.td-attendu, des options (.td-options, data-juste) ; les .td-correction, .td-aide
    et .td-retour y sont cachés par le moteur (imprimer-td.py le vérifie) ;
Pour information (sans compter comme un point, car une question peut être à l'écran seulement ou sur
papier seulement) : une question papier sans question écran juste avant ou juste après.
Code de sortie : 0 rien à signaler ; 1 au moins un point.
"""
import html.parser
import re
import sys

NOM = re.compile(r'^[a-z][a-z0-9-]*$')
VIDES = {'br', 'img', 'input', 'meta', 'link', 'hr', 'wbr', 'source', 'col'}
# dans une question papier (data-type="libre"), le moteur ne cache que .td-correction, .td-aide et .td-retour
# (et imprimer-td.py vérifie qu'ils ne s'impriment pas) : le reste s'imprime tel quel
VISIBLES_PAPIER = ('td-attendu', 'td-options')


class Lecteur(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.points, self.pile, self.questions = [], [], []
        self.q = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        ligne = self.getpos()[0]
        for k, v in attrs:
            if v and re.search(r'\sdata-[a-z-]+=', v):
                self.points.append((ligne, f'balise <{tag}> cassée : la valeur de {k} contient un autre attribut ({v[:70]!r})'))
        for k in a:
            if not NOM.match(k) and not k.startswith('{{'):     # {{…}} : un gabarit (charte/gabarit-td/modele.html)
                self.points.append((ligne, f'balise <{tag}> cassée : {k!r} n\'est pas un nom d\'attribut'))
        cl = (a.get('class') or '').split()
        if tag == 'section' and 'td-q' in cl:
            self.q = {'id': a.get('id'), 'support': a.get('data-support', ''), 'ligne': ligne, 'prof': len(self.pile) + 1,
                      'marques': set()}
            self.questions.append(self.q)
        elif self.q is not None and self.q['support'] == 'papier':
            for c in VISIBLES_PAPIER:
                if c in cl:
                    self.q['marques'].add(c)
            if 'data-juste' in a:
                self.q['marques'].add('data-juste')
        if tag not in VIDES:
            self.pile.append(tag)

    def handle_endtag(self, tag):
        while self.pile:
            t = self.pile.pop()
            if t == tag:
                break
        if self.q is not None and len(self.pile) < self.q['prof']:
            self.q = None

    def handle_data(self, d):
        if re.search(r'["\']>\s*$', d.strip() + ' ') and re.search(r'\|', d):
            self.points.append((self.getpos()[0], f'texte visible qui finit comme une balise : {d.strip()[:80]!r}'))
        if self.q is not None and self.q['support'] == 'papier' and '[[' in d and ']]' in d:
            self.q['marques'].add('[[ ]]')


def controler(chemin):
    lu = Lecteur()
    lu.feed(open(chemin, encoding='utf-8').read())
    points = list(lu.points)
    qs = lu.questions
    for q in qs:
        if q['support'] == 'papier' and q['marques']:
            points.append((q['ligne'], f'question papier {q["id"]} : {", ".join(sorted(q["marques"]))} (une réponse peut s\'imprimer)'))
    infos = []
    for i, q in enumerate(qs):
        if q['support'] == 'papier' and 'ecran' not in [qs[j]['support'] for j in (i - 1, i + 1) if 0 <= j < len(qs)]:
            infos.append((q['ligne'], f'(information) question papier {q["id"]} sans question écran à côté'))
    return len(qs), sorted(set(points)), infos


def main():
    total = 0
    for chemin in sys.argv[1:]:
        n, points, infos = controler(chemin)
        total += len(points)
        print(f'{chemin} : {n} question(s), {len(points)} point(s)')
        for ligne, texte in points + infos:
            print(f'  l. {ligne} : {texte}')
    sys.exit(1 if total else 0)


if __name__ == '__main__':
    main()
