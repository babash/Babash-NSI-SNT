# -*- coding: utf-8 -*-
"""Données brutes des annales de l'écrit de NSI (T104), relevées le 20/11/2026.
Format d'un sujet : (cle, annee, session, centre, jour, date, code, pages, mise_en_page, liens, exercices, remarque)
liens : dict(kxs=slug|None, aeif=(sujet, corrige|None, testes)|None, autres=[...])
exercice : (points, "debut-fin" | None, thème tel que lu dans le PDF)
"""
V = "2026-11-20"

def K(annee, slug):
    return (f"https://kxs.fr/files/sujets/{annee}/ecrit/terminale-{annee}-{slug}.pdf",
            f"https://kxs.fr/files/corriges/{annee}/ecrit/terminale-{annee}-{slug}-corrigé.pdf")

AE = "https://aeif.fr/wp-content/uploads/"

# kxs : slug -> corrigé existant ?  (d'après la page kxs, tous les corrigés ci-dessous ont été ouverts le 20/11/2026)
KXS_CORRIGE = {
 (2025,'metropole-jour-1'),(2025,'metropole-jour-2'),(2025,'amerique-nord-jour-1'),(2025,'amerique-nord-jour-2'),
 (2025,'amerique-nord-jour-2-bis'),(2025,'asie-jour-1'),(2025,'asie-jour-2'),
 (2024,'amerique-nord-jour-1'),(2024,'centres-etrangers-groupe-1-jour-2'),(2024,'asie-jour-1'),
 (2024,'metropole-juin-sujet-1'),(2024,'metropole-juin-sujet-2'),(2024,'metropole-septembre-sujet-1'),(2024,'polynesie-jour-2'),
 (2023,'amerique-du-sud-jour-1'),
 (2022,'rattrapage-jour-1'),(2022,'amerique-sud-jour-2'),(2022,'asie-jour-2'),(2022,'polynesie-jour-1'),(2022,'metropole-sujet-1'),(2022,'metropole-sujet-2'),
 (2021,'amerique-nord-sujet-1'),(2021,'centres-etrangers-sujet-1'),(2021,'centres-etrangers-sujet-2'),
 (2021,'metropole-candidat-libre-sujet-1'),(2021,'metropole-candidat-libre-sujet-2'),(2021,'metropole-sujet-1'),
 (2021,'polynesie-sujet-2'),(2021,'metropole-septembre-sujet-1'),(2021,'metropole-septembre-sujet-2'),
}
# kxs : sujets dont le PDF est une image (aucun texte extractible) : pages et points non relus
KXS_SCAN = {(2022,'rattrapage-jour-1'),(2022,'amerique-sud-jour-1'),(2022,'amerique-nord-jour-1'),(2022,'amerique-nord-jour-2'),(2023,'amerique-du-sud-jour-1'),(2023,'amerique-du-sud-jour-2')}

SUJETS = []
def S(cle, annee, session, centre, jour, date, code, pages, mep, liens, exos, rem=None, bareme="20"):
    SUJETS.append(dict(cle=cle, annee=annee, session=session, centre=centre, jour=jour, date=date, code=code,
                       pages=pages, mise_en_page=mep, liens=liens, exercices=exos, remarque=rem, bareme=bareme))

# ------------------------------------------------------------------ 2026
def a26(nom): return (AE+f"2026/06/{nom}.pdf")
S("2026-amerique-nord-j1",2026,"mai","Amérique du Nord",1,None,"26-NSIJ1AN1",16,"freemaths (reprise de la mise en page officielle)",
  dict(aeif=(a26("Amerique_Nord_mai_2026_sujet_1"),a26("Amerique_Nord_mai_2026_sujet_1_corrige"),"ok"),
       autres=[("freemaths","https://www.freemaths.fr/sujets-du-bac/baccalaureat-general/numerique-et-sciences-informatiques/annees/annee-2026/amerique-du-nord/sujet-1-et-correction/bac-numerique-et-sciences-informatiques-amerique-du-nord-2026-sujet-1.pdf","sujet","ok"),
               ("math93","https://math93.com/images/pdf/annales_bac/Bac_NSI/bac_NSI_2026/NSI_Epreuve_Ecrite-2026/NSI2026-AmNord-J1.pdf","sujet","ok (PDF image : texte non extractible)"),
               ("math93","https://math93.com/images/pdf/annales_bac/Bac_NSI/bac_NSI_2026/NSI_Epreuve_Ecrite-2026/BACNSI2026_AmeriqueNord_Sujet1_corr.pdf","corrigé","ok")],
       pages_aeif=10),
  [(6,"2-6","Cet exercice porte sur la programmation orientée objet et la récursivité (classes Grille et Noeud, algorithme min-max, arbre de coups)."),
   (6,"7-12","Cet exercice porte sur l'architecture matérielle (réseau), les structures de données et la programmation orientée objet (CIDR, RIP, OSPF, files, politique drop tail)."),
   (8,"13-16","Cet exercice porte sur la récursivité, la programmation dynamique et les bases de données (SQL, sous-séquence strictement croissante).")])
S("2026-amerique-nord-j2",2026,"mai","Amérique du Nord",2,None,"26-NSIJ2AN1",17,"freemaths (reprise de la mise en page officielle)",
  dict(aeif=(a26("Amerique_Nord_mai_2026_sujet_2"),a26("Amerique_Nord_mai_2026_sujet_2_corrige"),"ok"),
       autres=[("freemaths","https://www.freemaths.fr/sujets-du-bac/baccalaureat-general/numerique-et-sciences-informatiques/annees/annee-2026/amerique-du-nord/sujet-2-et-correction/bac-numerique-et-sciences-informatiques-amerique-du-nord-2026-sujet-2.pdf","sujet","ok")],
       pages_aeif=10),
  [(6,"2-6","Architecture matérielle, systèmes d'exploitation et structures linéaires en Python (processus et états, interblocage, ordonnancement par tourniquet, files, multiprocesseurs, systèmes sur puce)."),
   (6,"7-12","Programmation Python, POO et structures d'arbres (classe Joueuse, surcharge de l'opérateur <, tri par insertion, arbre binaire, récursivité, tuples)."),
   (8,"13-17","Bases de données relationnelles, SQL et dictionnaires Python (schéma relationnel, SELECT, JOIN, INSERT, UPDATE, DELETE, COUNT, assertions).")])
S("2026-asie-j1",2026,"juin","Asie",1,None,"26-NSIJ1JA1",16,"math93 (reprise du PDF officiel)",
  dict(aeif=(a26("Asie_juin_2026_sujet_1"),a26("Asie_juin_2026_sujet_1_corrige"),"ok"),
       autres=[("math93","https://math93.com/images/pdf/annales_bac/Bac_NSI/bac_NSI_2026/NSI_Epreuve_Ecrite-2026/spe_numerique_informatique_2026_asie_1_sujet_officiel.pdf","sujet","ok")],pages_aeif=11),
  [(6,"2-5","Cet exercice porte sur les bases de données, la programmation de base en Python et l'algorithmique (SQL, dictionnaires et listes, algorithme glouton, tris, coût temporel)."),
   (6,"6-9","Cet exercice porte sur les thèmes langages, programmation et algorithmique (perceptron et apprentissage supervisé, classes et méthodes, listes et tuples, coût temporel)."),
   (8,"10-16","Cet exercice porte sur les protocoles de routage, la programmation orientée objet et la notion de file (RIP et Bellman-Ford, adresses IP et masques, opérateurs binaires, files, POO).")],
  rem="Date : non lue dans le PDF ; la page math93 indique le 11 juin 2026 (à vérifier).")
S("2026-asie-j2",2026,"juin","Asie",2,"2026-06-10","26-NSIJ2JA1",14,"math93 (reprise du PDF officiel)",
  dict(aeif=(a26("Asie_juin_2026_sujet_2"),a26("Asie_juin_2026_sujet_2_corrige_Pascal"),"ok"),
       autres=[("math93","https://math93.com/images/pdf/annales_bac/Bac_NSI/bac_NSI_2026/NSI_Epreuve_Ecrite-2026/spe_numerique_informatique_2026_asie_2_sujet_officiel.pdf","sujet","ok")],pages_aeif=11),
  [(6,"1-4","Cet exercice porte sur la programmation orientée objet et les structures linéaires (classes, attributs, méthodes, listes, piles)."),
   (6,"5-8","Cet exercice porte sur les bases de données et les graphes (SQL SELECT, INSERT, UPDATE, DELETE, clés primaire et étrangère ; graphes orientés, listes d'adjacence, parcours de graphe, tri)."),
   (8,"9-14","Cet exercice porte sur la programmation Python et le routage RIP (fonctions, chaînes de caractères, récursivité, dictionnaires, routage, graphes).")],
  rem="Date lue dans le PDF : 10 juin 2026 ; la page math93 indique le 12 juin (à vérifier).")
S("2026-centres-etrangers-g1-j1",2026,"juin","Centres étrangers (groupe 1)",1,None,"26-NSIJ1G11",17,"math93 (reprise du PDF officiel)",
  dict(aeif=(a26("Centres_etrangers_juin_2026_sujet_1"),a26("Centres_etrangers_juin_2026_sujet_1_corrige"),"ok"),
       autres=[("math93","https://math93.com/images/pdf/annales_bac/Bac_NSI/bac_NSI_2026/NSI_Epreuve_Ecrite-2026/26_NSIJ1G11.pdf","sujet","ok")],pages_aeif=10),
  [(6,"2-6","Cet exercice porte sur les algorithmes de tri et d'un parcours d'arbre binaire de recherche et sur la programmation (tri par sélection, dictionnaires et listes, POO, ABR insertion et parcours, coût d'un algorithme)."),
   (6,"7-9","Cet exercice porte sur la sécurisation des communications et la programmation (chiffrement de Polybe, chiffrement symétrique et asymétrique, fonctions, listes, dictionnaires, tuples, chaînes)."),
   (8,"10-17","Cet exercice porte sur la programmation orientée objet, la récursivité et les bases de données relationnelles (jeu du démineur, tableaux à deux dimensions, SQL SELECT, JOIN, UPDATE, INSERT, DELETE).")])
