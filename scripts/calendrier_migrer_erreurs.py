#!/usr/bin/env python3
"""Calendrier des vacances (T105) : range ce que montre le programme fautif d'une « erreur »
dans son champ propre, au lieu de la fin du « but ».

Pour chaque question « erreur » des thèmes du catalogue :
  - retire du « but » la phrase « Python affiche : … », « Python s'arrête et affiche : … »,
    « SQLite répond : … », « Le programme affiche : … » ou « Pas de message d'erreur, mais … » ;
  - exécute le programme fautif (comme le contrôle) et écrit le champ qui convient :
    « message » (le message réel), « affiche_fautif » (sa sortie) ou « boucle_infinie » ;
  - signale quand le texte retiré ne correspond pas à l'exécution (à relire).
Usage : python3 scripts/calendrier_migrer_erreurs.py [--ecrire]   (sans --ecrire : ne fait que montrer)
"""
import importlib.util
import json
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ce", os.path.join(ICI, "calendrier_exercices.py"))
ce = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ce)

MARQUE = re.compile(r"\s*(?:(?:Python|Le programme|La requête|SQLite)\s+(?:s'arrête et\s+)?(?:affiche|répond|renvoie)\s*:|Pas de message d'erreur, mais)\s*(.*)$", re.S)


def nettoyer(t):
    return t.strip().strip("«» .").replace("« ", "").replace(" »", "")


def pareil(ancien, nouveau):
    """Le texte retiré du but dit-il la même chose que l'exécution ?"""
    if re.search(r"aucune ligne|n'affiche rien|rien ne s'affiche", ancien):
        return nouveau == ""
    a = re.sub(r"^(la requête|le programme) (affiche|renvoie)\s*", "", ancien.strip(), flags=re.I)
    a = re.sub(r"^Error: ", "", a)
    n = re.sub(r"^Error: ", "", nouveau)
    norm = lambda t: re.sub(r"\s+", " ", t.replace(" / ", "\n")).strip(" .")
    return norm(a) == norm(n) or norm(a) in norm(n)


def main():
    ecrire = "--ecrire" in sys.argv
    cat = json.load(open(ce.CATALOGUE, encoding="utf-8"))
    for th in cat["themes"]:
        chemin = os.path.join(ce.DOSSIER, th["fichier"])
        if not os.path.exists(chemin):
            continue
        d = json.load(open(chemin, encoding="utf-8"))
        chap = d.get("theme") or d.get("chapitre")
        chap["_base"] = d.get("base_sql", "")
        n = diff = 0
        for ex in d["exercices"]:
            if ex["type"] != "erreur":
                continue
            for niv in ex["niveaux"]:
                for it in niv["items"]:
                    m = MARQUE.search(it["but"])
                    ancien = nettoyer(m.group(1)) if m else None
                    if m:
                        it["but"] = it["but"][:m.start()].rstrip()
                        if not it["but"].endswith((".", "?", "!", ")")):
                            it["but"] += "."
                    for k in ("message", "affiche_fautif", "boucle_infinie"):
                        it.pop(k, None)
                    s, err = ce.executer(chap, "\n".join(it["lignes"]))
                    if err == ce.SANS_FIN:
                        it["boucle_infinie"] = True
                    elif err:
                        it["message"] = err
                    else:
                        it["affiche_fautif"] = s
                    n += 1
                    nouveau = it.get("message") or it.get("affiche_fautif") or ""
                    if ancien is not None and not pareil(ancien, nouveau):
                        diff += 1
                        print(f"  à relire {ex['id']} : annoncé « {ancien[:70]} », exécution « {nouveau[:70]} »")
        chap.pop("_base", None)
        print(f"{th['id']} : {n} questions « erreur » rangées, {diff} à relire")
        if ecrire:
            with open(chemin, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=1)
                f.write("\n")


if __name__ == "__main__":
    main()
