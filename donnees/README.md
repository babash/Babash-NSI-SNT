# Les données de la bibliothèque

**Statut : format validé par l'enseignant le 07/11/2026 (tâche T02).** Le site actuel ne lit pas encore
ces fichiers : il continue d'utiliser les listes `*/ressources.js`.

```
donnees/
  ressources/<id>.json        une fiche par ressource (6 fiches d'exemple pour l'instant)
  vitrine.exemple.json        la mise en avant de la partie extérieure (exemple ; deviendra vitrine.json)
  progressions/               plus tard : les progressions annuelles de la partie élève
  referentiels/
    programmes.json           l'arbre des textes officiels : SNT 2019, NSI 1re et Tle 2019, missions du PP
    valeurs.json              les listes de valeurs : types, usages, origines, rôles, langages…
  schema/                     la description exacte du format (JSON Schema)
  correspondance-etiquettes.md  comment les listes actuelles passeront dans ce format
scripts/valider_donnees.py    la vérification automatique
```

---

## Pour l'enseignant : le format en bref

**Une ressource = une fiche.** CyberCase, le TD 1 de POO ou la Timeline ont chacun leur fiche. Elle dit
ce qu'est la ressource (titre, accroche, résumé, présentation, objectif, durée), pour qui (enseignement,
niveau, thème ou contenu du programme), comment elle s'utilise (un ou plusieurs types, usages, prérequis,
langages), d'où elle vient (origine, auteurs, licence, crédits), si elle **collecte des données d'élèves**,
et son état (brouillon, prête, à revoir, obsolète). Tes ressources sont signées « Babash - NSI Tani
Malandi », sous licence CC BY-SA pour les documents et MIT pour le code des applications ; une ressource
externe est créditée à son site d'origine.

**Une ressource a un ou plusieurs documents** : l'activité, sa version PDF, le corrigé, le guide du
professeur, le code source… Un seul est le **document principal** : celui qu'ouvre un clic sur le titre.

**Chaque document a deux réglages de visibilité** : visible de l'extérieur (oui ou non), visible des élèves
(oui ou non). Toi, dans l'admin, tu vois tout. Les règles :
- une ressource apparaît pour un public si au moins un de ses documents lui est visible ;
- si le document principal est caché pour un public, le premier document visible le remplace ;
- pour cacher une ressource, on cache tous ses documents.

> Exemple (fiche `operation-mirage`) : la fiche élève et le terminal sont visibles de tous ; la fiche
> professeur et le code source sont visibles de l'extérieur, pour les collègues, et cachés aux élèves
> (badge « caché : élèves »).

**Au départ**, tout ce qui est affiché aujourd'hui reste visible de l'extérieur ; l'espace professeur, le
guide du professeur, le corrigé et le code source sont cachés aux élèves. Les corrigés restent donc
visibles de l'extérieur pour les collègues, même si des élèves peuvent les y trouver.

**À savoir** : le dépôt est public. Un document caché n'est pas affiché, mais il reste lisible par qui
consulte le dépôt ou connaît son adresse. C'est pourquoi les fiches et les notes ne contiennent jamais de
mot de passe, d'identifiant (ceux de démonstration de CyberCase compris) ni de nom d'élève.

**La vitrine** choisit ce que montre la partie extérieure : pour chaque rubrique (SNT, NSI 1re…), ses
sections dans l'ordre, et dans chaque section la liste ordonnée des ressources à montrer. Une section suit
un thème du programme (« Internet », « Structures de données ») ou porte un titre libre (« Sites
ressources », « Préparer le bac »). Une même ressource peut être à plusieurs endroits : CyberCase est en SNT
et en NSI Terminale. « À la une » met quelques ressources en avant sur l'accueil (la ressource du mois).

**Les programmes** sont rangés comme les textes officiels, chaque thème et chaque contenu ayant un
identifiant qui ne changera plus (`snt-2019.internet.dns`). Quand la SNT révisée arrivera (annoncée pour
2027), elle s'ajoutera à côté (`snt-2027`), sans rien casser. La rubrique Professeur principal garde ses
thèmes actuels (Conseils de classe, Suivi des élèves, Orientation, Familles, Vie de classe, Textes
officiels) ; la circulaire de 2018 y est citée comme référence.

**Les listes de valeurs** reprennent celles du cahier des charges. Les ajouts validés le 07/11 (quatre
rôles de documents, deux usages) sont marqués `"ajout": true` dans `valeurs.json`.

---

## Pour les agents

### Les règles
- **Une fiche par ressource** : `donnees/ressources/<id>.json`, où `<id>` est l'identifiant de la fiche.
- **Identifiants** : minuscules, sans accents, mots séparés par des tirets (`td1-poo`). Stables : ils servent
  dans les adresses (`bibliotheque/?r=td1-poo`), la vitrine et les progressions.
- **Classements** : on écrit l'`id` d'une valeur des référentiels, jamais son libellé. Une valeur qui manque
  se demande dans le rapport ; les référentiels ne changent qu'après validation de l'enseignant.
- **Types** : une liste (`types`), au moins un, le principal en premier.
- **Programme** : on cite un thème ou un contenu de `programmes.json`, le plus précis possible.
- **Auteurs et licences** : ressource de l'enseignant → `{ "nom": "Babash - NSI Tani Malandi", "role": "auteur" }`,
  licence « CC BY-SA » pour les documents, « MIT » pour le code des applications. Ressource externe → créditée à
  son site d'origine (`credits`, et un auteur avec le rôle « site d'origine »).
