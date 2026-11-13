# Les données de la bibliothèque

**Statut : format validé par l'enseignant le 07/11/2026 (tâche T02) ; visibilité de départ changée par sa
consigne du 12/11/2026 ; thésaurus des notions publié le 12/11/2026 (T50a, T60) et validé par l'enseignant le 13/11/2026 ;
champ `notions` des fiches simplifié le 13/11/2026 (T64) : une seule liste des notions travaillées, plus les prérequis.**
Le site actuel ne lit pas encore ces fichiers : il continue d'utiliser les listes `*/ressources.js`.

```
donnees/
  ressources/<id>.json        une fiche par ressource (6 fiches d'exemple pour l'instant)
  vitrine.exemple.json        la mise en avant de la partie extérieure (exemple ; deviendra vitrine.json)
  progressions/               plus tard : les progressions annuelles de la partie élève
  referentiels/
    programmes.json           l'arbre des textes officiels : SNT 2019, NSI 1re et Tle 2019, missions du PP
    notions.json              le thésaurus des notions : boucle, dichotomie, routage… (modèle SKOS)
    valeurs.json              les listes de valeurs : types, usages, origines, rôles, langages…
    competences-pix.json      les 16 compétences numériques évaluées par Pix (champ facultatif en SNT)
  schema/                     la description exacte du format (JSON Schema)
  correspondance-etiquettes.md  comment les listes actuelles passeront dans ce format
scripts/valider_donnees.py    la vérification automatique
scripts/tests/test_notions.py ses tests pour le thésaurus, les notions des fiches et la visibilité
```

---

## Pour l'enseignant : le format en bref

**Une ressource = une fiche.** CyberCase, le TD 1 de POO ou la Timeline ont chacun leur fiche. Elle dit
ce qu'est la ressource (titre, accroche, résumé, présentation, durée), ce qu'elle vise (objectif, et au
besoin des critères de réussite), pour qui (enseignement, niveau, thème ou contenu du programme), comment
elle s'utilise (un ou plusieurs types, usages dont « utilisable sur téléphone » et « éditeur de code », prérequis,
langages, et en SNT les compétences Pix), ce que respectent son éditeur de code et la page en ligne d'un TD
(règles 20 et 19), d'où elle vient (origine, auteurs, licence, crédits), si elle **collecte des données d'élèves**,
et son état (brouillon, prête, à revoir, obsolète). Tes ressources sont signées « Babash - NSI Tani
Malandi », sous licence CC BY-SA 4.0 pour les documents et MIT pour le code des applications ; une ressource
externe est créditée à son site d'origine, et une ressource reprise et modifiée à toute la chaîne de ses auteurs
et autrices.

**Une ressource a un ou plusieurs documents** : l'activité, sa version PDF, le corrigé, le guide du
professeur, le code source… Un seul est le **document principal** : celui qu'ouvre un clic sur le titre.

**Chaque document a deux réglages de visibilité** : visible de l'extérieur (oui ou non), visible des élèves
(oui ou non). Toi, dans l'admin, tu vois tout. Les règles :
- une ressource apparaît pour un public si au moins un de ses documents lui est visible ;
- si le document principal est caché pour un public, le premier document visible le remplace ;
- pour cacher une ressource, on cache tous ses documents.

**Au départ, rien n'est caché** (ta consigne du 12/11/2026, 08:36 : « Pour le moment ne mets rien en caché,
je ferai tout à la main ») : chaque document, corrigé, guide du professeur, espace professeur et code source
compris, est visible de l'extérieur et des élèves. Elle remplace la règle du 07/11, qui cachait aux élèves
l'espace professeur, le guide, le corrigé et le code source. Tu règles toi-même la visibilité de chaque
document dans l'admin ; un document que tu caches y porte un badge (« caché : extérieur », « caché : élèves »
ou « caché : tous »).

> Exemple : pour réserver aux collègues la fiche professeur d'Opération MIRAGE, tu la laisses visible de
> l'extérieur et tu la caches aux élèves ; elle porte alors le badge « caché : élèves ».

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
rôles de documents, deux usages) sont marqués `"ajout": true` dans `valeurs.json`. Certaines valeurs ont des
synonymes pour la recherche (`"alternatifs"`) : « sans ordinateur » trouve les ressources débranchées, « QCM »
les évaluations. Ils ne s'affichent pas.

