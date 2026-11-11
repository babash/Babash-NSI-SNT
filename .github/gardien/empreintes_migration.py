#!/usr/bin/env python3
"""Fichiers de migration Supabase : règle M3 et empreinte du texte (Gardien).

Usage (depuis la copie du dépôt) :
  python3 -I .github/gardien/empreintes_migration.py FICHIER.sql|DOSSIER [ …] [--requete]

Pour chaque fichier .sql (ceux d'un dossier, sous-dossiers compris) :
  - règle M3 (architecture/regles-supabase.md) : « begin; » est la première instruction et
    « commit; » la dernière, chacun seul sur sa ligne ; les commentaires d'en-tête peuvent
    précéder « begin; » ;
  - empreinte md5 du texte sans ces deux lignes, sans commentaires (/* … */, puis -- …), sans
    espaces ni « ; ». C'est l'empreinte du texte qu'enregistre apply_migration, qui reçoit le
    fichier sans « begin; » ni « commit; » : la comparer à celle du texte enregistré montre que le
    fichier du dépôt est bien celui qui a été appliqué, même si ses commentaires ou ses espaces ont
    changé depuis.
--requete affiche la requête SQL qui calcule la même empreinte du texte enregistré, à lancer en
lecture (execute_sql) : elle ne lit que supabase_migrations.schema_migrations, des métadonnées.
Code de sortie 1 si un fichier ne respecte pas M3.
"""
import argparse
import hashlib
import os
import re
import sys

REQUETE = r"""select version, name,
  md5(regexp_replace(regexp_replace(regexp_replace(array_to_string(statements, E'\n'),
      '/\*.*?\*/', '', 'g'), '--[^\n]*', '', 'g'), '[[:space:];]', '', 'g')) as empreinte
from supabase_migrations.schema_migrations order by version;"""


def empreinte(texte):
    """md5 du texte sans commentaires, sans espaces ni « ; » (même calcul que REQUETE)."""
    t = re.sub(r"/\*.*?\*/", "", texte, flags=re.S)
    t = re.sub(r"--[^\n]*", "", t)
    t = re.sub(r"[\s;]", "", t)
    return hashlib.md5(t.encode("utf-8")).hexdigest()


def examiner(chemin):
    with open(chemin, encoding="utf-8") as f:
        lignes = f.read().split("\n")
    debut = [i + 1 for i, l in enumerate(lignes) if l.strip().lower() == "begin;"]
    fin = [i + 1 for i, l in enumerate(lignes) if l.strip().lower() == "commit;"]
    pleines = [i + 1 for i, l in enumerate(lignes) if l.strip() and not l.strip().startswith("--")]
    m3 = (len(debut) == 1 and len(fin) == 1 and bool(pleines) and debut[0] == pleines[0] and fin[0] == pleines[-1])
    corps = "\n".join(l for i, l in enumerate(lignes) if (i + 1) not in debut + fin)
    return {"m3": m3, "begin": debut, "commit": fin, "md5": empreinte(corps)}


def fichiers(chemins):
    for c in chemins:
        if os.path.isdir(c):
            for racine, _, noms in os.walk(c):
                for n in sorted(noms):
                    if n.endswith(".sql"):
                        yield os.path.join(racine, n)
        else:
            yield c


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("chemins", nargs="+", help="fichiers .sql ou dossiers")
    a.add_argument("--requete", action="store_true", help="afficher la requête qui calcule l'empreinte du texte enregistré")
    o = a.parse_args()
    non_conformes = 0
    vus = 0
    for chemin in fichiers(o.chemins):
        if not os.path.isfile(chemin):
            a.error("introuvable : " + chemin)
        vus += 1
        r = examiner(chemin)
        non_conformes += not r["m3"]
        print("%-60s M3 %-4s begin %-6s commit %-6s md5 %s" % (
            chemin, "ok" if r["m3"] else "NON", r["begin"] or "-", r["commit"] or "-", r["md5"]))
    print("\n%d fichier(s), %d hors de la règle M3" % (vus, non_conformes))
    if o.requete:
        print("\nRequête (lecture de métadonnées seulement) :\n" + REQUETE)
    sys.exit(1 if non_conformes else 0)


if __name__ == "__main__":
    main()
