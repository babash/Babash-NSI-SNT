#!/usr/bin/env python3
"""Serveur d'essai du Calendrier des vacances et du compte commun, pour un poste de développement.

Il sert les fichiers du site et imite l'appel des fonctions de Supabase
(POST /rest/v1/rpc/<fonction>) sur une base Postgres LOCALE, où l'on a lancé le
socle (supabase/schema.sql) et calendrier/supabase/schema.sql. Chaque appel est
fait sous le rôle anon, comme par l'API. Jamais la base en ligne : la règle des
bases interdit d'essayer des codes sur la base réelle.

Il sert aussi les fonctions du compte commun (commun_…, SQL 0007 et 0008) : les essais
de T132d (scripts/tests/test_compte_commun_en_ligne.py) le lancent eux-mêmes. L'en-tête
X-Forwarded-For de la requête est passé à la base (request.headers), comme le fait l'API :
le compteur d'essais par réseau se vérifie donc aussi en local.

Usage :
  python3 scripts/calendrier_serveur_essai.py --port 18106 --psql "psql -h /chemin/socket -p 55432 -U postgres"
puis ouvrir http://127.0.0.1:18106/calendrier/?api=http://127.0.0.1:18106
(et prof.html?api=… pour l'espace enseignant·e). Python 3 standard.
"""
import argparse
import http.server
import json
import os
import re
import shlex
import subprocess

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PSQL = []
TYPES = {}


def psql(sql):
    r = subprocess.run(PSQL + ["-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1", "-c", sql], capture_output=True, text=True, timeout=20)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[-400:])
    return r.stdout.strip()


def signature(fn):
    if fn not in TYPES:
        sortie = psql("select coalesce(array_to_string(p.proargnames, ','), '') || '|' || coalesce(pg_get_function_identity_arguments(p.oid), '') "
                      "from pg_proc p where p.pronamespace = 'public'::regnamespace and p.proname = " + litteral(fn))
        if not sortie:
            return None
        noms, args = sortie.split("|", 1)
        types = {}
        for morceau in [a.strip() for a in args.split(",") if a.strip()]:
            nom, typ = morceau.split(" ", 1)
            types[nom] = typ.replace(" DEFAULT NULL", "")
        TYPES[fn] = types
    return TYPES[fn]


def litteral(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, list):
        return "array[" + ",".join(litteral(x) for x in v) + "]"
    if isinstance(v, dict):
        return litteral(json.dumps(v, ensure_ascii=False))
    return "'" + str(v).replace("'", "''") + "'"


class Gestion(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=RACINE, **k)

    def log_message(self, *a):
        pass

    def do_POST(self):
        m = re.fullmatch(r"/rest/v1/rpc/((?:cv|commun)_[a-z_]+)", self.path)
        if not m:
            return self.send_error(404)
        fn = m.group(1)
        corps = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        types = signature(fn)
        if types is None:
            return self.repondre(404, {"message": "fonction inconnue"})
        try:
            args = ", ".join(f"{n} => {litteral(v)}::{types[n]}" for n, v in corps.items() if n in types)
            entetes = json.dumps({"x-forwarded-for": self.headers.get("X-Forwarded-For", "127.0.0.1")})
            sortie = psql(f"select set_config('request.headers', {litteral(entetes)}, false); set role anon; select public.{fn}({args})::text")
            self.repondre(200, json.loads(sortie.splitlines()[-1]))
        except (RuntimeError, ValueError, KeyError) as e:
            self.repondre(400, {"message": str(e)})

    def repondre(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=18106)
    ap.add_argument("--psql", required=True, help='la commande psql de la base LOCALE, entre guillemets')
    a = ap.parse_args()
    PSQL = shlex.split(a.psql)
    print(f"http://127.0.0.1:{a.port}/calendrier/?api=http://127.0.0.1:{a.port}")
    http.server.ThreadingHTTPServer(("127.0.0.1", a.port), Gestion).serve_forever()
