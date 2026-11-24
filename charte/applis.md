# Habiller une application : le socle et le moteur d'avatars

Mode d'emploi pour les applications de jeu (QuizzNSI, Hello GO, Calendrier des vacances, Expédition Gombessa, Lagon Arena et les suivantes). Décisions de l'enseignant du 24/11 (T133) : « piste B » (le design du site, plus une touche légère par application) ; pendant la question, la variante discrète ; l'Esprit en capuche pour les joueurs et joueuses sans compte ; les pseudos visibles au lobby, masquables d'un clic ; les 15 objets des applications. Démonstration : [`charte/applis.html`](applis.html).

## 1. Ce qu'une application charge, et dans quel ordre

Tout vient du site, une seule source ; rien n'est copié dans l'application.

```html
<html lang="fr" data-appli="quizz-nsi">
<link rel="stylesheet" href="https://babash.github.io/Babash-NSI-SNT/assets/signal-commun.css"> <!-- 1. palette et polices -->
<link rel="stylesheet" href="https://babash.github.io/Babash-NSI-SNT/assets/applis.css">        <!-- 2. le socle -->
<script src="https://babash.github.io/Babash-NSI-SNT/assets/equipage.js"></script>                <!-- 3. le moteur d'avatars -->
```

1. `assets/signal-commun.css` : la palette `--td-*` (clair et obscur, contrastes vérifiés) et les polices hébergées.
2. `assets/applis.css` : le socle (classes `ap-…`), à mettre sur `<body class="ap">` ou sur le conteneur de l'application.
3. `assets/equipage.js` : `window.Equipage`. Il injecte sa propre petite feuille (`#equipage-css`).

`data-appli` donne la touche propre : `quizz-nsi`, `hello-go`, `calendrier`, `gombessa` ou `lagon-arena`. Elle ne change que le décor (`.ap-touche`, sous la barre du haut) et le néon des ombres (`--ap-touche`) : jamais une couleur de texte.

## 2. Exemple minimal : le lobby, la question, le podium

```html
<body class="ap ap-projete">
<div class="ap-touche" aria-hidden="true"></div>
<div class="ap-plateau" id="plateau"></div>
<script>
var joueurs = [], E = Equipage;
E.plafond(8);                                        // 8 avatars animés à la fois au plus
function arrive(j) {                                 // j : { pseudo, avatar } (avatar : null sans compte)
  var c = document.createElement('div'); c.className = 'ap-joueur';
  c.innerHTML = '<span></span><span class="ap-dalle"></span><span class="ap-pseudo"></span>';
  c.lastChild.textContent = j.pseudo;                // jamais innerHTML pour un pseudo
  plateau.appendChild(c);
  j.p = E.creer(c.firstChild, j.avatar || E.neutre(), { taille: 96, etat: 'lobby', compagnon: false, alt: j.pseudo });
  joueurs.push(j);
}
function message(j, m) {                             // ce qui arrive du réseau : des numéros, jamais du texte
  if (m.bulle !== undefined) j.p.bulle(m.bulle);     // 0 à 20 : Equipage.phrases ; un autre numéro est ignoré
  if (m.geste) j.p.geste(m.geste, { duree: 3000 }); // 'salue' | 'saute' | 'rit' | 'sieste'
}
function question() { joueurs.forEach(function (j) { j.p.options({ taille: 48, cadre: 'buste', anime: false }).etat('attente'); }); }
function repond(j, serie) { j.p.etat('repondu').serie(serie); }   // fanion, flamme à partir de 2 ; jamais juste ou faux
function podium(trois) { joueurs.forEach(function (j) { j.p.options({ anime: true }).serie(0).etat(trois.indexOf(j) >= 0 ? 'fete' : 'applaudit'); }); }
</script>
```

Les codes montrés dans la démonstration sont des exemples neutres (« ABCD ») : la liste de mots des codes d'élèves est en cours de choix (des mots « de hacker ou de pirate »).

Masquer les pseudos d'un clic : la classe `ap-sans-pseudos` sur `.ap-plateau` (la place reste, rien ne saute).

## 3. L'interface du moteur (version 2.1.0)