S("2026-centres-etrangers-g1-j2",2026,"juin","Centres étrangers (groupe 1)",2,None,"26-NSIJ2G11",18,"math93 (reprise du PDF officiel)",
  dict(aeif=(a26("Centres_etrangers_juin_2026_sujet_2"),a26("Centres_etrangers_juin_2026_sujet_2_corrige"),"ok"),
       autres=[("math93","https://math93.com/images/pdf/annales_bac/Bac_NSI/bac_NSI_2026/NSI_Epreuve_Ecrite-2026/spe_numerique_informatique_2026_centres_etranger_2_sujet_officiel_1_.pdf","sujet","ok")],pages_aeif=12),
  [(6,"2-7","Cet exercice porte sur la programmation orientée objet et la sécurité des communications (classes, constructeur, méthodes, assertions, chiffrement symétrique et asymétrique)."),
   (6,"8-12","Cet exercice porte sur les bases de données relationnelles, les requêtes SQL, les réseaux et les protocoles de routage (RIP, OSPF, adressage IP)."),
   (8,"13-18","Cet exercice porte sur l'architecture matérielle (dont le langage assembleur), les structures linéaires de données et la programmation orientée objet (modèle de von Neumann, portes logiques, assembleur RISC-V, files).")])
S("2026-metropole-j1",2026,"juin","Métropole",1,"2026-06-16","26-NSIJ1ME1",16,"math93 (reprise du PDF officiel)",
  dict(aeif=(a26("Metropole_juin_2026_sujet_1"),a26("Metropole_juin_2026_sujet_1_corrige"),"ok"),
       autres=[("math93","https://math93.com/images/pdf/annales_bac/Bac_NSI/bac_NSI_2026/NSI_Epreuve_Ecrite-2026/26_NSIJ1ME1.pdf","sujet","ok")],pages_aeif=10),
  [(6,"2-5","Cet exercice porte sur les réseaux, les protocoles de routage et la sécurisation des communications (adressage IP et CIDR, passerelles, RIP, OSPF, coût et débit, chiffrement symétrique et asymétrique, HTTPS)."),
   (6,"6-10","Cet exercice porte sur le binaire, les graphes, la récursivité (représentation binaire, XOR, listes de bits, graphe et dictionnaire, parcours en profondeur et en largeur)."),
   (8,"11-16","Cet exercice porte sur les arbres, l'algorithmique des arbres, et les bases de données (arbres binaires et n-aires, classes et méthodes récursives, SGBD, clés primaires et étrangères, SELECT, JOIN, UPDATE, INSERT, DELETE).")])
S("2026-metropole-j2",2026,"juin","Métropole",2,"2026-06-17","26-NSIJ2ME1",16,"math93 (reprise du PDF officiel)",
  dict(aeif=(a26("Metropole_juin_2026_sujet_2"),a26("Metropole_juin_2026_sujet_2_corrige"),"ok"),
       autres=[("math93","https://math93.com/images/pdf/annales_bac/Bac_NSI/bac_NSI_2026/NSI_Epreuve_Ecrite-2026/26_NSIJ2ME1.pdf","sujet","ok")],pages_aeif=10),
  [(6,"2-5","Cet exercice porte sur les réseaux et la programmation orientée objet (adressage IPv4, masques, RIP, OSPF, tables de routage, classe, constructeur, listes)."),
   (6,"6-10","Cet exercice porte sur la mise au point de programme, la gestion des bugs et les graphes (débogage, tests assert, listes de listes, mélange aléatoire, inversions et parité, listes d'adjacence)."),
   (8,"11-16","Cet exercice porte sur les bases de données ainsi que les structures de file et de graphe (SQL, files, graphes, parcours en largeur, dictionnaires).")])
S("2026-antilles-guyane-j1",2026,"juin","Antilles-Guyane",1,"2026-06-16","26-NSIJ1AG1",13,"freemaths (reprise de la mise en page officielle)",
  dict(aeif=(a26("Antilles-Guyane_juin_2026_sujet_1"),None,"ok"),
       autres=[("freemaths","https://www.freemaths.fr/sujets-du-bac/baccalaureat-general/numerique-et-sciences-informatiques/annees/annee-2026/antilles-guyane/sujet-1-et-correction/bac-numerique-et-sciences-informatiques-antilles-guyane-2026-sujet-1.pdf","sujet","ok"),
               ("math93","https://math93.com/images/pdf/annales_bac/Bac_NSI/bac_NSI_2026/NSI_Epreuve_Ecrite-2026/26_NSIJ1AG1.pdf","sujet","non lu (l'outil n'a pas pu l'ouvrir le 20/11)")],pages_aeif=8),
  [(6,"2-4","Modèle relationnel et SQL pour une pizzeria (avantages d'un SGBD sur un tableur, clés primaires et étrangères, SELECT, JOIN, UPDATE, INSERT, DELETE, agrégation, sécurité d'un serveur accessible en ligne)."),
   (6,"5-8","Algorithmique et Python : plus longue sous-liste commune (recherche exhaustive, récursivité, relation de récurrence, complexité, éviter la récursion trop coûteuse)."),
   (8,"9-13","Routage, sécurisation des communications et POO (RIP, OSPF, DNS, chiffrement symétrique et asymétrique, signature numérique, tableaux, classe Cle_symetrique).")],
  rem="Pas de corrigé trouvé (le 20/11/2026).")
S("2026-antilles-guyane-j2",2026,"juin","Antilles-Guyane",2,"2026-06-17","26-NSIJ2AG1",15,"freemaths (reprise de la mise en page officielle)",
  dict(aeif=(a26("Antilles-Guyane_juin_2026_sujet_2"),None,"ok"),
       autres=[("freemaths","https://www.freemaths.fr/sujets-du-bac/baccalaureat-general/numerique-et-sciences-informatiques/annees/annee-2026/antilles-guyane/sujet-2-et-correction/bac-numerique-et-sciences-informatiques-antilles-guyane-2026-sujet-2.pdf","sujet","ok")],pages_aeif=9),
  [(6,"2-5","Cet exercice porte sur les bases de données relationnelles, les requêtes SQL et la programmation objet."),
   (6,"6-10","Cet exercice porte sur les protocoles de routage et les graphes (RIP, OSPF, tables de routage, parcours en largeur)."),
   (8,"11-15","Cet exercice traite de tableaux, de dictionnaires, de récursivité et de programmation dynamique.")],
  rem="Pas de corrigé trouvé (le 20/11/2026).")

# ------------------------------------------------------------------ 2025
def a25(nom, d="2025/07"): return AE+f"{d}/{nom}.pdf"
def kx(annee, slug, aeif=None, pages=None, mep="PDF officiel (kxs)", autres=None):
    s, c = K(annee, slug)
    l = dict(kxs=(s, c if (annee,slug) in KXS_CORRIGE else None))
    if aeif: l["aeif"] = aeif
    if autres: l["autres"] = autres
    return l

S("2025-metropole-j1",2025,"juin","Métropole",1,"2025-06-17","25-NSIJ1ME1",17,"PDF officiel (kxs)",
  kx(2025,"metropole-jour-1",(a25("Metropole_2025_1"),a25("25NSIJ1ME1"),"non testé")),
  [(6,None,"Cet exercice porte sur les bases de données relationnelles et SQL (clés primaires et étrangères, interrogation, insertion, mise à jour, suppression, fonction d'agrégation SUM)."),
   (6,None,"Algorithmique, structures de données et gestion de processus (classes et objets en Python, files à priorité, complexité dans le pire des cas, ordonnancement, méthode Pomodoro)."),
   (8,None,"Architecture matérielle (réseau), arbres binaires de recherche et programmation Python (adressage IPv4, masques de sous-réseau, RIP, OSPF, tables de routage, comparaison d'adresses en binaire, ABR).")],
  rem="Pages par exercice non relevées pour ce sujet (17 pages au total).")
S("2025-metropole-j2",2025,"juin","Métropole",2,"2025-06-18","25-NSIJ2ME1",15,"PDF officiel (kxs)",
  kx(2025,"metropole-jour-2",(a25("Metropole_2025_2"),a25("25NSIJ2ME1"),"non testé")),
  [(6,"2-6","Cet exercice porte sur les arbres binaires et la programmation Python (parcours d'arbre, codage de Shannon-Fano, récursivité, dictionnaires et listes)."),
   (6,"7-10","Cet exercice porte sur les bases de données relationnelles, le langage SQL et la programmation (SELECT, JOIN, UPDATE, INSERT, DELETE, COUNT, ORDER BY, DISTINCT, sqlite3)."),
   (8,"10-15","Cet exercice porte sur la programmation de base en Python, la sécurisation des communications et les réseaux (masque jetable, chiffrement symétrique et asymétrique, HTTPS, adressage IPv4, masques de sous-réseau, ET bit à bit).")])
S("2025-amerique-nord-j1",2025,"mai","Amérique du Nord",1,None,"25-NSIJ1AN1",15,"PDF officiel (kxs)",
  kx(2025,"amerique-nord-jour-1",(a25("Amerique_Nord_2025_1"),a25("25NSIJ1AN1"),"non testé")),
  [(6,"2-6","Arbres binaires, récursivité, programmation orientée objet."),
   (6,"7-9","Programmation orientée objet, récursivité, algorithmes gloutons."),
   (8,"10-15","Graphes, bases de données, tris, algorithmes gloutons, récursivité.")])
