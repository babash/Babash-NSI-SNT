# Des listes actuelles au nouveau format : la correspondance

Ce document dit comment chaque champ et chaque étiquette des listes actuelles (`snt/ressources.js`,
`nsi-premiere/ressources.js`, `nsi-terminale/ressources.js`, `pp/ressources.js`, `autres/ressources.js`)
passera dans les fiches (`donnees/ressources/<id>.json`) et dans la vitrine (`donnees/vitrine.json`).

**Statut : validé par l'enseignant le 07/11/2026 (tâche T02), décisions intégrées.** La conversion
elle-même est la tâche suivante : rien n'est converti ici, en dehors des 6 fiches d'exemple.

## 1. En chiffres

- **89 entrées** dans les 5 listes, pour **82 ressources distinctes** : 7 ressources sont placées à deux endroits.
  Chacune deviendra **une seule fiche**, placée deux fois dans la vitrine.

  | Ressource | Placée en |
  |---|---|
  | Fiche : les variables et opérateurs en Python | SNT (Affectations, variables) et NSI 1re (Constructions élémentaires) |
  | Fiche : les structures de contrôle en Python | SNT (Instructions conditionnelles) et NSI 1re (Constructions élémentaires) |
  | CyberCase | SNT (Données structurées) et NSI Tle (Langage SQL) |
  | Timeline de l'histoire de l'informatique | NSI 1re et NSI Tle (Événements clés) |
  | Opération MIRAGE | NSI 1re (Systèmes d'exploitation) et NSI Tle (Gestion des processus) |
  | Éduscol : sciences du numérique | NSI 1re et NSI Tle (Sites ressources) |
  | CodEx | NSI 1re (S'entraîner en autonomie) et NSI Tle (Sites ressources) |

- Quand les deux textes diffèrent (CyberCase, Timeline, MIRAGE, structures de contrôle, CodEx, Éduscol),
  on garde le plus complet et on y ajoute les phrases propres à un niveau (« en seconde, les premières
  affaires suffisent »). Les annexes des deux entrées sont réunies (Éduscol : programme de première
  **et** programme de terminale).

## 2. Les champs d'une ressource

| Aujourd'hui | Demain | Comment |
|---|---|---|
| `titre` | `titre` | tel quel |
| — | `id` | tiré du titre : minuscules, sans accents, mots utiles reliés par des tirets, 40 caractères au plus (« POO, TD 1 : premiers pas en objets » → `td1-poo`). Le Bibliothécaire peut l'ajuster avant publication ; ensuite il ne change plus. |
| `lien` | le **document principal** (`documents`, `"principal": true`) | une adresse va dans `url` ; un fichier `fichiers/x.pdf` va dans `fichier`, complété par le dossier de la rubrique (`nsi-terminale/fichiers/x.pdf`). Rôle : `enonce` pour une activité, `page` pour un site ou une fiche, `diaporama`, `version-eleve`… Visible de l'extérieur et des élèves. |
| `texte` | `presentation` | tel quel, avec la même mise en forme (`code`, **gras**, retours à la ligne) |
| — | `resume` | la première phrase de `texte`, à reprendre par le Bibliothécaire |
| — | `accroche`, `objectif`, `duree`, `mots_cles`, `liees` | à écrire par le Bibliothécaire (souvent déjà dans `texte` : durée) |
| — | `auteurs`, `licence`, `credits` | ressource de l'enseignant (origine `ma-creation`) : auteur « Babash - NSI Tani Malandi », licence CC BY-SA pour les documents, MIT pour le code des applications. Ressource externe : créditée à son site d'origine (`credits`, et `auteurs` avec le rôle « site d'origine »). |
| `tags` | `usages`, `langages`, `types`, `niveaux`, vitrine | voir § 3 |
| `annexes` | les autres `documents` | voir § 4 |
| la rubrique (le fichier) | `enseignements` et `niveaux` | `snt` → SNT, seconde ; `nsi-premiere` → NSI, première ; `nsi-terminale` → NSI, terminale ; `pp` → PP, niveau selon la ressource ; `autres` → transversal (ou SNT, NSI), niveaux selon la ressource |
| `theme(…)` et `groupe(…)` | `programme` de la fiche, et la place dans la vitrine | voir § 5 |
| l'ordre dans le fichier | l'ordre des listes de la vitrine | tel quel : la vitrine reprend exactement l'affichage actuel |
| `// À compléter` | `statut` : `a-revoir` | toutes les fiches converties partent en `a-revoir` ; elles passent en `prete` après relecture |
| — | `donnees_eleves` | « non » par défaut, **sauf** les ressources connues pour collecter des données (SNT 1er jour, Alien Python, Lagon Arena, Expédition Gombessa, CyberCase…). Quand l'élève peut s'en servir sans rien transmettre (CyberCase : le compte sert seulement à garder l'avancement), on ajoute `"facultative": true`. Toute ressource avec un espace professeur, un tableau de bord, un compte ou une connexion ENT est listée pour vérification. |
| — | `dates.ajout` | la date de la conversion |

## 3. Les étiquettes (`tags`)

| Étiquette (nombre) | Devient |
|---|---|
| En ligne (45) | usage `en-ligne` |
| Python (40) | langage `python` |
| À imprimer (27) | usage `a-imprimer` |
| Jeu (7) | ajoute le type `jeu` |
| Débranché (6) | usage `debranche` ; et ajoute le type `activite-debranchee` quand c'est une activité |
| Pour aller plus loin (6) | usage `pour-aller-plus-loin` (ajout validé le 07/11) |
| Rien à installer (4) | rien à écrire : c'est l'absence du prérequis `installation`, que l'affichage peut signaler |
| Connexion ENT (4) | usage (prérequis) `compte-ent` |
| SQL (4) | langage `sql` |
| À adapter (2) | usage (prérequis) `a-adapter` (ajout validé le 07/11), l'explication restant dans la présentation |
| Ressource du mois (2) | sort de la fiche : la ressource va dans `a_la_une` de la vitrine, avec l'étiquette « Ressource du mois » |
| Cours (1) | ajoute le type `cours` |
| Notebook (1) | rien à écrire : le format « notebook » est déduit de l'adresse |
| Terminale (1) | niveau `terminale` |

Une ressource a **un ou plusieurs types** (`types`, au moins un, le principal en premier : décision du
07/11). Les étiquettes en ajoutent ; quand aucune ne le donne, le Bibliothécaire choisit. Par défaut :
« Sites ressources » → `site-ressource`, « S'entraîner en autonomie » → `exerciseur`, « Concours et défis » →
`concours`, « Se former et échanger » → `formation`, « Outils pour la classe » → `outil-classe`, fiches
« Fiche : … » → `fiche`. Une ressource étiquetée à la fois « Jeu » et « Débranché » qui est une activité reçoit
les types `jeu` et `activite-debranchee`, et l'usage `debranche`.

## 4. Les annexes et leur rôle

Chaque annexe devient un document : son libellé actuel devient `titre`, son lien `url` ou `fichier`.

| Libellé actuel (nombre) | Rôle |
|---|---|
| Version PDF (16) | `version-pdf` |
| Code source (5), Code source et générateur de cartes (2), Code source, à dupliquer (1), Sources LaTeX (1), Installer sa propre base (Supabase) (1) | `code-source` |
| Espace enseignant (2), Tableau de bord du professeur (1), Essayer en mode démo (1) | `espace-professeur` |
| Fiche professeur (2), Guide de l'activité (1), Guide pédagogique (1) | `guide-professeur` |
| Fiches processus, activité 1, 2 et 3 | `version-eleve` |
| Notebook à télécharger (.ipynb) | `enonce` |
| Données des pokémons (JSON) | `donnees` |
| Les vidéos « Comprendre l'informatique en jouant », Chaîne YouTube « Python au lycée » | `video` |
| Terminal JSLinux (2) | `outil` |
| Programme de première (PDF), Programme de terminale (PDF), Tome 2, Banque d'exercices d'origine (M. Degrange), Licence, Version Quizizz (compte enseignant), VisuAlgo, autre visualisation, Découvrez le fonctionnement des algorithmes, Wiki Capytale, Bibliothèque partagée entre enseignants, Auto-évaluation des notebooks, Se préparer avec Pyxel (cahier numérique), S'entraîner : Challenges Kids, S'entraîner : Root Me | `complement` |

Les rôles `page`, `espace-professeur`, `outil` et `complement` sont des ajouts au cahier, validés le 07/11.

**Visibilité au départ** (validée le 07/11, et inscrite pour chaque rôle dans `valeurs.json`,
champ `visible_par_defaut`) : tout ce qui est affiché aujourd'hui reste visible de l'extérieur. Pour les
élèves, tout est visible **sauf** les rôles `espace-professeur`, `guide-professeur`, `corrige` et
`code-source`. Les corrigés sont donc visibles de l'extérieur, pour les collègues : l'enseignant accepte que
des élèves puissent les y trouver. Il change ensuite ce qu'il veut dans l'admin.

**Liens GitHub** : aucun lien principal actuel ne pointe vers GitHub. Les annexes vers github.com sont
toutes des codes source (rôle `code-source`, seul autorisé). Les liens `raw.githubusercontent.com`
(notebook et données du Pokédex) sont des liens directs vers un fichier : ils restent permis.

## 5. Rubriques, thèmes et groupes

**La rubrique** (`rubrique({ … })`) :
- `nom`, `court`, `niveau`, `couleur`, `presentation` → la rubrique dans la vitrine (`titre`, `court`, `niveau`, `couleur`, `presentation`) ;
- `programme: { texte, lien }` → `texte_officiel` du programme dans `referentiels/programmes.json` (déjà repris) ;
  la rubrique de la vitrine cite seulement l'identifiant du programme (`"programme": "snt-2019"`).

**Un thème ou un groupe qui suit le BO** :
- `theme("Structures de données", { programme: […] })` → une section de la vitrine `{ "programme": "nsi-tle-2019.structures-de-donnees" }` ;
  la liste `programme: […]` est déjà dans `programmes.json` ; `court` y est aussi.
- `groupe("Arbres")` sous ce thème → une sous-section `{ "programme": "nsi-tle-2019.structures-de-donnees.arbres" }`.
- La fiche reçoit l'identifiant le plus précis : le contenu si la ressource est sous un groupe du BO,
  sinon le thème.
- `couleur` du thème → `couleur` de la section.

**Les thèmes et groupes hors programme** deviennent des sections (ou sous-sections) libres de la vitrine,
avec un identifiant et un titre :

| Rubrique | Thème ou groupe actuel | Section libre (`id`) | Sur les fiches concernées |
|---|---|---|---|
| SNT | Première séance | `premiere-seance` | — |
| SNT | Pour occuper les plus fort·e·s (groupe) | `pour-les-plus-rapides`, titre « Pour les élèves les plus rapides » (sans point médian, tâche T07 à valider) | usage `pour-aller-plus-loin` |
| SNT | Bureautique | `bureautique` | — |
| SNT | Sites ressources | `sites-ressources` | type `site-ressource` |
| SNT | Informatique sans ordinateur (groupe) | `informatique-sans-ordinateur` | usage `debranche` |
| SNT | Vulgarisation (groupe) | `vulgarisation` | — |
| NSI 1re | Projets | `projets` | — |
| NSI 1re | Sites ressources, et ses groupes Cours en ligne, S'entraîner en autonomie | `sites-ressources`, `cours-en-ligne`, `s-entrainer-en-autonomie` | type `site-ressource` ou `exerciseur` |
| NSI Tle | Rentrée : reprendre la première | `rentree` | `programme` : les contenus de première revus ; `niveaux` : terminale (le script l'accepte, avec un avertissement) |
| NSI Tle | Préparer le bac, et ses groupes Épreuve écrite, Épreuve pratique, Grand oral | `preparer-le-bac`, `epreuve-ecrite`, `epreuve-pratique`, `grand-oral` | type `evaluation` pour les sujets |
| NSI Tle | Sites ressources | `sites-ressources` | type `site-ressource` |
| PP | Coordination de l'équipe et conseils de classe (court : Conseils de classe) | `conseils-de-classe` | — |
| PP | Suivi des élèves | `suivi-des-eleves` | — |
| PP | Orientation, et ses trois sous-titres (Seconde, Première, Terminale) | `orientation`, `orientation-seconde`, `orientation-premiere`, `orientation-terminale` | niveaux selon la classe concernée |
| PP | Lien avec les familles (court : Familles) | `familles` | — |
| PP | Vie de classe | `vie-de-classe` | — |
| PP | Textes officiels | `textes-officiels` | — |
| Autres | Outils pour la classe | `outils` | type `outil-classe` |
| Autres | Concours et défis | `concours` | type `concours` |
| Autres | Se former et échanger | `se-former` | type `formation` |

**Professeur principal** (décision du 07/11) : la rubrique garde ses thèmes actuels, qui deviennent les
sections libres du tableau ci-dessus. La circulaire n° 2018-108 reste dans `programmes.json` comme
référence : la rubrique la cite avec `"reference_officielle": "pp-2018"` (affichée sous la présentation),
sans que ses missions structurent les sections. Une fiche de PP peut citer une mission ou un volet dans
`programme` si c'est utile ; la conversion laisse ce champ vide.

## 6. Le reste

- **`reglages.js`** : le titre, la phrase de présentation et le dépôt restent pour l'instant dans `reglages.js`.
  L'ordre des rubriques passe dans la vitrine (ordre de `rubriques`), pour n'avoir qu'une seule source.
  À trancher quand les pages seront branchées sur les données.
- **Point médian** : deux libellés actuels en contiennent. « Pour occuper les plus fort·e·s » (voir T07) et
  « Forum des enseignant·e·s NSI » (Autres), qui deviendra « Forum des enseignantes et enseignants de NSI ».
- **Les listes `*/ressources.js`** restent en place et le site actuel continue de les lire tant que les pages
  ne sont pas branchées sur les données (cahier des charges, § 5). Elles seront retirées ensuite.
