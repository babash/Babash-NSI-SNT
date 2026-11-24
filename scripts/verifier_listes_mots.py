#!/usr/bin/env python3
"""Contrôle des listes de mots des codes (spécification des codes, architecture/codes-acces.md, § 1.3).

La liste du site (compte commun, thème « pirates », 0007 v2.3 du 24/11/2026) est lue dans
supabase/0007-compte-commun.sql ; celle du Calendrier dans calendrier/supabase/0001-calendrier.sql.
Les listes des applications qui ont leur propre dépôt (Gombessa, Lagon Arena, Alien Python,
Court-circuit, Hello GO) sont recopiées ci-dessous, telles qu'en base.

Règles, pour chaque liste contre toutes les autres :
- 64 mots, 4 à 8 lettres A-Z, sans doublon ;
- aucun mot déjà dans une autre liste, aucun mot début d'un autre (toutes listes) ;
- distance d'édition >= 3 dans la liste, >= 2 avec les autres listes ;
- aucune suite de lettres gênante, aucun début réservé (PROF, GB).
Les 7 paires historiques entre listes déjà en service (avant le 24/11) sont signalées à part,
sans faire échouer le contrôle : ces codes sont distribués et ne changent pas.

Usage (à la racine du dépôt) :
  python3 -B scripts/verifier_listes_mots.py            contrôle la liste du site et celle du Calendrier
  python3 -B scripts/verifier_listes_mots.py FICHIER    contrôle une liste proposée (64 mots séparés par des blancs)
Code de retour : 0 si tout passe, 1 sinon. Python 3 standard.
"""
import itertools
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EN_SERVICE = {
    "gombessa": "CORAIL MANTA DUGONG LAGON RECIF ALGUE NACRE PERLE TORTUE DAUPHIN BALEINE MEROU POULPE CRABE OURSIN ETOILE EPONGE RAIE CALMAR ECUME MAREE VAGUE HOULE SABLE GALET ILOT PASSE BOUEE ANCRE VOILE PIROGUE HERBIER MANGROVE COQUILLE PHARE CORDAGE LUCIOLE HUBLOT SONAR BOUSSOLE REQUIN SARDINE THON ESPADON CREVETTE HOMARD MEDUSE PLANCTON MOUETTE ALBATROS FREGATE RADEAU KAYAK PAGAIE ESCALE ATOLL RIVAGE FALAISE GROTTE ABYSSE SILLAGE COMPAS MASQUE TUBA",
    "lagon": "BAOBAB MANGUE PAPAYE GOYAVE LETCHI ANANAS CITRON TAMARIN COROSSOL JACQUIER POMELO MANIOC VANILLE CANNELLE CURCUMA PIMENT SAFRAN GIROFLE YLANG FILAO BADAMIER PALMIER BAMBOU FOUGERE LIANE ORCHIDEE HIBISCUS EBENE MAKI GECKO CAMELEON HERON PAPILLON FOURMI CIGALE CRIQUET ESCARGOT TENREC ZEBU CABRI COLLINE VOLCAN CASCADE RIVIERE SENTIER PRAIRIE PLATEAU MONTAGNE VALLEE SOURCE ROCHER PLAGE BOSQUET SAVANE FORET JARDIN VERGER TERMITE ABEILLE KAPOK ARGILE RACINE POLLEN NECTAR",
    "alien": "COMETE FUSEE PLANETE GALAXIE METEORE SATURNE JUPITER MERCURE NEPTUNE VENUS PLUTON MARS LUNE SOLEIL ECLIPSE ZENITH COSMOS QUASAR ELECTRON NEUTRON ATOME PARSEC RADAR ANTENNE ROBOT SONDE MODULE CAPSULE NAVETTE STATION CRATERE ASTRE SIRIUS VEGA ALTAIR ORION PEGASE LICORNE PHENIX CYGNE POLAIRE CENTAURE SIGNAL LASER PLASMA GRAVITE APOGEE PERIGEE EQUINOXE SOLSTICE NOVA ALIEN TITAN SPOUTNIK APOLLO CALLISTO VAISSEAU BOREAL BOSON QUARK HALO MAGNETAR PHOBOS ORBITAL",
    "court_circuit": "MARTEAU PINCE SCIE ENCLUME PERCEUSE BOULON ECROU RIVET CHEVILLE RESSORT LEVIER TREUIL ROUAGE PISTON MOTEUR DYNAMO FUSIBLE BOBINE AIMANT DIODE PRISE AMPOULE LAMPE TORCHE SOUDURE CUIVRE NICKEL BRONZE CHROME VOLT WATT AMPERE TENSION COURANT CIRCUIT BATTERIE RELAIS FICHE NEON CAPTEUR TENAILLE SPATULE EQUERRE NIVEAU REGLE CRAYON GOMME ROULEAU COLLE AGRAFE PUNAISE VERNIS MASTIC TRUELLE BROUETTE ECHELLE ETABLI SOURIS PIXEL TURBINE HELICE TABLIER COPEAU PLANCHE",
    "grand_oral": "MICRO DECOR ESTRADE PUPITRE PODIUM COULISSE GRADIN FAUTEUIL BILLET AFFICHE SPOT TAPIS CARNET CAHIER STYLO FEUILLE LIVRE ALBUM DISQUE VINYLE COSTUME CRAVATE CHAPEAU TROPHEE RUBAN BADGE SIFFLET TAMBOUR GUITARE PIANO VIOLON SAXO CYMBALE BANJO UKULELE CLAIRON HAUTBOIS CHANSON REFRAIN COUPLET JOURNAL DIALOGUE SCRIPT LETTRE PODCAST CLIP FILM TICKET PANTIN AGENDA LANTERNE BOUGIE CHRONO HORLOGE TABLEAU ARDOISE PLUME GONG CLOCHE MIROIR TRIANGLE FANFARE BAGUETTE TROMBONE",
}
# L'ancienne liste du site (T101, jamais appliquée en v2, aucun code distribué) : pour information.
ANCIENNE_DU_SITE = set("TROTTOIR VENELLE IMPASSE ESCALIER TOITURE VERANDA PYLONE LAMPION FRESQUE POCHOIR GRAFFITI SKATE ROLLER SCOOTER VELO TAXI METRO TRAM PONT TUNNEL QUAI PARKING GARAGE KIOSQUE MARCHE ENSEIGNE VITRINE BITUME BETON BRIQUE GRILLE CLOTURE PORTAIL PARABOLE ROUTEUR MODEM BOITIER WIFI RESEAU FIBRE PAQUET OCTET CLAVIER ECRAN MANETTE BONNET AMPLI SIRENE ROCADE AVENUE FANAL VIADUC PERRON HANGAR ENTREPOT DOCK DEPOT CARGO GRUE CHANTIER GOUDRON AEROSOL RADIO BALADEUR".split())
GENANTS = sorted(set(
    "BITE ANUS SEX CUL CON PUTE PUTA NAZI PENIS ZIZI CACA PIPI MERDE NIQUE NIK FION SALOP BATAR NEGR PD KKK FDP TEUB "
    "CHATTE SEIN MORT TUER NIQU ZOB PINE MERD SS VIOL BEUH SHIT FUCK DIEU PORN CHIER PET PUE SATAN DEMON DROGUE SANG "
    "GUN KILL SALE NUL MOCHE GROS".split()))
