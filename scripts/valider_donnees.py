#!/usr/bin/env python3
"""Vérifie les données de la bibliothèque (dossier donnees/).

Contrôles :
  - chaque fichier est un JSON valide et conforme à son schéma (donnees/schema/) ;
  - les identifiants sont uniques, et chaque fiche s'appelle <id>.json ;
  - toutes les références existent : référentiels (donnees/referentiels/valeurs.json),
    programmes (programmes.json), compétences Pix (competences-pix.json), autres fiches,
    fichiers déposés sur le site ;
  - chaque ressource a exactement un document principal ;
  - aucun document ne pointe vers une page GitHub, sauf le rôle « code source » ;
  - visibilité (cahier des charges, § 3.2) : ce que voient l'extérieur et les élèves ;
  - règle 19 (un TD de l'enseignant en PDF et en page HTML), licences et auteurs : avertissements ;
  - aucune donnée sensible : mot de passe, identifiant, clé secrète, jeton.

Python 3 standard, sans dépendance. Si le module jsonschema est installé, il sert de
contrôle supplémentaire de conformité aux schémas.

Usage :
  python3 scripts/valider_donnees.py              données du dépôt
  python3 scripts/valider_donnees.py --racine DIR  données d'une autre copie du dépôt
  python3 scripts/valider_donnees.py --strict     les avertissements comptent comme des erreurs

Code de retour : 0 si tout est valide, 1 s'il y a au moins une erreur.
"""
import argparse
import base64
import datetime
import glob
import json
import os
import re
import sys
from urllib.parse import urlsplit

RACINE_DEFAUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LISTES = ["enseignements", "niveaux", "types", "usages", "origines", "roles", "formats", "langages", "statuts"]
PUBLICS = {"exterieur": "l'extérieur", "eleve": "les élèves"}
HOTES_GITHUB = {"github.com", "gist.github.com"}
# Licences et auteurs (décision du 07/11/2026)
AUTEUR = "Babash - NSI Tani Malandi"
LICENCES_ENSEIGNANT = re.compile(r"CC BY-SA 4\.0|\bMIT\b")
ORIGINES_A_CREDITER = {"externe", "institutionnelle", "communaute"}


# ── Le rapport ──────────────────────────────────────────────────────────────

class Rapport:
    NIVEAUX = {"erreur": "ERREUR   ", "attention": "ATTENTION", "info": "INFO     "}

    def __init__(self):
        self.lignes = []

    def ajouter(self, niveau, fichier, champ, message):
        self.lignes.append((niveau, fichier, champ, message))

    def erreur(self, fichier, champ, message):
        self.ajouter("erreur", fichier, champ, message)

    def attention(self, fichier, champ, message):
        self.ajouter("attention", fichier, champ, message)

    def info(self, fichier, champ, message):
        self.ajouter("info", fichier, champ, message)

    def nombre(self, niveau):
        return sum(1 for l in self.lignes if l[0] == niveau)

    def afficher(self):
        # Regroupées par fichier, dans l'ordre où elles ont été trouvées
        for niveau, fichier, champ, message in sorted(self.lignes, key=lambda l: l[1]):
            ou = fichier + (" › " + champ if champ else "")
            print(f"{self.NIVEAUX[niveau]}  {ou} : {message}")


def pluriel(n, un, plusieurs=None):
    return f"{n} {un if n <= 1 else (plusieurs or un + 's')}"


# ── Un petit validateur de JSON Schema (le sous-ensemble utilisé par nos schémas) ─

TYPES_FR = {
    "object": "un objet { … }", "array": "une liste [ … ]", "string": "un texte entre guillemets",
    "boolean": "true ou false", "integer": "un nombre entier", "number": "un nombre", "null": "null",
}

AIDES_MOTIFS = {
    "^[a-z0-9]+(-[a-z0-9]+)*$":
        "un identifiant s'écrit en minuscules, sans accents ni espaces, avec des tirets entre les mots (exemple : td1-poo)",
    "^[a-z0-9]+(-[a-z0-9]+)*(\\.[a-z0-9]+(-[a-z0-9]+)*){0,2}$":
        "un identifiant de programme s'écrit comme snt-2019.donnees-structurees.traitement",
    "^[0-9]{4}-[0-9]{2}-[0-9]{2}$": "une date s'écrit AAAA-MM-JJ (exemple : 2026-11-07)",
    "^https?://[^\\s/$.?#][^\\s]*$": "une adresse commence par https:// et ne contient pas d'espace",
    "^[A-Za-z0-9_][A-Za-z0-9._/-]*([#?][^\\s]*)?$":
        "un chemin part de la racine du dépôt, sans « / » au début, sans espaces ni accents "
        "(exemple : nsi-terminale/fichiers/td1-poo-premiers-pas.pdf)",
    "^[0-9]{4}-[0-9]{4}$": "une année scolaire s'écrit 2026-2027",
    "^[a-z]+$": "un nom en minuscules, sans accents (exemple : bleu)",
}


def type_de(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, int):
        return "integer"
    if isinstance(v, float):
        return "number"
    if isinstance(v, str):
        return "string"
    if isinstance(v, list):
        return "array"
    return "object"


def du_type(v, attendu):
    reel = type_de(v)
    for t in (attendu if isinstance(attendu, list) else [attendu]):
        if t == reel or (t == "number" and reel == "integer"):
            return True
    return False


def joindre(chemin, cle):
    if isinstance(cle, int):
        return f"{chemin}[{cle}]"
    return f"{chemin}.{cle}" if chemin else cle


def court(v):
    t = json.dumps(v, ensure_ascii=False)
    return t if len(t) <= 60 else t[:57] + "…"