**Les notions** (`notions.json`, validé par l'enseignant le 13/11/2026) classent les ressources par ce
qu'elles font apprendre, plus finement que le programme : « boucle bornée », « recherche dichotomique »,
« routage », « complément à deux »… C'est un thésaurus, construit sur les normes du domaine (SKOS du W3C et
ISO 25964) :
- 177 notions rangées en 12 domaines (programmation, algorithmique, données, réseaux, Web, interaction
  homme-machine, architecture, sécurité, intelligence artificielle, enjeux, histoire, localisation), de la
  plus large à la plus précise : programmation › structures de contrôle › boucle › boucle bornée ;
- pour chacune, son libellé, ses synonymes (« répétition », « itération »), ses termes anglais (« for loop »),
  les mots du code (`for`, `range`), des fautes fréquentes pour la recherche (« algorythme »), les notions
  associées (boucle et parcours de tableau), une note d'une phrase, et les thèmes ou contenus du programme
  où elle est enseignée ;
- ses correspondances avec trois référentiels internationaux : le *K–12 Computer Science Framework* (2016),
  l'*Informatics Reference Framework for School* d'Informatics for All (2022) et les domaines de CS2023
  (ACM, IEEE-CS, AAAI) ;
- pour 36 notions, 57 **difficultés connues des élèves**, avec leur source : par exemple,
  croire qu'une variable garde plusieurs valeurs à la fois (43 % des 145 élèves de 7 à 17 ans interrogé·e·s
  par Swidan, Hermans et Smit, 2018), confondre Internet et le Web, ou ne pas savoir prévoir ce que fait un
  court programme en le suivant pas à pas (Lister et al., 2004). Les sources sont citées dans le fichier, avec
  leur adresse et leur date de lecture. Le constat de l'enseignant dans ses classes (la trace d'exécution, la
  modélisation d'un problème, la compréhension globale d'un programme) y figure comme un relevé, distinct des
  études ;
- un **historique** des versions : ce que chacune a ajouté ou modifié (la deuxième, T60, a ajouté 15 notions
  d'après le classement des 90 fiches : trace d'exécution, références et copies, jointures SQL, RIP et OSPF… ;
  la troisième, T64, inscrit la validation de l'enseignant et la compréhension globale d'un programme).

