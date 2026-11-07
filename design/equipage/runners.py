"""L'équipage : neuf runners originaux (illustrations vectorielles).

3 profils × (1 femme, 1 homme, 1 indéterminé). Deux rendus :
  mode="nuit"  : couleurs pleines, néon (écran, site)
  mode="trait" : au trait sur fond blanc, teintes claires (impression)
"""

PROFILS = {
    "architecte": {"nom": "Architecte", "neon": "#22D3EE", "encre": "#0B6378",
                   "devise": "Construire des programmes solides", "glyphe": "Ar"},
    "analyste":   {"nom": "Analyste", "neon": "#A78BFA", "encre": "#5B2BB5",
                   "devise": "Faire parler les données et les réseaux", "glyphe": "An"},
    "hacker":     {"nom": "Hacker", "neon": "#FF5CA8", "encre": "#A3155C",
                   "devise": "Trouver la faille, puis la réparer", "glyphe": "Hk"},
}

PEAUX = {
    "ebene": "#4A2E22", "brune": "#6B4430", "cuivre": "#8D5B3E",
    "caramel": "#B07A55", "sable": "#D6A882", "claire": "#EBC7A6",
}

# handle, prénom affiché (aucun), genre, profil, peau, coiffure, accessoires, spécialité, réplique
RUNNERS = [
    dict(id="kestrel", nom="Kestrel", genre="f", profil="architecte", peau="brune",
         cheveux="longs", acc=["oreillette"], col="haut",
         specialite="Algorithmes et boucles",
         capacite="Quand un programme tourne en rond, Kestrel déroule chaque tour de boucle à la main.",
         replique="« Un bon plan vaut mille lignes de code. »",
         stats={"Algo": 3, "Réseau": 1, "Données": 2}),
    dict(id="vector", nom="Vector", genre="m", profil="architecte", peau="ebene",
         cheveux="degrade", acc=["barbe", "oeil"], col="veste",
         specialite="Programmation objet",
         capacite="Vector découpe tout problème en classes et en méthodes avant d'écrire la moindre ligne.",
         replique="« Chaque objet a sa place. »",
         stats={"Algo": 3, "Réseau": 1, "Données": 2}),
    dict(id="pixel", nom="Pixel", genre="n", profil="architecte", peau="caramel",
         cheveux="casque", acc=[], col="haut",
         specialite="Web et interfaces",
         capacite="Pixel teste chaque page sur trois écrans avant de la mettre en ligne.",
         replique="« Si ça ne s'affiche pas, ça n'existe pas. »",
         stats={"Algo": 2, "Réseau": 2, "Données": 2}),
    dict(id="nova", nom="Nova", genre="f", profil="analyste", peau="ebene",
         cheveux="afro", acc=["bandeau"], col="veste",
         specialite="Données et bases de données",
         capacite="Nova trouve la bonne requête du premier coup en lisant d'abord le schéma.",
         replique="« Les données ne mentent pas. Les requêtes, parfois. »",
         stats={"Algo": 2, "Réseau": 1, "Données": 3}),
    dict(id="byte", nom="Byte", genre="m", profil="analyste", peau="claire",
         cheveux="meche", acc=["lunettes"], col="haut",
         specialite="Représentation des données",
         capacite="Byte convertit de tête du binaire, de l'hexadécimal et du texte encodé.",
         replique="« Tout finit en 0 et en 1. »",
         stats={"Algo": 2, "Réseau": 2, "Données": 3}),
    dict(id="mwezi", nom="Mwezi", genre="n", profil="analyste", peau="cuivre",
         cheveux="rase", acc=["circuit"], col="veste",
         specialite="Réseaux et protocoles",
         capacite="Mwezi suit un paquet de données de routeur en routeur sans jamais le perdre.",
         replique="« Toute route mène quelque part. »",
         stats={"Algo": 1, "Réseau": 3, "Données": 2}),
    dict(id="nyota", nom="Nyota", genre="f", profil="hacker", peau="cuivre",
         cheveux="tresses", acc=["anneau"], col="haut",
         specialite="Débogage",
         capacite="Nyota lit un message d'erreur jusqu'au bout, puis trouve la ligne fautive.",
         replique="« Une erreur, c'est un indice. »",
         stats={"Algo": 2, "Réseau": 2, "Données": 1}),
    dict(id="mistral", nom="Mistral", genre="m", profil="hacker", peau="brune",
         cheveux="locks", acc=["casque_audio", "bouc"], col="veste",
         specialite="Systèmes et ligne de commande",
         capacite="Mistral fait en trois commandes ce que d'autres font en trente clics.",
         replique="« Le terminal, c'est la liberté. »",
         stats={"Algo": 2, "Réseau": 3, "Données": 1}),
    dict(id="zero", nom="Zéro", genre="n", profil="hacker", peau="sable",
         cheveux="capuche", acc=["masque"], col="haut",
         specialite="Sécurité et cryptographie",
         capacite="Zéro repère un mot de passe faible avant même qu'on le tape.",
         replique="« Personne n'est à l'abri. Surtout pas moi. »",
         stats={"Algo": 2, "Réseau": 2, "Données": 2}),
]