S("2025-amerique-nord-j2",2025,"mai","Amérique du Nord",2,None,"25-NSIJ2AN1",21,"PDF officiel (kxs)",
  kx(2025,"amerique-nord-jour-2",(a25("Amerique_Nord_2025_2"),a25("25NSIJ2AN1"),"non testé")),
  [(6,"2-7","Tableaux, dictionnaires, arbres binaires, programmation en Python, récursivité."),
   (6,"8-13","Gestion des bugs, algorithmique, structures de données, programmation orientée objet."),
   (8,"14-21","Bases de données, programmation en Python, récursivité, algorithmes de parcours de graphes.")])
S("2025-amerique-nord-j2-bis",2025,"mai","Amérique du Nord",None,None,"25-NSIPE2",18,"PDF officiel (kxs)",
  kx(2025,"amerique-nord-jour-2-bis",(a25("Amerique_Nord_2025_3"),a25("25NSIPE2"),"non testé")),
  [(6,"2-8","Cet exercice porte sur la programmation en Python et la programmation dynamique (assertions, tranches de listes, division euclidienne, complexité)."),
   (6,"9-13","Cet exercice porte sur les arbres binaires et la représentation binaire (codage de Huffman, classes et objets, dictionnaires, tri par insertion, listes)."),
   (8,"14-18","Cet exercice porte sur la programmation objet en langage Python, les graphes et les bases de données (graphes non orientés, parcours, récursivité, clés primaires et étrangères, SQL).")],
  rem="Sujet de secours de la session Amérique du Nord 2025 (kxs : « jour 2 bis » ; AEIF : « sujet 3 »).")
S("2025-asie-j1",2025,"juin","Asie",1,None,"25-NSIJ1JA1",13,"PDF officiel (kxs)",
  kx(2025,"asie-jour-1",(a25("Asie_2025_1"),a25("25NSIJ1JA1"),"non testé")),
  [(6,"2-4","Cet exercice porte sur la décidabilité, l'algorithmique et la programmation en Python (problème de l'arrêt, exec, chaînes de caractères, boucles while, algorithme de Boyer-Moore)."),
   (6,"5-10","Cet exercice porte sur les arbres et la compression d'un fichier texte (codage ASCII, arbres binaires, file à priorité, code de Huffman, parcours, dictionnaires, taux de compression)."),
   (8,"10-13","Cet exercice porte sur les dictionnaires et leurs algorithmes associés, le traitement de données en table, la sécurisation des communications et la programmation en général (SQL SELECT, JOIN, INSERT, DELETE, schéma relationnel).")])
S("2025-asie-j2",2025,"juin","Asie",2,None,"25-NSIJ2JA1",14,"PDF officiel (kxs)",
  kx(2025,"asie-jour-2",(a25("Asie_2025_2"),a25("25NSIJ2JA1"),"non testé")),
  [(6,"2-5","Programmation orientée objet, algorithmique (classe Date)."),
   (6,"6-8","Programmation Python, gestion des processus."),
   (8,"9-14","Programmation Python (dictionnaire, récursivité, spécification), programmation orientée objet, bases de données relationnelles, requêtes SQL, arbres binaires.")])
S("2025-centres-etrangers-j1",2025,"juin","Centres étrangers",1,None,"25-NSIJ1G11",13,"AEIF (recomposé en LaTeX)",
  dict(aeif=(a25("Centres_etrangers_2025_1"),a25("25NSIJ1G11"),"ok")),
  [(6,"1-5","Graphes et POO."),(6,"6-8","Algorithmique, récursivité et files."),(8,"9-13","Listes, dictionnaires, POO, arbres binaires de recherche et bases de données.")],
  rem="Absent de kxs. Le PDF AEIF est une recomposition : sa pagination n'est pas celle du sujet officiel.")
S("2025-centres-etrangers-j2",2025,"juin","Centres étrangers",2,None,"25-NSIJ2G11",11,"AEIF (recomposé en LaTeX)",
  dict(aeif=(a25("Centres_etrangers_2025_2"),a25("25NSIJ2G11"),"ok")),
  [(6,"1-2","Bases de données et langage SQL (SELECT, FROM, WHERE, JOIN, UPDATE, INSERT, DELETE, DISTINCT, ORDER BY, clés primaires et étrangères)."),
   (6,"3-5","Listes, dictionnaires, fonctions et récursivité (fonction de hachage, recherche dichotomique, ajout ordonné)."),
   (8,"6-11","Graphes, POO, files et récursivité (graphe du jeu, classe File, chemins non prolongeables).")],
  rem="Absent de kxs. Pagination AEIF (recomposition).")
S("2025-polynesie-j1",2025,"juin","Polynésie",1,None,"25-NSIJ1PO1",12,"AEIF (recomposé en LaTeX)",
  dict(aeif=(a25("Polynesie_2025_1"),a25("25NSIJ1PO1"),"ok")),
  [(6,"1-4","Protocoles réseaux, algorithmique et POO."),(6,"5-7","Programmation Python et récursivité."),(8,"8-12","Programmation Python, langage SQL, systèmes d'exploitation, sécurisation des communications.")],
  rem="Absent de kxs. Pagination AEIF.")
S("2025-polynesie-j2",2025,"juin","Polynésie",2,None,"25-NSIJ2PO1",7,"AEIF (recomposé en LaTeX)",
  dict(aeif=(a25("Polynesie_juin_2025_sujet_2","2025/11"),a25("25NSIJ2PO1"),"ok")),
  [(6,"1-2","POO (classes, constructeurs, méthodes de classe), listes, génération aléatoire, boucles."),
   (6,"3-4","SQL (SELECT, INSERT, UPDATE, clés étrangères), schéma relationnel, POO, fonctions de recherche textuelle."),
   (8,"5-7","Piles, files, graphes, dictionnaires, tableaux, POO, fonctions récursives sur les mots.")],
  rem="Absent de kxs. Pagination AEIF.")
S("2025-metropole-sept-j1",2025,"septembre","Métropole (remplacement)",1,None,"25-NSIJ1ME3",12,"AEIF (recomposé en LaTeX)",
  dict(aeif=(a25("Metropole_septembre_2025_sujet_1","2025/09"),a25("Metropole_septembre_2025_sujet_1_corrige","2026/06"),"ok")),
  [(6,"1-4","Programmation Python, réseaux, protocoles de routage."),(6,"5-8","Algorithmique, listes et programmation dynamique."),(8,"9-12","Langage SQL, programmation Python et recherche textuelle.")],
  rem="Absent de kxs. Pagination AEIF.")
S("2025-metropole-sept-j2",2025,"septembre","Métropole (remplacement)",2,None,"25-NSIJ2ME3",11,"AEIF (recomposé en LaTeX)",
  dict(aeif=(a25("Metropole_septembre_2025_sujet_2","2025/09"),a25("Metropole_septembre_2025_sujet_2_corrige","2026/06"),"ok")),
  [(6,"1-4","Programmation Python et cryptographie (chiffrement de Playfair, listes, fonctions)."),(6,"5-7","Systèmes d'exploitation et POO (permissions Linux, chmod, classes)."),(8,"8-11","Langage SQL, graphes et programmation générale (parcours).")],
  rem="Absent de kxs. Pagination AEIF. La page AEIF libelle par erreur le corrigé du sujet 2 « septembre 2026 ».")
S("2025-asie-sept",2025,"septembre","Asie (remplacement)",None,None,"25-NSIPE4",8,"AEIF (recomposé en LaTeX)",
  dict(aeif=(a25("25-nsipe4","2025/12"),a25("25nsipe4-1","2026/03"),"ok"),
       autres=[("AEIF (version P. Rémy)",a25("Asie_septembre_2025","2025/12"),"sujet","ok")]),
  [(6,"1-2","Cet exercice porte sur les bases de données relationnelles et les requêtes SQL."),
   (6,"2-5","Cet exercice porte sur les réseaux, le routage, les graphes et la programmation (adressage IP, RIP, OSPF, graphes en Python, récursivité, parcours en largeur)."),
   (8,"5-8","Cet exercice porte sur l'algorithmique des tableaux, la gestion de bugs, les listes, les piles et la programmation orientée objet (listes chaînées).")],
  rem="Absent de kxs. Un seul sujet pour la session. Pagination AEIF.")
S("2025-amerique-sud-nov-j1",2025,"novembre","Amérique du Sud",1,None,"25-NSIJ1AS1",12,"AEIF (recomposé en LaTeX)",
  dict(aeif=(a25("Amerique_Sud_novembre_2025_sujet_1","2025/12"),a25("Amerique_Sud_novembre_2025_sujet_1_corrige","2026/01"),"ok")),
  [(6,"1-4","Bases de données, SQL, arbres binaires."),(6,"5-7","Systèmes d'exploitation, processus, POO."),(8,"8-12","Systèmes d'exploitation, réseaux et programmation Python.")],
  rem="Absent de kxs. Pagination AEIF. Autre corrigé listé par AEIF : https://aeif.fr/wp-content/uploads/2025/12/25nsij1as1_v2.pdf (non testé).")
S("2025-amerique-sud-nov-j2",2025,"novembre","Amérique du Sud",2,None,"25-NSIJ2AS1",11,"AEIF (recomposé en LaTeX)",
  dict(aeif=(a25("Amerique_Sud_novembre_2025_sujet_2","2025/12"),a25("Amerique_Sud_novembre_2025_sujet_2_corrige","2026/01"),"ok")),
  [(6,"1-4","Bases de données, SQL, programmation Python, listes."),(6,"5-7","Structure de pile, POO et algorithmique."),(8,"8-11","POO, graphes et réseaux.")],
  rem="Absent de kxs. Pagination AEIF.")
