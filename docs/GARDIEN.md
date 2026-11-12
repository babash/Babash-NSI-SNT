# Les outils du Gardien

*Les contrôles avant et après chaque publication, les outils du dossier `.github/gardien/` et leurs tests. Les règles qu'ils vérifient sont dans [CONTRIBUTING.md](../CONTRIBUTING.md) ; la liste de contrôle complète, dans la fiche du Gardien (`.claude/agents/gardien.md`). Retour au [README](../README.md).*

Avant chaque publication, le Gardien pré-valide la branche avec ses outils, rangés dans
`.github/gardien/` : `python3 -I .github/gardien/controler.py --branche origin/<branche>`
vérifie que la branche part du dernier `main`, puis contrôle les données sensibles, les liens
internes, le rendu avant et après (320, 768 et 1440 px, clair et obscur), les contrastes, la
navigation au clavier et l'impression A4 des documents touchés ; il lance aussi le contrôle
des pages de [la vérification automatique](VERIFICATION.md). La conformité, elle, se vérifie à la lecture : cahier des charges,
décisions de l'enseignant et règles de conception (voir [L'équipe d'agents](AGENTS.md)). Il vérifie de
même les liens vers les dépôts (voir [la règle des liens](LISTES.md#la-règle-des-liens)) : chaque ressource que la branche
ajoute ou modifie et qui a un dépôt le donne en « Code source », et chaque page touchée porte en
pied de page le lien « Code source sur GitHub » ; si l'un de ces liens manque, il est ajouté
dans une branche de suite, sans bloquer la publication. Après la publication,
`bash .github/gardien/attendre_actions.sh <commit>` suit la mise en ligne et lit les résultats
des contrôles automatiques. Il faut Python avec Playwright et Pillow, Chrome ou Chromium, et
l'outil `gh` de GitHub pour suivre la mise en ligne.

D'autres outils du même dossier servent au cas par cas. Pour le site :

- `caracteres.py` relève, dans les lignes qu'ajoute une branche, les caractères invisibles et
  les points qui imitent le point médian (le vrai point médian, lui, est permis) ;
- `zones.py` situe les différences de rendu entre avant et après, pour vérifier par exemple
  qu'un changement se limite au pied de page ; `contraste_zone.py` donne le contraste le plus
  faible d'une zone de la page, le pied de page par défaut ;
- `texte_rendu.py` montre les textes et les liens affichés qu'une branche ajoute ou retire,
  page par page, sans lire le code ;
- `annexes_code_source.py` liste les ressources qui ont un dépôt sans le donner en
  « Code source » ; `chemins_readme.py` vérifie que les chemins cités dans un README existent.

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
accepte le point médian dans les textes, que les scripts du contrôle en ligne décident juste,
que le pied de page suit ses réglages et porte le lien « Code source sur GitHub », que l'encadré
d'erreur nomme sa cause, et que les outils du Gardien eux-mêmes trouvent ce qu'ils doivent
trouver. Chaque outil se lance avec `python3 -I` (ou `bash`) ; son en-tête et `--help` en
décrivent l'usage.
