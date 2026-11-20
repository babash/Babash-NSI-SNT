# Mise à jour semestrielle des annales de NSI (chaque 1er août et chaque 1er janvier)

Tâche du Bibliothécaire, confiée à une tâche planifiée. Elle met à jour `donnees/annales/annales-bac-nsi.json`
et les fiches de la bibliothèque, sur une branche. **Elle ne publie jamais sur `main`** (le Gardien le fait).

## Ce qu'on cherche à chaque date

| Date | Sessions à trouver ou à compléter |
|---|---|
| **1er août** | Amérique du Nord (mars-mai), Asie, Centres étrangers (groupes 1 et 2), Métropole, Antilles-Guyane, Polynésie, La Réunion et Mayotte (juin), plus les corrigés parus depuis janvier. |
| **1er janvier** | Métropole (septembre), Asie-Pacifique (septembre), Amérique du Sud (novembre), Nouvelle-Calédonie (novembre), plus les corrigés tardifs. L'AEIF publie les corrigés de septembre et de novembre en décembre-juin. |

Un sujet porte un code officiel `AA-NSIJxCCn` : `ME1` Métropole juin, `ME3` Métropole septembre, `AN1` Amérique du Nord,
`JA1` Asie, `G11` Centres étrangers groupe 1, `PO1` Polynésie, `AG1` Antilles-Guyane, `AS1` Amérique du Sud, `NC1`
Nouvelle-Calédonie, `LR1` La Réunion et Mayotte, `PE4` Asie-Pacifique septembre ; `J1` ou `J2` donne le jour.

## Étape 0 : se mettre au travail