Une fiche cite ses notions en deux listes (décision du 13/11/2026) : les notions **travaillées** (ce qu'elle
fait apprendre, travailler ou évaluer) et les notions **prérequises** (ce qu'il faut savoir avant). Qu'une
ressource évalue se lit à son type pédagogique (évaluation, exerciseur) et à ses usages (auto-correctif), pas
à ses notions. Les deux listes correspondent aux propriétés que schema.org a reprises de LRMI pour les
ressources pédagogiques : `teaches` et `assesses` réunies, puis `competencyRequired` ; un export vers d'autres
plateformes restera possible. Les `mots_cles` libres restent.

---

## Pour les agents

### Les règles
- **Une fiche par ressource** : `donnees/ressources/<id>.json`, où `<id>` est l'identifiant de la fiche.
- **Identifiants** : minuscules, sans accents, mots séparés par des tirets (`td1-poo`). Stables : ils servent
  dans les adresses (`bibliotheque/?r=td1-poo`), la vitrine et les progressions.
- **Classements** : on écrit l'`id` d'une valeur des référentiels, jamais son libellé. Une valeur qui manque
  se demande dans le rapport ; les référentiels ne changent qu'après validation de l'enseignant.
- **Types** : une liste (`types`), au moins un, le principal en premier.
- **Usages** : « utilisable sur téléphone » est une modalité (`sur-telephone`) ; il n'y a pas de prérequis « téléphone ».
- **Compétences Pix** (facultatif, ressources de SNT) : `competences_pix`, identifiants de
  `referentiels/competences-pix.json` (les 16 compétences du cadre de référence, par exemple `programmer`).
  Les pages affichent les intitulés de la plateforme Pix, que voient les élèves.
- **Éditeur de code** (règle 20) : une ressource où l'élève écrit du code a l'usage `editeur-de-code`
  (filtrable) et le champ `editeur_code`, avec ses cinq critères toujours notés, `true` ou `false` :
  `coloration`, `indentation` (la touche Tab indente), `guides_indentation` (les blocs visibles, modèle :
  Lagon Arena), `autocompletion` (contextualisée), `erreurs_expliquees` (telles quelles, puis traduites
  ou expliquées en français), plus une `remarque` facultative. Ressource externe : on note ce qui lui
  manque, sans rien lui reprocher.
- **Page en ligne d'un TD** (règle 19, facultatif) : `td_en_ligne`, avec `responsive` et `auto_corrective`
  (`true` ou `false`) et une `remarque`. Le PDF et la page HTML se déduisent des documents.
- **Critères de réussite** (facultatif, au cas par cas) : `criteres_reussite`, du niveau 1 au plus exigeant.
- **Programme** : on cite un thème ou un contenu de `programmes.json`, le plus précis possible.
- **Notions** (facultatif, à remplir pour chaque fiche) : `"notions": { "travaillees": […], "prerequises": […] }`,
  avec des identifiants de `referentiels/notions.json` (`prog.boucle.bornee`). Citer la notion la plus précise :
  les notions plus larges s'en déduisent (« boucle bornée » range aussi la fiche sous « boucle » et « structures
  de contrôle »). Une notion travaillée n'est pas aussi prérequise. Un rôle sans notion ne s'écrit pas. Une
  notion qui manque se demande dans le rapport : le thésaurus ne change qu'après validation de l'enseignant.
  - Les anciens rôles `enseignees` et `evaluees` (avant le 13/11/2026) se convertissent avec
    `python3 scripts/convertir_notions_t64.py` (`--verifier` pour voir sans écrire) : `travaillees` réunit les deux,
    sans doublon et dans l'ordre ; une notion aussi prérequise reste dans `travaillees` et quitte `prerequises` ;
    seul le bloc `notions` des fiches est réécrit. Les fiches du dépôt sont converties depuis le 13/11/2026 : le
    validateur refuse les anciens rôles (`--anciens-roles signaler` les tolère sur une copie pas encore convertie).
- **Thésaurus** (`notions.json`) : un identifiant de notion ne change jamais (`prog.boucle.bornee`), même si la
  notion change de place ; une notion abandonnée reste, avec `"obsolete": true` et `"remplacee_par"`. On écrit
  seulement les notions plus larges (`plus_larges`), jamais les plus étroites, qui s'en déduisent ; une notion
  associée s'écrit d'un seul côté. Un libellé préféré est unique ; un libellé caché sert à une graphie que les
  autres libellés n'ont pas (fautes, termes déconseillés comme « crypter »).
  - Un terme trop précis pour devenir une notion devient un libellé alternatif de la notion plus large (ISO 25964 :
    « CIDR » pour les adresses IP, « tranche » pour les tableaux). Une démarche ou un format (jeu de rôle, activité
    débranchée, capture the flag, Grand oral) n'est pas une notion : c'est un type, un usage ou une section de la vitrine.
  - Un libellé contient au moins une lettre ou un chiffre (les symboles `//` ou `%` vont dans la note). Un mot courant
    ou ambigu (« reste », « saut ») ne devient pas un libellé : la recherche étendrait chaque requête qui le contient.
    Deux notions ne partagent pas un libellé, même au pluriel près : la recherche compare les racines des mots
    (« test » et « Tests » se confondaient).
  - Chaque version s'inscrit dans `historique` : sa date, sa tâche, un résumé, les notions ajoutées et modifiées.
    Une notion s'ajoute une seule fois ; une notion publiée n'est jamais retirée : `--avant` le vérifie.
- **Auteurs et licences** : ressource de l'enseignant → `{ "nom": "Babash - NSI Tani Malandi", "role": "auteur" }`,
  licence « CC BY-SA 4.0 » pour les documents, « MIT » pour le code des applications. Ressource externe → créditée à
  son site d'origine : `credits`, et dans `auteurs` la personne qui l'a faite, avec le site dans son rôle et un `lien`
  (« auteur (exomorphisme.fr, lycée de Sada) ») ; si on ne la connaît pas, un auteur au nom du site, rôle « site d'origine ».
