# 🗂️ Ressources NSI et SNT

**Cours, activités et outils pour la classe, rangés par niveau et par thème.** Pour la SNT, la NSI de 1re et de terminale, et le rôle de professeur·e principal·e.

> Pour chaque thème du programme, les collègues trouvent des ressources prêtes pour la classe : des jeux et des applications où les élèves programment, des TD à imprimer, des activités débranchées, et une sélection de sites ressources. Chaque ressource dit ce que font les élèves, sur ordinateur, sur téléphone ou sur papier.

## 👉 [Ouvrir le site : babash.github.io/Babash-NSI-SNT](https://babash.github.io/Babash-NSI-SNT/)

**Gratuit · sans compte · rien à installer · le site n'enregistre rien sur les élèves ; les ressources qui le font le signalent**

---

## Les rubriques

Les rubriques suivent les **textes officiels** :

| Rubrique | Texte de référence | Thèmes du site |
|---|---|---|
| SNT | Programme de SNT, BO spécial n° 1 du 22 janvier 2019 | Les 7 thèmes et les notions transversales de programmation |
| NSI Première | Programme de NSI de première, BO spécial n° 1 du 22 janvier 2019 | Les 8 rubriques, avec la colonne « Contenus » |
| NSI Terminale | Programme de NSI de terminale, BO spécial n° 8 du 25 juillet 2019 | Les 6 rubriques, avec la colonne « Contenus » |
| Professeur principal | Circulaire n° 2018-108 du 10 octobre 2018 | Les missions de professeur·e principal·e |

La cinquième rubrique, **Autres ressources**, réunit ce qui sert à tous les niveaux : les outils de la classe, les concours et de quoi se former.

## Les adresses