class ValidateurSchema:
    def __init__(self, schema):
        self.racine = schema

    def resoudre(self, ref):
        if not ref.startswith("#/"):
            raise ValueError(f"référence de schéma non gérée : {ref}")
        noeud = self.racine
        for morceau in ref[2:].split("/"):
            noeud = noeud[morceau]
        return noeud

    def erreurs(self, v, s=None, chemin=""):
        s = self.racine if s is None else s
        out = []
        if "$ref" in s:
            out += self.erreurs(v, self.resoudre(s["$ref"]), chemin)
        if "type" in s and not du_type(v, s["type"]):
            attendu = s["type"] if isinstance(s["type"], str) else s["type"][0]
            out.append((chemin, f"doit être {TYPES_FR[attendu]}, et non {TYPES_FR[type_de(v)]}"))
            return out
        if "const" in s and v != s["const"]:
            out.append((chemin, f"doit valoir {court(s['const'])}"))
        if "enum" in s and v not in s["enum"]:
            out.append((chemin, f"valeur {court(v)} non permise (valeurs possibles : {', '.join(map(str, s['enum']))})"))
        if isinstance(v, str):
            if "minLength" in s and len(v) < s["minLength"]:
                out.append((chemin, f"texte trop court ({pluriel(s['minLength'], 'caractère')} au moins)"))
            if "maxLength" in s and len(v) > s["maxLength"]:
                out.append((chemin, f"texte trop long ({len(v)} caractères pour {s['maxLength']} au plus)"))
            if "pattern" in s and not re.search(s["pattern"], v):
                aide = AIDES_MOTIFS.get(s["pattern"], f"motif attendu : {s['pattern']}")
                out.append((chemin, f"forme incorrecte {court(v)} : {aide}"))
            if s.get("format") == "date" and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", v):
                try:
                    datetime.date.fromisoformat(v)
                except ValueError:
                    out.append((chemin, f"date impossible {court(v)}"))
        if type_de(v) in ("integer", "number"):
            if "minimum" in s and v < s["minimum"]:
                out.append((chemin, f"doit valoir au moins {s['minimum']}"))
        if isinstance(v, list):
            if "minItems" in s and len(v) < s["minItems"]:
                out.append((chemin, f"la liste doit contenir au moins {pluriel(s['minItems'], 'élément')}"))
            if "maxItems" in s and len(v) > s["maxItems"]:
                out.append((chemin, f"la liste contient {len(v)} éléments pour {s['maxItems']} au plus"))
            if s.get("uniqueItems"):
                vus = set()
                for i, x in enumerate(v):
                    cle = json.dumps(x, sort_keys=True)
                    if cle in vus:
                        out.append((joindre(chemin, i), f"{court(x)} figure deux fois dans la liste"))
                    vus.add(cle)
            if "items" in s:
                for i, x in enumerate(v):
                    out += self.erreurs(x, s["items"], joindre(chemin, i))
        if isinstance(v, dict):
            for champ in s.get("required", []):
                if champ not in v:
                    out.append((chemin, f"champ obligatoire manquant : « {champ} »"))
            props = s.get("properties", {})
            for cle, x in v.items():
                if cle in props:
                    out += self.erreurs(x, props[cle], joindre(chemin, cle))
                elif s.get("additionalProperties") is False:
                    possibles = ", ".join(k for k in props if k != "$schema")
                    out.append((chemin, f"champ inconnu « {cle} » (champs possibles : {possibles})"))
        if "not" in s and not self.erreurs(v, s["not"], chemin):
            if "pattern" in s["not"]:
                if "\\.\\." in s["not"]["pattern"]:
                    out.append((chemin, "le chemin ne doit pas remonter d'un dossier avec « .. »"))
                else:
                    out.append((chemin, f"forme interdite (motif {s['not']['pattern']})"))
            elif s["not"].get("required"):
                noms = ["« " + n + " »" for n in s["not"]["required"]]
                if len(noms) > 1:
                    out.append((chemin, f"les champs {' et '.join(noms)} ne vont pas ensemble : n'en garder qu'un"))
                else:
                    out.append((chemin, f"le champ {noms[0]} ne doit pas être présent ici"))
            else:
                out.append((chemin, "valeur interdite"))
        if "if" in s and isinstance(v, dict):
            if not self.erreurs(v, s["if"], chemin):
                if "then" in s:
                    out += self.erreurs(v, s["then"], chemin)
            elif "else" in s:
                out += self.erreurs(v, s["else"], chemin)
        for mot in ("oneOf", "anyOf"):
            if mot in s:
                resultats = [self.erreurs(v, b, chemin) for b in s[mot]]
                valides = sum(1 for r in resultats if not r)
                if valides == 0:
                    out += self.message_formes(v, s[mot], resultats, chemin)
                elif mot == "oneOf" and valides > 1:
                    out.append((chemin, "correspond à plusieurs formes à la fois"))
        return out

    def message_formes(self, v, branches, resultats, chemin):
        # Branches de simple présence (« url » ou « fichier », un seul des deux)
        if all(set(b) <= {"required", "not"} for b in branches):
            noms = []
            for b in branches:
                noms += [n for n in b.get("required", []) if n not in noms]
            presents = [n for n in noms if isinstance(v, dict) and n in v]
            if len(presents) > 1:
                return [(chemin, f"un seul des champs {' ou '.join('« ' + n + ' »' for n in noms)}, pas les deux")]
            return [(chemin, f"il manque un des champs {' ou '.join('« ' + n + ' »' for n in noms)}")]
        # Sinon : la forme la plus proche, celle qui a le moins d'erreurs
        meilleure = min(resultats, key=len)
        return meilleure


# ── Outils ──────────────────────────────────────────────────────────────────

def relatif(racine, chemin):
    return os.path.relpath(chemin, racine).replace(os.sep, "/")


def lire_json(racine, chemin, rapport):
    nom = relatif(racine, chemin)
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        rapport.erreur(nom, f"ligne {e.lineno}, colonne {e.colno}",
                       f"JSON invalide ({e.msg}). Souvent : une virgule en trop ou oubliée, un guillemet pas refermé.")
    except UnicodeDecodeError:
        rapport.erreur(nom, "", "le fichier n'est pas enregistré en UTF-8")
    except OSError as e:
        rapport.erreur(nom, "", f"lecture impossible ({e.strerror})")
    return None


def textes(obj, chemin=""):
    """Tous les textes d'un objet JSON, avec leur emplacement."""
    if isinstance(obj, str):
        yield chemin, obj
    elif isinstance(obj, list):
        for i, x in enumerate(obj):
            yield from textes(x, joindre(chemin, i))
    elif isinstance(obj, dict):
        for k, x in obj.items():
            if k != "$schema":
                yield from textes(x, joindre(chemin, k))


def date_ok(s):
    try:
        return datetime.date.fromisoformat(s)
    except (TypeError, ValueError):
        return None


# ── Les motifs interdits ────────────────────────────────────────────────────