- **Crédits en chaîne** (décision du 07/11) : une ressource reprise et modifiée crédite toute la chaîne de ses auteurs
  et autrices, dans l'ordre, dans `auteurs` comme dans `credits` : la personne qui l'a faite, ses sources, puis la
  reprise. Exemple, CyberCase : Etienne Clave (exomorphisme.fr, lycée de Sada), d'après une idée de Marion Dufour,
  avec le moteur SQL Noir de Hristo Bogoev (licence MIT), repris par Babash - NSI Tani Malandi (rôle « reprise »).
- **Documents** : `url` (lien direct) **ou** `fichier` (chemin depuis la racine du dépôt, par exemple
  `nsi-terminale/fichiers/td1-poo-premiers-pas.pdf`, ancre permise). Jamais de page GitHub, sauf pour le
  rôle `code-source`. Le `format` est déduit de l'adresse (règles dans `valeurs.json`) : ne l'écrire que pour
  corriger une déduction fausse.
- **`visible`** est obligatoire sur chaque document, avec ses deux réglages : rien n'est caché ou montré par oubli.
  La valeur de départ d'un nouveau document est celle du rôle (`visible_par_defaut` dans `valeurs.json`) :
  depuis la consigne de l'enseignant du 12/11/2026, `{ "exterieur": true, "eleve": true }` pour tous les rôles.
  Un agent ne cache rien : l'enseignant règle la visibilité dans l'admin.
- **`donnees_eleves`** est obligatoire : `{ "collecte": false }`, ou `{ "collecte": true, "detail": "…" }`.
  Ajouter `"facultative": true` quand l'élève peut s'en servir sans rien transmettre (CyberCase).
- **Vitrine** : une rubrique suit un programme (`"programme": "snt-2019"`) ou cite seulement un texte de
  référence (`"reference_officielle": "pp-2018"`), jamais les deux.
- **`dates`** sont remplies automatiquement ; **`notes`** sont réservées à l'enseignant (`[{ "date": "…", "texte": "…" }]`).
- Textes : français clair, et langage inclusif complet chaque fois que c'est pertinent : formulations épicènes,
  double flexion, féminisation des fonctions et point médian (« enseignant·e·s », « fort·e·s »), décision du 07/11.
  Les identifiants restent en ASCII, sans point médian (`pour-occuper-les-plus-forts`). Mise en forme permise :
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
| `cybercase` | ressource externe reprise, créditée en chaîne (auteur, idée originale, moteur, reprise), « à la une », placée en SNT et en NSI Tle, collecte facultative, aucun identifiant de démonstration |
| `td1-poo` | ressource interne : page HTML du site et sa version PDF ; `td_en_ligne` (règle 19), avec ce qui manque |
| `timeline-histoire-informatique` | placée en NSI 1re et en NSI Tle ; code source sur GitHub, en document secondaire |
| `alien-python` | collecte de données d'élèves (`donnees_eleves`, à titre d'information), crédits d'un tiers, espace professeur ; usage `editeur-de-code` et `editeur_code` (règle 20), avec ce qui manque |
| `fiche-variables-python` | fiche FichesNSI et sa version PDF, deux enseignements (SNT et NSI 1re) |
| `operation-mirage` | plusieurs types (TP et jeu) ; fiche professeur, outil associé et code source |

Ces fiches illustrent le format : leur contenu est repris par le Bibliothécaire. Depuis le 12/11/2026, leurs documents
sont tous visibles de tous ; l'enseignant cache lui-même ce qu'il veut dans l'admin.

### Vérifier

