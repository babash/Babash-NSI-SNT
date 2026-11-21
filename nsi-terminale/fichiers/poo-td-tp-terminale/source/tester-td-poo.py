"""Vérifie par exécution (Python 3.13) les réponses des TD 1 et 2 de POO (pages HTML, T125).

- chaque question « code » : la correction, puis les tests cachés (script.td-tests) ;
- les réponses calculées des questions « courte » et « qcu » (valeurs, types, années).

Depuis la racine du dépôt :  python3 -I nsi-terminale/fichiers/poo-td-tp-terminale/source/tester-td-poo.py
(charte/verifier-td.py vérifie en plus les sorties, les cases à compléter et les corrections.)
"""
import html, os, re, sys

assert sys.version_info[:2] == (3, 13), "les réponses doivent venir de Python 3.13"
ICI = os.path.dirname(os.path.abspath(__file__))
PAGES = [os.path.join(ICI, '..', '..', f) for f in (
    'td1-poo-premiers-pas.html', 'td1-poo-premiers-pas-2.html',
    'td2-poo-vers-le-bac.html', 'td2-poo-vers-le-bac-2.html')]
erreurs = 0


def texte(t):
    return html.unescape(re.sub(r'<[^>]+>', '', t)).strip('\n')


def tester_codes(page):
    global erreurs
    src = open(page, encoding='utf-8').read()
    for m in re.finditer(r'<section class="td-q" data-type="code" id="([^"]+)".*?</section>', src, flags=re.S):
        q = m.group(0)
        pre = re.search(r'class="td-preambule">(.*?)</script>', q, flags=re.S)
        tests = re.search(r'class="td-tests">(.*?)</script>', q, flags=re.S)
        corr = re.search(r'data-verifier="correction">(.*?)</pre>', q, flags=re.S)
        g = {'__name__': '__main__'}
        code = (texte(pre.group(1)) + '\n' if pre else '') + texte(corr.group(1)) + '\n' + (texte(tests.group(1)) if tests else '')
        try:
            exec(compile(code, m.group(1), 'exec'), g)
            print(f'  {os.path.basename(page)} {m.group(1)} : correction et tests justes')
        except Exception as e:
            erreurs += 1
            print(f'  {os.path.basename(page)} {m.group(1)} : ÉCHEC {e!r}')


def egal(nom, obtenu, attendu):
    global erreurs
    ok = obtenu == attendu
    erreurs += not ok
    print(f'  {nom} : {obtenu!r}' + ('' if ok else f'  (attendu dans la page : {attendu!r})'))


print('Questions « code » :')
for p in PAGES:
    tester_codes(p)

print('Réponses calculées :')
# TD 1, exercice 1 : Machine
class Machine:
    def __init__(self, nom, annee):
        self.nom = nom
        self.annee = annee
        self.en_marche = False
    def allumer(self):
        self.en_marche = True
    def get_etat(self):
        return self.en_marche
machine_babbage = Machine("Analytique", 1843)
egal('TD1 q3 type', type(machine_babbage).__name__, 'Machine')
egal('TD1 q4 attributs', sorted(vars(machine_babbage)), ['annee', 'en_marche', 'nom'])
egal('TD1 q5 méthodes', sorted(k for k, v in vars(Machine).items() if callable(v)), ['__init__', 'allumer', 'get_etat'])
egal('TD1 q7 type de en_marche', type(machine_babbage.en_marche).__name__, 'bool')
egal('TD1 q8 allumer renvoie', machine_babbage.allumer(), None)
egal('TD1 q9 annee', machine_babbage.annee, 1843)
# TD 1, exercice 2 : Pascaline
class MachineACalculer:
    def __init__(self, createur):
        self.createur = createur
        self.compteur = 0
    def ajouter(self, nombre):
        self.compteur += nombre
    def lire_resultat(self):
        return self.compteur
pascaline = MachineACalculer("Pascal")
pascaline.ajouter(10)
pascaline.ajouter(5)
resultat_final = pascaline.lire_resultat()
compteur_actuel = pascaline.compteur
egal('TD1 q12 types', (type(resultat_final).__name__, type(compteur_actuel).__name__), ('int', 'int'))
# TD 1, feuille 2, exercice 3 : Code
class Code:
    def __init__(self, lignes):
        self.lignes = lignes
        self.est_nettoye = False
    def preparer_compilation(self):
        self.lignes = self.lignes.upper()
        self.est_nettoye = True
    def afficher_etat(self):
        return (self.lignes, self.est_nettoye)