S("2025-nouvelle-caledonie-nov-j1",2025,"novembre","Nouvelle-Calédonie",1,None,None,8,"AEIF (recomposé en LaTeX)",
  dict(aeif=(a25("Nouvelle_Caledonie_novembre_2025_sujet_1","2026/01"),a25("Nouvelle_Caledonie_novembre_2025_sujet_1_corrige","2026/06"),"ok")),
  [(6,"1-3","Graphes, réseaux et POO."),(6,"4-5","Bases de données, SQL et POO."),(8,"6-8","Algorithmique, représentation binaire et programmation Python.")],
  rem="Absent de kxs. Pagination AEIF.")
S("2025-nouvelle-caledonie-nov-j2",2025,"novembre","Nouvelle-Calédonie",2,None,None,11,"AEIF (recomposé en LaTeX)",
  dict(aeif=(a25("Nouvelle_Caledonie_novembre_2025_sujet_2","2026/01"),a25("Nouvelle_Caledonie_novembre_2025_sujet_2_corrige","2026/06"),"ok")),
  [(6,"1-3","Cryptographie symétrique et asymétrique, signature, empreintes, encodage des données, programmation Python."),(6,"4-6","Bases de données, SQL, programmation Python, gestion de bugs."),(8,"7-11","Structures de données, programmation Python, graphes.")],
  rem="Absent de kxs. Pagination AEIF.")

# ------------------------------------------------------------------ 2024
def a24(nom, d="2025/07"): return AE+f"{d}/{nom}.pdf"
S("2024-amerique-nord-j1",2024,"mai","Amérique du Nord",1,None,"24-NSIJ1AN1",13,"PDF officiel (kxs)",
  kx(2024,"amerique-nord-jour-1",(a24("Amerique_Nord_2024_1"),a24("corr_amerique_nord_2024_1"),"non testé")),
  [(6,"2-5","Cet exercice porte sur la programmation Python, la programmation orientée objet, les structures de données (file), l'ordonnancement et l'interblocage."),
   (6,"6-8","Cet exercice porte sur les graphes (matrice d'adjacence, dictionnaire de listes d'adjacence, parcours en profondeur)."),
   (8,"9-13","Cet exercice porte sur la programmation Python, la modularité, les bases de données relationnelles et les requêtes SQL.")])
S("2024-amerique-nord-j2",2024,"mai","Amérique du Nord",2,None,"24-NSIJ2AN1",12,"PDF officiel (kxs)",
  kx(2024,"amerique-nord-jour-2",(a24("Amerique_Nord_2024_2"),a24("corr_amerique_nord_2024_2"),"non testé")),
  [(6,"2-4","Cet exercice porte sur les algorithmes de tri et la programmation en Python (tri de Stooge, récursivité, coût en temps dans le pire des cas)."),
   (6,"5-7","Cet exercice porte sur le langage SQL et les bases de données (SELECT, ORDER BY, INSERT, UPDATE, clés étrangères)."),
   (8,"8-12","Cet exercice porte sur la programmation objet, les structures de données, les réseaux et l'architecture matérielle (listes chaînées, récursivité, adressage IP, hachage, recherche exhaustive).")])
S("2024-centres-etrangers-g1-j1",2024,"juin","Centres étrangers (groupe 1)",1,None,"24-NSIJ1G11",11,"PDF officiel (kxs)",
  kx(2024,"centres-etrangers-groupe-1-jour-1",(a24("Centres_Etrangers_juin_2024_sujet_1_v2","2026/04"),a24("Centres_Etrangers_juin_2024_sujet_1_corr_v2","2026/04"),"non testé")),
  [(6,"2-3","Cet exercice porte sur la programmation Python, la programmation dynamique, les graphes et les réseaux."),
   (6,"4-6","Cet exercice porte sur les réseaux et les protocoles de routage."),
   (8,"7-11","Cet exercice porte sur la programmation Python, la programmation orientée objet, les bases de données relationnelles et les requêtes SQL.")])
S("2024-centres-etrangers-g1-j2",2024,"juin","Centres étrangers (groupe 1)",2,None,"24-NSIJ2G11",14,"PDF officiel (kxs)",
  kx(2024,"centres-etrangers-groupe-1-jour-2",(a24("Centres_etrangers_juin_2024_2"),a24("corr_centre_etrangers_2024_2"),"non testé")),
  [(6,"2-5","Cet exercice porte sur la programmation en Python en général, la programmation orientée objet et la récursivité (génération aléatoire, dénombrement de chemins)."),
   (6,"6-8","Cet exercice porte sur la programmation objet, la récursivité, les arbres binaires et les systèmes d'exploitation (parcours préfixe, suffixe, en largeur, commandes Linux)."),
   (8,"9-14","Cet exercice porte sur le codage binaire, les bases de données relationnelles et les requêtes SQL.")])
S("2024-asie-j1",2024,"juin","Asie",1,None,"24-NSIJ1JA1",14,"PDF officiel (kxs)",
  kx(2024,"asie-jour-1",(a24("Asie_juin_2024_1"),a24("corr_Asie_2024_1"),"non testé")),
  [(6,"2-5","Cet exercice porte sur la programmation Python, la programmation orientée objet et l'algorithmique (algorithme glouton de placement d'antennes, coût d'un algorithme)."),
   (6,"6-11","Cet exercice porte sur les graphes, la programmation, la structure de pile et l'algorithmique des graphes (matrices d'adjacence, tri topologique, cycles, parcours en profondeur récursif)."),
   (8,"12-14","Cet exercice porte sur la programmation Python, la programmation orientée objet, les bases de données relationnelles et les requêtes SQL (jointures, SELECT, UPDATE, DELETE).")])
S("2024-asie-j2",2024,"juin","Asie",2,None,"24-NSIJ2JA1",12,"PDF officiel (kxs)",
  kx(2024,"asie-jour-2",(a24("Asie_Juin_2024_2"),a24("corr_Asie_2024_2"),"non testé")),
  [(6,"2-4","Cet exercice porte sur la programmation Python (listes, dictionnaires) et la méthode « diviser pour régner »."),
   (6,"5-8","Cet exercice porte sur la programmation, la programmation orientée objet et les structures de données linéaires (classe Pile, vérification de parenthésage)."),
   (8,"8-12","Cet exercice porte sur les bases de données relationnelles, les requêtes SQL et la programmation en Python.")])
S("2024-metropole-juin-j1",2024,"juin","Métropole",1,"2024-06-19","24-NSIJ1ME1",15,"PDF officiel (kxs)",
  kx(2024,"metropole-juin-sujet-1",(a24("Metropole_juin_2024_1"),a24("corr_metropole_juin_2024_1"),"non testé")),
  [(6,"2-5","Cet exercice porte sur la programmation objet en Python et les graphes (parcours de graphe, files, recherche d'un maximum)."),
   (6,"6-8","Cet exercice traite de protocoles de routage, de sécurité des communications et de base de données relationnelle (RIP, OSPF, SQL, SGBD)."),
   (8,"9-15","Cet exercice porte sur la programmation orientée objet, sur les arbres binaires de recherche et la récursivité.")],
  rem="Date lue dans le PDF d'après la relecture automatique : 19 juin 2024 (à confirmer).")
S("2024-metropole-juin-j2",2024,"juin","Métropole",2,"2024-06-20","24-NSIJ2ME1",15,"PDF officiel (kxs)",
  kx(2024,"metropole-juin-sujet-2",(a24("Metropole_juin_2024_2"),a24("corr_metropole_juin_2024_2"),"non testé")),
  [(6,"2-4","Cet exercice porte sur la notion de bases de données relationnelles, le langage SQL et les protocoles de sécurisation (chiffrement symétrique et asymétrique)."),
   (6,"5-8","Cet exercice porte sur la programmation orientée objets, les tris, les algorithmes gloutons, la récursivité et les assertions."),
   (8,"9-13","Cet exercice porte sur la programmation orientée objet, les graphes et utilise la structure de données dictionnaire.")])
S("2024-metropole-sept-j1",2024,"septembre","Métropole (remplacement)",1,"2024-09-11","24-NSIJ1ME3",16,"PDF officiel (kxs)",
  kx(2024,"metropole-septembre-sujet-1",(a24("Metropole_sept_2024_1"),a24("corr_metropole_sept_2024_1"),"non testé")),
  [(6,"2-5","Cet exercice porte sur la programmation Python, les bases de données relationnelles et les requêtes SQL."),
   (6,"6-10","Cet exercice porte sur les réseaux, les protocoles de routage et les graphes (adressage IPv4, RIP, OSPF, listes et matrice d'adjacence, degré, chaîne eulérienne)."),
   (8,"11-16","Cet exercice porte sur les bases de numération, la structure de données PILE et la POO (numération positionnelle en base 20).")])
S("2024-metropole-sept-j2",2024,"septembre","Métropole (remplacement)",2,"2024-09-12","24-NSIJ2ME3",12,"PDF officiel (kxs)",
  kx(2024,"metropole-septembre-sujet-2",(a24("Matropole_sept_2024_2"),a24("corr_metropole_sept_2024_2"),"non testé")),
  [(6,"2-3","Cet exercice porte sur l'exécution d'un programme Python et sur la décidabilité (boucle while, fonction récursive, problème de l'arrêt)."),
   (6,"4-7","Cet exercice porte sur la programmation Python, la programmation orientée objet, les tests et la structure de données pile."),
   (8,"7-12","Cet exercice porte sur les réseaux, les protocoles réseau, les bases de données relationnelles et les requêtes SQL (adressage IPv4, tables de routage, RIP).")])
