#!/usr/bin/env python3
"""Une imitation STRICTE de l'API de Supabase (PostgREST), sur une base Postgres LOCALE (Gardien, T132d).

Ce que l'imitation de l'Architecte (scripts/calendrier_serveur_essai.py) ne fait pas, et que l'API réelle fait :
- une clé inconnue dans le corps (ou un paramètre obligatoire absent) : 404 PGRST202, comme PostgREST ;
- les arguments convertis par json_to_recordset avec les types de la fonction, comme PostgREST ;
- une fonction STABLE ou IMMUTABLE tourne dans une transaction en lecture seule, comme PostgREST ;
- le rôle anon a statement_timeout = 3 s (réglage relevé sur la base réelle) ;
- l'en-tête apikey doit être la clé publique ; un en-tête Authorization est noté comme une faute ;
- chaque appel est inscrit dans un journal (fonction, clés du corps, en-têtes présents) pour les contrôles.
Il sert aussi les fichiers du site (le dossier RACINE). Rien ne part vers la base réelle.
"""
import http.server
import json
import os
import re
import subprocess
import threading
import time

RACINE = None
PSQL = []
CLE = None  # la clé publique de reglages.js (compte_commun.cle_publique), lue au démarrage
SIGN = {}
JOURNAL = []
FAUTES = []
RETARD = {"secondes": 0.0}
VERROU = threading.Lock()


def psql(sql, entree=None):
    r = subprocess.run(PSQL + ["-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1"], input=sql, capture_output=True, text=True, timeout=40)
    return r.returncode, r.stdout, r.stderr


def lit(v):
    return "'" + str(v).replace("'", "''") + "'"


def signature(fn):
    if fn in SIGN:
        return SIGN[fn]
    code, out, err = psql(
        "select coalesce(array_to_string(p.proargnames, ','), '') || '|' || coalesce(pg_get_function_identity_arguments(p.oid), '')"
        " || '|' || p.pronargdefaults || '|' || p.provolatile::text from pg_proc p where p.pronamespace = 'public'::regnamespace and p.proname = " + lit(fn) + ";")
    lignes = [x for x in out.splitlines() if x.strip()]
    if code or len(lignes) != 1:
        SIGN[fn] = None
        return None
    parts = lignes[0].split("|")
    args, ndef, vol = parts[1], int(parts[2]), parts[3]
    params = []
    for morceau in [a.strip() for a in args.split(",") if a.strip()]:
        nom, typ = morceau.split(" ", 1)
        params.append((nom, typ))
    obligatoires = [p[0] for p in params[:len(params) - ndef]]
    SIGN[fn] = {"params": params, "obligatoires": obligatoires, "volatilite": vol}
    return SIGN[fn]


class Gestion(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=RACINE, **k)

    def log_message(self, *a):
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "apikey, authorization, content-type, x-client-info")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.end_headers()

    def do_POST(self):
        m = re.fullmatch(r"/rest/v1/rpc/([a-z_]+)", self.path)
        if not m:
            return self.repondre(404, {"message": "chemin inconnu"})
        fn = m.group(1)
        brut = self.rfile.read(int(self.headers.get("Content-Length", 0)) or 0)
        entree = {"fn": fn, "apikey": self.headers.get("apikey"), "authorization": self.headers.get("Authorization"),
                  "chemin": self.path, "t": time.time()}
        try:
            corps = json.loads(brut or b"{}")
        except ValueError:
            return self.repondre(400, {"message": "corps illisible"})
        entree["cles"] = sorted(corps.keys()) if isinstance(corps, dict) else None
        with VERROU:
            JOURNAL.append(entree)
        if entree["apikey"] != CLE:
            FAUTES.append(f"{fn} : apikey absente ou différente de la clé publique")
            return self.repondre(401, {"message": "Invalid API key"})
        if entree["authorization"]:
            FAUTES.append(f"{fn} : en-tête Authorization envoyé ({entree['authorization'][:12]}…)")
        if not fn.startswith(("commun_", "cv_")):
            return self.repondre(404, {"code": "PGRST202", "message": "fonction hors du périmètre de l'essai"})
        s = signature(fn)
        if not isinstance(corps, dict) or s is None:
            return self.repondre(404, {"code": "PGRST202", "message": f"Could not find the function public.{fn}"})
        noms = [p[0] for p in s["params"]]
        inconnues = [k for k in corps if k not in noms]
        manquantes = [k for k in s["obligatoires"] if k not in corps]
        if inconnues or manquantes:
            FAUTES.append(f"{fn} : clés inconnues {inconnues} ou paramètres obligatoires absents {manquantes} (PGRST202 en ligne)")
            return self.repondre(404, {"code": "PGRST202", "message": f"Could not find the function public.{fn}({', '.join(sorted(corps))}) in the schema cache"})
        if RETARD["secondes"]:
            time.sleep(RETARD["secondes"])
        types = dict(s["params"])
        decl = ", ".join(f'"{k}" {types[k]}' for k in corps) or None
        args = ", ".join(f'"{k}" := (select "{k}" from a)' for k in corps)
        entetes = {"x-forwarded-for": self.headers.get("X-Forwarded-For", "127.0.0.1"), "apikey": entree["apikey"],
                   "content-type": "application/json", "host": "cukahpyqkljiddmimpyi.supabase.co"}
        lecture = "read only" if s["volatilite"] in ("s", "i") else "read write"
        corps_json = json.dumps([corps], ensure_ascii=False)
        avec = f"with a as (select * from json_to_recordset({lit(corps_json)}::json) as _({decl}) limit 1) " if decl else ""
        sql = (f"begin isolation level read committed {lecture};\n"
               f"select set_config('request.headers', {lit(json.dumps(entetes))}, true);\n"
               f"select set_config('request.method', 'POST', true);\n"
               f"set local role anon;\n"
               f"set local statement_timeout = '3s';\n"
               f"{avec}select public.{fn}({args})::text;\n"
               f"commit;\n")
        code, out, err = psql(sql)
        if code:
            msg = err.strip().splitlines()[-1] if err.strip() else "erreur"
            FAUTES.append(f"{fn} : erreur de la base : {msg[:200]}")
            return self.repondre(400, {"code": "P0001", "message": msg[:300]})
        lignes = [x for x in out.splitlines() if x.strip()]
        try:
            rep = json.loads(lignes[-1])
        except (ValueError, IndexError):
            return self.repondre(500, {"message": "réponse illisible"})
        self.repondre(200, rep)

    def repondre(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b)


def demarrer(racine, psql_cmd):
    global RACINE, PSQL, CLE
    RACINE, PSQL = racine, psql_cmd
    with open(os.path.join(racine, "reglages.js"), encoding="utf-8") as f:
        m = re.search(r"cle_publique:\s*\"([^\"]+)\"", f.read())
    CLE = m.group(1) if m else "cle-absente"
    if not CLE.startswith("sb_publishable_"):
        raise SystemExit("reglages.js : la clé du compte commun n'est pas une clé « publishable ».")
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Gestion)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, f"http://127.0.0.1:{s.server_address[1]}"