- **Le site** : [babash.github.io/Babash-NSI-SNT](https://babash.github.io/Babash-NSI-SNT/).
- **Les rubriques** : [SNT](https://babash.github.io/Babash-NSI-SNT/snt/), [NSI Première](https://babash.github.io/Babash-NSI-SNT/nsi-premiere/), [NSI Terminale](https://babash.github.io/Babash-NSI-SNT/nsi-terminale/), [Professeur principal](https://babash.github.io/Babash-NSI-SNT/pp/) et [Autres ressources](https://babash.github.io/Babash-NSI-SNT/autres/).
- **Un thème** : son nom court après `#`, par exemple `…/nsi-premiere/#types-construits`.
- **Une recherche** : `…/Babash-NSI-SNT/?q=débranché`.
- **La bibliothèque** : [babash.github.io/Babash-NSI-SNT/bibliotheque/](https://babash.github.io/Babash-NSI-SNT/bibliotheque/). Son adresse garde la recherche, les filtres et le tri (`…/bibliotheque/?q=boucle`), et la fiche d'une ressource s'ouvre par son identifiant (`…/bibliotheque/?r=lagon-arena`).
- **L'espace administrateur** : [babash.github.io/Babash-NSI-SNT/admin/](https://babash.github.io/Babash-NSI-SNT/admin/), sans lien depuis les pages publiques ([docs/ADMIN.md](docs/ADMIN.md)).
- **Le dépôt** : [github.com/babash/Babash-NSI-SNT](https://github.com/babash/Babash-NSI-SNT).

## Utiliser le site

- **Chaque rubrique** range ses ressources par thème. En SNT et en NSI, la ligne « Au programme » d'un thème affiche les contenus du texte officiel : ceux qui ont une ressource sont des liens, les autres restent en pointillés.
- **La recherche** de la page d'accueil fouille les titres, les textes, les étiquettes et les thèmes de toutes les rubriques. Chercher « ressource du mois » retrouve la ressource mise en avant.
- **L'onglet Bibliothèque**, dans la barre du haut, réunit toutes les ressources, y compris celles que les rubriques ne montrent pas encore (les activités Capytale, par exemple). Sa recherche comprend les synonymes et les notions du programme, tolère les fautes de frappe et fouille aussi le texte des documents hébergés sur le site ; ses filtres portent sur tous les classements (enseignement, niveau, programme officiel, notions, type, durée, langages, autrices et auteurs…), et deux vues, en liste ou en cartes, présentent les résultats. Chaque ressource y a sa fiche complète : programme, notions, durée, autrices et auteurs, licence, données d'élèves et tous ses documents. La recherche de l'accueil propose de poursuivre dans la bibliothèque.
- **Une ressource** s'ouvre dans un nouvel onglet. Un fichier que le navigateur ne sait pas afficher (`.py`, `.odt`, `.docx`, `.zip`…) se télécharge.
- **Clair ou obscur** : par défaut, le site suit le réglage de l'appareil, et le choix fait dans la barre du haut (Auto, Clair, Obscur) est retenu par le navigateur.

## Ajouter une ressource

Chaque rubrique a sa liste, `ressources.js`, et ses fichiers, dans son dossier `fichiers` (par exemple `snt/ressources.js` et `snt/fichiers/`) : on les modifie directement sur GitHub. Le mode d'emploi pas à pas est dans [docs/LISTES.md](docs/LISTES.md) : [ajouter une ressource](docs/LISTES.md#ajouter-une-ressource-en-ligne), [un PDF](docs/LISTES.md#ajouter-un-pdf-ou-nimporte-quel-fichier), [ranger une rubrique](docs/LISTES.md#organiser-une-rubrique), et que faire [si la page affiche une erreur](docs/LISTES.md#si-la-page-affiche-une-erreur). Les liens « Modifier la liste » et « Déposer un fichier » ne sont plus en bas des rubriques depuis le 17 novembre 2026. La bibliothèque, elle, lit les fiches du dossier `donnees/ressources/` ([docs/BIBLIOTHEQUE.md](docs/BIBLIOTHEQUE.md)) : une ressource ajoutée seulement à une liste apparaît dans sa rubrique, pas dans la bibliothèque.

**L'espace administrateur** ([docs/ADMIN.md](docs/ADMIN.md)) annote et modifie les fiches, compose les onglets du site (la vitrine) et en montre l'aperçu, puis enregistre les changements d'un clic, protégé par un mot de passe administrateur, ou les donne à télécharger. Ajouter une nouvelle ressource par un formulaire viendra à l'étape suivante.

**La mise en ligne** : chaque envoi sur `main` est publié par le workflow « Publier le site », dans l'onglet Actions du dépôt, en quelques minutes. Il valide les données, construit la bibliothèque, puis met le site en ligne. S'il échoue (croix rouge), rien n'est publié et le site garde sa version précédente ([docs/VERIFICATION.md](docs/VERIFICATION.md#la-mise-en-ligne)).

## Réutiliser le site

Tu peux copier le site pour tes classes, avec tes rubriques et tes ressources : [docs/REUTILISER.md](docs/REUTILISER.md) explique comment le copier, le mettre en ligne avec GitHub Pages, l'essayer sur ton ordinateur, et ce qu'il faut garder des licences.

## Pour aller plus loin

| Document | Contenu |
|---|---|
| [Les listes de ressources](docs/LISTES.md) | ajouter une ressource ou un fichier, ranger une rubrique, les réglages et le pied de page, les erreurs |
| [Réutiliser le site](docs/REUTILISER.md) | ta copie du site, GitHub Pages (source « GitHub Actions »), l'essai sur ton ordinateur, ce qui vient d'ailleurs |
| [L'organisation du dépôt](docs/ORGANISATION.md) | les dossiers et les fichiers, les activités Capytale, le décor |
| [L'espace administrateur](docs/ADMIN.md) | modifier les fiches et les onglets, l'aperçu, le mot de passe administrateur et le jeton GitHub pas à pas, enregistrer ou télécharger, les tests |
| [Les données de la bibliothèque](docs/BIBLIOTHEQUE.md) | l'onglet Bibliothèque, le format des fiches du dossier `donnees/`, le thésaurus des notions, la validation et la construction à chaque publication |
| [La publication et la vérification automatique](docs/VERIFICATION.md) | la mise en ligne par « Publier le site », les contrôles de l'onglet Actions (la bibliothèque en ligne comprise), et le même contrôle sur ton ordinateur |
| [Les bases Supabase](docs/SUPABASE.md) | Alien Python, Court-circuit (son code élève facultatif, en service depuis le 13 novembre 2026 : ce qui est enregistré, l'effacement après 12 mois) et le socle commun de la base |
| [L'équipe d'agents](docs/AGENTS.md) | les rôles, qui possède quels fichiers, les règles de conception des ressources |
| [Les outils du Gardien](docs/GARDIEN.md) | les contrôles avant et après chaque publication |
| [Contribuer](CONTRIBUTING.md) | les règles du travail sur GitHub |

---

## Contact

Conçu par Babash - NSI Tani Malandi pour les classes de SNT et de NSI de l'académie de Mayotte ; beaucoup de ressources le sont avec l'aide de l'IA, et le site est entretenu par une équipe d'agents Claude (voir [L'équipe d'agents](docs/AGENTS.md)).
Une question, une idée, un lien cassé ? Les [issues GitHub](https://github.com/babash/Babash-NSI-SNT/issues) du dépôt.

## Licence

- **Le code du site** (`assets/*.js`, `assets/*.css`, les pages `index.html`, `bibliotheque/bibliotheque.css`, `reglages.js`, `scripts/`, `supabase/`, `.github/`) est sous licence [MIT](LICENSE).
- **Les documents** (les fiches, TD, cours, guides et diaporamas des dossiers `fichiers/`, les textes des listes de ressources, le décor du bandeau, et la documentation : ce README, `CONTRIBUTING.md` et `docs/`) sont sous licence [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.fr), sauf ce qui est repris d'ailleurs et garde sa licence (ci-dessous).
- **Les activités Capytale** (les dossiers `fichiers/capytale/` de SNT, de NSI Première et de NSI Terminale) : chaque activité garde sa licence, donnée au pied de sa page de lecture et dans sa fiche. Celles de Babash - NSI Tani Malandi sont sous CC BY-SA 4.0, et le code de leurs modules sous MIT. Celles de collègues gardent la licence de leurs auteurs et autrices : CC BY-SA 4.0 (l'équipe de SNT et Germain Becker, du lycée Emmanuel Mounier), CC BY-SA 3.0 FR (Nathalie Weibel), CC BY-SA (Christophe Mieszczak). **Trois activités sont sous une licence non commerciale, la [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.fr)** : « Internet : des réseaux et des protocoles » (David Landry), les algorithmes gloutons de la clé USB (Germain Becker et Sébastien Point) et l'escape game de SNT (Laura Fléron) ; de même, les modules `alien_python.py` et `pixel_art.py` de Germain Becker sont sous CC BY-NC-SA. La CC BY-SA 4.0 des dossiers `fichiers/` ne s'applique pas à eux : on ne les réutilise pas dans un cadre commercial. SQL Murder Mystery reste au Knight Lab (code MIT, énoncé, base et schéma CC BY-SA 4.0) ; les images de Wikimedia Commons et l'alien de Kenney (CC0) sont crédités sur leur page.
- **Alien Python** (`snt/fichiers/alien-python/`) : d'après [Alien-Python](https://forge.apps.education.fr/DegrangeM/alien-python), de Mathieu Degrange (MIT) ; la notice est dans `snt/fichiers/alien-python/LICENCE.txt`, à garder avec `data.js` en cas de copie.
- **Court-circuit** (`snt/fichiers/court-circuit/`) : code MIT et documents CC BY-SA 4.0 de Babash - NSI Tani Malandi ; les bibliothèques incluses (CodeMirror 6, client temps réel de Supabase, QR Code Generator) gardent leur licence MIT, avec leur notice dans `snt/fichiers/court-circuit/vendor/LICENCES-BIBLIOTHEQUES.txt`, et les polices intégrées (Chakra Petch, JetBrains Mono, Atkinson Hyperlegible) la leur, la SIL Open Font License 1.1, avec leurs copyrights et son texte dans `snt/fichiers/court-circuit/LICENCE.txt`.
- **La fiche Python de SNT** (`snt/fichiers/python-compute-it.html`) : d'après la fiche Compute-it d'Etienne Clave, sur le site exomorphisme.fr (lycée de Sada).
- **Le TP « le reboucheur de donuts »** (`snt/fichiers/web-interview-donuts/`) : documents CC BY-SA 4.0 de Babash - NSI Tani Malandi ; la page modèle vient de « Interview Reboucheur de Donuts », de supersnt sur CodePen, sous licence MIT (notice dans `LICENSE-modele-codepen.txt`) ; Bootstrap 5.3.0 et reveal.js 4.3.1, copiés dans le dossier, gardent leur licence MIT, avec leur notice dans les dossiers `vendor/`.
- **Le voyageur de commerce à Mayotte** (`nsi-terminale/fichiers/voyageur-de-commerce-mayotte/`) : le contour de l'île vient de Natural Earth (domaine public) et les positions des villages de GeoNames (CC BY 4.0), crédités au pied de la page.
- **Les ressources externes** restent la propriété de leurs auteurs et autrices : leur site d'origine est indiqué sur chaque ressource.

Tu peux les réutiliser et les modifier, y compris pour tes classes, en mentionnant Babash - NSI Tani Malandi et la licence ; un document modifié se partage sous la même licence. Pour une ressource reprise d'ailleurs, ce sont ses auteurs et autrices et sa propre licence qu'on mentionne. Si tu utilises l'IA pour les modifier, merci de le préciser.
