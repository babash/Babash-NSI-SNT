# Les outils du Gardien

*Les contrôles avant et après chaque publication, les outils du dossier `.github/gardien/` et leurs tests. Les règles qu'ils vérifient sont dans [CONTRIBUTING.md](../CONTRIBUTING.md) ; la liste de contrôle complète, dans la fiche du Gardien (`.claude/agents/gardien.md`). Retour au [README](../README.md).*

Avant chaque publication, le Gardien pré-valide la branche avec ses outils, rangés dans
`.github/gardien/` : `python3 -I .github/gardien/controler.py --branche origin/<branche>`
vérifie que la branche part du dernier `main`, construit la bibliothèque dans les copies avant et
après (comme « Publier le site »), puis contrôle les données sensibles (une adresse
électronique est reconnue même écrite sous une forme masquée pour les robots, avec « [point] »,
« (at) » ou « [sur] » ; un code de classe, trois capitales ou chiffres, un tiret et trois autres,
est signalé, et sa valeur masquée dans le rapport), les liens internes, le rendu avant et après de l'accueil, des rubriques et de
la bibliothèque (320, 768 et 1440 px, clair et obscur), les contrastes (mesurés sur la partie affichée
de chaque texte), la
navigation au clavier et l'impression A4 des documents touchés. Depuis la bascule des rubriques vers
la vitrine (T51b), ses outils comptent les ressources attendues d'après la vitrine et les fiches, et
lisent les liens dans les documents des fiches (ils lisent encore les anciennes listes `ressources.js`
pour une version du site d'avant la bascule) ; il lance aussi le contrôle
des pages de [la vérification automatique](VERIFICATION.md). La conformité, elle, se vérifie à la lecture : cahier des charges,
décisions de l'enseignant et règles de conception (voir [L'équipe d'agents](AGENTS.md)). Il vérifie de
même les liens vers les dépôts (voir [la règle des liens](LISTES.md#la-règle-des-liens)) : chaque ressource que la branche
ajoute ou modifie et qui a un dépôt le donne en « Code source », et chaque page touchée porte en
pied de page le lien « Code source sur GitHub » ; si l'un de ces liens manque, il est ajouté
dans une branche de suite, sans bloquer la publication. Après la publication,
`bash .github/gardien/attendre_actions.sh <commit>` suit la mise en ligne (« Publier le site »,
dont le job « Mettre en ligne » doit être vert et non sauté) et lit les résultats des contrôles
automatiques, dont celui de la bibliothèque en ligne. Il faut Python avec Playwright et Pillow, Chrome ou Chromium, et
l'outil `gh` de GitHub pour suivre la mise en ligne.

D'autres outils du même dossier servent au cas par cas. Pour le site :

- `caracteres.py` relève, dans les lignes qu'ajoute une branche, les caractères invisibles et
  les points qui imitent le point médian (le vrai point médian, lui, est permis) ; il ignore les
  fichiers binaires, car git lit parfois un PDF comme du texte, et les octets de ses flux compressés
  passeraient pour des caractères invisibles ;
- pour les TD en ligne (style « Signal pirate »), en plus de `charte/verifier-td.py` (qui exécute aussi les tests cachés),
  de `charte/imprimer-td.py`, de `charte/tester-outils.py` (les outils doivent voir une correction, une sortie attendue ou un
  coup de pouce imprimés sur des témoins) et de `charte/numeroter-feuilles.py --tout --verifier` (numéros des feuilles 2, 3…) ;
  jusqu'à la passe finale des TD, un PDF publié n'est plus identique à la feuille régénérée par le moteur (pied, réponses
  courtes, code de départ, numéros) : on le compare au PDF régénéré avec le moteur d'avant le 21 novembre au soir, ou on
  contrôle le fond seul (réponses, questions, pages) ; `bandeau_td.py` mesure le bandeau d'une page à seize largeurs d'écran et
  sur papier (rien de coupé, rien de recouvert) ; `qcu_forme.py` dit si la bonne option d'un choix
  unique se repère à sa forme, la consigne étant qu'elle ne le soit jamais : un TD est à revoir quand
  elle est nettement la plus longue (10 % de plus que chacune des autres) dans au moins la moitié de
  ses QCU, et l'outil signale aussi, à relire, une bonne option seule avec du code, du gras ou un
  point final, ou au premier mot à part ;
- `td_papier.py` (T124) cherche dans la source d'un TD ce qui ferait voir une réponse, à l'écran
  ou sur papier, sans qu'elle soit un texte caché (que cherchent `imprimer-td.py` et le contrôle des
  PDF) : une balise de question cassée (un attribut inséré dans la valeur d'un autre, dont la fin
  s'affiche alors en clair), une variante papier qui recopie un code à compléter avec ses réponses
  (`[[…]]`), une réponse attendue ou des options dans une question papier ;
- `zones.py` situe les différences de rendu entre avant et après, pour vérifier par exemple
  qu'un changement se limite au pied de page ; `contraste_zone.py` donne le contraste le plus
  faible d'une zone de la page, le pied de page par défaut ;
- `texte_rendu.py` montre les textes et les liens affichés qu'une branche ajoute ou retire,
  page par page, sans lire le code ;
- `annexes_code_source.py` liste les fiches qui ont un dépôt sans le donner en
  « Code source » ; `chemins_readme.py` vérifie que les chemins cités dans un README existent.

Les dépôts de l'enseignant sont renommés sans redirection depuis le 21 novembre 2026 (T100) : le
validateur refuse, dans les fiches et la vitrine, l'ancienne adresse d'un dépôt inscrit dans
`scripts/depots-renommes/`. Pour les autres fichiers d'une branche écrite avant un renommage (pages,
scripts, documentation), le Gardien lance, sur un essai de fusion avec `main` et sur `main`,
`python3 -I scripts/renommer_depots.py <copie> --site --audit` (la copie est une copie Git, par
exemple un `git worktree`), qui liste chaque ligne où reste
un ancien nom (adresse ou nom affiché), et compare les deux listes sans les numéros de ligne : une
adresse ajoutée qui cite l'ancien nom d'un dépôt déjà renommé est à corriger avant la
publication. À l'inverse, une adresse au nouveau nom d'un dépôt pas encore renommé ne répond pas
encore (sauf quand seule la casse change, car GitHub l'ignore) : la branche attend ce renommage.

Pour les autres dépôts de l'enseignant (applications, mini-sites des TD, diaporamas) :

- `pages_depot.py` compare les pages avant et après une branche : erreurs JavaScript,
  débordement, lien « Code source sur GitHub » (adresse, contraste, accès au clavier),
  contrastes et impression A4 ; seul ce qui est nouveau est une alerte. Il fonctionne sans
  réseau : les bibliothèques des CDN sont servies depuis leurs paquets, et Supabase est remplacé
  par un faux client, qui ne lit ni n'écrit aucune donnée ;
- `diapo_dessous.py` vérifie que le pied de page d'un diaporama reveal.js ne cache ni contenu ni
  commande, sur chaque diapositive ;
- `pdf_comparer.py` compare deux versions d'un PDF : pages, mots perdus ou nouveaux, et la
  mention de l'auteur et de la licence sur chaque page ;
- `empreintes_migration.py` vérifie qu'une migration Supabase commence par `begin;` et finit
  par `commit;`, et calcule l'empreinte qui montre que le fichier du dépôt est bien celui qui a
  été appliqué à la base (en ne lisant que des métadonnées) ;
- `depots.sh` suit la mise en ligne de ces dépôts et dit si une branche est déjà contenue dans
  leur `main`.

Les tests de non-régression du Gardien se lancent d'un coup :
`python3 -I .github/gardien/tests/lancer.py --ref origin/<branche>`. Ils vérifient notamment que
la validation des données détecte toujours les fautes graves, applique les règles 19 et 20 et
accepte le point médian dans les textes, que les scripts du contrôle en ligne décident juste (le contrôle complet construit d'abord la
bibliothèque dans chaque copie, comme « Publier le site »),
que le pied de page suit ses réglages et porte le lien « Code source sur GitHub », que l'encadré
d'erreur nomme sa cause, et que les outils du Gardien eux-mêmes trouvent ce qu'ils doivent
trouver. Chaque outil se lance avec `python3 -I` (ou `bash`) ; son en-tête et `--help` en
décrivent l'usage.
