# L'organisation du dépôt

*Les dossiers et les fichiers du site. Retour au [README](../README.md).*

Le site est publié par GitHub Pages depuis la branche `main`, dossier racine : les pages et les fichiers déposés sont en ligne à la même place, sous `https://babash.github.io/Babash-NSI-SNT/` ([Activer GitHub Pages](REUTILISER.md#activer-github-pages-une-seule-fois)).

```
README.md                   la présentation du site
CONTRIBUTING.md             les règles du travail sur GitHub
docs/                       la documentation : ce fichier et les autres
LICENSE                     la licence MIT du code
CLAUDE.md                   les règles communes de l'équipe d'agents
.claude/agents/             la fiche de chaque rôle
index.html                  l'accueil (ne pas toucher)
reglages.js                 titre du site, liste des rubriques, textes du pied de page
snt/
  ressources.js             ← la liste de la rubrique SNT
  fichiers/                 ← les PDF et fiches de la rubrique SNT
  index.html                (ne pas toucher)
nsi-premiere/   …           même organisation pour chaque rubrique
nsi-terminale/  …
pp/             …
autres/         …
assets/                     mise en page et fonctionnement (ne pas toucher)
donnees/                    le format de la future bibliothèque (BIBLIOTHEQUE.md)
.github/                    vérification automatique (VERIFICATION.md) et outils du Gardien (GARDIEN.md)
scripts/                    vérification automatique, validation des données, script complet de la base
supabase/                   le socle commun de la base des applications (SUPABASE.md)
```

Chaque fichier a un rôle propriétaire : voir [L'équipe d'agents](AGENTS.md).

## Le décor

La ville, sa liaison montante et le sol quadrillé du bandeau sont un dessin original, généré
par `assets/site.js` (fonction `scene`) dans la couleur de chaque rubrique. Les couleurs
générales des deux affichages sont en haut de `assets/style.css`.