def assombrir(h, f):
    h = h.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return '#%02X%02X%02X' % tuple(max(0, min(255, int(c * f))) for c in (r, g, b))


def melanger(h, k, t):
    """Mélange la couleur h avec k (proportion t de k)."""
    a = [int(h.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(k.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    return '#%02X%02X%02X' % tuple(int(x + (y - x) * t) for x, y in zip(a, b))


VISAGE = "M150 92C186 92 206 118 206 154C206 186 190 207 172 217C163 222 157 224 150 224C143 224 137 222 128 217C110 207 94 186 94 154C94 118 114 92 150 92Z"
CRANE = "M94 150C94 112 118 86 150 86S206 112 206 150"


def portrait(r, mode="nuit", uid=None, fond=True, badge=False):
    """Renvoie le SVG (viewBox 300×360) du runner r."""
    p = PROFILS[r["profil"]]
    neon = p["neon"]
    uid = uid or r["id"] + "-" + mode
    nuit = mode == "nuit"
    peau = PEAUX[r["peau"]]
    if nuit:
        peau_f, ombre, trait, tw = peau, assombrir(peau, .72), "none", 0
        cheveux = "#14101A"
        tissu, tissu2 = "#141B2E", "#0D1222"
        acc = neon
    else:
        peau_f, ombre = melanger(peau, "#FFFFFF", .55), melanger(peau, "#FFFFFF", .35)
        trait, tw = "#0B1020", 3
        cheveux = "#3A3F4C"
        tissu, tissu2 = "#FFFFFF", "#E9ECF2"
        acc = p["encre"]
    S = 'stroke="%s" stroke-width="%s" stroke-linejoin="round" stroke-linecap="round"' % (trait, tw)
    if badge:
        fond = False
    vb = "58 60 184 184" if badge else "0 0 300 360"
    out = ['<svg class="%s" viewBox="%s" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s, %s">'
           % ("runner-badge" if badge else "runner", vb, r["nom"], p["nom"].lower())]
    out.append('<defs><clipPath id="cp-%s"><path d="M0 0H282L300 18V360H18L0 342Z"/></clipPath>' % uid)
    out.append('<linearGradient id="bg-%s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#070B16"/>'
               '<stop offset=".7" stop-color="%s"/><stop offset="1" stop-color="#070B16"/></linearGradient>'
               % (uid, melanger("#070B16", neon, .22)))
    out.append('<radialGradient id="halo-%s" cx=".5" cy=".42" r=".5"><stop offset="0" stop-color="%s" stop-opacity=".55"/>'
               '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient></defs>' % (uid, neon, neon))
    out.append('<g clip-path="url(#cp-%s)">' % uid)

    # ── Décor ──
    if fond and nuit:
        out.append('<rect width="300" height="360" fill="url(#bg-%s)"/>' % uid)
        for i in range(9):  # grille hexagonale lointaine
            y = 18 + i * 26
            for j in range(8):
                x = 10 + j * 40 + (20 if i % 2 else 0)
                out.append('<path d="M%d %dl10 -6l10 6v12l-10 6l-10 -6z" fill="none" stroke="%s" stroke-opacity=".08"/>' % (x, y, neon))
        # immeubles
        xs = [(0, 250, 34), (30, 228, 26), (60, 262, 40), (232, 236, 30), (258, 214, 44)]
        for x, y, w in xs:
            out.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#050810"/>' % (x, y, w, 360 - y))
            for k in range(4):
                out.append('<rect x="%d" y="%d" width="3" height="4" fill="%s" opacity=".7"/>' % (x + 6 + (k * 7) % (w - 8), y + 10 + k * 13, neon))
        out.append('<circle cx="150" cy="150" r="140" fill="url(#halo-%s)"/>' % uid)
        # pluie de données
        for k in range(14):
            x = (k * 53 + 17) % 300
            out.append('<rect x="%d" y="%d" width="1.5" height="%d" fill="%s" opacity=".35"/>' % (x, (k * 37) % 140, 14 + (k * 11) % 30, neon))
    elif fond:
        out.append('<rect width="300" height="360" fill="#FFFFFF"/>')
        for i in range(9):
            y = 18 + i * 26
            for j in range(8):
                x = 10 + j * 40 + (20 if i % 2 else 0)
                out.append('<path d="M%d %dl10 -6l10 6v12l-10 6l-10 -6z" fill="none" stroke="#C9D0DC" stroke-width="1"/>' % (x, y))

    c = r["cheveux"]
    # ── Cheveux, arrière ──
    if c == "longs":
        out.append('<path d="M86 156C82 112 108 80 150 80S218 112 214 156C216 210 226 250 236 286C206 300 94 300 64 286C74 250 84 210 86 156Z" fill="%s" %s/>' % (cheveux, S))
    elif c == "afro":
        import math
        pts = []
        for i in range(19):
            a = math.radians(200 - i * (220 / 18))
            pts.append((150 + 92 * math.cos(a), 140 - 86 * math.sin(a)))
        d = "M%.1f %.1f" % pts[0] + "".join("A18 18 0 0 1 %.1f %.1f" % q for q in pts[1:]) + "Z"
        out.append('<path d="%s" fill="%s" %s/>' % (d, cheveux, S))
    elif c == "locks":
        for x0, x1, y1 in [(100, 84, 262), (112, 98, 276), (124, 116, 284), (176, 184, 284), (188, 202, 276), (200, 216, 262)]:
            out.append('<path d="M%d 120C%d 180 %d 220 %d %d" fill="none" stroke="%s" stroke-width="15" stroke-linecap="round"/>'
                       % (x0, x0 - 6, x1, x1, y1, trait if not nuit else cheveux))
            if not nuit:
                out.append('<path d="M%d 120C%d 180 %d 220 %d %d" fill="none" stroke="%s" stroke-width="9" stroke-linecap="round"/>'
                           % (x0, x0 - 6, x1, x1, y1, "#D9DCE3"))
    elif c == "tresses":
        for x0, x1, y1 in [(196, 214, 280), (206, 228, 268)]:
            out.append('<path d="M%d 130C%d 190 %d 230 %d %d" fill="none" stroke="%s" stroke-width="13" stroke-dasharray="9 3" stroke-linecap="round"/>'
                       % (x0, x0 + 8, x1, x1, y1, trait if not nuit else cheveux))
    elif c == "capuche":
        out.append('<path d="M70 300C62 220 66 150 92 112C112 84 132 74 150 74S188 84 208 112C234 150 238 220 230 300Z" fill="%s" %s/>' % (tissu2 if nuit else "#E9ECF2", S))

    # ── Corps ──
    out.append('<path d="M30 360C34 300 70 268 124 254H176C230 268 266 300 270 360Z" fill="%s" %s/>' % (tissu, S))
    out.append('<path d="M128 206V262C138 270 162 270 172 262V206Z" fill="%s" %s/>' % (ombre, S))
    if r["col"] == "haut":
        out.append('<path d="M116 250C120 236 128 230 150 230S180 236 184 250L190 276C170 284 130 284 110 276Z" fill="%s" %s/>' % (tissu2, S))
        out.append('<path d="M112 274C136 282 164 282 188 274" fill="none" stroke="%s" stroke-width="3"/>' % acc)
    else:
        out.append('<path d="M124 254L150 312L176 254" fill="%s" %s/>' % (ombre if nuit else peau_f, S))
        out.append('<path d="M98 262L150 340L202 262" fill="none" stroke="%s" stroke-width="3"/>' % acc)
        out.append('<path d="M124 254L104 262L150 334M176 254L196 262L150 334" fill="none" stroke="%s" stroke-width="%s"/>' % (trait if not nuit else "#1E2B47", 3 if not nuit else 4))
    # épaulettes / liseré néon
    out.append('<path d="M46 318C60 296 80 282 104 274" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round" opacity=".9"/>' % acc)
    out.append('<path d="M254 318C240 296 220 282 196 274" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round" opacity=".6"/>' % acc)

    # ── Tête ──
    out.append('<path d="M96 146C84 146 82 170 98 178ZM204 146C216 146 218 170 202 178Z" fill="%s" %s/>' % (peau_f, S))
    out.append('<path d="%s" fill="%s" %s/>' % (VISAGE, peau_f, S))
    # ombre portée côté gauche, lumière néon côté droit
    out.append('<path d="M150 92C114 92 94 118 94 154C94 186 110 207 128 217C137 222 143 224 150 224C128 210 118 180 120 150C122 118 134 100 150 92Z" fill="%s" opacity="%s"/>' % (ombre, ".55" if nuit else ".6"))
    if nuit:
        out.append('<path d="M190 112C202 126 206 142 206 156C206 182 194 202 178 213" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round" opacity=".9"/>' % neon)

    masque = "masque" in r["acc"]
    casque = c == "casque"
    # ── Visage ──
    yeux_neon = casque or masque
    if not casque:
        if not masque:
            # sourcils
            out.append('<path d="M116 143C123 138 133 138 140 142M160 142C167 138 177 138 184 143" fill="none" stroke="%s" stroke-width="4" stroke-linecap="round"/>' % ("#0B1020" if not nuit else "#14101A"))
        # yeux
        if masque:
            out.append('<path d="M118 158C124 152 134 152 140 158M160 158C166 152 176 152 182 158" fill="none" stroke="%s" stroke-width="4" stroke-linecap="round"/>' % (neon if nuit else acc))
        else:
            for ex in (128, 172):
                out.append('<path d="M%d 158C%d 151 %d 151 %d 158C%d 163 %d 163 %d 158Z" fill="%s"/>'
                           % (ex - 11, ex - 5, ex + 5, ex + 11, ex + 5, ex - 5, ex - 11, "#0B1020" if not nuit else "#F4F1EC"))
                out.append('<circle cx="%d" cy="157.6" r="3.6" fill="%s"/>' % (ex, "#FFFFFF" if not nuit else "#2A1C16"))
                if nuit:
                    out.append('<circle cx="%d" cy="156.4" r="1.2" fill="#FFFFFF"/>' % (ex + 1))
            # nez, bouche
            out.append('<path d="M150 162C148 172 145 178 144 183C147 186 153 186 157 184" fill="none" stroke="%s" stroke-width="2.6" stroke-linecap="round" opacity=".8"/>' % assombrir(peau, .55))
            out.append('<path d="M138 198C145 202 155 202 162 198" fill="none" stroke="%s" stroke-width="3.2" stroke-linecap="round"/>' % assombrir(peau, .45))
    # ── Accessoires du visage ──
    if "barbe" in r["acc"]:
        out.append('<path d="M100 170C104 196 122 222 150 224C178 222 196 196 200 170C192 186 182 192 172 192C164 186 136 186 128 192C118 192 108 186 100 170Z" fill="%s" %s/>' % (cheveux, S))
        out.append('<path d="M140 199C146 202 154 202 160 199" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % assombrir(peau, .45))
    if "bouc" in r["acc"]:
        out.append('<path d="M140 206C144 216 156 216 160 206C154 210 146 210 140 206Z" fill="%s" %s/>' % (cheveux, S))
    if "oeil" in r["acc"]:
        out.append('<circle cx="172" cy="158" r="9" fill="none" stroke="%s" stroke-width="2.4"/><circle cx="172" cy="157.6" r="3.6" fill="%s"/>' % (acc, acc))
        out.append('<path d="M181 158H198M190 158V168" fill="none" stroke="%s" stroke-width="2"/>' % acc)
    if "lunettes" in r["acc"]:
        out.append('<rect x="112" y="148" width="32" height="20" rx="3" fill="%s" fill-opacity=".18" stroke="%s" stroke-width="3.2"/>' % (acc, acc))
        out.append('<rect x="156" y="148" width="32" height="20" rx="3" fill="%s" fill-opacity=".18" stroke="%s" stroke-width="3.2"/><path d="M144 156H156" stroke="%s" stroke-width="3"/>' % (acc, acc, acc))
    if "circuit" in r["acc"]:
        out.append('<path d="M110 120L124 106H140M124 106V96M186 128L196 118V104M196 118H208" fill="none" stroke="%s" stroke-width="2.6" stroke-linecap="round"/>' % acc)
        for x, y in ((140, 106), (124, 96), (196, 104)):
            out.append('<circle cx="%d" cy="%d" r="3" fill="%s"/>' % (x, y, acc))
    if masque:
        out.append('<path d="M100 172C112 168 128 170 150 170S188 168 200 172C198 196 182 222 150 224C118 222 102 196 100 172Z" fill="%s" %s/>' % (tissu2 if nuit else "#E9ECF2", S))
        out.append('<path d="M112 186H188M118 200H182" fill="none" stroke="%s" stroke-width="2" opacity=".7"/>' % acc)
        for ex in (128, 172):
            out.append('<circle cx="%d" cy="158" r="2.6" fill="%s"/>' % (ex, neon if nuit else acc))

    # ── Cheveux, avant ──
    if c == "longs":
        out.append('<path d="M94 152C92 112 116 86 152 86C184 86 206 108 208 142C190 128 166 112 146 106C132 124 112 138 94 152Z" fill="%s" %s/>' % (cheveux, S))
    elif c == "afro":
        out.append('<path d="M96 140C100 108 122 90 150 90S200 108 204 140C186 124 168 118 150 118S114 124 96 140Z" fill="%s" %s/>' % (cheveux, S))
    elif c == "degrade":
        out.append('<path d="M96 138C96 106 118 84 150 84S204 106 204 138C196 124 180 116 150 116S104 124 96 138Z" fill="%s" %s/>' % (cheveux, S))
        out.append('<path d="M98 132C99 140 99 150 98 158M202 132C201 140 201 150 202 158" fill="none" stroke="%s" stroke-width="5" opacity=".55"/>' % cheveux)
    elif c == "meche":
        out.append('<path d="M98 140C96 104 120 82 154 82C184 82 206 98 210 122C196 112 172 108 150 112C130 116 112 124 98 140Z" fill="%s" %s/>' % (cheveux, S))
        out.append('<path d="M150 112C170 104 196 110 210 122C194 120 172 122 156 128Z" fill="%s" %s/>' % (assombrir(cheveux, 1.6) if nuit else "#6B7180", S))
    elif c == "rase":
        out.append('<path d="M96 132C98 104 120 88 150 88S202 104 204 132C186 118 168 114 150 114S114 118 96 132Z" fill="%s" opacity="%s"/>' % (cheveux, ".35" if nuit else ".25"))
    elif c == "tresses":
        out.append('<path d="M96 140C96 106 118 84 150 84S204 106 204 140C190 120 172 112 150 112S110 120 96 140Z" fill="%s" %s/>' % (cheveux, S))
        for k in range(4):
            out.append('<path d="M%d 92C%d 104 %d 112 %d 120" fill="none" stroke="%s" stroke-width="2" opacity=".6"/>' % (118 + k * 18, 120 + k * 18, 122 + k * 18, 124 + k * 18, acc))
        out.append('<path d="M96 130C94 140 94 150 96 160" fill="none" stroke="%s" stroke-width="5" opacity=".5"/>' % cheveux)
    elif c == "locks":
        out.append('<path d="M96 140C96 104 118 82 150 82S204 104 204 140C196 120 176 108 150 110S104 120 96 140Z" fill="%s" %s/>' % (cheveux, S))
        out.append('<rect x="138" y="80" width="24" height="10" rx="3" fill="%s"/>' % acc)
    elif c == "capuche":
        out.append('<path d="M92 210C80 160 88 118 108 98C124 82 138 78 150 78S176 82 192 98C212 118 220 160 208 210C206 168 196 128 180 110C170 100 160 96 150 96S130 100 120 110C104 128 94 168 92 210Z" fill="%s" %s/>' % (tissu if nuit else "#FFFFFF", S))
        out.append('<path d="M108 102C126 88 174 88 192 102" fill="none" stroke="%s" stroke-width="3"/>' % acc)
    elif c == "casque":
        out.append('<path d="M86 196C82 132 108 80 150 80S218 132 214 196C200 206 100 206 86 196Z" fill="%s" %s/>' % (tissu2 if nuit else "#FFFFFF", S))
        out.append('<path d="M104 140H196L202 176C180 184 120 184 98 176Z" fill="%s" fill-opacity="%s" stroke="%s" stroke-width="3"/>' % (acc, ".85" if nuit else ".25", acc))
        out.append('<path d="M112 152H188" stroke="%s" stroke-width="2.4" opacity=".9"/>' % ("#FFFFFF" if nuit else acc))
        out.append('<path d="M204 110L222 82M216 168H232" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round"/><circle cx="224" cy="78" r="5" fill="%s"/>' % (trait if not nuit else "#A9B6D0", acc))

    if "oreillette" in r["acc"]:
        out.append('<path d="M98 166V188L124 200" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round"/><circle cx="98" cy="160" r="6" fill="%s"/>' % (acc, acc))
    if "bandeau" in r["acc"]:
        out.append('<path d="M98 122C126 108 174 108 202 122" fill="none" stroke="%s" stroke-width="7" stroke-linecap="round"/>' % acc)
    if "anneau" in r["acc"]:
        out.append('<circle cx="204" cy="178" r="5" fill="none" stroke="%s" stroke-width="2.6"/>' % acc)
    if "casque_audio" in r["acc"]:
        out.append('<path d="M92 156C88 102 116 74 150 74S212 102 208 156" fill="none" stroke="%s" stroke-width="7"/>' % (trait if not nuit else "#2A3654"))
        out.append('<rect x="80" y="140" width="20" height="36" rx="6" fill="%s" %s/><rect x="200" y="140" width="20" height="36" rx="6" fill="%s" %s/>' % (acc, S, acc, S))

    out.append('</g>')
    if badge:
        out.append('</svg>')
        return "".join(out)
    # cadre avec coin coupé
    out.append('<path d="M1.5 1.5H281.4L298.5 18.6V358.5H18.6L1.5 341.4Z" fill="none" stroke="%s" stroke-width="3"/>' % (neon if nuit else "#0B1020"))
    out.append('</svg>')
    return "".join(out)


if __name__ == "__main__":
    import sys
    cartes = []
    for r in RUNNERS:
        cartes.append('<figure><div>%s</div><div>%s</div><figcaption>%s · %s · %s</figcaption></figure>'
                      % (portrait(r, "nuit"), portrait(r, "trait"), r["nom"], r["genre"], r["profil"]))
    open(sys.argv[1], "w").write('<!doctype html><meta charset=utf-8><style>body{margin:0;padding:10px;font:13px sans-serif;display:grid;grid-template-columns:repeat(5,1fr);gap:10px}figure{margin:0}figure>div{display:inline-block;width:49%}svg{width:100%;display:block}</style>' + "".join(cartes))