MOTIFS_SECRETS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "une clé privée"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"), "un jeton GitHub"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}"), "un jeton GitHub"),
    (re.compile(r"\bsb_secret_[A-Za-z0-9_-]{10,}"), "une clé secrète Supabase"),
    (re.compile(r"service[_ -]?role", re.I), "une clé « service_role » Supabase"),
    (re.compile(r"\bsk-(ant-)?[A-Za-z0-9_-]{20,}"), "une clé secrète d'API"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "une clé d'accès AWS"),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{35}"), "une clé d'API Google"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"), "un jeton Slack"),
]
# « mot de passe : xxx », « identifiant = xxx », « login: xxx »…
CHAMP_SECRET = re.compile(
    r"(?i)\b(mots? de passe|mdp|password|passwd|pwd|identifiants?|logins?|nom d'utilisateur|username|"
    r"clé secrète|cle secrete|secret|token|jeton|code d'accès)\s*[:=]\s*[«\"']?\s*([^\s,;»\"']+)")
# « identifiants de démonstration : xxx », « compte de démo : xxx »
DEMO = re.compile(
    r"(?i)\b(identifiants?|comptes?|logins?|accès|codes?)\b[^:=\n]{0,40}\b(d[ée]mo|d[ée]monstration|test)\w*"
    r"[^:=\n]{0,20}[:=]\s*\S+")
# « le mot de passe est xxx »
MDP_EST = re.compile(r"(?i)\bmots? de passe\s+(est|sera)\s+[«\"']?\s*([^\s,;»\"']+)")
URL_SECRET = re.compile(
    r"(?i)[?&](password|passwd|pwd|pass|token|access_token|api_?key|apikey|secret|auth|key|cle)=([^&#\s]+)")
JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.(eyJ[A-Za-z0-9_-]{8,})\.[A-Za-z0-9_-]{8,}")
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b")
# Ce qui suit « identifiant : » sans être une valeur secrète (« comptes : sur demande »…)
MOTS_ANODINS = {
    "a", "à", "au", "aux", "aucun", "aucune", "des", "donné", "donnés", "donnée", "données", "en", "fourni",
    "fournis", "fournie", "fournies", "l'enseignant", "l'élève", "la", "le", "les", "non", "oui", "par",
    "personnel", "personnels", "propre", "propres", "sur", "un", "une", "voir", "demander", "demande",
}


def chercher_secrets(fichier, obj, rapport):
    for chemin, t in textes(obj):
        for motif, quoi in MOTIFS_SECRETS:
            if motif.search(t):
                rapport.erreur(fichier, chemin, f"ce texte semble contenir {quoi}. Le dépôt est public : retirer la valeur.")
        for m in CHAMP_SECRET.finditer(t):
            valeur = m.group(2).lower().strip(".")
            if valeur not in MOTS_ANODINS:
                rapport.erreur(fichier, chemin,
                               f"« {m.group(0)[:40]}… » ressemble à un identifiant ou un mot de passe. Le dépôt est "
                               "public : ne jamais l'écrire (dire plutôt « comptes sur demande »).")
        if DEMO.search(t):
            rapport.erreur(fichier, chemin, "ce texte semble donner des identifiants de démonstration : ils ne sont jamais publiés.")
        if MDP_EST.search(t) and MDP_EST.search(t).group(2).lower() not in MOTS_ANODINS:
            rapport.erreur(fichier, chemin, "ce texte semble donner un mot de passe : ne jamais l'écrire.")
        for m in URL_SECRET.finditer(t):
            rapport.erreur(fichier, chemin,
                           f"l'adresse contient « {m.group(1)}=… », qui ressemble à une clé ou un mot de passe : la retirer.")
        for m in JWT.finditer(t):
            role = ""
            try:
                charge = m.group(1) + "=" * (-len(m.group(1)) % 4)
                role = str(json.loads(base64.urlsafe_b64decode(charge)).get("role", ""))
            except (ValueError, UnicodeDecodeError, AttributeError):
                pass
            if role == "service_role":
                rapport.erreur(fichier, chemin, "clé Supabase « service_role » : elle est secrète et ne doit jamais être publiée.")
            else:
                rapport.attention(fichier, chemin, "une clé (jeton JWT) figure dans ce texte : inutile dans les données, la retirer.")
        for m in EMAIL.finditer(t):
            rapport.attention(fichier, chemin, f"adresse électronique « {m.group(0)} » : vérifier qu'elle peut être publiée.")


# ── Le validateur ───────────────────────────────────────────────────────────