Déjà là (inchangé) : `Equipage.creer(element, description, options)`, `svg`, `texte`, `normaliser`, `aleatoire`, `margouillat`, `compagnonSVG`, `catalogue`, les sept états, les trois cadres. Contrat complet : [`assets/equipage/LISEZMOI.md`](../assets/equipage/LISEZMOI.md).

| Ajout | Rôle |
|---|---|
| `etat: 'lobby' \| 'attente' \| 'repondu' \| 'fete' \| 'applaudit'` | états d'usage, alias de `repos`, `concentre`, `repos` avec le fanion, `tres_content`, `content` (`Equipage.USAGES`) |
| `poignee.geste(nom, { duree })` | `'salue'`, `'saute'`, `'rit'`, `'sieste'` (`Equipage.gestes`) : joue l'état (3 s par défaut, 20 s au plus), puis revient ; nom inconnu : `false` |
| `poignee.bulle(numero, liste)` | une phrase d'une liste FERMÉE : par défaut `Equipage.phrases` (21 phrases, de 0 à 20) ; numéro non entier ou inconnu : ignoré (`false`) ; 6 bulles au plus par page, les autres attendent ; 5 s par défaut (`{ duree }` en 3e argument) ; texte posé avec `textContent`, jamais du HTML |
| `poignee.marque('repondu' \| null)` | le fanion « a répondu » |
| `poignee.serie(n)` | la flamme et son chiffre, à partir de 2 ; `serie(0)` l'enlève |
| `Equipage.calme(true \| false \| null)` | toute la page en image fixe ; `Equipage.calme()` dit si la page est calme (forcée, ou réglage « mouvement réduit » de l'appareil) |
| `Equipage.plafond(8)` | au plus 8 avatars animés à la fois (les gestes passent devant), les autres en image fixe ; `plafond(null)` l'enlève |
| `Equipage.pause(true \| false)` | arrête les animations ; automatique quand l'onglet est caché |
| `Equipage.adresse('monsieur' \| 'madame')` | la forme des phrases qui s'adressent à l'enseignant·e (la 19 : « Ne vous inquiétez pas, Monsieur. » ou « … Madame. ») : un réglage de la page projetée, « Monsieur » par défaut ; l'élève envoie toujours le même numéro. `Equipage.phrase(n)` donne le texte affiché, `Equipage.variantes` les numéros concernés |
| `Equipage.neutre()` | l'Esprit en capuche, le même pour tous (une copie) |
| `Equipage.applis` | les 15 objets des applications, avec leur haut fait |
| cache | les dessins sont gardés par description, état et cadre (400 au plus) ; `Equipage.viderCache()` |

Retours de l'enseignant (24/11) : « Plus rapide que le bouchon de Mamoudzou ! » est retirée ; « Ne vous inquiétez pas, Monsieur. » (ou « Madame. ») et « Moi, c'est au talent. » sont ajoutées. La liste des phrases et des gestes est aussi dans le fichier versionné [`assets/equipage/applis.json`](../assets/equipage/applis.json) (régénéré et vérifié par `node charte/equipage-donnees.js`). Les numéros des phrases ne changent jamais : on ajoute à la fin, et la version monte.

## 4. Le socle `assets/applis.css`

| Composant | Classes |
|---|---|
| Barre du haut | `ap-barre`, `ap-logo`, `ap-lieu`, `ap-espace`, puis `ap-touche` (le décor de l'application) |
| Liens rapides | `ap-bandeau`, `ap-moi` (bouton « Zoé · mes applications »), `ap-menu` (liste, `hidden` pour la fermer) |
| Boutons | `ap-bt`, `ap-bt-principal`, `ap-bt-large`, `ap-bt-grand`, `ap-bt-mini` ; le lien discret `ap-discret` (« Jouer sans compte ») |
| Entrée | `ap-entree`, `ap-label`, `ap-champ`, `ap-champ-code`, `ap-entree-ou` |
| Lobby | `ap-lobby`, `ap-seance`, `ap-qr`, `ap-code-seance`, `ap-plateau` (`ap-sans-pseudos`), `ap-joueur`, `ap-dalle`, `ap-pseudo` |
| Question | l'écran de QuizzNSI repris tel quel (retour de l'enseignant du 24/11) : `options`, `option o0`…`o3`, `pastille`, `forme f0`…`f3` (une couleur ET une forme : A ▲, B ◆, C ●, D ■), `pre.code` avec `ligne`, `num`, `guide` et `c-mot`, `c-ch`, `c-nb`, `c-com`, `c-fn`, `c-nat`, `c-def`, `c-self`, `c-err` (le balisage de `QuizzNSI.blocCode`) ; plus `ap-question`, `ap-question-tete`, `ap-enonce`, le chrono `ap-minuteur`, `ap-temps`, les bustes `ap-reponses`, `ap-legende` ; `ap-tel` pour le téléphone |
| Podium | `ap-podium`, `ap-place ap-place-1` (2, 3), `ap-marche`, `ap-rang`, `ap-classe`, `ap-confettis` |
| Annonces | `ap-annonce`, `ap-annonce-titre`, `ap-gros-chiffre`, `ap-credits`, `ap-piece` |
| Bibliothèque des quiz | `ap-biblio`, `ap-filtres`, `ap-theme-titre`, `ap-grille-quiz`, `ap-carte-quiz` (`ap-revision` : cadre pointillé), `ap-actions` |
| Divers | `ap-carte`, `ap-puce`, `ap-message`, `ap-titre`, `ap-sous`, `ap-petit`, `ap-signal`, `ap-vh` |
| Écran projeté | `ap-projete` : texte de 22 px, code de 24 px, aucune ombre de néon |

Règles : le texte est toujours en `--td-encre` (7:1) ou `--td-encre-douce` (4,5:1) ; les néons ne portent aucun sens ; « Cours-quiz » et « Révision » se distinguent par le mot **et** par le cadre ; tout se lit dès 320 px ; avec le réglage « mouvement réduit » ou `Equipage.calme(true)`, plus aucune animation (confettis compris).

## 5. Les 15 objets des applications (famille `applis`)

Dessinés dans le moteur, accrochés au corps (l'objet tenu suit la main dans chaque pose de bras, le chapeau suit la tête). Ce sont des trophées : jamais achetés, jamais tirés au hasard. Emplacement `epaule` : sur les épaules.

| Objet (`id`) | Emplacement | Application | Haut fait (`id`) | Catégorie |
|---|---|---|---|---|
| `de_flottille` | main | `quizz_nsi` | `premier-pas` | premiers_pas |
| `chapeau_pion` | tete | `quizz_nsi` | `tour-du-plateau` | exploration |
| `flamme_apprivoisee` | autour | `quizz_nsi` | `rebond` | perseverance |
| `micro_paillettes` | main | `grand_oral` | `premier-passage` | premiers_pas |
| `noeud_chrono` | cou | `grand_oral` | `ni-trop-ni-trop-peu` | maitrise |
| `projecteur_poursuite` | autour | `grand_oral` | `vous-avez-un-sujet` | creation |
| `case_surprise` | main | `calendrier` | `premiere-case` | premiers_pas |
| `bob_fanion` | tete | `calendrier` | `costaud` | maitrise |
| `guirlande_cases` | autour | `calendrier` | `tous-les-themes` | exploration |
| `monocle_hublot` | visage | `gombessa` | `la-luciole-avance` | premiers_pas |
| `collier_sonar` | cou | `gombessa` | `les-grottes-du-gombessa` | exploration |
| `bulle_luci` | epaule | `gombessa` | `debogage` | perseverance |
| `casque_carapace` | tete | `lagon` | `ponte-reussie` | premiers_pas |
| `bebe_tortue` | epaule | `lagon` | `rematch` | perseverance |
| `palmes_lagon` | pieds | `lagon` | `le-parcours` | exploration |

Les noms, les noms des hauts faits et leurs conditions : `Equipage.applis` et `assets/equipage/applis.json`. Récompense au compte commun : `<emplacement>:<id>` (par exemple `main:de_flottille`).

## 6. Vérifier

- `node charte/tester-equipage.js` : l'existant ne change pas (même image au caractère près), les 15 objets, les états d'usage, les phrases, les fichiers de données.
- `python3 -I -B charte/tester-applis.py [--lent]` : l'interface dans une page (bulles, marques, plafond, calme, pause), le coût de 35 avatars, `charte/applis.html` à 320, 768 et 1440 px en clair et en obscur.

Auteur : Babash - NSI Tani Malandi. Code sous licence MIT ; dessins CC BY-SA 4.0.