mon_code = Code("while true")
egal('TD1-2 q1 classe de upper', type(mon_code.lignes).__name__, 'str')
mon_code.preparer_compilation()
egal('TD1-2 q2 lignes', mon_code.lignes, 'WHILE TRUE')
egal('TD1-2 q3 type', type(mon_code.afficher_etat()).__name__, 'tuple')
# exercice 4 : Turing
ma_liste = [10, 20, 30]; mon_dict = {'a': 1, 'b': 2}; mon_texte = "TURING"; mon_chiffre = 3.14
A = ma_liste.append(40); B = mon_dict.keys(); C = mon_texte.lower(); D = mon_chiffre.is_integer(); E = mon_dict['a']
egal('TD1-2 q5 objet modifié', (ma_liste, mon_dict, mon_texte, mon_chiffre), ([10, 20, 30, 40], {'a': 1, 'b': 2}, 'TURING', 3.14))
egal('TD1-2 q6 types', [type(x).__name__ for x in (A, B, C, D, E)], ['NoneType', 'dict_keys', 'str', 'bool', 'int'])
# TD 2, exercice 1 : ENIAC
class Ordinateur:
    def __init__(self, nom, annee, puissance):
        self.nom = nom
        self.annee = annee
        self.puissance = puissance
    def augmenter_puissance(self, facteur):
        self.puissance *= facteur
mon_vieux_coucou = Ordinateur("ENIAC", 1946, 5000)
for i in range(10):
    mon_vieux_coucou.augmenter_puissance(2.5)
egal('TD2 q1 puissance', mon_vieux_coucou.puissance, 47683715.8203125)
eniac = Ordinateur("ENIAC", 1946, 5000)
nb_annees = 0
while eniac.puissance < 2**28:
    nb_annees += 2
    eniac.augmenter_puissance(2)
egal('TD2 q2 années', nb_annees, 32)
egal('TD2 q4 année du modèle', 1946 + nb_annees, 1978)
egal('TD2 q5 dans dix ans', 2**28 * 2**(10 // 2), 2**33)
# TD 2, feuille 2 : ARPANET
class Hote:
    def __init__(self, adresse_ip):
        self.adresse_ip = adresse_ip
        self.messages_recus = []
    def recevoir_message(self, message):
        self.messages_recus.append(message)
    def lire_boite_reception(self):
        return self.messages_recus
class Reseau:
    def __init__(self):
        self.participants = []
    def connecter(self, hote):
        self.participants.append(hote)
    def envoyer_message(self, emetteur_ip, destinataire_ip, message):
        for hote in self.participants:
            if hote.adresse_ip == destinataire_ip:
                hote.recevoir_message(message)
                return True
        return False
reseau_arpa = Reseau()
h1 = Hote("192.168.1.1"); h2 = Hote("192.168.1.2")
reseau_arpa.connecter(h1); reseau_arpa.connecter(h2)
r1 = reseau_arpa.envoyer_message("192.168.1.1", "192.168.1.2", "LOG=LOGIN")
r2 = reseau_arpa.envoyer_message("192.168.1.1", "192.168.1.3", "ERROR")
egal('TD2-2 q1 type', type(h1.messages_recus).__name__, 'list')
egal('TD2-2 q2 type des participants', {type(h).__name__ for h in reseau_arpa.participants}, {'Hote'})
reseau_arpa.connecter(Hote("192.168.1.3"))
egal('TD2-2 q3 longueur (3 hôtes)', len(reseau_arpa.participants), 3)
egal('TD2-2 q6 resultat', h2.lire_boite_reception(), ['LOG=LOGIN'])
egal('TD2-2 q7 retours', (r1, r2), (True, False))
# TCP/IP
class Serveur:
    def __init__(self):
        self.nb_clients_connectes = 0
    def ajouter_client(self):
        self.nb_clients_connectes += 1
class Client:
    def __init__(self):
        self.connecte_a = None
    def se_connecter_a(self, serveur):
        self.connecte_a = serveur
        serveur.ajouter_client()
s1 = Serveur(); c1 = Client(); c2 = Client()
c1.se_connecter_a(s1); c2.se_connecter_a(s1); c3 = Client(); c3.se_connecter_a(s1)
egal('TD2-2 q10 nb', s1.nb_clients_connectes, 3)
egal('TD2-2 q11 type_c1', type(c1.connecte_a).__name__, 'Serveur')
egal('TD2-2 q12 même objet', c1.connecte_a is c2.connecte_a, True)
egal('TD2-2 q13 c2 est c1.connecte_a', c2 is c1.connecte_a, False)

print('tout est juste' if not erreurs else f'{erreurs} erreur(s)')
sys.exit(1 if erreurs else 0)
