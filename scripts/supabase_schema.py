#!/usr/bin/env python3
"""Fabrique ou vérifie supabase/schema.sql, le script complet du socle commun (règle M2).

supabase/schema.sql réunit, dans une seule transaction, le texte des migrations
0001-droits-par-defaut.sql (les droits par défaut), 0003-schema-commun.sql (le schéma
commun) et 0005-registre-court-circuit.sql (Court-circuit dans le registre), sans le contrôle
du projet de l'enseignant : un·e collègue le lance dans son propre projet Supabase. Le texte
des migrations est recopié tel quel ; seul ce contrôle est retiré (pour 0005, tout son
garde-fou : celui de 0003, en tête, vérifie déjà le rôle et l'origine du registre).

Usage :
  python3 scripts/supabase_schema.py             récrit supabase/schema.sql
  python3 scripts/supabase_schema.py --verifier  vérifie qu'il est à jour (code 1 sinon)

Python 3 standard, sans dépendance.
"""
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER = os.path.join(RACINE, "supabase")
CIBLE = os.path.join(DOSSIER, "schema.sql")

ENTETE = """begin;
-- =============================================================================
--  Base unique : le socle commun, script complet
-- =============================================================================
--  À quoi il sert : installer le socle commun dans un projet Supabase neuf
--  (la copie d'un·e collègue), avant le script complet d'une application.
--  Il réunit, dans une seule transaction :
--   A. les droits par défaut fermés (migration 0001) ;
--   B. le schéma commun : compteur d'essais, sel secret, fonctions internes
--      et registre des tables (migration 0003) ;
--   C. le registre mis à jour : Court-circuit en plus (migration 0005) ;
--   D. le registre mis à jour : le Calendrier des vacances (migration 0009) ;
--   E. le compte commun des élèves : codes, avatar, hauts faits, XP et
--      crédits (migration 0007, version 2.3) ;
--   F. l'espace commun des enseignant·e·s et les classes communes
--      (migration 0008).
--  La migration 0002 n'y est pas : elle corrige les droits d'objets qui
--  existaient déjà dans le projet de l'enseignant.
--
--  Mode d'emploi : dans le tableau de bord de Supabase, SQL Editor, coller
--  tout le fichier, puis Run. Relancé sur un projet déjà installé, il
--  s'arrête au garde-fou du compte commun (E) sans rien modifier : tout est
--  dans une seule transaction, et le sel n'est jamais tiré deux fois.
--
--  NE PAS MODIFIER À LA MAIN : ce fichier est fabriqué à partir de 0001,
--  0003, 0005, 0009, 0007 et 0008 par scripts/supabase_schema.py (même texte, sans le
--  contrôle du projet de l'enseignant). Il change dans le même commit qu'eux
--  (règle M2).
--  Détails : LISEZMOI.md.
-- =============================================================================

"""


def lire(nom):
    with open(os.path.join(DOSSIER, nom), encoding="utf-8") as f:
        return f.read()


def entre(texte, debut, fin, nom):
    i = texte.find(debut)
    j = texte.find(fin, i)
    if i < 0 or j < 0:
        sys.exit(f"{nom} : repère introuvable ({debut!r} … {fin!r}). Le fichier a changé de forme : "
                 "adapter scripts/supabase_schema.py.")
    return texte[i:j]