S("2024-polynesie-j1",2024,"juin","Polynésie",1,None,"24-NSIJ1PO1",11,"PDF officiel (kxs)",
  kx(2024,"polynesie-jour-1",(a24("Polynesie_juin_2024_1"),a24("corr_polynesie_2024_1"),"non testé")),
  [(6,"2-5","Cet exercice porte sur les graphes et les protocoles réseau (adressage IP et masques, tables de routage, RIP, parcours récursif de recherche de chemin)."),
   (6,"6-7","Cet exercice porte sur la récursivité (cas de base, dénombrement, programmation dynamique avec mémorisation, listes)."),
   (8,"8-11","Cet exercice porte sur la programmation Python (dictionnaire), les bases de données relationnelles et les requêtes SQL (tri par insertion, listes de tuples).")])
S("2024-polynesie-j2",2024,"juin","Polynésie",2,None,"24-NSIJ2PO1",15,"PDF officiel (kxs)",
  kx(2024,"polynesie-jour-2",(a24("Polynesie_juin_2024_2"),a24("corr_polynesie_2024_2"),"non testé")),
  [(6,"2-5","Cet exercice porte sur les structures de données FILE et PILE, les graphes et les algorithmes de parcours (parcours en largeur et en profondeur, plus court chemin, distance)."),
   (6,"6-9","Cet exercice porte sur les arbres binaires de recherche, la POO et la récursivité (parcours préfixe, suffixe, infixe, hauteur et équilibre)."),
   (8,"10-15","Cet exercice porte sur les protocoles réseau, les bases de données relationnelles et les requêtes SQL, l'algorithmique et la programmation en Python (RIP, OSPF, chaînes de caractères, mots de passe).")],
  rem="Exercice 3 noté sur 8 points, dont 2 pour la partie A (« 6 points sans la partie A », d'après le PDF).")
S("2024-amerique-sud-sept-j1",2024,"septembre","Amérique du Sud",1,None,None,9,"AEIF (recomposé en LaTeX)",
  dict(aeif=(a24("Amerique_Sud_2024_sept_1"),a24("Amerique_Sud_septembre_2024_sujet_1_corrige_v2","2025/09"),"ok")),
  [(6,"1-2","Programmation Python, POO, bases de données et requêtes SQL."),(6,"3-6","Programmation Python, dictionnaires et algorithmique (chaînes, tirage aléatoire, fichiers)."),(8,"7-9","Graphes (matrice d'adjacence, parcours en profondeur, file), récursivité.")],
  rem="Absent de kxs. Pagination AEIF. Le texte du PDF (et celui du corrigé) a des accents manquants à l'extraction.")
S("2024-amerique-sud-sept-j2",2024,"septembre","Amérique du Sud",2,None,None,8,"AEIF (recomposé en LaTeX)",
  dict(aeif=(a24("Amerique_Sud_2024_sept_2"),a24("corr_amerique_sud_2024_2"),"ok")),
  [(6,"1-2","Récursivité et langage SQL (clés primaire et étrangère, requêtes)."),(6,"3-4","Graphe et POO (parcours en profondeur et en largeur, récursivité)."),(8,"5-8","Réseau, protocoles de routage et algorithmique (adressage IP, tri par comptage, RIP, OSPF).")],
  rem="Absent de kxs. Pagination AEIF.")
S("2024-sujet-0-a",2024,"sujet 0","Sujet 0 (format 2024)",None,None,"Sujet 0.A",14,"PDF officiel (kxs)",
  kx(2024,"sujet-zero-A",(a24("Sujet_zero_2024_1"),a24("corr_sujet_zero_2024_1"),"non testé")),
  [(6,"2-5","Cet exercice porte sur l'architecture matérielle, les réseaux, les routeurs et les protocoles de routage."),
   (6,"6-9","Cet exercice porte sur les listes, les dictionnaires et la programmation de base en Python (tuples, recherche dichotomique, coût en temps)."),
   (8,"10-14","Cet exercice porte sur les graphes, les algorithmes sur les graphes, les bases de données et les requêtes SQL (graphes pondérés, matrice d'adjacence, parcours en largeur, récursivité).")])
S("2024-sujet-0-b",2024,"sujet 0","Sujet 0 (format 2024)",None,None,"Sujet 0.B",14,"PDF officiel (kxs)",
  kx(2024,"sujet-zero-B",(a24("Sujet_zero_2024_2"),a24("corr_sujet_zero_2024_2"),"non testé")),
  [(6,"2-4","Cet exercice porte sur la notion de listes, la récursivité et la programmation dynamique."),
   (6,"5-8","Cet exercice porte sur les systèmes d'exploitation, les commandes UNIX, les structures de données (de type LIFO et FIFO) et les processus."),
   (8,"9-14","Cet exercice porte sur la programmation Python (dictionnaire), la programmation orientée objet, les bases de données relationnelles et les requêtes SQL.")])

# ------------------------------------------------------------------ 2023  (12 points, 3 exercices obligatoires)
def a23(nom): return AE+f"2025/07/{nom}.pdf"
S("2023-amerique-nord-j1",2023,"mars","Amérique du Nord",1,None,"23-NSIJ1AN1",13,"PDF officiel (kxs)",
  kx(2023,"amerique-du-nord-jour-1",(a23("Amerique_Nord_mars_2023_1"),a23("corr_Amerique_nord_2023_1"),"non testé")),
  [(5,"2-6","Cet exercice porte sur le traitement des données en table et les bases de données (tableaux de dictionnaires, SQL SELECT, JOIN, COUNT, DELETE, UPDATE)."),
   (3,"7-9","Cet exercice porte sur les processus, l'ordonnancement, la logique booléenne (commande ps, tourniquet, tables de vérité)."),
   (4,"10-13","Cet exercice porte sur la programmation orientée objet et sur les arbres (classes, pile, ABR, parcours infixe, recherche dichotomique dans un arbre).")],bareme="12")
S("2023-amerique-nord-j2",2023,"mars","Amérique du Nord",2,None,"23-NSIJ2AN1",12,"PDF officiel (kxs)",
  kx(2023,"amerique-du-nord-jour-2",(a23("Amerique_Nord_mars_2023_2"),a23("corr_Amerique_nord_2023_2"),"non testé")),
  [(4,"2-4","Cet exercice porte sur les bases de données et les protocoles de routage (SQL, RIP, tables de routage)."),
   (5,"5-8","Cet exercice porte sur les arbres binaires, notamment les arbres binaires de recherche et sur la programmation en langage Python (parcours infixe, récursivité)."),
   (3,"9-12","Cet exercice porte sur les systèmes d'exploitation, la programmation en général et les dictionnaires (UNIX, droits d'accès).")],bareme="12")
S("2023-amerique-sud-j1",2023,"septembre (selon AEIF)","Amérique du Sud",1,None,"23-NSIJ1AS1",8,"AEIF (recomposé en LaTeX)",
  kx(2023,"amerique-du-sud-jour-1",(a23("Amerique_Sud_sept_2023_1"),a23("corr_amerique_sud_2023_1"),"ok")),
  [(5,"1-3","Réseaux, POO et bases de données (RIP, tables de routage, classes, dictionnaires, SQL SELECT, JOIN, INSERT, UPDATE, ORDER BY)."),
   (3,"4-5","Arbres binaires et files, récursivité."),
   (4,"6-8","Programmation générale (représentation des images, tableaux de tuples RVB, complexité, algorithme glouton).")],
  rem="Le PDF kxs est une image (non relu) ; points et pages relevés sur le PDF AEIF. La session est datée « septembre 2023 » par AEIF (à vérifier).",bareme="12")
S("2023-amerique-sud-j2",2023,"septembre (selon AEIF)","Amérique du Sud",2,None,"23-NSIJ2AS1",10,"AEIF (recomposé en LaTeX)",
  kx(2023,"amerique-du-sud-jour-2",(a23("Amerique_Sud_sept_2023_2"),a23("corr_amerique_sud_2023_2"),"ok")),
  [(4,"1-3","File, pile et POO (arbres binaires, parcours suffixe, notation polonaise inversée)."),
   (4,"4-6","Routage et bases de données (tables de routage, métrique, SQL, schéma relationnel)."),
   (4,"7-10","Tableaux, programmation, récursivité (listes de listes).")],
  rem="Le PDF kxs est une image (non relu) ; points et pages relevés sur le PDF AEIF.",bareme="12")
S("2023-centres-etrangers-j1",2023,"mars","Centres étrangers (groupe 1)",1,None,"23-NSIJ1G11",9,"PDF officiel (kxs)",
  kx(2023,"centres-etrangers-jour-1",(a23("Centres_Etrangers_mars_2023_1"),None,"non testé")),
  [(3,"2-3","Cet exercice porte sur les bases de données relationnelles et le langage SQL."),
   (3,"4-5","Cet exercice porte sur les réseaux et les protocoles de routages (IPv4, CIDR, RIP, OSPF)."),
   (6,"6-9","Cet exercice porte sur les structures de Files (fonctions et tuples, tirage aléatoire, boucles).")],bareme="12")
S("2023-centres-etrangers-j2",2023,"mars","Centres étrangers (groupe 1)",2,None,"23-NSIJ2G11",9,"PDF officiel (kxs)",
  kx(2023,"centres-etrangers-jour-2",(a23("Centres_etrangers_mars_2023_2"),a23("23nsij2g11"),"non testé")),
  [(4,"2-4","Cet exercice porte sur l'adressage IP et les protocoles de routage (masque de sous-réseau, ET logique, RIP, OSPF)."),
   (4,"5-6","Cet exercice porte sur les bases de données relationnelles et le langage SQL."),
   (4,"7-9","Cet exercice porte sur la programmation en Python, la manipulation des chaînes de caractères, les arbres binaires de recherche et le parcours de liste.")],bareme="12")
