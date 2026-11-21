"""Le robot des TD de boucles et de conditions (NSI 1re), pour vérifier les corrigés.

Grilles de 8 colonnes (A à H) et 6 lignes, ou de 6 colonnes et 5 lignes (ligne 1 en haut) ; le nord est en haut.
Les fonctions sont celles des fiches : nord(), sud(), est(), ouest() avancent d'une case ;
obstacleNord(), obstacleSud(), obstacleEst(), obstacleOuest() renvoient True si la case
voisine est un obstacle ou le bord. Avancer vers un obstacle ou le bord : le robot s'écrase
(exception Ecrase), et le programme s'arrête.

Usage : GRILLES[nom] donne les obstacles et le départ ; nouvelle(nom) remet le robot au départ ;
fonctions() renvoie le dictionnaire des huit fonctions, à mettre dans les globales d'un exec.
"""
COLONNES = "ABCDEFGH"

GRILLES = {
    # TD boucle for, exercices 4 et 5 : départ en A6
    "for": {"obstacles": {"A2", "F2", "G3", "B4", "C4", "D4", "G4", "E6"}, "depart": "A6", "lignes": 6},
    # grille sans obstacle, pour les programmes donnés hors de toute grille (« trouve l'erreur », « complète »)
    "libre": {"obstacles": set(), "depart": "A6", "lignes": 6},
    # TD instructions conditionnelles, exercices 4 et 5 : 6 colonnes (A à F), 5 lignes, départ en A3
    "si": {"obstacles": {"B1", "E2", "C3", "D5"}, "depart": "A3", "lignes": 5, "colonnes": 6},
}


class Ecrase(Exception):
    pass


class Robot:
    def __init__(self, nom="for", depart=None):
        g = GRILLES[nom]
        self.obstacles, self.lignes = set(g["obstacles"]), g["lignes"]
        self.colonnes = g.get("colonnes", len(COLONNES))
        d = depart or g["depart"]
        self.x, self.y = COLONNES.index(d[0]), int(d[1:])
        self.trajet = [self.case()]

    def case(self):
        return f"{COLONNES[self.x]}{self.y}"

    def libre(self, dx, dy):
        x, y = self.x + dx, self.y + dy
        if not (0 <= x < self.colonnes and 1 <= y <= self.lignes):
            return False
        return f"{COLONNES[x]}{y}" not in self.obstacles

    def aller(self, dx, dy):
        if not self.libre(dx, dy):
            raise Ecrase(f"le robot s'écrase en partant de {self.case()}")
        self.x += dx
        self.y += dy
        self.trajet.append(self.case())

    def fonctions(self):
        return {
            "nord": lambda: self.aller(0, -1), "sud": lambda: self.aller(0, 1),
            "est": lambda: self.aller(1, 0), "ouest": lambda: self.aller(-1, 0),
            "obstacleNord": lambda: not self.libre(0, -1), "obstacleSud": lambda: not self.libre(0, 1),
            "obstacleEst": lambda: not self.libre(1, 0), "obstacleOuest": lambda: not self.libre(-1, 0),
        }


def executer(code, nom="for", depart=None):
    """Exécute code avec le robot ; renvoie (case d'arrivée, trajet, sortie, erreur ou None)."""
    import contextlib
    import io
    r = Robot(nom, depart)
    g = {"__name__": "__main__", **r.fonctions()}
    out = io.StringIO()
    err = None
    with contextlib.redirect_stdout(out):
        try:
            exec(compile(code, "robot.py", "exec"), g)
        except Ecrase as e:
            err = str(e)
    return r.case(), r.trajet, out.getvalue(), err, g