def fabriquer():
    p1, p3, p5 = lire("0001-droits-par-defaut.sql"), lire("0003-schema-commun.sql"), lire("0005-registre-court-circuit.sql")
    droits = entre(p1, "-- 1. Schéma public", "\ncommit;", "0001")
    garde = entre(p3, "-- Garde-fou : le bon rôle", "\n-- ----", "0003")
    garde = garde.replace("-- Garde-fou : le bon rôle, le bon projet, pgcrypto, et aucun objet « commun »\n-- venu d'ailleurs.",
                          "-- Garde-fou : le bon rôle, pgcrypto, et aucun objet « commun » venu d'ailleurs.")
    projet = re.compile(r"  if to_regclass\('public\.snt_responses'\) is null and .*?\n  end if;\n", re.S)
    if len(projet.findall(garde)) != 1:
        sys.exit("0003 : le contrôle du projet est introuvable dans le garde-fou : adapter scripts/supabase_schema.py.")
    garde = projet.sub("", garde)
    commun = entre(p3, "-- -----------------------------------------------------------------------------\n-- 1. Le schéma",
                   "\ncommit;", "0003")
    for n in range(1, 7):
        commun = re.sub(rf"^-- {n}\. ", f"-- B{n}. ", commun, count=1, flags=re.M)
    registre = entre(p5, "-- -----------------------------------------------------------------------------\n-- 1. Le registre",
                     "\ncommit;", "0005")
    for n in range(1, 3):
        registre = re.sub(rf"^-- {n}\. ", f"-- C{n}. ", registre, count=1, flags=re.M)
    p9, p7, p8 = lire("0009-registre-vacances.sql"), lire("0007-compte-commun.sql"), lire("0008-enseignants-communs.sql")
    vacances = entre(p9, "create or replace view commun.registre", "\ncommit;", "0009")
    eleves = entre(p7, "-- Garde-fou : le bon rôle, le bon projet, le socle 0003", "\ncommit;", "0007")
    projet7 = re.compile(r"  if to_regclass\('public\.snt_responses'\) is null and .*?\n  end if;\n", re.S)
    if len(projet7.findall(eleves)) != 1:
        sys.exit("0007 : le contrôle du projet est introuvable dans le garde-fou : adapter scripts/supabase_schema.py.")
    eleves = projet7.sub("", eleves).replace("-- Garde-fou : le bon rôle, le bon projet, le socle 0003", "-- Garde-fou : le bon rôle, le socle 0003", 1)
    profs = entre(p8, "do $$", "\ncommit;", "0008")
    for n in range(1, 10):
        eleves = re.sub(rf"^-- {n}\. ", f"-- E{n}. ", eleves, count=1, flags=re.M)
    for n in range(1, 6):
        profs = re.sub(rf"^-- {n}\. ", f"-- F{n}. ", profs, count=1, flags=re.M)
    droits = droits.replace("-- 1. Schéma public", "-- A1. Schéma public").replace("-- 2. Tous les schémas", "-- A2. Tous les schémas")
    barre = "-- =============================================================================\n"
    return (ENTETE + garde.rstrip() + "\n\n"
            + barre + "-- A. Les droits par défaut (migration 0001)\n" + barre + droits.rstrip() + "\n\n"
            + barre + "-- B. Le schéma commun (migration 0003)\n" + barre + commun.rstrip() + "\n\n"
            + barre + "-- C. Le registre : Court-circuit en plus (migration 0005)\n" + barre + registre.rstrip() + "\n\n"
            + barre + "-- D. Le registre : le Calendrier des vacances (migration 0009)\n" + barre + vacances.rstrip() + "\n\n"
            + barre + "-- E. Le compte commun des élèves (migration 0007, version 2.3)\n" + barre + eleves.rstrip() + "\n\n"
            + barre + "-- F. L'espace commun des enseignant·e·s et les classes communes (migration 0008)\n" + barre + profs.rstrip()
            + "\n\ncommit;\n")


def main():
    texte = fabriquer()
    if "--verifier" in sys.argv[1:]:
        actuel = open(CIBLE, encoding="utf-8").read() if os.path.exists(CIBLE) else ""
        if actuel != texte:
            print("supabase/schema.sql n'est pas à jour : lancer python3 scripts/supabase_schema.py et le commiter "
                  "avec les migrations (règle M2).")
            return 1
        print("supabase/schema.sql est à jour (0001 + 0003 + 0005 + 0009 + 0007 + 0008).")
        return 0
    with open(CIBLE, "w", encoding="utf-8") as f:
        f.write(texte)
    print(f"supabase/schema.sql récrit ({len(texte.splitlines())} lignes).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
