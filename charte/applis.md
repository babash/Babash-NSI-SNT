# Habiller une application : le socle et le moteur d'avatars

Mode d'emploi pour les applications de jeu (QuizzNSI, Hello GO, Calendrier des vacances, Expédition Gombessa, Lagon Arena, Alien Python et les suivantes). Décisions de l'enseignant du 24/11 (T133) : « piste B » (le design du site, plus une touche légère par application) ; pendant la question, la variante discrète ; l'Esprit en capuche pour les joueurs et joueuses sans compte ; les pseudos visibles au lobby, masquables d'un clic ; les 18 objets des applications. Démonstration : [`charte/applis.html`](applis.html).

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

`data-appli` donne la touche propre : `quizz-nsi`, `hello-go`, `calendrier`, `gombessa`, `lagon-arena` ou `alien-python` (T137 : la règle graduée et le signal en traits et en points, le viseur de la grille, l'alien vert à antennes ; ses classes `al-…` : code coloré, éditeur à miroir, grille). Elle ne change que le décor (`.ap-touche`, sous la barre du haut) et le néon des ombres (`--ap-touche`) : jamais une couleur de texte.

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

## L'avatar pendant une séance

- **Règle** (proposée par le chef d'orchestre, sauf avis contraire de l'enseignant) : l'avatar est pris à l'entrée dans la séance ; il peut encore changer au lobby ; il reste figé de la première question au podium. Un objet gagné pendant la séance est annoncé sur le téléphone (`ap-annonce`) et porté à la séance suivante.
- **Sur le téléphone, à côté de la question** (demande de l'enseignant du 24/11, 11:16) : le buste de l'élève est dans la barre du haut, à côté du chrono (`<span class="ap-moi-q"><span>…avatar…</span><span class="ap-chrono-tel">18 s</span></span>`, `taille: 40, cadre: 'buste'`). Il ne prend aucune place sur la question ni sur le code, même à 320 px. Il réagit comme sur l'écran projeté : `etat('attente')` pendant la question ; `etat('repondu')` (fanion) et `serie(n)` (flamme) après avoir répondu ; à la correction, `etat('fete')` si c'est juste, `etat('lobby')` si c'est faux (au repos : rien de moqueur, jamais triste). Sans compte : `Equipage.neutre()`. Avec le réglage « mouvement réduit », tout est en image fixe.

Masquer les pseudos d'un clic : la classe `ap-sans-pseudos` sur `.ap-plateau` (la place reste, rien ne saute).

## 3. L'interface du moteur (version 2.1.0)

Déjà là (inchangé) : `Equipage.creer(element, description, options)`, `svg`, `texte`, `normaliser`, `aleatoire`, `margouillat`, `compagnonSVG`, `catalogue`, les sept états, les trois cadres. Contrat complet : [`assets/equipage/LISEZMOI.md`](../assets/equipage/LISEZMOI.md).

| Ajout | Rôle |
|---|---|
| `etat: 'lobby' \| 'attente' \| 'repondu' \| 'fete' \| 'applaudit'` | états d'usage, alias de `repos`, `concentre`, `repos` avec le fanion, `tres_content`, `content` (`Equipage.USAGES`) |
| `poignee.geste(nom, { duree })` | `'salue'`, `'saute'`, `'rit'`, `'sieste'`, `'tempete'` (`Equipage.gestes`) : joue l'état (3 s par défaut, 1,8 s pour la tempête, 20 s au plus), puis revient ; nom inconnu : `false` ; un geste compte dans le plafond d'avatars animés |
| `poignee.bulle(numero, null, { duree })` | une phrase de la liste FERMÉE du moteur, `Equipage.phrases` (21 phrases, de 0 à 20) ; le 2e argument ne peut être que `undefined`, `null` ou `'lobby'` : tout tableau ou objet fourni par l'appelant est refusé (`false`, rien d'affiché), jamais de texte libre ; numéro non entier ou inconnu : ignoré (`false`) ; 6 bulles au plus par page, les autres attendent ; 5 s par défaut (`{ duree }` en 3e argument) ; la bulle reste dans le plateau (`.ap-plateau` ou un parent `[data-eq-bord]`) et dans la largeur de la page : décalée de côté, sa pointe reste au-dessus de l'avatar ; deux lignes au plus au lobby (`--eq-bulle-max: 12em`), sous un écart de rangée qui ne cache jamais le pseudo du dessus ; texte posé avec `textContent`, jamais du HTML |
| `poignee.marque('repondu' \| null)` | le fanion « a répondu » ; `etat('lobby' \| 'attente' \| 'fete' \| 'applaudit')` l'enlève : il ne reste jamais sur le podium |
| `poignee.serie(n)` | la flamme et son chiffre, à partir de 2 ; `serie(0)` l'enlève |
| `Equipage.calme(true \| false \| null)` | toute la page en image fixe ; `Equipage.calme()` dit si la page est calme (forcée, ou réglage « mouvement réduit » de l'appareil) |
| `Equipage.plafond(8)` | au plus 8 avatars animés à la fois (les gestes passent devant), les autres en image fixe ; `plafond(null)` l'enlève |
| `Equipage.pause(true \| false)` | arrête les animations ; automatique quand l'onglet est caché |
| `Equipage.adresse('monsieur' \| 'madame')` | la forme des phrases qui s'adressent à l'enseignant·e (la 19 : « Ne vous inquiétez pas, Monsieur. » ou « … Madame. ») : un réglage de la page projetée, « Monsieur » par défaut ; l'élève envoie toujours le même numéro. `Equipage.phrase(n)` donne le texte affiché, `Equipage.variantes` les numéros concernés |
| `own` (interne) | une chaîne de l'appelant ne sert de clé que si le moteur l'a en propre : `constructor`, `toString`, `__proto__`… sont ignorés (états, gestes, adresses, couleurs, cadres, compagnons, bords) |
| `Equipage.neutre()` | l'Esprit en capuche, le même pour tous (une copie) |
| `Equipage.applis` | les 18 objets des applications, avec leur haut fait |
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

## 5. Les 18 objets des applications (famille `applis`)

Dessinés dans le moteur, accrochés au corps (l'objet tenu suit la main dans chaque pose de bras, le chapeau suit la tête). Ce sont des trophées : jamais achetés, jamais tirés au hasard. Emplacement `epaule` : sur les épaules.

Identifiants, noms, catégories et conditions alignés sur la migration 0010 de l'Architecte (application `vacances` pour le Calendrier ; `de_flottille` est donné par `jusqu-au-bout`, `monocle_hublot` par `premiere-plongee`, décision du 24/11).

| Objet (`id`) | Emplacement | Application | Haut fait (`id`, nom) | Catégorie |
|---|---|---|---|---|
| `de_flottille` | main | `quizz_nsi` | `jusqu-au-bout` (« Jusqu’au bout ») | premiers_pas |
| `chapeau_pion` | tete | `quizz_nsi` | `tour-du-plateau` (« Tour du plateau ») | exploration |
| `flamme_apprivoisee` | autour | `quizz_nsi` | `rebond` (« Rebond ») | perseverance |
| `micro_paillettes` | main | `grand_oral` | `premier-passage` (« Premier passage ») | premiers_pas |
| `noeud_chrono` | cou | `grand_oral` | `ni-trop-ni-trop-peu` (« Ni trop ni trop peu ») | maitrise |
| `projecteur_poursuite` | autour | `grand_oral` | `vous-avez-un-sujet` (« Tu as un sujet ! ») | creation |
| `case_surprise` | main | `vacances` | `premiere-case` (« Première case ») | premiers_pas |
| `bob_fanion` | tete | `vacances` | `costaud` (« Costaud ») | maitrise |
| `guirlande_cases` | autour | `vacances` | `tous-les-themes` (« Trois thèmes explorés ») | exploration |
| `monocle_hublot` | visage | `gombessa` | `premiere-plongee` (« Première plongée ») | premiers_pas |
| `collier_sonar` | cou | `gombessa` | `les-grottes-du-gombessa` (« Les grottes du gombessa ») | exploration |
| `bulle_luci` | epaule | `gombessa` | `debogage` (« Débogage ») | perseverance |
| `casque_carapace` | tete | `lagon` | `ponte-reussie` (« Ponte réussie ») | creation |
| `bebe_tortue` | epaule | `lagon` | `rematch` (« Rematch ») | perseverance |
| `palmes_lagon` | pieds | `lagon` | `le-parcours` (« Le parcours ») | exploration |
| `antennes_ecoute` | tete | `alien` | `sur-la-piste` (« Sur la piste ») | exploration |
| `decodeur_poche` | main | `alien` | `a-l-envers` (« À l’envers ») | creation |
| `halo_coordonnees` | autour | `alien` | `le-grand-tour` (« Le grand tour ») | maitrise |

Les noms, les noms des hauts faits et leurs conditions : `Equipage.applis` et `assets/equipage/applis.json`. Récompense au compte commun : `<emplacement>:<id>` (par exemple `main:de_flottille`).

## 5 bis. Ajouts du 24/11 (T133c)

- **La bouteille d'eau percée**, `main:bouteille_percee` (famille `classe`, « Les gimmicks de la classe » : un trophée offert par l'enseignant·e, jamais acheté ; décision du 24/11, 12:33) : une bouteille en plastique transparent au bouchon percé, sans marque ni étiquette. Tenue au repos ; pendant un geste (bras levé ou ouvert), un mince jet monte du bouchon, toujours vers le haut, jamais vers quelqu'un.
- **Le geste « tempête »**, `geste('tempete')` (5e geste, état du moteur `tempete`, « tourbillonne ») : un tour sur soi-même (de face, de profil, en miroir) dans un petit tourbillon de traits de vent, avec une feuille, une goutte et une graine emportées ; 6 images, 1,8 s, puis retour à l'état d'avant. Image fixe (de face, avec le tourbillon) avec « mouvement réduit » ou `Equipage.calme(true)`.
- **Les objets des hauts faits de fidélité** (famille `fidelite`, des trophées ; noms à confirmer par l'enseignant ; `Equipage.fidelite`) : `autour:aura_etincelle` (« Deuxième saison » : trois étoiles), `autour:aura_halo` (« Troisième saison » : une orbite en pointillés à la taille, qui passe derrière le corps, et quatre étoiles), `autour:aura_supernova` (« Supernova » : deux orbites, des rayons en pointillés derrière le corps et quatre grandes étoiles), `dos:ailes_circuit` (« Nouveau palier » : des pistes de cuivre à angles droits, des pastilles qui s'allument). Une montée en puissance par paliers, sans flammes ni cheveux dressés ; contour sombre, lisible en noir et blanc.
- **Le kishali et le bandana, libres pour tout le monde** (décision du 24/11, 12:34) : `epaule:kishali` (« Kishali sur les épaules », déjà dessiné), `tete:kishali_tete` (« Kishali sur la tête », nouveau) et `tete:bandana` (« Bandana à pois », déjà dessiné). Le catalogue les marque `libre: true` : ni crédits ni haut fait, proposés dans la loge avec les tenues de base, sur tout avatar. Sous le kishali porté sur la tête, les cheveux sont rangés (aucune mèche ne dépasse, quelle que soit la coiffure) ; sa couleur et son motif viennent des couleurs de l'avatar.
- **Le dessin de Karim**, `main:dessin_karim` (famille `classe` : un trophée offert, jamais acheté) : une feuille de classeur (trous, marge rouge, lignes bleues) où est griffonné un margouillat, tenue levée. Haut fait proposé : « Coup de crayon » (catégorie `creation`, accord de l'enseignant·e : un dessin, un schéma ou une illustration qui aide la classe). Le nom affiché est une donnée du catalogue (il peut devenir « Le dessin du fond de la classe » si l'élève préfère ne pas être nommé) : l'identifiant, lui, ne change pas.
- Ces objets ne sortent jamais de `Equipage.aleatoire` : les tirages au hasard des pages existantes ne changent pas.

## 6. Vérifier

- `node charte/tester-equipage.js` : l'existant ne change pas (même image au caractère près), les 18 objets, les états d'usage, les phrases, les fichiers de données.
- `python3 -I -B charte/tester-applis.py [--lent]` : l'interface dans une page (bulles, marques, plafond, calme, pause), le coût de 35 avatars, `charte/applis.html` à 320, 768 et 1440 px en clair et en obscur.

Auteur : Babash - NSI Tani Malandi. Code sous licence MIT ; dessins CC BY-SA 4.0.