S("2023-liban-j1",2023,"mars","Liban",1,None,"23-NSIJ1LI1",10,"PDF officiel (kxs)",
  kx(2023,"liban-jour-1",(a23("Liban_mars_2023_1"),None,"non testé")),
  [(3,"2-3","Cet exercice porte sur l'algorithmique et la programmation (récursivité, terminaison, gestion des erreurs de type, chaînes)."),
   (5,"4-7","Cet exercice porte sur les bases de données, la représentation des données et les réseaux (SQL, types, listes et dictionnaires, OSPF)."),
   (4,"8-10","Cet exercice traite des piles, des arbres et de l'algorithmique (notation polonaise inversée, parcours d'arbres).")],bareme="12")
S("2023-liban-j2",2023,"mars","Liban",2,None,"23-NSIJ2LI1",12,"PDF officiel (kxs)",
  kx(2023,"liban-jour-2",(a23("Liban_mars_2023_2"),None,"non testé")),
  [(4,"2-3","Cet exercice traite des bases de données (modèle relationnel, SELECT, WHERE, JOIN)."),
   (3,"4-7","Cet exercice traite des réseaux, de la programmation Python et de l'algorithmique (RIP, tables de routage, récursivité, tri fusion)."),
   (5,"7-12","Cet exercice traite des arbres et de l'algorithmique (ABR, hauteur, parcours récursif, classes, rotations).")],bareme="12")
S("2023-metropole-j1",2023,"mars","Métropole",1,"2023-03-20","23-NSIJ1ME1",10,"PDF officiel (kxs)",
  kx(2023,"metropole-juin-jour-1",(a23("Metropole_mars_2023_1"),None,"non testé")),
  [(3,"2-3","Cet exercice porte sur la notion de base de données relationnelle et le langage SQL."),
   (3,"4-5","Cet exercice porte sur les réseaux (routage, tables de routage, RIP, OSPF, coût des liaisons)."),
   (6,"6-10","Cet exercice traite de programmation orientée objet en Python et d'algorithmique (classes, listes).")],
  rem="kxs libelle ce sujet « Métropole juin » ; le PDF indique le 20 mars 2023 (AEIF : mars 2023).",bareme="12")
S("2023-metropole-j2",2023,"mars","Métropole",2,"2023-03-21","23-NSIJ2ME1",10,"PDF officiel (kxs)",
  kx(2023,"metropole-juin-jour-2",(a23("Metropole_mars_2023_2"),a23("23nsij2me1"),"non testé")),
  [(3,"2-3","Cet exercice porte sur les protocoles réseau (RIP, OSPF, tables de coûts)."),
   (3,"4-6","Cet exercice porte sur les bases de données et le langage SQL."),
   (6,"7-10","Cet exercice porte sur les arbres binaires, les files et la programmation orientée objet (ABR, parcours en profondeur et en largeur, récursivité).")],
  rem="kxs libelle ce sujet « Métropole juin » ; le PDF indique le 21 mars 2023 (AEIF : mars 2023).",bareme="12")
S("2023-polynesie-j1",2023,"mars","Polynésie",1,None,"23-NSIJ1PO1",8,"PDF officiel (kxs)",
  kx(2023,"polynesie-jour-1",(a23("Polynesie_mars_2023_1"),None,"non testé")),
  [(4,"1-4","Cet exercice porte sur les bases de données relationnelles et le langage SQL."),
   (4,"4-6","Cet exercice porte sur la gestion des processus et la programmation orientée objet (ordonnancement par tourniquet, files d'attente)."),
   (4,"6-8","Cet exercice porte sur l'algorithmique, la programmation orientée objet et la méthode diviser-pour-régner (tuples, complexité, récursivité).")],bareme="12")
S("2023-polynesie-j2",2023,"mars","Polynésie",2,None,"23-NSIJ2PO1",10,"PDF officiel (kxs)",
  kx(2023,"polynesie-jour-2",(a23("Polynesie_mars_2023_2"),None,"non testé")),
  [(4,"2-4","Cet exercice porte sur les arbres binaires, les arbres binaires de recherche, la programmation orientée objet et la récursivité."),
   (4,"5-7","Cet exercice traite du thème base de données (modèle relationnel, langage SQL)."),
   (4,"8-10","Cet exercice traite du thème architecture matérielle, et plus particulièrement des processus et leur ordonnancement (ps, kill, arborescence des processus).")],bareme="12")
S("2023-reunion-mayotte-j1",2023,"mars","La Réunion et Mayotte",1,None,"23-NSIJ1LR1",8,"PDF officiel (kxs)",
  kx(2023,"reunion-jour-1",(a23("Mayotte_mars_2023_1"),None,"ok")),
  [(4,"2-4","Cet exercice porte sur les réseaux et les protocoles de routages (adressage IPv4, CIDR, RIP, OSPF)."),
   (4,"5-6","Cet exercice porte sur la programmation orientée objet et les dictionnaires."),
   (4,"7-8","Cet exercice porte sur les bases de données relationnelles et le langage SQL.")],
  rem="kxs : « Réunion » ; AEIF : « Mayotte » (même sujet, code LR1).",bareme="12")
S("2023-reunion-mayotte-j2",2023,"mars","La Réunion et Mayotte",2,None,"23-NSIJ2LR1",10,"PDF officiel (kxs)",
  kx(2023,"reunion-jour-2",(a23("Mayotte_mars_2023_2"),None,"ok")),
  [(4,"2-4","Cet exercice porte sur les arbres binaires de recherche, la programmation orientée objet et la récursivité."),
   (4,"4-7","Cet exercice porte sur les réseaux et les protocoles de routage (adressage IPv4, RIP, OSPF)."),
   (4,"8-10","Cet exercice porte sur les bases de données relationnelles et le langage SQL.")],
  rem="kxs : « Réunion » ; AEIF : « Mayotte ».",bareme="12")
S("2023-sujet-0-a",2023,"sujet 0","Sujet 0 (format 2023)",None,None,"Sujet 0.A",9,"PDF officiel (kxs)",
  kx(2023,"sujet-zero-A",(a23("Sujet_zero_2023_1"),None,"non testé"),autres=[("AEIF (officiel)","https://aeif.fr/wp-content/uploads/2022/12/2023-sujet_0-a.pdf","sujet","non testé")]),
  [(3,"2-3","L'exercice porte sur les bases de données et les types construits de données."),
   (3,"4-5","L'exercice porte sur l'architecture matérielle, les réseaux et les systèmes d'exploitation (OSPF, IPv4)."),
   (6,"6-9","L'exercice porte sur les arbres binaires de recherche et la programmation objet.")],bareme="12")
S("2023-sujet-0-b",2023,"sujet 0","Sujet 0 (format 2023)",None,None,"Sujet 0.B",9,"PDF officiel (kxs)",
  kx(2023,"sujet-zero-B",(a23("Sujet_zero_2023_2"),None,"non testé")),
  [(4,"2-4","Cet exercice est consacré aux commandes de base en ligne de commande sous Linux (tables CSV, modèle relationnel, clé primaire, SQL)."),
   (4,"5-6","Cet exercice est consacré à l'analyse et à l'écriture de programmes récursifs (factorielle)."),
   (4,"7-9","Cet exercice est consacré aux arbres binaires de recherche et à la notion d'objet.")],bareme="12")

# ------------------------------------------------------------------ 2022  (5 exercices, 3 à traiter, 4 points chacun)
def a22(nom): return AE+f"2025/07/{nom}.pdf"
def e5(*liste):  # liste de (pages, thème)
    return [(4,p,t) for p,t in liste]
S("2022-metropole-mai-j1",2022,"mai","Métropole",1,"2022-05-11","22-NSIJ1ME1",14,"PDF officiel (kxs)",
  kx(2022,"metropole-sujet-1",(a22("Metropole_2022_1"),a22("corr_metropole_mai_2022_1"),"non testé")),
  e5(("2-4","Structures de données : piles et files, parenthésage d'expressions, vérification de balisage avec une pile."),("5-6","Bases de données (SELECT, INSERT, UPDATE, clés primaires et étrangères, jointures)."),("7-8","Représentations binaires et protocoles de routage (adressage IPv4, RIP, OSPF)."),("9-11","Parcours des arbres binaires, principe diviser pour régner, récursivité."),("12-14","Programmation orientée objet.")),bareme="12")
S("2022-metropole-mai-j2",2022,"mai","Métropole",2,"2022-05-12","22-NSIJ2ME1",14,"PDF officiel (kxs)",
  kx(2022,"metropole-sujet-2",(a22("Metropole_2022_2"),a22("corr_metropole_mai_2022_2"),"non testé")),
  e5(("2-3","Arbres binaires de recherche, programmation orientée objet et récursivité."),("4-6","Structures de données (piles), récursivité."),("7-9","Réseaux et protocoles de routage (adressage IPv4, RIP, OSPF)."),("10-11","Bases de données relationnelles et langage SQL."),("12-14","Programmation objet et méthode diviser pour régner.")),bareme="12")
S("2022-metropole-sept",2022,"septembre","Métropole (remplacement)",None,None,"22-NSIJ1ME3",10,"AEIF (recomposé en LaTeX)",
  kx(2022,"rattrapage-jour-1",(a22("Metropole_2022_sept"),a22("corr_metropole_septembre_2022"),"ok")),
  e5(("1-2","Algorithmique et arbres binaires de recherche (parcours infixe, préfixe, suffixe, en largeur, récursivité)."),("3-4","POO et récursivité (classes, attributs, méthodes, listes)."),("5-6","Bases de données et SQL."),("7-8","Processus et réseaux (architecture de von Neumann, adressage IPv4 et CIDR, RIP, switch et routeur)."),("9-10","Files et programmation générale (structures de données abstraites).")),
  rem="kxs : « Rattrapage jour 1 » ; ce PDF kxs est une image : les exercices sont relevés sur le PDF AEIF « Métropole septembre 2022 » (mêmes thèmes que ceux listés par kxs). Code d'en-tête non lu.",bareme="12")
