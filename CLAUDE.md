# Ressources NSI et SNT : règles communes des agents

Ce fichier s'applique à **toute session Claude qui travaille dans ce dépôt**. Les fiches de rôle sont dans `.claude/agents/`.

## Le contexte
- Site publié par GitHub Pages : https://babash.github.io/Babash-NSI-SNT/ (dépôt public `babash/Babash-NSI-SNT`).
- Une refonte est en cours : une bibliothèque unique de ressources et trois parties (extérieur, admin, élève). La référence est le cahier des charges, dans le projet claude.ai « Site SNT-NSI ».
- Documents du projet à lire **avant tout travail** (outil Projects) :
  - `coordination/cahier-des-charges.md` : ce qu'on construit ;
  - `coordination/organisation-des-agents.md` : qui fait quoi ;
  - `coordination/decisions.md` : ce que l'enseignant a décidé ; la décision la plus récente l'emporte ;
  - `coordination/taches.md` : le tableau des tâches ;
  - `design/charte.md` : la charte graphique ;
  - `claude/etat-du-site.md` : l'état laissé par l'ancienne collecte.

## L'organisation
- **Le chef d'orchestre** est le seul interlocuteur de l'enseignant. Il lance les agents, leur écrit et reçoit leurs rapports. Un agent ne pose pas de question à l'enseignant : il la met dans son rapport.
- **Chaque agent ne modifie que les fichiers de son rôle** (voir sa fiche). Pour un autre fichier, il le signale dans son rapport.
- **Le Gardien est le seul à publier sur `main`.**

## Les règles Git
- Une branche par tâche, partant de `origin/main` à jour. Préfixes : `biblio/`, `archi/`, `design/`, `atelier/`, `orga/`.
  Exemple : `archi/t02-format-donnees`.
- Avant de commencer et avant de pousser : `git fetch origin`, puis `git rebase origin/main` si `main` a avancé.
- Messages de commit : `[T02][archi] Format des données : schéma et référentiels`.
- Auteur des commits : `git config user.name Claude` et `git config user.email noreply@anthropic.com`.
- **Jamais d'envoi forcé** sur `main`. Sur sa propre branche, seulement `--force-with-lease`.
- **Pousser sa branche avant de rendre son rapport** : les espaces de travail sont effacés après un temps d'inactivité.
- Ne jamais supprimer une branche qui n'est pas la sienne.

## Les règles de contenu
- **Le lien principal** d'une ressource pointe directement vers elle (page, fiche, PDF), jamais vers une page GitHub. Le dépôt peut apparaître en document « code source ».
- **Aucune donnée sensible dans le dépôt**, qui est public : ni mot de passe, ni identifiant (par exemple ceux de démonstration de CyberCase), ni clé secrète, ni nom d'élève. Une clé Supabase « anon » ou « publishable » est publique par conception ; une clé « service_role » ou « secret », jamais.
- **Toute ressource qui collecte des données d'élèves** est signalée (`donnees_eleves`) et soumise à l'enseignant.
- **La structure suit les textes officiels** : programmes de SNT et de NSI de 2019, circulaire PP n° 2018-108. Tout écart est soumis à l'enseignant.
- **Écriture** : français clair, formulations épicènes et double flexion, **pas de point médian**.
- **Design** : la charte « Réseau la nuit » (`design/charte.md`, branche `design/charte-v1` tant qu'elle n'est pas validée). Dessin original : aucun personnage, logo ou illustration d'Android: Netrunner.

## Vérifier
- `babash.github.io` est inaccessible depuis les sessions. Pour vérifier le site en ligne, on passe par GitHub Actions : le workflow `.github/workflows/verifier.yml` contrôle les liens et le rendu des pages en ligne, et on lit ses résultats avec `gh api repos/babash/Babash-NSI-SNT/actions/runs` (puis les jobs et les logs).
- En local : `python3 -m http.server` à la racine, puis Playwright (Chromium est préinstallé) pour le rendu à 320, 768 et 1440 px, en clair et en obscur.
- Le README est mis à jour à chaque publication.

## Le rapport de fin de tâche
Chaque agent termine par un rapport au chef d'orchestre, dans cet ordre :
1. **Fait** : ce qui a été fait, en quelques lignes.
2. **Branche** : son nom et le dernier commit poussé.
3. **À valider par l'enseignant** : les choix structurels, avec les options.
4. **Questions** : ce qui bloque ou reste incertain.
5. **Hors de mon domaine** : les fichiers d'un autre rôle à modifier, et pourquoi.
6. **Reste à faire.**