```
python3 scripts/valider_donnees.py                 les données de ce dépôt
python3 scripts/valider_donnees.py --racine DIR    une autre copie du dépôt
python3 scripts/valider_donnees.py --strict        les avertissements bloquent aussi
python3 scripts/valider_donnees.py --github        dans GitHub Actions : annotations et résumé du run
python3 scripts/valider_donnees.py --avant F      compare le thésaurus à une version précédente F (celle de main)
python3 scripts/valider_donnees.py --anciens-roles signaler  tolère les anciens rôles (copie pas encore convertie)
python3 scripts/convertir_notions_t64.py           convertit les notions des fiches vers « travaillees » (T64)
python3 -I -B scripts/tests/test_notions.py        les tests du validateur pour le thésaurus et les notions (57 cas)
```

Python 3 standard, sans dépendance (le module `jsonschema`, s'il est installé, sert de contrôle supplémentaire).
Chaque message donne le fichier et le champ. Trois niveaux : **ERREUR** (à corriger, code de retour 1),
**ATTENTION** (à regarder), **INFO** (pour information : documents cachés, collecte de données, intitulés à vérifier).

Le même contrôle tourne dans GitHub Actions à chaque envoi, sur toutes les branches : job « Données de la
bibliothèque » de `.github/workflows/verifier.yml`. Une erreur le fait échouer (croix rouge). Les avertissements
et les informations sont dans le résumé du run, sans échec ; erreurs et avertissements apparaissent aussi en
annotations sur les fichiers.

Ce qui est vérifié :
- JSON valide et conforme aux schémas ; identifiants uniques ; chaque fiche nommée `<id>.json` ;
- références existantes : valeurs des référentiels, thèmes et contenus, fiches liées, fichiers du dépôt ;
- cohérence : l'enseignement d'un contenu cité figure dans `enseignements` (son niveau dans `niveaux`, sinon avertissement) ;
- exactement un document principal ; aucune page GitHub hors du rôle `code-source` ;
- visibilité : ce que voit chaque public, remplacement du document principal caché (un document caché est une simple
  information ; un corrigé ou un guide visible des élèves n'est plus signalé, depuis la consigne du 12/11/2026) ;
- notions : chaque identifiant cité dans `notions` existe dans le thésaurus ; une notion obsolète, ou à la fois travaillée et
  prérequise, donne un avertissement ; les anciens rôles `enseignees` et `evaluees` sont refusés (seulement signalés avec
  `--anciens-roles signaler`, sauf dans une fiche qui a déjà `travaillees`) ; le nombre de fiches sans notions est donné
  pour information ;
- thésaurus (`notions.json`) : notions plus larges, associées et remplaçantes existantes ; hiérarchie sans cycle ; domaines ;
  libellé préféré unique ; dans une même langue, chaque libellé d'une notion écrit une seule fois ; libellé caché distinct des
  autres ; libellé sans lettre ni chiffre refusé ; homographes entre notions (y compris ceux que la recherche confond, de mêmes
  racines) et notion associée sur sa propre branche signalés ; thèmes et contenus du programme, référentiels externes et sources
  cités existants ; historique : dates dans l'ordre et jusqu'à la version, notions existantes, ajoutées une seule fois et
  modifiées après leur ajout ; synonymes des valeurs (`alternatifs`) sans répétition ;
- avec `--avant F` (le thésaurus de `main`, par exemple : `git show origin/main:donnees/referentiels/notions.json > F`) :
  une notion de F qui a disparu est une erreur (un identifiant publié est définitif) ; les libellés changés, les notions
  déplacées ou devenues obsolètes et les notions nouvelles sont donnés pour la relecture ; une notion nouvelle absente de
  l'historique donne un avertissement. Le job « Données de la bibliothèque » le fait à chaque envoi, contre `main` ;
  limite : une branche en retard sur `main` y échoue si `main` a reçu des notions depuis (elles manquent à la branche) :
  la rebaser sur `main` le règle ;
- règle 19 de la philosophie éducative : un TD de l'enseignant sans version PDF ou sans page HTML donne un avertissement,
  de même qu'un critère à `false` dans `td_en_ligne` ;
- règle 20 : pour une création de l'enseignant, l'usage `editeur-de-code` sans `editeur_code`, ou un critère à `false`,
  donne un avertissement ; pour une ressource externe, une simple information. `editeur_code` sans l'usage donne aussi
  un avertissement. Les critères de `valeurs.json` et du schéma doivent concorder ;
- licences et auteurs : une création de l'enseignant sans l'auteur « Babash - NSI Tani Malandi », sans licence ou sous une
  autre licence que CC BY-SA 4.0 ou MIT, et une ressource externe sans crédit, donnent un avertissement ;
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
- Compétences Pix : cadre de référence des compétences numériques, annexe du décret n° 2019-919 du
  30 août 2019 (BO n° 37 du 10 octobre 2019 et JO du 1er septembre 2019), revérifié mot pour mot le 07/11/2026,
  et fiche RS6894 du certificat Pix (France Compétences). Les intitulés affichés sont ceux de Pix (décision du
  07/11/2026) ; deux diffèrent du décret, dont le texte est gardé dans `libelle_decret` : « Création de contenu »
  (« de contenus ») et « Construire un environnement numérique » (« Évoluer dans… »). Sources citées dans
  `competences-pix.json`.
- PP : circulaire n° 2018-108 du 10 octobre 2018 (BO n° 37 du 11 octobre 2018), partie « I. Leurs missions » ;
  un intitulé est marqué `a_verifier`. Elle sert de référence et ne structure pas la rubrique.

### Sources du thésaurus des notions
Elles sont citées dans `referentiels/notions.json` (champ `sources`), chacune avec son adresse et sa date de lecture
(12/11/2026). En résumé :
- le modèle : SKOS (recommandation du W3C du 18 août 2009) et ISO 25964-1:2011 (thésaurus, confirmée en 2022) ;
  pour les rôles des notions dans une fiche, les propriétés `teaches`, `assesses` et `competencyRequired` de
  schema.org, issues de LRMI (valeurs `teaches`, `assesses`, `requires` de LRMI 1.1) : `travaillees` réunit les deux
  premières, `prerequises` correspond à la troisième ;
- les correspondances : *K–12 Computer Science Framework* (2016, cinq concepts et leurs sous-concepts),
  *Informatics Reference Framework for School* (Informatics for All, février 2022, onze domaines), CS2023
  (ACM, IEEE-CS, AAAI, rapport final de janvier 2024, 17 domaines de connaissances et leurs unités) ;
- les difficultés des élèves : recherches publiées (Qian et Lehman, 2017 ; Sorva, 2013 ; Swidan, Hermans et
  Smit, 2018 ; Grover et Basu, 2017 ; Duran, Sorva et Seppälä, 2021 ; Sanders, Galpin et Götschi, 2006 ;
  Holland, Griffiths et Woodman, 1997 ; et depuis T60 : Lister et al., 2004, et Lopez, Whalley, Robbins et
  Lister, 2008, pour la trace d'exécution ; Ma, Ferguson, Roper et Wood, 2011, pour les références ; Ragonis et
  Ben-Ari, 2005, pour la programmation objet au lycée ; Miedema, Aivaloglou et Fletcher, 2021, pour SQL ; et depuis
  T64 : Lister, Simon, Thompson, Whalley et Prasad, 2006, pour la compréhension globale d'un programme), la thèse
  de Qian (2018) pour les travaux qu'elle cite, une synthèse de la Raspberry Pi Foundation (2023), un relevé
  d'enseignant·e·s de Computing at School (2016-2021) et le constat de l'enseignant du 13/11/2026, signalés comme
  tels (`"nature": "releve-enseignants"`).
  Quand seuls la notice et le résumé ont été lus, le champ `lu` le dit ;
- les correspondances des notions de T60 avec CS2023 ont été relevées dans le rapport final (unités SDF-Fundamentals,
  NC-Fundamentals, NC-Reliability, OS-Concurrency) ; une notion sans correspondance propre hérite de celles de ses
  notions plus larges ;
- ScoLOMFR (profil français de LOM) : ses vocabulaires (types pédagogiques, niveaux) n'ont pas pu être lus depuis
  la session (Éduscol et data.education.fr inaccessibles) ; l'alignement de `valeurs.json` par `closeMatch` reste
  à faire, sans inventer d'identifiant. Les concepts de ScoLOMFR ont des adresses de la forme
  `http://data.education.fr/voc/scolomfr/concept/scolomfr-voc-…`.