1. Lire `CLAUDE.md`, la fiche `.claude/agents/bibliothecaire.md`, `coordination/decisions.md` (la décision la plus récente l'emporte).
2. `git fetch origin '+refs/heads/*:refs/remotes/origin/*'`, puis une copie de travail propre :
   `git worktree add <dossier-de-travail>/site -b biblio/annales-AAAA-MM origin/main` (AAAA-MM = mois de la mise à jour : `…-08` ou `…-01`).
3. Lire le fichier `donnees/annales/annales-bac-nsi.json` : la liste `a_trouver` dit ce qui manquait la fois d'avant.

## Étape 1 : les pages à relire

Ouvrir chacune avec l'outil de lecture du web (`WebFetch`) ; si un site refuse l'accès, le noter, ne pas le contourner.

| Source | Page | Ce qu'on y relève |
|---|---|---|
| AEIF (la plus complète, CC BY-SA 4.0) | `https://aeif.fr/index.php/annee-AAAA/` pour l'année en cours et la précédente (2024 : `annales-2024/`) ; `https://aeif.fr/index.php/themes-par-sujets/` | tous les sujets, corrigés, sources LaTeX ; le tableau des thèmes par sujet |
| kxs | `https://kxs.fr/sujets/terminale-ecrit` et `https://kxs.fr/sujets/terminale-pratique` | nouvelles lignes, nouveaux corrigés ; années présentes |
| Math93 | page « Annales du Bac NSI AAAA » (la trouver par `WebSearch` : « math93 annales bac NSI AAAA ») | sujets officiels, corrigés détaillés |
| Éduscol | `https://eduscol.education.fr/2661/banque-des-epreuves-pratiques-de-specialite-nsi` et la page NSI de la voie générale | banque de l'épreuve pratique (publiée au plus tard le 24 mars), sujets 0, textes de cadrage |
| Académie de Bordeaux | `https://ent2d.ac-bordeaux.fr/disciplines/nsi/category/ressources-officielles/` | articles datés sur l'épreuve pratique et les sujets 0 |
| Bulletin officiel | `WebSearch` : « note de service épreuve spécialité NSI baccalauréat session AAAA+1 » | **changement de format** (durée, points, structure, partie pratique) : si oui, l'écrire dans `epreuve_ecrite.formats` et le signaler en tête du rapport |

Ajouter une source nouvelle seulement si elle est reconnue (association, académie, enseignant·e qui publie ses sources) et si elle
indique sa licence ; sinon, la signaler dans le rapport sans l'ajouter.

## Étape 2 : repérer un nouveau sujet

1. Dresser la liste des sessions de la page AEIF de l'année et de la page kxs.
2. La comparer aux `id` déjà présents (`AAAA-<centre>-<j1|j2>`, ex. `2026-metropole-j1`) et à la liste `a_trouver`.
3. Un sujet est **nouveau** s'il n'a pas d'`id`, ou s'il a un `id` mais pas de lien vers la source qui vient d'apparaître (nouveau corrigé, version officielle).
4. Un sujet **disparu** d'une source (lien mort) n'est pas supprimé : son état passe à « à revoir » et on cherche une autre source.
5. Attention aux libellés trompeurs déjà rencontrés : kxs « Métropole juin » 2023 (c'est mars 2023), kxs « Mayotte » 2022 (c'est La Réunion),
   kxs « jour 2 bis » 2025 = AEIF « sujet 3 » (sujet de secours), doublons (« Centres étrangers 2022 sujet 1 » = « jour 1 »). Se fier au code d'en-tête du PDF.

## Étape 3 : ajouter ou corriger un sujet

Les données brutes sont dans `donnees/annales/outils/donnees_brutes.py` ; le JSON se **reconstruit** :

```
python3 donnees/annales/outils/construire_annales.py . donnees/annales/annales-bac-nsi.json
python3 scripts/annales_notions.py
```

Le second script range chaque exercice dans les 22 chapitres des fiches de révision (`donnees/annales/notions-par-exercice.json`,
lu par la page `bibliotheque/annales/`). **Toujours le relancer après le premier** : sinon le contrôle « Classement des annales
par chapitre à jour » du workflow « Vérifier le site » échoue et la branche ne peut pas être publiée.

Pour chaque sujet nouveau, ajouter un appel `S(…)` dans `donnees_brutes.py` (copier un voisin de même année), avec :

- le code d'en-tête, la date si le PDF la donne, le nombre de pages du PDF principal et la source de la mise en page ;
- les liens : kxs (`kx(...)`), AEIF (sujet, corrigé, `"ok"` si ouvert, `"non testé"` sinon), autres sources ;
- un tuple par exercice : points, pages `"début-fin"`, et le texte « Cet exercice porte sur… » **recopié** du PDF (ajouter entre parenthèses les mots-clés du programme que l'énoncé travaille : le script en déduit les notions).

Relever pages, points et exercices **dans le PDF**, pas dans une page de présentation. Si le PDF est une image (aucun texte
extractible), lire la version AEIF recomposée, et l'écrire dans `remarque`. Ce qu'on n'a pas pu lire reste `None` ou « à vérifier » : on n'invente rien.

Les notions viennent des règles du script (`REGLES`) et du thésaurus `donnees/referentiels/notions.json` (jamais modifié ici). Contrôler à la main
le classement des exercices nouveaux : leurs notions, puis leurs chapitres dans `donnees/annales/notions-par-exercice.json` (sortie de
`scripts/annales_notions.py`). Un chapitre faux ou manquant se corrige dans ce fichier, sur l'exercice (`<id du sujet>#<n°>`) :
`"chapitres": ["tris", "recursivite"], "verifie": true` (identifiants des chapitres : liste `chapitres` en tête du fichier), puis on relance
`python3 scripts/annales_notions.py`, qui garde désormais cet exercice tel quel. Les exercices de `a_classer` (aucun chapitre trouvé) et ceux
qui ont un champ `a_verifier` (classement écarté à cause d'un faux ami) sont à regarder en premier. **Une notion qui manque au thésaurus se demande dans le rapport** (déjà demandées : files à priorité,
fonction de hachage, tri topologique, arbres n-aires, algorithme min-max).

## Étape 4 : tester les liens (date de vérification)

1. Les liens des sujets nouveaux : les ouvrir tous, un par un (PDF lisible, bon sujet, bonne session).
2. Les liens existants : `python3 donnees/annales/outils/verifier_liens.py --ecrire` si le réseau atteint les sites ; sinon, ouvrir
   avec `WebFetch` au moins la page de chaque source, un sujet et un corrigé par année et par source, et ceux qui avaient un problème.
3. Un lien qui répond mal : état « à revoir », date du jour, et chercher un lien de remplacement (même sujet chez une autre source).
4. Mettre à jour `verifie_le` et `prochaine_mise_a_jour` (1er janvier ou 1er août suivant) en tête du JSON.

Règle de réutilisation : **on lie, on n'héberge pas**. Aucun PDF de sujet ni de corrigé n'entre dans le dépôt. Les sujets de l'AEIF
(CC BY-SA 4.0 selon sa page) pourraient être repris dans des feuilles de l'enseignant avec la mention « AEIF, CC BY-SA 4.0 » ; les autres
sources n'indiquent pas de licence : on ne les copie pas.

## Étape 5 : fiches de la bibliothèque

- Fiches des sources : `sujets-2025-aeif` (AEIF, toutes années), `sujets-ecrit-nsi-kxs`, `sujets-ecrit-nsi-math93`, `sujets-pratique-nsi-kxs`
  (et `banque-epreuve-pratique-ecebac`, `epreuve-pratique-exomorphisme`).
- Mettre à jour : `dates.modification` et `dates.verification_liens`, une note datée (ce qui a changé), la liste des documents (nouvelle page annuelle AEIF, par exemple),
  le résumé si une couverture change (années, nombre de sujets).
- Une source nouvelle : une fiche, avec auteur·rice, licence relevée sur la source (ou « inconnue »), origine (`communaute`, `collegue`, `institutionnelle`).
- Ne pas changer les identifiants. Vitrine : section « Préparer le bac », sous-sections « Épreuve écrite » et « Épreuve pratique », déjà en place ; y ajouter une fiche nouvelle.

## Étape 6 : l'épreuve pratique (version courte)

- Relire la page kxs : nombre de sujets par année, nouvelle banque (publiée au plus tard le 24 mars), format.
- Mettre à jour `epreuve_pratique.banques` dans `construire_annales.py` (année, nombre, modèles d'URL), ouvrir le sujet 01 et un corrigé de la banque nouvelle.
- Si le format change (durée, nombre d'exercices, points), l'écrire dans `epreuve_pratique.synthese` et le signaler en tête du rapport.

## Étape 7 : valider et pousser

1. `python3 donnees/annales/outils/construire_annales.py . donnees/annales/annales-bac-nsi.json`
2. `python3 scripts/annales_notions.py`, puis `python3 scripts/annales_notions.py --verifier` : « est à jour » exigé. Relever dans le rapport
   le bilan qu'il affiche (exercices classés, à classer, à vérifier).
3. `python3 scripts/valider_donnees.py` : 0 erreur exigée.
4. `git add donnees/annales donnees/ressources donnees/vitrine.json` ; commit : `[T104][biblio] Annales de NSI : mise à jour du 1er janvier AAAA` ; auteur `Claude <noreply@anthropic.com>`.
5. `git fetch origin '+refs/heads/*:refs/remotes/origin/*'`, `git rebase origin/main` si `main` a avancé (relancer alors les étapes 2 et 3),
   puis `git push -u origin biblio/annales-AAAA-MM`.
6. Rapport de fin de tâche (format de `CLAUDE.md`) au chef d'orchestre : sessions nouvelles (liste), corrigés nouveaux, liens à revoir, sources inaccessibles,
   changement de format éventuel, notions manquantes, et ce qui reste à trouver (`a_trouver`). Pas de question à l'enseignant : tout passe par le rapport.

## Texte à confier à la tâche planifiée

> Tu es le Bibliothécaire du dépôt `babash/Babash-NSI-SNT`. Exécute la procédure `donnees/annales/MISE-A-JOUR.md` (mise à jour semestrielle des annales
> du bac de NSI). Lis d'abord `CLAUDE.md` et `.claude/agents/bibliothecaire.md`. Travaille dans une copie isolée, sur la branche `biblio/annales-AAAA-MM`,
> ne publie rien sur `main`, n'héberge aucun PDF de sujet. Pousse ta branche et rends le rapport de fin de tâche.