RESERVES = ("PROF", "GB")


def lire_sql(chemin, motif):
    with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
        texte = f.read()
    bloc = re.search(motif, texte, re.S)
    if not bloc:
        sys.exit(f"ERREUR : la liste de mots est introuvable dans {chemin}")
    return re.findall(r"'([A-Z]{2,})'", bloc.group(1))


def site():
    return lire_sql("supabase/0007-compte-commun.sql", r"insert into commun\.mots \(application, rang, mot\) values(.*?);")


def vacances():
    return lire_sql("calendrier/supabase/0001-calendrier.sql", r"insert into vacances\.mots \(rang, mot\)(.*?)\]")


def dist(a, b):
    p = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        c = [i]
        for j, cb in enumerate(b, 1):
            c.append(min(p[j] + 1, c[j - 1] + 1, p[j - 1] + (ca != cb)))
        p = c
    return p[-1]


def verifier(nom, liste, autres):
    err = []
    if len(liste) != 64:
        err.append(f"{len(liste)} mots au lieu de 64")
    if len(set(liste)) != len(liste):
        err.append("doublons")
    for m in liste:
        if not (m.isascii() and m.isalpha() and m.isupper() and 4 <= len(m) <= 8):
            err.append(f"{m} : forme (4 à 8 lettres A-Z)")
        if m.startswith(RESERVES):
            err.append(f"{m} : début réservé")
        err += [f"{m} : contient {g}" for g in GENANTS if g in m]
        for app, l in autres.items():
            for x in l:
                if x == m:
                    err.append(f"{m} : déjà dans {app}")
                elif x.startswith(m) or m.startswith(x):
                    err.append(f"{m} / {app}.{x} : l'un est le début de l'autre")
                elif dist(x, m) < 2:
                    err.append(f"{m} / {app}.{x} : distance < 2")
    for a, b in itertools.combinations(liste, 2):
        if a.startswith(b) or b.startswith(a):
            err.append(f"{a} / {b} : l'un est le début de l'autre (dans la liste)")
        elif dist(a, b) < 3:
            err.append(f"{a} / {b} : distance < 3 dans la liste")
    return [f"[{nom}] {e}" for e in sorted(set(err))]


def main(args):
    listes = {k: v.split() for k, v in EN_SERVICE.items()}
    listes["vacances"] = vacances()
    commun = site()
    if args:
        with open(args[0], encoding="utf-8") as f:
            commun = f.read().split()
    erreurs = verifier("commun", commun, listes)
    erreurs += verifier("vacances", listes["vacances"], {k: v for k, v in listes.items() if k != "vacances"} | {"commun": commun})
    historiques = []
    for (a, la), (b, lb) in itertools.combinations(EN_SERVICE.items(), 2):
        for x in la.split():
            for y in lb.split():
                if x == y or x.startswith(y) or y.startswith(x):
                    historiques.append(f"{a}.{x} / {b}.{y}")
    print(f"Liste du site : {len(commun)} mots ({commun[0]} … {commun[-1]}) ; Calendrier : {len(listes['vacances'])} mots.")
    if historiques:
        print(f"Paires historiques entre listes déjà en service (signalées, non bloquantes) : {len(historiques)}")
    reprises = sorted(set(commun) & ANCIENNE_DU_SITE)
    if reprises:
        print("Mots repris de l'ancienne liste du site (aucun code distribué) : " + ", ".join(reprises))
    print("\n".join(erreurs) if erreurs else "OK : les deux listes passent toutes les règles, contre toutes les listes en service.")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