- **Documents** : `url` (lien direct) **ou** `fichier` (chemin depuis la racine du dépôt, par exemple
  `nsi-terminale/fichiers/td1-poo-premiers-pas.pdf`, ancre permise). Jamais de page GitHub, sauf pour le
  rôle `code-source`. Le `format` est déduit de l'adresse (règles dans `valeurs.json`) : ne l'écrire que pour
  corriger une déduction fausse.
- **`visible`** est obligatoire sur chaque document, avec ses deux réglages : rien n'est caché ou montré par oubli.
  La valeur de départ d'un nouveau document est celle du rôle (`visible_par_defaut` dans `valeurs.json`).
- **`donnees_eleves`** est obligatoire : `{ "collecte": false }`, ou `{ "collecte": true, "detail": "…" }`.
  Ajouter `"facultative": true` quand l'élève peut s'en servir sans rien transmettre (CyberCase).
- **Vitrine** : une rubrique suit un programme (`"programme": "snt-2019"`) ou cite seulement un texte de
  référence (`"reference_officielle": "pp-2018"`), jamais les deux.
- **`dates`** sont remplies automatiquement ; **`notes`** sont réservées à l'enseignant (`[{ "date": "…", "texte": "…" }]`).
- Textes : français clair, formulations épicènes et double flexion, pas de point médian. Mise en forme permise :
  `code`, **gras**, retours à la ligne.

### Une fiche minimale

```json
{
  "id": "td1-poo",
  "titre": "POO, TD 1 : premiers pas en objets",
  "resume": "Séance de 30 min en cours inversé : trois encadrés puis quatre exercices courts.",
  "enseignements": ["nsi"],
  "niveaux": ["terminale"],
  "programme": ["nsi-tle-2019.structures-de-donnees.poo"],
  "types": ["td"],
  "usages": ["a-imprimer"],
  "origine": "ma-creation",
  "donnees_eleves": { "collecte": false },
  "statut": "brouillon",
  "documents": [
    { "role": "enonce", "fichier": "nsi-terminale/fichiers/td1-poo-premiers-pas.html",
      "principal": true, "visible": { "exterieur": true, "eleve": true } }
  ]
}
```

### Les 6 fiches d'exemple

| Fiche | Le cas qu'elle illustre |
|---|---|
| `cybercase` | ressource externe créditée à son site d'origine, « à la une », placée en SNT et en NSI Tle, collecte facultative, aucun identifiant de démonstration |
| `td1-poo` | ressource interne : page HTML du site et sa version PDF |
| `timeline-histoire-informatique` | placée en NSI 1re et en NSI Tle ; code source sur GitHub, caché aux élèves |
| `alien-python` | collecte de données d'élèves (`donnees_eleves`, à titre d'information), crédits d'un tiers, espace professeur |
| `fiche-variables-python` | fiche FichesNSI et sa version PDF, deux enseignements (SNT et NSI 1re) |
| `operation-mirage` | plusieurs types (TP et jeu) ; fiche professeur et code source visibles de l'extérieur, cachés aux élèves |

Ces fiches illustrent le format : leur contenu sera repris par le Bibliothécaire.

### Vérifier

```
python3 scripts/valider_donnees.py                 les données de ce dépôt
python3 scripts/valider_donnees.py --racine DIR    une autre copie du dépôt
python3 scripts/valider_donnees.py --strict        les avertissements bloquent aussi
```

Python 3 standard, sans dépendance (le module `jsonschema`, s'il est installé, sert de contrôle supplémentaire).
Chaque message donne le fichier et le champ. Trois niveaux : **ERREUR** (à corriger, code de retour 1),
**ATTENTION** (à regarder), **INFO** (pour information : documents cachés, collecte de données, intitulés à vérifier).

Ce qui est vérifié :
- JSON valide et conforme aux schémas ; identifiants uniques ; chaque fiche nommée `<id>.json` ;
- références existantes : valeurs des référentiels, thèmes et contenus, fiches liées, fichiers du dépôt ;
- cohérence : l'enseignement d'un contenu cité figure dans `enseignements` (son niveau dans `niveaux`, sinon avertissement) ;
- exactement un document principal ; aucune page GitHub hors du rôle `code-source` ;
- visibilité : ce que voit chaque public, remplacement du document principal caché, corrigé ou guide visible des élèves ;
- vitrine : ressources existantes, sections rangées dans le bon programme, contenus sous leur thème, thèmes du programme absents ;
- progressions : ressources existantes et visibles des élèves ;
- motifs interdits : mots de passe, identifiants, identifiants de démonstration, clés secrètes (Supabase `service_role`
  ou `sb_secret_`, GitHub, AWS, Google…), jetons, paramètres secrets dans les adresses, adresses électroniques.

### Sources des programmes
Elles sont citées dans `referentiels/programmes.json` (champ `sources`). En résumé :
- SNT 2019 : annexe de l'arrêté du 17 janvier 2019, BO spécial n° 1 du 22 janvier 2019 ; intitulés relevés dans
  deux copies concordantes du BO (SNES), la page Éduscol n'ayant pas pu être ouverte.
- NSI 1re et Tle 2019 : repris des listes `programme` du site actuel ; une relecture contre les PDF du BO reste à faire
  (certains intitulés y sont abrégés).
- PP : circulaire n° 2018-108 du 10 octobre 2018 (BO n° 37 du 11 octobre 2018), partie « I. Leurs missions » ;
  un intitulé est marqué `a_verifier`. Elle sert de référence et ne structure pas la rubrique.