class Validation:
    def __init__(self, racine):
        self.racine = os.path.abspath(racine)
        self.donnees = os.path.join(self.racine, "donnees")
        self.rapport = Rapport()
        self.schemas = {}
        self.valeurs = {}       # liste → {id: entrée}
        self.noeuds = {}        # id → {"niveau", "racine", "parent", "intitule", "enseignement", "niveaux"}
        self.fiches = {}        # id → (fichier, fiche)
        self.visibles = {}      # id → {"exterieur": bool, "eleve": bool}
        self.placees = set()
        self.compteurs = {"fiches": 0, "vitrines": 0, "progressions": 0, "caches": 0, "collecte": 0, "a_verifier": 0}

    def nom(self, chemin):
        return relatif(self.racine, chemin)

    # Schémas -------------------------------------------------------------
    def charger_schemas(self):
        for nom in ("ressource", "vitrine", "progression"):
            chemin = os.path.join(self.donnees, "schema", f"{nom}.schema.json")
            if not os.path.exists(chemin):
                self.rapport.erreur(self.nom(chemin), "", "schéma introuvable")
                continue
            s = lire_json(self.racine, chemin, self.rapport)
            if s is None:
                continue
            self.schemas[nom] = s
            try:
                import jsonschema
                jsonschema.Draft202012Validator.check_schema(s)
            except ImportError:
                pass
            except Exception as e:  # schéma mal écrit
                self.rapport.erreur(self.nom(chemin), "", f"le schéma lui-même est invalide : {e}")

    def conforme(self, quoi, obj, fichier):
        if quoi not in self.schemas:
            return False
        errs = ValidateurSchema(self.schemas[quoi]).erreurs(obj)
        for champ, message in errs:
            self.rapport.erreur(fichier, champ, message)
        if not errs:
            try:
                import jsonschema
                v = jsonschema.Draft202012Validator(self.schemas[quoi])
                for e in v.iter_errors(obj):
                    champ = ""
                    for k in e.absolute_path:
                        champ = joindre(champ, k)
                    self.rapport.erreur(fichier, champ, f"non conforme au schéma (contrôle jsonschema) : {e.message}")
                    errs.append(e)
            except ImportError:
                pass
        return not errs

    # Référentiels --------------------------------------------------------
    def charger_referentiels(self):
        chemin = os.path.join(self.donnees, "referentiels", "valeurs.json")
        fichier = self.nom(chemin)
        v = lire_json(self.racine, chemin, self.rapport) if os.path.exists(chemin) else None
        if v is None:
            if not os.path.exists(chemin):
                self.rapport.erreur(fichier, "", "référentiel introuvable")
            return False
        chercher_secrets(fichier, v, self.rapport)
        motif = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
        for liste in LISTES:
            entrees = v.get(liste)
            if not isinstance(entrees, list) or not entrees:
                self.rapport.erreur(fichier, liste, "liste manquante ou vide")
                self.valeurs[liste] = {}
                continue
            self.valeurs[liste] = {}
            for i, e in enumerate(entrees):
                champ = joindre(liste, i)
                if not isinstance(e, dict) or not isinstance(e.get("id"), str) or not motif.match(e["id"]):
                    self.rapport.erreur(fichier, champ, "chaque valeur a un « id » en minuscules, sans accents, avec des tirets")
                    continue
                if not isinstance(e.get("libelle"), str) or not e["libelle"].strip():
                    self.rapport.erreur(fichier, champ, f"la valeur « {e['id']} » n'a pas de « libelle »")
                if e["id"] in self.valeurs[liste]:
                    self.rapport.erreur(fichier, champ, f"l'identifiant « {e['id']} » figure deux fois dans « {liste} »")
                self.valeurs[liste][e["id"]] = e
                if liste == "usages" and e.get("famille") not in ("modalite", "prerequis"):
                    self.rapport.erreur(fichier, champ, "« famille » vaut « modalite » ou « prerequis »")
                if liste == "roles":
                    vpd = e.get("visible_par_defaut")
                    if not (isinstance(vpd, dict) and isinstance(vpd.get("exterieur"), bool) and isinstance(vpd.get("eleve"), bool)):
                        self.rapport.erreur(fichier, champ, f"le rôle « {e['id']} » a besoin de « visible_par_defaut » : "
                                                            "{ \"exterieur\": true ou false, \"eleve\": true ou false }")
        defauts = [f for f in self.valeurs.get("formats", {}).values() if f.get("par_defaut")]
        if len(defauts) != 1:
            self.rapport.erreur(fichier, "formats", "exactement un format doit avoir « par_defaut »: true")

        chemin = os.path.join(self.donnees, "referentiels", "programmes.json")
        fichier = self.nom(chemin)
        p = lire_json(self.racine, chemin, self.rapport) if os.path.exists(chemin) else None
        if p is None:
            if not os.path.exists(chemin):
                self.rapport.erreur(fichier, "", "référentiel introuvable")
            return False
        chercher_secrets(fichier, p, self.rapport)
        motif_noeud = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

        def noeud(n, champ, niveau, parent, racine):
            if not isinstance(n, dict) or not isinstance(n.get("id"), str):
                self.rapport.erreur(fichier, champ, "élément sans « id »")
                return None
            nid = n["id"]
            attendu = (parent + ".") if parent else ""
            dernier = nid[len(attendu):] if nid.startswith(attendu) else None
            if dernier is None or "." in dernier or not motif_noeud.match(dernier):
                self.rapport.erreur(fichier, champ, f"l'identifiant « {nid} » doit s'écrire {attendu}<mot-avec-tirets>")
            if nid in self.noeuds:
                self.rapport.erreur(fichier, champ, f"l'identifiant « {nid} » figure deux fois")
            if not isinstance(n.get("intitule"), str) or not n["intitule"].strip():
                self.rapport.erreur(fichier, champ, f"« {nid} » n'a pas d'« intitule »")
            if n.get("a_verifier"):
                self.compteurs["a_verifier"] += 1
                self.rapport.info(fichier, champ, f"intitulé à vérifier : {n['a_verifier']}")
            r = racine or nid
            self.noeuds[nid] = {
                "niveau": niveau, "parent": parent, "racine": r, "intitule": n.get("intitule", nid),
                "enseignement": n.get("enseignement") if niveau == "programme" else self.noeuds[r]["enseignement"],
                "niveaux": n.get("niveaux", []) if niveau == "programme" else self.noeuds[r]["niveaux"],
                "enfants": [],
            }
            if parent:
                self.noeuds[parent]["enfants"].append(nid)
            return nid

        self.charger_pix()

        progs = p.get("programmes")
        if not isinstance(progs, list) or not progs:
            self.rapport.erreur(fichier, "programmes", "liste manquante ou vide")
            return False
        for i, prog in enumerate(progs):
            champ = joindre("programmes", i)
            pid = noeud(prog, champ, "programme", None, None)
            if not pid:
                continue
            if prog.get("enseignement") not in self.valeurs.get("enseignements", {}):
                self.rapport.erreur(fichier, joindre(champ, "enseignement"),
                                    f"« {prog.get('enseignement')} » n'est pas dans le référentiel « enseignements »")
            for j, niv in enumerate(prog.get("niveaux", [])):
                if niv not in self.valeurs.get("niveaux", {}):
                    self.rapport.erreur(fichier, joindre(joindre(champ, "niveaux"), j), f"niveau inconnu « {niv} »")
            for j, th in enumerate(prog.get("themes", [])):
                cth = joindre(joindre(champ, "themes"), j)
                tid = noeud(th, cth, "theme", pid, pid)
                if not tid:
                    continue
                for k, co in enumerate(th.get("contenus", [])):
                    noeud(co, joindre(joindre(cth, "contenus"), k), "contenu", tid, pid)
        return True

    def charger_pix(self):
        """Le référentiel des compétences Pix (cadre de référence des compétences numériques)."""
        chemin = os.path.join(self.donnees, "referentiels", "competences-pix.json")
        fichier = self.nom(chemin)
        self.valeurs["competences_pix"] = {}
        if not os.path.exists(chemin):
            self.rapport.erreur(fichier, "", "référentiel introuvable")
            return
        c = lire_json(self.racine, chemin, self.rapport)
        if not isinstance(c, dict):
            return
        chercher_secrets(fichier, c, self.rapport)
        domaines = {d.get("numero") for d in c.get("domaines", []) if isinstance(d, dict) and d.get("libelle")}
        if not domaines:
            self.rapport.erreur(fichier, "domaines", "liste manquante ou vide")
        competences = c.get("competences")
        if not isinstance(competences, list) or not competences:
            self.rapport.erreur(fichier, "competences", "liste manquante ou vide")
            return
        for i, e in enumerate(competences):
            champ = joindre("competences", i)
            if not isinstance(e, dict) or not isinstance(e.get("id"), str) or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", e["id"]):
                self.rapport.erreur(fichier, champ, "chaque compétence a un « id » en minuscules, sans accents, avec des tirets")
                continue
            if e["id"] in self.valeurs["competences_pix"]:
                self.rapport.erreur(fichier, champ, f"l'identifiant « {e['id']} » figure deux fois")
            if not isinstance(e.get("libelle"), str) or not e["libelle"].strip():
                self.rapport.erreur(fichier, champ, f"la compétence « {e['id']} » n'a pas de « libelle »")
            if e.get("domaine") not in domaines:
                self.rapport.erreur(fichier, champ, f"la compétence « {e['id']} » cite un domaine inconnu ({e.get('domaine')})")
            if not re.fullmatch(r"[1-9]\.[1-9]", str(e.get("numero", ""))) or not str(e["numero"]).startswith(f"{e.get('domaine')}."):
                self.rapport.erreur(fichier, champ, f"le numéro de « {e['id']} » doit s'écrire <domaine>.<rang> (exemple : 3.4)")
            self.valeurs["competences_pix"][e["id"]] = e

    def verifier_valeur(self, fichier, champ, valeur, liste):
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", valeur):
            return False  # forme déjà signalée par le contrôle du schéma
        if valeur not in self.valeurs.get(liste, {}):
            possibles = ", ".join(self.valeurs.get(liste, {}))
            self.rapport.erreur(fichier, champ,
                                f"« {valeur} » n'est pas dans le référentiel « {liste} » (valeurs possibles : {possibles})")
            return False
        return True

    def verifier_noeud(self, fichier, champ, nid, enseignements=None, niveaux=None):
        n = self.noeuds.get(nid)
        if not n:
            proches = [k for k in self.noeuds if k.split(".")[-1] == nid.split(".")[-1]][:3]
            aide = f" (vouliez-vous dire : {', '.join(proches)} ?)" if proches else ""
            self.rapport.erreur(fichier, champ, f"« {nid} » n'existe pas dans programmes.json{aide}")
            return None
        if enseignements is not None and n["enseignement"] not in enseignements:
            self.rapport.erreur(fichier, champ,
                                f"« {nid} » relève de l'enseignement « {n['enseignement']} », absent de « enseignements »")
        if niveaux is not None and not set(n["niveaux"]) & set(niveaux):
            self.rapport.attention(fichier, champ,
                                   f"« {nid} » relève du niveau {', '.join(n['niveaux'])}, absent de « niveaux » : "
                                   "normal pour une révision (première revue en terminale), sinon ajouter le niveau")
        return n

    # Formats -------------------------------------------------------------
    def deduire_format(self, doc):
        cible = doc.get("url") or doc.get("fichier") or ""
        if doc.get("url"):
            morceaux = urlsplit(cible)
            hote = morceaux.netloc.lower().split(":")[0]
            hote = hote[4:] if hote.startswith("www.") else hote
            chemin = morceaux.path
        else:
            hote, chemin = "", re.split(r"[#?]", cible)[0]
        formats = list(self.valeurs.get("formats", {}).values())
        for f in formats:
            if any(re.search(m, cible) for m in f.get("motifs", [])):
                return f["id"]
        for f in formats:
            if hote and hote in f.get("hotes", []):
                return f["id"]
        dernier = chemin.rstrip("/").rsplit("/", 1)[-1]
        if "." in dernier and not chemin.endswith("/"):
            ext = dernier.rsplit(".", 1)[-1].lower()
            for f in formats:
                if ext in f.get("extensions", []):
                    return f["id"]
        for f in formats:
            if f.get("par_defaut"):
                return f["id"]
        return None

    # Fiches --------------------------------------------------------------
    def charger_fiches(self):
        dossier = os.path.join(self.donnees, "ressources")
        chemins = sorted(glob.glob(os.path.join(dossier, "*.json")))
        for chemin in chemins:
            fichier = self.nom(chemin)
            fiche = lire_json(self.racine, chemin, self.rapport)
            self.compteurs["fiches"] += 1
            if fiche is None:
                continue
            chercher_secrets(fichier, fiche, self.rapport)
            if not isinstance(fiche, dict):
                self.rapport.erreur(fichier, "", "une fiche est un objet { … }")
                continue
            self.conforme("ressource", fiche, fichier)
            rid = fiche.get("id")
            if not isinstance(rid, str):
                continue
            attendu = os.path.splitext(os.path.basename(chemin))[0]
            if rid != attendu:
                self.rapport.erreur(fichier, "id", f"l'identifiant « {rid} » ne correspond pas au nom du fichier : "
                                                   f"renommer le fichier en {rid}.json, ou l'identifiant en « {attendu} »")
            if rid in self.fiches:
                self.rapport.erreur(fichier, "id", f"l'identifiant « {rid} » est déjà utilisé par {self.fiches[rid][0]}")
                continue
            self.fiches[rid] = (fichier, fiche)

    def verifier_fiche(self, rid, fichier, f):
        for champ, liste in (("enseignements", "enseignements"), ("niveaux", "niveaux"), ("types", "types"),
                             ("usages", "usages"), ("langages", "langages"), ("competences_pix", "competences_pix")):
            for i, val in enumerate(f.get(champ, []) if isinstance(f.get(champ), list) else []):
                if isinstance(val, str):
                    self.verifier_valeur(fichier, joindre(champ, i), val, liste)
        if f.get("competences_pix") and "snt" not in (f.get("enseignements") or []):
            self.rapport.attention(fichier, "competences_pix",
                                   "les compétences Pix sont prévues pour les ressources de SNT : ajouter « snt » aux enseignements, ou retirer ce champ")
        for champ, liste in (("origine", "origines"), ("statut", "statuts")):
            if isinstance(f.get(champ), str):
                self.verifier_valeur(fichier, champ, f[champ], liste)

        ens = [e for e in f.get("enseignements", []) if e in self.valeurs.get("enseignements", {})]
        nivs = [n for n in f.get("niveaux", []) if n in self.valeurs.get("niveaux", {})]
        if len(ens) < len(f.get("enseignements", [])):
            ens = None  # valeur déjà signalée : pas de reproche en cascade
        if len(nivs) < len(f.get("niveaux", [])):
            nivs = None
        for i, nid in enumerate(f.get("programme", []) if isinstance(f.get("programme"), list) else []):
            if not isinstance(nid, str):
                continue
            n = self.verifier_noeud(fichier, joindre("programme", i), nid, ens, nivs)
            if n and n["niveau"] == "programme":
                self.rapport.erreur(fichier, joindre("programme", i),
                                    f"« {nid} » est un programme entier : citer un thème ou un contenu")

        for i, l in enumerate(f.get("liees", []) if isinstance(f.get("liees"), list) else []):
            cible = l.get("ressource") if isinstance(l, dict) else None
            if cible == rid:
                self.rapport.erreur(fichier, joindre(joindre("liees", i), "ressource"), "une ressource ne peut pas être liée à elle-même")
            elif isinstance(cible, str) and cible not in self.fiches:
                self.rapport.erreur(fichier, joindre(joindre("liees", i), "ressource"),
                                    f"aucune fiche « {cible} » dans donnees/ressources/")

        self.verifier_credits(fichier, f)

        de = f.get("donnees_eleves")
        if isinstance(de, dict) and de.get("collecte") is True:
            self.compteurs["collecte"] += 1
            if de.get("facultative") is True:
                self.rapport.info(fichier, "donnees_eleves",
                                  "collecte facultative de données d'élèves (la ressource s'utilise aussi sans) : signalée à l'enseignant")
            else:
                self.rapport.info(fichier, "donnees_eleves", "la ressource collecte des données d'élèves : signalée à l'enseignant")
        elif isinstance(de, dict) and de.get("facultative") is True:
            self.rapport.erreur(fichier, "donnees_eleves.facultative",
                                "« facultative » n'a de sens que si « collecte » vaut true")

        docs = f.get("documents")
        if not isinstance(docs, list):
            self.visibles[rid] = {"exterieur": False, "eleve": False}
            return
        docs = [d for d in docs if isinstance(d, dict)]
        roles = self.valeurs.get("roles", {})

        def nom_doc(i, d):
            titre = d.get("titre") or roles.get(d.get("role"), {}).get("libelle") or d.get("role") or "?"
            return f"documents[{i}] « {titre} »"

        def ou(i, d, sous=""):
            titre = d.get("titre") or roles.get(d.get("role"), {}).get("libelle") or d.get("role") or "?"
            return f"documents[{i}]{'.' + sous if sous else ''} (« {titre} »)"

        principaux = [i for i, d in enumerate(docs) if d.get("principal") is True]
        if len(principaux) == 0:
            self.rapport.erreur(fichier, "documents", "aucun document principal : mettre « principal »: true sur le document qu'ouvre le titre")
        elif len(principaux) > 1:
            self.rapport.erreur(fichier, "documents",
                                f"{len(principaux)} documents principaux ({', '.join(str(i) for i in principaux)}) : il en faut exactement un")

        for i, d in enumerate(docs):
            role = d.get("role")
            if isinstance(role, str):
                self.verifier_valeur(fichier, ou(i, d, "role"), role, "roles")
            if isinstance(d.get("format"), str):
                self.verifier_valeur(fichier, ou(i, d, "format"), d["format"], "formats")
            r = roles.get(role, {})
            url = d.get("url")
            if isinstance(url, str):
                morceaux = urlsplit(url)
                hote = morceaux.netloc.lower().split(":")[0]
                if morceaux.scheme == "http":
                    self.rapport.attention(fichier, ou(i, d, "url"), "adresse en http:// : préférer https:// si le site le permet")
                if hote in HOTES_GITHUB or hote == "www.github.com":
                    if not r.get("github_autorise"):
                        if d.get("principal"):
                            self.rapport.erreur(fichier, ou(i, d, "url"),
                                                "le lien principal pointe vers une page GitHub : il doit mener directement à la "
                                                "ressource (page, fiche, PDF). Le dépôt peut figurer à part, avec le rôle « code-source ».")
                        else:
                            self.rapport.erreur(fichier, ou(i, d, "url"),
                                                "lien vers une page GitHub : seul le rôle « code-source » le permet "
                                                "(pour un fichier, utiliser son lien direct ou le déposer sur le site)")
            fich = d.get("fichier")
            if isinstance(fich, str):
                chemin = re.split(r"[#?]", fich)[0]
                complet = os.path.join(self.racine, *chemin.split("/"))
                if chemin.endswith("/") or os.path.isdir(complet):
                    if not os.path.isfile(os.path.join(complet, "index.html")):
                        self.rapport.erreur(fichier, ou(i, d, "fichier"), f"le dossier « {chemin} » n'a pas de index.html dans le dépôt")
                elif not os.path.isfile(complet):
                    self.rapport.erreur(fichier, ou(i, d, "fichier"), f"fichier introuvable dans le dépôt : « {chemin} »")
            vis = d.get("visible") if isinstance(d.get("visible"), dict) else {}
            if r.get("sensible") and vis.get("eleve") is True:
                self.rapport.attention(fichier, ou(i, d, "visible.eleve"),
                                       f"un document « {r.get('libelle', role)} » est visible des élèves : est-ce voulu ?")
            if vis.get("exterieur") is False or vis.get("eleve") is False:
                self.compteurs["caches"] += 1
                badge = ("tous" if vis.get("exterieur") is False and vis.get("eleve") is False
                         else "extérieur" if vis.get("exterieur") is False else "élèves")
                self.rapport.info(fichier, ou(i, d), f"caché : {badge}")
            if d.get("principal") is True and r and not r.get("principal_conseille", True):
                self.rapport.attention(fichier, ou(i, d, "role"),
                                       f"un document « {r.get('libelle', role)} » comme document principal : est-ce voulu ?")

        # Règle 19 de la philosophie éducative : un TD de l'enseignant existe en PDF et en page HTML.
        # Simple avertissement, pour que les TD actuels ne bloquent pas la conversion.
        if "td" in (f.get("types") or []) and f.get("origine") == "ma-creation":
            formats = {d.get("format") or self.deduire_format(d) for d in docs}
            manque = [quoi for quoi, fmt in (("version PDF", "pdf"), ("page HTML en ligne", "page-web"))
                      if fmt not in formats]
            if manque:
                self.rapport.attention(fichier, "documents",
                                       f"TD sans {' ni '.join(manque)} : un TD existe toujours en PDF imprimable et en page "
                                       "HTML en ligne, responsive et auto-corrective (philosophie éducative, § 14, règle 19)")

        # Visibilité (§ 3.2) : ce que voit chaque public
        vu = {}
        for public, qui in PUBLICS.items():
            visibles = [(i, d) for i, d in enumerate(docs) if isinstance(d.get("visible"), dict) and d["visible"].get(public) is True]
            vu[public] = bool(visibles)
            if not visibles:
                self.rapport.info(fichier, "documents", f"tous les documents sont cachés pour {qui} : la ressource n'y apparaît pas")
                continue
            if principaux and docs[principaux[0]].get("visible", {}).get(public) is True:
                continue
            i, rempl = visibles[0]
            self.rapport.info(fichier, "documents",
                              f"le document principal est caché pour {qui} : {nom_doc(i, rempl)} s'ouvrira à sa place")
            hote = urlsplit(rempl.get("url", "")).netloc.lower()
            if hote in HOTES_GITHUB or hote == "www.github.com":
                self.rapport.attention(fichier, "documents",
                                       f"pour {qui}, un clic sur le titre ouvrirait une page GitHub : rendre visible un autre document")
        self.visibles[rid] = vu

    def verifier_credits(self, fichier, f):
        """Licences et auteurs (décision du 07/11/2026). Simples avertissements."""
        origine = f.get("origine")
        auteurs = [a for a in f.get("auteurs", []) if isinstance(a, dict)] if isinstance(f.get("auteurs"), list) else []
        licence = f.get("licence") if isinstance(f.get("licence"), str) else ""
        if origine == "ma-creation":
            if not any(a.get("nom") == AUTEUR for a in auteurs):
                self.rapport.attention(fichier, "auteurs",
                                       f"création de l'enseignant : ajouter l'auteur {{ \"nom\": \"{AUTEUR}\", \"role\": \"auteur\" }}")
            if not licence:
                self.rapport.attention(fichier, "licence",
                                       "création de l'enseignant sans licence : « CC BY-SA 4.0 » pour les documents, "
                                       "« MIT » pour le code des applications")
            elif not LICENCES_ENSEIGNANT.search(licence):
                self.rapport.attention(fichier, "licence",
                                       f"« {licence} » : les créations de l'enseignant sont sous « CC BY-SA 4.0 » (documents) "
                                       "ou « MIT » (code des applications)")
        elif origine in ORIGINES_A_CREDITER and not f.get("credits") and not auteurs:
            self.rapport.attention(fichier, "credits",
                                   "ressource externe : la créditer à son site d'origine (champ « credits », ou un auteur "
                                   "avec le rôle « site d'origine » et son lien)")

    # Vitrine -------------------------------------------------------------
    def verifier_vitrine(self, chemin):
        fichier = self.nom(chemin)
        v = lire_json(self.racine, chemin, self.rapport)
        self.compteurs["vitrines"] += 1
        if v is None:
            return
        chercher_secrets(fichier, v, self.rapport)
        if not self.conforme("vitrine", v, fichier):
            return
        rubriques_vues = set()

        def placer(liste, champ, noeud_place):
            for k, rid in enumerate(liste):
                c = joindre(champ, k)
                if rid not in self.fiches:
                    self.rapport.erreur(fichier, c, f"aucune fiche « {rid} » dans donnees/ressources/")
                    continue
                self.placees.add(rid)
                f = self.fiches[rid][1]
                if not self.visibles.get(rid, {}).get("exterieur", True):
                    self.rapport.attention(fichier, c, f"« {rid} » a tous ses documents cachés pour l'extérieur : elle n'apparaîtra pas")
                if f.get("statut") == "obsolete":
                    self.rapport.attention(fichier, c, f"« {rid} » est marquée obsolète")
                if noeud_place:
                    cites = [n for n in f.get("programme", []) if isinstance(n, str)]
                    if not any(n == noeud_place or n.startswith(noeud_place + ".") for n in cites):
                        self.rapport.attention(fichier, c, f"« {rid} » est placée sous « {noeud_place} », que sa fiche ne cite pas "
                                                           "dans « programme »")

        for i, rub in enumerate(v["rubriques"]):
            cr = joindre("rubriques", i)
            if rub["id"] in rubriques_vues:
                self.rapport.erreur(fichier, joindre(cr, "id"), f"la rubrique « {rub['id']} » figure deux fois")
            rubriques_vues.add(rub["id"])
            prog = rub.get("programme")
            if prog:
                n = self.verifier_noeud(fichier, joindre(cr, "programme"), prog)
                if n and n["niveau"] != "programme":
                    self.rapport.erreur(fichier, joindre(cr, "programme"), f"« {prog} » n'est pas un programme entier (exemple : snt-2019)")
                    prog = None
                elif not n:
                    prog = None
            ref = rub.get("reference_officielle")
            if ref:
                n = self.verifier_noeud(fichier, joindre(cr, "reference_officielle"), ref)
                if n and n["niveau"] != "programme":
                    self.rapport.erreur(fichier, joindre(cr, "reference_officielle"),
                                        f"« {ref} » n'est pas un texte entier (exemple : pp-2018)")
            ids_libres, themes_vus = set(), set()
            for j, s in enumerate(rub["sections"]):
                cs = joindre(joindre(cr, "sections"), j)
                theme = s.get("programme")
                if theme:
                    n = self.verifier_noeud(fichier, joindre(cs, "programme"), theme)
                    if n and n["niveau"] != "theme":
                        self.rapport.erreur(fichier, joindre(cs, "programme"), f"« {theme} » n'est pas un thème : une section suit un thème du programme")
                    elif n and prog and n["racine"] != prog:
                        self.rapport.erreur(fichier, joindre(cs, "programme"), f"« {theme} » n'appartient pas au programme de la rubrique ({prog})")
                    elif n and not prog:
                        self.rapport.erreur(fichier, joindre(cs, "programme"), "la rubrique n'a pas de « programme » : ses sections ne peuvent pas suivre un thème")
                    if theme in themes_vus:
                        self.rapport.erreur(fichier, joindre(cs, "programme"), f"le thème « {theme} » figure deux fois dans la rubrique")
                    themes_vus.add(theme)
                else:
                    if s["id"] in ids_libres:
                        self.rapport.erreur(fichier, joindre(cs, "id"), f"l'identifiant « {s['id']} » figure deux fois dans la rubrique")
                    ids_libres.add(s["id"])
                placer(s["ressources"], joindre(cs, "ressources"), theme if theme in self.noeuds else None)
                for k, ss in enumerate(s.get("sous_sections", [])):
                    css = joindre(joindre(cs, "sous_sections"), k)
                    contenu = ss.get("programme")
                    if contenu:
                        n = self.verifier_noeud(fichier, joindre(css, "programme"), contenu)
                        if n and not theme:
                            self.rapport.erreur(fichier, joindre(css, "programme"),
                                                "un contenu du programme se place sous la section de son thème, pas sous une section libre")
                        elif n and n["parent"] != theme:
                            self.rapport.erreur(fichier, joindre(css, "programme"), f"« {contenu} » n'est pas un contenu du thème « {theme} »")
                    else:
                        if ss["id"] in ids_libres:
                            self.rapport.erreur(fichier, joindre(css, "id"), f"l'identifiant « {ss['id']} » figure deux fois dans la rubrique")
                        ids_libres.add(ss["id"])
                    placer(ss["ressources"], joindre(css, "ressources"),
                           contenu if contenu in self.noeuds else (theme if theme in self.noeuds else None))
            if prog:
                manquants = [t for t in self.noeuds[prog]["enfants"] if t not in themes_vus]
                for t in manquants:
                    self.rapport.attention(fichier, joindre(cr, "sections"),
                                           f"le thème « {t} » ({self.noeuds[t]['intitule']}) n'a pas de section dans la rubrique")

        for i, une in enumerate(v["a_la_une"]):
            c = joindre("a_la_une", i)
            rid = une["ressource"]
            if rid not in self.fiches:
                self.rapport.erreur(fichier, joindre(c, "ressource"), f"aucune fiche « {rid} » dans donnees/ressources/")
                continue
            self.placees.add(rid)
            if not self.visibles.get(rid, {}).get("exterieur", True):
                self.rapport.attention(fichier, c, f"« {rid} » a tous ses documents cachés pour l'extérieur : elle n'apparaîtra pas")
            d1, d2 = date_ok(une.get("debut")), date_ok(une.get("fin"))
            if d1 and d2 and d1 > d2:
                self.rapport.erreur(fichier, c, "la date de début est après la date de fin")

    # Progressions --------------------------------------------------------
    def verifier_progression(self, chemin):
        fichier = self.nom(chemin)
        p = lire_json(self.racine, chemin, self.rapport)
        self.compteurs["progressions"] += 1
        if p is None:
            return
        chercher_secrets(fichier, p, self.rapport)
        if not self.conforme("progression", p, fichier):
            return
        attendu = os.path.splitext(os.path.basename(chemin))[0]
        if p["id"] != attendu:
            self.rapport.erreur(fichier, "id", f"l'identifiant « {p['id']} » ne correspond pas au nom du fichier ({attendu}.json)")
        self.verifier_valeur(fichier, "enseignement", p["enseignement"], "enseignements")
        self.verifier_valeur(fichier, "niveau", p["niveau"], "niveaux")
        ids = set()
        for i, ch in enumerate(p["chapitres"]):
            c = joindre("chapitres", i)
            if ch["id"] in ids:
                self.rapport.erreur(fichier, joindre(c, "id"), f"le chapitre « {ch['id']} » figure deux fois")
            ids.add(ch["id"])
            for j, nid in enumerate(ch.get("programme", [])):
                self.verifier_noeud(fichier, joindre(joindre(c, "programme"), j), nid, [p["enseignement"]], [p["niveau"]])
            per = ch.get("periode", {})
            d1, d2 = date_ok(per.get("debut")), date_ok(per.get("fin"))
            if d1 and d2 and d1 > d2:
                self.rapport.erreur(fichier, joindre(c, "periode"), "la date de début est après la date de fin")
            for j, rid in enumerate(ch["ressources"]):
                cj = joindre(joindre(c, "ressources"), j)
                if rid not in self.fiches:
                    self.rapport.erreur(fichier, cj, f"aucune fiche « {rid} » dans donnees/ressources/")
                elif not self.visibles.get(rid, {}).get("eleve", False):
                    self.rapport.erreur(fichier, cj, f"« {rid} » n'a aucun document visible des élèves")

    # Ensemble ------------------------------------------------------------
    def lancer(self):
        if not os.path.isdir(self.donnees):
            self.rapport.erreur(self.nom(self.donnees), "", "dossier introuvable")
            return
        self.charger_schemas()
        if not self.charger_referentiels():
            return
        self.charger_fiches()
        for rid, (fichier, fiche) in self.fiches.items():
            self.verifier_fiche(rid, fichier, fiche)
        for nom in ("vitrine.json", "vitrine.exemple.json"):
            chemin = os.path.join(self.donnees, nom)
            if os.path.exists(chemin):
                self.verifier_vitrine(chemin)
        for chemin in sorted(glob.glob(os.path.join(self.donnees, "progressions", "*.json"))):
            self.verifier_progression(chemin)
        if self.compteurs["vitrines"]:
            for rid in sorted(set(self.fiches) - self.placees):
                self.rapport.info(self.fiches[rid][0], "", "la ressource n'est placée nulle part dans la vitrine (elle reste dans la bibliothèque)")
        if self.compteurs["caches"]:
            self.rapport.info("donnees/ressources", "", f"{pluriel(self.compteurs['caches'], 'document caché', 'documents cachés')} "
                                                       "pour au moins un public. Rappel : le dépôt est public, un document caché "
                                                       "reste lisible par qui consulte le dépôt ou connaît son adresse.")