S("2022-amerique-nord-j1",2022,"mai","Amérique du Nord",1,None,"22-NSIJ1AN1",9,"AEIF (recomposé en LaTeX)",
  kx(2022,"amerique-nord-jour-1",(a22("Amerique_Nord_2022_1"),a22("corr_amerique_nord_2022_1"),"ok")),
  e5(("1-2","SQL et bases de données (contraintes d'intégrité, SELECT, JOIN, INSERT, UPDATE, COUNT)."),("3-4","Réseaux et protocoles de routage (tables de routage, RIP, OSPF, coût de liaison, tolérance aux pannes)."),("5-5","Arbres binaires de recherche (hauteur, parcours en largeur, récursivité)."),("6-7","Chaînes de caractères, tableaux et programmation (récursivité)."),("8-9","Files et tableaux (FIFO).")),
  rem="Le PDF kxs est une image (non relu) ; pages et points relevés sur le PDF AEIF (pagination AEIF).",bareme="12")
S("2022-amerique-nord-j2",2022,"mai","Amérique du Nord",2,None,"22-NSIJ2AN1",11,"AEIF (recomposé en LaTeX)",
  kx(2022,"amerique-nord-jour-2",(a22("Amerique_nord_2022_2"),a22("corr_amerique_nord_2022_2"),"ok")),
  e5(("1-2","Arbres binaires de recherche et POO (structure de liste abstraite)."),("3-4","OS et processus (systèmes de fichiers UNIX, ordonnancement, interblocage)."),("5-6","Bases de données et SQL (contraintes d'intégrité)."),("7-9","Arbres binaires (récursivité, parcours)."),("10-11","Tableaux à deux dimensions (boucles, conversion binaire-décimal, automates cellulaires).")),
  rem="Le PDF kxs est une image (non relu) ; relevé sur le PDF AEIF (pagination AEIF).",bareme="12")
S("2022-amerique-sud-j1",2022,"mai","Amérique du Sud",1,None,None,11,"AEIF (recomposé en LaTeX)",
  kx(2022,"amerique-sud-jour-1",(a22("Amerique_sud_2022_1"),a22("corr_amerique_sud_2022_1"),"ok")),
  e5(("1-2","Bases de données (SQL, SELECT, JOIN, INSERT, UPDATE, DELETE, agrégation)."),("3-4","Programmation et tri (tuples et listes, tris par sélection et par insertion, complexité)."),("5-7","Arbres binaires (représentation par dictionnaires, parcours récursif, hauteur, taille)."),("8-9","Processus et OS (ordonnancement préemptif, interblocage)."),("10-11","Réseaux et protocoles de routage (adressage IP, RIP, OSPF).")),
  rem="Le PDF kxs est une image (non relu) ; relevé sur le PDF AEIF (pagination AEIF).",bareme="12")
S("2022-amerique-sud-j2",2022,"mai","Amérique du Sud",2,None,"22-NSIJ2AS1",12,"PDF officiel (kxs)",
  kx(2022,"amerique-sud-jour-2",(a22("Amerique_Sud_2022_2"),a22("corr_amerique_sud_2022_2"),"non testé")),
  e5(("2-3","Programmation, algorithmique et complexité (k plus proches voisins, listes triées)."),("4-5","Réseaux et routage (adressage IP, DHCP, masques, OSPF)."),("6-7","Bases de données (SQL UPDATE, INSERT, SELECT, jointures, agrégation)."),("8-10","Programmation en Python, récursivité et méthode diviser pour régner (algorithme de Douglas-Peucker)."),("11-12","Arbres binaires, programmation orientée objet et récursivité.")),bareme="12")
S("2022-asie-j1",2022,"mai","Asie",1,None,"22-NSIJ1JA1",13,"PDF officiel (kxs)",
  kx(2022,"asie-jour-1",(a22("Asie_2022_1"),a22("corr_asie_2022_1"),"non testé")),
  e5(("2-3","Algorithmique, chaînes de caractères, complexité."),("4-5","Bases de données."),("6-7","Système d'exploitation (Linux)."),("8-9","Programmation objet en langage Python."),("10-11","Programmation Python.")),bareme="12")
S("2022-asie-j2",2022,"mai","Asie",2,None,"22-NSIJ2JA1",14,"PDF officiel (kxs)",
  kx(2022,"asie-jour-2",(a22("Asie_2022_2"),a22("corr_asie_2022_2"),"non testé")),
  e5(("2-3","Systèmes d'exploitation Linux (commandes, droits de fichiers, module os)."),("4-6","Arbres binaires de recherche (hauteur, équilibre, récursivité)."),("7-8","Structures de données, programmation (listes de listes, jeu de la vie)."),("9-10","Bases de données et langage SQL."),("11-12","Exécution de programmes, recherche et correction de bugs (débogage).")),bareme="12")
S("2022-centres-etrangers-j1",2022,"mai","Centres étrangers (groupe 1)",1,None,"22-NSIJ1G11",14,"PDF officiel (kxs)",
  kx(2022,"centres-etrangers-jour-1",(a22("Centres_etrangers_2022_1"),a22("corr_centres_etrangers_2022_1"),"non testé")),
  e5(("2-3","Structures de données (listes, p-uplets et dictionnaires)."),("4-5","Structures de données (files et programmation objet)."),("6-8","Structures de données (dictionnaires)."),("9-10","Bases de données (SQL)."),("11-13","Architecture matérielle, réseaux et protocoles de routage (SoC, adressage MAC et IP, RIP, OSPF).")),
  rem="kxs liste ce sujet deux fois (« jour 1 » et « sujet 1 » : même PDF, code 22-NSIJ1G11).",bareme="12")
S("2022-centres-etrangers-j2",2022,"mai","Centres étrangers (groupe 1)",2,None,"22-NSIJ2G11",13,"PDF officiel (kxs)",
  kx(2022,"centres-etrangers-jour-2",(a22("Centres_etrangers_2022_2"),None,"non testé")),
  e5(("2-3","Langages et programmation (récursivité, listes, chaînes)."),("4-5","Structures de données (dictionnaires, chiffrement)."),("6-7","Bases de données (clé primaire, INSERT, SELECT)."),("8-9","Structures de données (programmation objet, tableau, file, pile)."),("10-12","Architectures matérielles, systèmes d'exploitation et réseaux (adressage IPv4, CIDR, RIP, OSPF).")),rem="Le fichier « corr_centres_etrengers_2022_2 » de l'AEIF est le corrigé du jour 1 (constat du 21/11/2026, T124) : le corrigé du jour 2 est à retrouver.",bareme="12")
S("2022-polynesie-j1",2022,"mai","Polynésie",1,None,"22-NSIJ1PO1",16,"PDF officiel (kxs)",
  kx(2022,"polynesie-jour-1",(a22("Polynesie_mai_2022"),a22("corr_polynesie_2022"),"non testé")),
  e5(("1-3","Programmation, récursivité (chaînes de caractères, fonctions)."),("4-6","Architecture matérielle : ordonnancement et expressions booléennes (bus, portes logiques)."),("7-9","Base de données (modèle relationnel, SQL)."),("9-11","Structures de données : piles (classes, listes Python)."),("12-15","Algorithmique : arbres binaires (récursivité, hauteur).")),bareme="12")
S("2022-reunion-mayotte-j1",2022,"mai","La Réunion et Mayotte",1,None,"22-NSIJ1LR1",16,"PDF officiel (kxs)",
  kx(2022,"mayotte-jour-1",(AE+"2022/11/2022_LeReunion_J1.pdf",None,"ok")),
  e5(("2-3","Structures de données (listes, piles et files)."),("4-6","Structures de données (programmation objet)."),("7-9","Bases de données (SQL)."),("10-12","Algorithmique (arbres binaires, parcours préfixe et infixe)."),("13-15","Transmission de données, architecture d'un réseau, protocoles de routage, programmation.")),
  rem="kxs libelle ce sujet « Mayotte » ; le code d'en-tête (LR1) et AEIF indiquent La Réunion.",bareme="12")
S("2022-reunion-mayotte-j2",2022,"mai","La Réunion et Mayotte",2,None,"22-NSIJ2LR1",13,"PDF officiel (kxs)",
  kx(2022,"mayotte-jour-2",(AE+"2022/11/2022_LaReunion_J2.pdf",None,"non testé")),
  e5(("2-3","Structures de données (pile), notation polonaise inverse."),("4-5","Bases de données (SQL SELECT, JOIN, UPDATE, dates)."),("6-7","Représentation binaire d'un entier relatif (complément à deux) et systèmes d'exploitation (Linux)."),("8-9","Arbres binaires de recherche."),("10-11","Algorithmes et programmation Python (listes, conversion binaire-décimal, doublons).")),
  rem="kxs libelle ce sujet « Mayotte » ; AEIF : La Réunion.",bareme="12")
S("2022-nouvelle-caledonie-j1",2022,"2022","Nouvelle-Calédonie",1,None,"22-NSIJ1NC1",15,"PDF officiel (AEIF)",
  dict(aeif=(AE+"2022/12/22_NSIJ1NC1.pdf",None,"ok")),
  e5(("3-4","Schéma relationnel de bases de données et requêtes SQL."),("5-8","Architecture des ordinateurs et protocoles réseau."),("9-10","Algorithmique et programmation Python avec un fichier csv."),("11-13","Algorithmique et programmation Python, arbre binaire."),("14-15","Algorithmique et programmation Python, programmation orientée objet.")),
  rem="Absent de kxs. Sujet officiel republié par AEIF.",bareme="12")
