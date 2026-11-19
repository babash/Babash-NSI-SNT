# QuizzNSI

**Un cours court en diapositives, et des questions tout de suite, sur le téléphone de chaque élève.** Pour la NSI (et la SNT), un cours-quiz par notion.

> Tu projettes le cours : une notion par diapositive, puis une question pour la pratiquer. Tes élèves rejoignent la séance avec un QR code et un prénom ou un pseudo, répondent depuis leur téléphone, et voient aussitôt l'explication de leur réponse, juste ou fausse. Le même cours se révise seul·e à la maison et s'imprime sur papier.

## 👉 Essayer maintenant

- **[Réviser seul·e : piles et files](https://babash.github.io/Babash-NSI-SNT/nsi-terminale/fichiers/quizz-nsi/revision.html?cours=piles-files)** (le cours et ses 20 questions, corrigées tout de suite)
- **[Animer en classe](https://babash.github.io/Babash-NSI-SNT/nsi-terminale/fichiers/quizz-nsi/animer.html?cours=piles-files)**, ou d'abord [en mode démo](https://babash.github.io/Babash-NSI-SNT/nsi-terminale/fichiers/quizz-nsi/animer.html?cours=piles-files&demo), entre les onglets de ton navigateur
- **[Les questions à imprimer](https://babash.github.io/Babash-NSI-SNT/nsi-terminale/fichiers/quizz-nsi/imprimer.html?cours=piles-files)** et [leur corrigé](https://babash.github.io/Babash-NSI-SNT/nsi-terminale/fichiers/quizz-nsi/imprimer.html?cours=piles-files&corrige)

**Gratuit · sans compte · rien à installer · sur téléphone · rien n'est enregistré en ligne ; le prénom ou le pseudo et les réponses passent seulement en direct dans la séance**

QuizzNSI fait partie des [Ressources NSI et SNT](https://babash.github.io/Babash-NSI-SNT/), rubrique [NSI Terminale](https://babash.github.io/Babash-NSI-SNT/nsi-terminale/). *Les adresses changeront quand QuizzNSI aura son propre dépôt.*

---

## Une séance en trois étapes

1. **Tu** ouvres [la page d'animation](animer.html?cours=piles-files) et la projettes : un code de 4 lettres, un lien et un QR code s'affichent. Tu choisis le temps par question (sans minuterie, ou de 20 s à 1 min 30) et le classement (à la fin, après chaque question, ou aucun).
2. **Les élèves** rejoignent avec le QR code, le lien ou le code, depuis un téléphone ou un ordinateur, avec un prénom ou un pseudo (jamais un nom de famille). Un pseudo déplacé se retire d'un clic : l'élève en choisit un autre.
3. **Tu avances dans le cours** (flèches, Entrée) : sur une notion, les téléphones montrent la notion ; sur une question, chaque élève répond, l'écran compte les réponses ; **Montrer la réponse** affiche la répartition, l'erreur la plus fréquente avec son explication, puis le feedback de chaque option. Chaque élève voit sur son écran l'explication de **sa** réponse.

Sans réseau ou sans élève connecté·e, la page d'animation marche comme un simple diaporama, et la page élève propose le mode autonome.

## Le barème (à valider)

| Action | Points | Pourquoi |
|---|---|---|
| Répondre, même faux | +10 | oser répondre |
| Bonne réponse | +100 | l'essentiel : réfléchir |
| Rapidité (avec une minuterie seulement, et seulement si c'est juste) | de +20 à 0 | un peu d'élan, sans écraser la réflexion |
| Rebond : une bonne réponse juste après une erreur | +30 | valoriser la progression, pas seulement les meilleur·e·s |

Le classement compte peu (philosophie éducative, § 9) : par défaut, le podium (les 3 premières places) n'apparaît qu'à la fin. Les « beaux rebonds » sont annoncés à toute la classe après chaque question. Chaque élève suit sur son téléphone ses points, ses bonnes réponses, sa série et ses rebonds, calculés par son téléphone ; sa place n'est connue que s'il ou elle est sur le podium affiché (aucune autre place n'est envoyée).

## Le premier cours : piles et files (Terminale NSI)

15 notions courtes et 20 questions, du plus simple (pile ou file ? quel élément sort ?) à l'analyse de code et à la recherche d'erreur : primitives `empiler`, `depiler`, `sommet`, `enfiler`, `defiler` ; état après une suite d'opérations ; dépiler une pile vide ; implémentation avec une liste Python et coût de `pop(0)` ; parcourir une pile sans la détruire ; une file avec deux piles ; parenthèses ; pile d'appels. Inspiré des contrôles de Terminale « Pile, File et rappels de 1re » (2024 et 2025) et des sujets de bac qu'ils citent. Chaque question a un objectif, quatre options tirées d'erreurs fréquentes et un feedback pour chacune. **Chaque code affiché a été exécuté** (`outils/verifier_cours.py`).

## Pour quels usages

| Usage | Comment |
|---|---|
| **En classe, toute la classe en même temps** (≈ 40 min, ou en deux fois) | La page d'animation projetée, les téléphones des élèves. |
| **En binôme ou en îlot** | Un téléphone pour deux ou pour l'îlot : on se met d'accord avant de répondre. |
| **Seul·e, en révision** | Le mode autonome : les diapositives et les questions, des essais illimités, la correction quand on veut. « Questions seules » saute les notions. La progression reste sur l'appareil. |
| **Sur papier** | La feuille A4 en noir et blanc (6 pages), le corrigé à part. |

## Données des élèves

- **Enregistré en ligne** : rien. Une séance passe par les canaux temps réel (diffusion et présence) d'un projet Supabase, **sans aucune table** : rien n'y reste après la séance.
- **Visible par les autres, pendant la séance seulement** : exactement ce que montre l'écran projeté. La liste des prénoms ou pseudos présents (avec un identifiant tiré au hasard par séance) ; pour chaque question, la bonne réponse et la répartition des réponses en nombres ; les pseudos des « beaux rebonds » ; le podium (pseudos et points des trois premières places) seulement quand l'enseignant·e l'affiche.
- **Jamais diffusé** : la réponse d'un·e élève (elle part **chiffrée** pour la seule page projetée, [js/chiffre.js](js/chiffre.js)), ses points, sa place hors du podium. Chaque téléphone calcule ses propres points avec le barème ; la page projetée fait son propre calcul, et elle seule fait foi pour le podium (les deux peuvent différer de quelques points de rapidité, selon le délai du réseau).
- **Sur l'appareil de l'élève** : le code de séance, le pseudo et l'identifiant, pour revenir après une coupure ; effacés à la fin de la séance, et sinon au premier chargement d'une page de QuizzNSI après 12 heures. Dans l'onglet, ses réponses et ses points de la séance, effacés à la fermeture de l'onglet. En révision, ses réponses du mode autonome, gardées jusqu'à « Recommencer à zéro » ou l'effacement des données du navigateur.
- **Sur l'appareil de l'enseignant·e** : l'état de la séance, dans l'onglet (effacé à sa fermeture).
- **Canal public, messages contrôlés** : n'importe qui qui connaît le code peut écrire dans le canal. Chaque message reçu est validé par un schéma strict ([js/messages.js](js/messages.js)) et ignoré s'il n'est pas conforme ; les messages ne portent que des identifiants et des nombres (le texte des questions vient du fichier du cours) ; une valeur reçue ne passe jamais par `innerHTML`. Les tests envoient des centaines de messages forgés ([tests/test_messages.js](tests/test_messages.js), [tests/test_parcours.py](tests/test_parcours.py)).
- **Pseudo filtré** : 2 à 16 caractères, lettres (de toutes les écritures), chiffres, espace, `-`, `'`, `.`, `_` ; une seule écriture par pseudo (pas de lettre cyrillique glissée dans un mot latin) ; tout caractère invisible est refusé ; un pseudo déjà pris est refusé, à la casse, aux accents et aux sosies près (« АВС » cyrillique = « ABC ») ; tout est affiché comme du texte, jamais comme du HTML.

## Ajouter un cours

Un cours-quiz est **un seul fichier JSON** : le moteur ne change pas. Le format est décrit dans [cours/FORMAT.md](cours/FORMAT.md), le modèle est [cours/piles-files.json](cours/piles-files.json).

```bash
python3 -I outils/verifier_cours.py cours/<id>.json     # 20 questions, 4 options, une juste, feedbacks,
                                                       # répartition A-D, caractères, exécution du code
```

### Les tests

```bash
node tests/test_moteur.js                                   # barème, pseudo, échappement, schémas
node tests/test_messages.js                                 # messages forgés : tous rejetés
python3 -I -m unittest discover -s tests -p "test_v*.py"    # le vérificateur
python3 -I tests/test_parcours.py                           # Playwright : séance à 2 élèves, injection, mode autonome,
                                                            # impression, 320/768/1440 px, clair et obscur
```

Le parcours utilise un faux client temps réel ([tests/faux-temps-reel.js](tests/faux-temps-reel.js)) : il ne se connecte à aucune base.

## Pour aller plus loin

| Fichier | Contenu |
|---|---|
| [config.js](config.js) | Le projet Supabase des séances ; pour ta copie, mets le tien, ou laisse l'adresse vide pour le mode démo |
| [cours/FORMAT.md](cours/FORMAT.md) | Écrire un cours-quiz |
| [outils/verifier_cours.py](outils/verifier_cours.py) | Le vérificateur |
| [vendor/LICENCES-BIBLIOTHEQUES.txt](vendor/LICENCES-BIBLIOTHEQUES.txt) | Le client temps réel de Supabase et le générateur de QR codes, avec leurs licences |

### Installer ta copie

1. **Copie le dépôt** (bouton *Fork*), puis publie-le : *Settings › Pages › Deploy from a branch*, branche `main`, dossier `/ (root)`.
2. **Crée un projet Supabase** (offre gratuite). Il n'y a ni table ni script SQL : les séances n'utilisent que les canaux temps réel.
3. **Dans `config.js`**, mets l'adresse de ton projet et sa clé publique (« publishable »), jamais une clé secrète.

Sans projet Supabase, laisse `SUPABASE_URL` vide : les séances passent en mode démo, entre les onglets d'un même navigateur. Le mode autonome et la version imprimable n'ont besoin de rien.

## Feuille de route

- **Un cours-quiz par fiche de FichesNSI** (22 fiches), après la validation de ce premier cours.
- **Un essai en classe**, pour régler le temps par question et le barème.
- **Les cours de SNT**, avec les compétences Pix explicitées.

## Contact

Conçu par Babash - NSI Tani Malandi pour les classes de NSI et de SNT de l'académie de Mayotte, développé avec l'aide de l'IA ([Claude Code](https://claude.com/claude-code)).
Une question, une idée, un bug ? Les [issues GitHub](https://github.com/babash/Babash-NSI-SNT/issues). Toutes les ressources sont sur le site [Ressources NSI et SNT](https://babash.github.io/Babash-NSI-SNT/).

## Licence

- **Le code** (les fichiers `.html`, `.css`, `.js` et `.py`, hors bibliothèques et polices) est sous licence [MIT](LICENSE).
- **Les contenus** (les cours de `cours/`, ce README et `cours/FORMAT.md`) sont sous licence [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.fr).
- **Les bibliothèques** de `vendor/` (le client temps réel de [Supabase](https://supabase.com), [qrcode-generator](https://github.com/kazuhikoarase/qrcode-generator) de Kazuhiko Arase) : licence MIT, notices dans [vendor/LICENCES-BIBLIOTHEQUES.txt](vendor/LICENCES-BIBLIOTHEQUES.txt). « QR Code » est une marque déposée de DENSO WAVE.
- **Les polices** Chakra Petch, JetBrains Mono et Atkinson Hyperlegible, intégrées dans `css/polices.css` : licence SIL OFL 1.1, copyrights et texte dans [css/LICENCE-POLICES.txt](css/LICENCE-POLICES.txt).

Tu peux les réutiliser et les modifier, y compris pour tes classes, en mentionnant Babash - NSI Tani Malandi et la licence ; un contenu modifié se partage sous la même licence. Si tu utilises l'IA pour les modifier, merci de le préciser.