def main():
    parser = argparse.ArgumentParser(description="Vérifie les données de la bibliothèque (dossier donnees/).")
    parser.add_argument("--racine", default=RACINE_DEFAUT, help="racine du dépôt à vérifier (par défaut : ce dépôt)")
    parser.add_argument("--strict", action="store_true", help="les avertissements comptent comme des erreurs")
    args = parser.parse_args()

    v = Validation(args.racine)
    v.lancer()
    v.rapport.afficher()
    c = v.compteurs
    ne, na, ni = (v.rapport.nombre(n) for n in ("erreur", "attention", "info"))
    print()
    print(f"Bilan : {pluriel(c['fiches'], 'fiche')}, {pluriel(c['vitrines'], 'vitrine')}, {pluriel(c['progressions'], 'progression')} ; "
          f"{pluriel(ne, 'erreur')}, {pluriel(na, 'avertissement')}, {pluriel(ni, 'information')}.")
    echec = ne > 0 or (args.strict and na > 0)
    if echec:
        print("Les données ne sont pas valides : corriger les lignes ERREUR" + (" et ATTENTION." if args.strict else "."))
    else:
        print("Les données sont valides." + (" Lire les lignes ATTENTION." if na else ""))
    sys.exit(1 if echec else 0)


if __name__ == "__main__":
    main()