S("2022-nouvelle-caledonie-j2",2022,"2022","Nouvelle-Calédonie",2,None,"22-NSIJ2NC1",16,"PDF officiel (AEIF)",
  dict(aeif=(AE+"2022/12/22_NSIJ2NC1.pdf",None,"ok")),
  e5(("3-5","Algorithmique et programmation Python (classes, attributs, méthodes)."),("6-7","Algorithmique et programmation Python (arbres binaires, parcours, dictionnaires, récursivité)."),("8-8","Schéma relationnel de bases de données et requêtes SQL."),("9-11","Architecture réseau et protocoles de communication (adressage IPv4, RIP, OSPF, commutateurs, routeurs)."),("12-16","Architecture réseau et tables de routage (masques, commandes réseau, fonctions Python).")),
  rem="Absent de kxs. Sujet officiel republié par AEIF.",bareme="12")

# ------------------------------------------------------------------ 2021  (5 exercices, 3 à traiter, 4 points chacun)
S("2021-sujet-0",2021,"sujet 0","Sujet 0 (format 2021)",None,None,None,12,"PDF officiel (kxs)",
  kx(2021,"sujet-0",(AE+"2022/11/2021-sujet-0.pdf",None,"non testé")) if False else dict(kxs=K(2021,"sujet-0")[:1]+(None,)),
  [(None,"2-4","Cet exercice porte sur la notion de pile et sur la programmation de base en Python."),
   (None,"5-6","Cet exercice porte sur la programmation en général et la récursivité en particulier (tableaux à deux dimensions, programmation dynamique)."),
   (None,"7-8","Cet exercice porte sur les arbres binaires et les arbres binaires de recherche."),
   (None,"9-10","Cet exercice porte sur les bases de données relationnelles et le langage SQL."),
   (None,"11-12","Cet exercice porte sur les réseaux en général et les protocoles RIP et OSPF en particulier.")],
  rem="Points non indiqués sur ce sujet 0.",bareme="12")
S("2021-amerique-nord-j1",2021,"mars","Amérique du Nord",1,None,"21-NSIJ1AN1",12,"PDF officiel (kxs)",
  kx(2021,"amerique-nord-sujet-1",(AE+"2025/07/Amerique_Nord_mars_2021.pdf",AE+"2025/07/corr_amerique_nord_mars_2021.pdf","non testé")),
  e5(("2-3","Bases de données relationnelles et langage SQL."),("4-5","Routage, processus et systèmes sur puces."),("6-7","Tableaux et programmation de base en Python."),("8-10","Arbres binaires et leurs algorithmes associés."),("11-12","Piles, files et programmation de base en Python.")),
  rem="AEIF liste aussi un « sujet 2 » (code 21NSIJ2AN1, 8 pages, https://aeif.fr/wp-content/uploads/2025/07/21-NSIJ2AN1.pdf, testé) dont les thèmes recoupent ceux du sujet 1 : à contrôler.",bareme="12")
S("2021-centres-etrangers-j1",2021,"mars","Centres étrangers",1,None,"21-NSIJ1G11",16,"PDF officiel (kxs)",
  kx(2021,"centres-etrangers-sujet-1",(AE+"2025/07/Centres_etrangers_2021_1.pdf",AE+"2025/07/corr_centres_etrangers_juin_2021_1.pdf","non testé")),
  e5(("2-3","Programmation objet."),("4-6","Structures de données (dictionnaires)."),("7-8","Arbres binaires de recherche."),("9-10","Étude d'un réseau informatique."),("11-13","Structures de données : les piles.")),bareme="12")
S("2021-centres-etrangers-j2",2021,"mars","Centres étrangers",2,None,"21-NSIJ2G11",18,"PDF officiel (kxs)",
  kx(2021,"centres-etrangers-sujet-2",(AE+"2025/07/Centres_etrangers_2021_2.pdf",AE+"2025/07/corr_centres_etrangers_juin_2021_2.pdf","non testé")),
  e5(("2-4","Structures de données : les piles."),("5-7","Programmation Python, tuples et listes."),("8-10","Conversion décimal/binaire, table de vérité, codage des caractères."),("11-12","Gestion d'un club de handball (bases de données, SQL)."),("13-15","Bandeau à LED (programmation orientée objet, codage des couleurs RGB).")),bareme="12")
S("2021-metropole-candidats-libres-j1",2021,"juin","Métropole (candidats libres)",1,"2021-06-07","21-NSIJ1ME2",13,"PDF officiel (kxs)",
  kx(2021,"metropole-candidat-libre-sujet-1",(AE+"2025/07/Metroplole_juin_2021_1.pdf",AE+"2025/07/correction_metropole_juin_2021_1.pdf","non testé")),
  e5(("2-2","Bases de données."),("3-5","Piles et programmation orientée objet."),("6-7","Gestion des processus par un système d'exploitation et protocoles de routage (RIP, OSPF)."),("8-10","Algorithmique et programmation en Python (tableaux à deux dimensions, parcours en profondeur)."),("11-13","Manipulation de tableaux, récursivité et paradigme « diviser pour régner » (algorithmes de tri).")),bareme="12")
S("2021-metropole-candidats-libres-j2",2021,"juin","Métropole (candidats libres)",2,"2021-06-08","21-NSIJ2ME2",13,"PDF officiel (kxs)",
  kx(2021,"metropole-candidat-libre-sujet-2",(AE+"2025/07/Metropole_juin_2021_2.pdf",AE+"2025/07/corr_metropole_juin_2021_2.pdf","non testé")),
  e5(("2-3","Bases de données relationnelles et langage SQL."),("4-5","Gestion des processus et des ressources par un système d'exploitation (interblocage)."),("6-8","Arbres binaires de recherche et programmation orientée objet."),("9-10","Programmation en général et récursivité (mélange de Fisher-Yates)."),("11-12","Programmation en général (sous-séquences, somme maximale, programmation dynamique).")),bareme="12")
S("2021-metropole-mars-j1",2021,"mars","Métropole",1,None,None,13,"PDF officiel (kxs)",
  kx(2021,"metropole-sujet-1",(AE+"2025/07/metropole_mars_2021_1.pdf",AE+"2025/07/corr_Metropole_mars_2021_1.pdf","non testé")),
  e5(("2-3","Arbres binaires de recherche (hauteur, taille, classes et méthodes récursives)."),("4-7","Gestion des processus et opérateurs booléens (ordonnancement, interblocage, commandes UNIX, XOR, Unicode)."),("8-9","Bases de données et langage SQL (SGBD, SELECT, INSERT, UPDATE, DELETE, COUNT)."),("10-11","Tri fusion et diviser pour régner (complexité, récursivité)."),("12-13","Réseaux et protocoles de routage (adressage IP, masques, RIP, OSPF).")),
  rem="Code d'en-tête non lu.",bareme="12")
S("2021-metropole-mars-j2",2021,"mars","Métropole",2,None,None,12,"PDF officiel (kxs)",
  kx(2021,"metropole-sujet-2",(AE+"2025/07/Metropole_mars_2021_2.pdf",AE+"2025/07/corr_metropole_mars_2021_2.pdf","non testé")),
  e5(("2-4","Arbres et programmation orientée objet (ABR, récursivité)."),("4-5","Bases de données relationnelles."),("6-7","Réseaux et protocoles de routage (adressage IPv4, tables de routage)."),("8-9","Systèmes d'exploitation : processus et ressources (interblocage, commandes Linux)."),("10-11","Structures de données linéaires (files et piles, listes Python).")),
  rem="Code d'en-tête non lu. Le corrigé kxs n'existe pas ; AEIF en propose un.",bareme="12")
S("2021-polynesie",2021,"mars","Polynésie",2,None,"21-NSIJ2PO1",15,"PDF officiel (kxs)",
  kx(2021,"polynesie-sujet-2",(AE+"2025/07/Polynesie_2021.pdf",AE+"2025/07/corr_polynesie_mars_2021.pdf","non testé")),
  e5(("2-4","Algorithmique, langages et programmation (tris par insertion et fusion, listes Python, récursivité, complexité)."),("5-7","Traitement de données en tables et bases de données (SQL, formulaires web GET/POST, HTTP/HTTPS)."),("8-9","Algorithmique, langages et programmation (ABR, POO, tri par ABR)."),("10-12","Architectures matérielles, systèmes d'exploitation et réseaux (routage, graphes pondérés, processus, interblocage, von Neumann et Harvard, systèmes sur puce)."),("13-15","Traitement de données en tables et bases de données (SQL, fonctions Python sur des données de votes).")),
  rem="kxs : « sujet 2 » ; AEIF ne liste qu'un sujet « Polynésie 2021 ».",bareme="12")
S("2021-metropole-sept-j1",2021,"septembre","Métropole (remplacement)",1,None,"21-NSIJ1ME3",13,"PDF officiel (kxs)",
  kx(2021,"metropole-septembre-sujet-1",(AE+"2025/07/Mertopole_2021_sept.pdf",AE+"2025/07/corr_metropole_sept_2021.pdf","non testé")),
  e5(("2-2","Protocoles de communication, architecture d'un réseau et protocoles de routage."),("3-4","Algorithmique (recherche dichotomique) et récursivité."),("5-6","Bases de données (modèle relationnel, SQL)."),("7-8","Structures de données (programmation objet) et spécification."),("9-9","Structures de données (arbre, arbre binaire, pile).")),bareme="12")
S("2021-metropole-sept-j2",2021,"septembre","Métropole (remplacement)",2,None,"21-NSIJ2ME3",13,"PDF officiel (kxs)",
  kx(2021,"metropole-septembre-sujet-2"),
  e5(("2-3","Protocoles de communication, architecture d'un réseau et protocoles de routage."),("4-5","Structures de données (tableaux, dictionnaires) et spécification."),("6-6","Bases de données (modèle relationnel, SQL)."),("7-8","Structures de données (programmation objet) et spécification."),("9-10","Traitement de données en tables (CSV) et spécification.")),
  rem="AEIF ne liste qu'un sujet « Métropole septembre 2021 ».",bareme="12")
