# Séance de révision (conditions et boucles) : sources

Par Babash - NSI Tani Malandi (CC BY-SA 4.0).

**Les documents des élèves sont désormais les pages en ligne** (style « Signal pirate », T125), qui en sont la référence : `../seance-revision-eleves.html` (feuille de route), `-2.html` (mini-contrôle croisé, auto-corrigé en ligne), `-3.html` (atelier robot : chaque défi est testé sur ses trois grilles). `../seance-revision-eleves.pdf` en est l'impression vierge, d'un seul tenant (`charte/imprimer-td.py`). Le contenu est inchangé : il vient des données de `revision.py`, mises en page par `seance-en-ligne.py`, qui vérifie aussi toutes les réponses par exécution (`python3 -I seance-en-ligne.py --verifier`).

- `revision.py` : les données de la séance et le corrigé papier (`../seance-revision-corriges.html`, `.pdf`, inchangés), dans le style des anciens TD ; l'ancienne feuille des élèves ne s'écrit plus qu'avec `--ancienne`.
- `style-td.html` : la feuille de style des anciens TD « Bases python », gardée ici ; `../../cc-prem-conditions-boucles-fonctions/source/generer.py` la lit aussi (le contrôle de Première reste tel quel : sortie identique à l'octet près).
- `outils.py`, `pdf.py` : robot, code coloré, grilles, PDF du corrigé.

**Moins de papier (T125b)** : le PDF des élèves passe de 8 à 7 pages A4, tout en 10 pt au moins (l'original tenait en 4 pages en 7 à 8 pt). Le fond ne change pas : questions du quiz deux par ligne ; réponses rédigées sur papier sans l'étiquette de l'écran, avec une ligne quand la réponse modèle est courte (110 caractères au plus) ; cadre du code à la taille de la solution ; méthode en un paragraphe et tableau « Je dis / J'écris » sur deux colonnes ; « testé par le robot » dans la consigne « Mon code » ; la phrase d'introduction des défis 2 à 4 (répétition du défi 1) à l'écran seulement.

**Passe finale (T125c)** : le mini-contrôle, que les élèves s'échangent, commence sa propre page du PDF, avec « Nom et prénom » et « Classe » (`data-nouvelle-page` sur `<main>` de `-2.html`) : le PDF repasse à 8 pages A4. Les numéros des questions continuent d'une feuille à l'autre (`charte/numeroter-feuilles.py`).
