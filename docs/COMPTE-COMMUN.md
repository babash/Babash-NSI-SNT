# Le compte commun : un code pour toutes les applications

*Mode d'emploi du module `assets/compte-commun.js` (T101b, T132d). Retour au [sommaire](README.md).*

Un·e élève a **un seul code** (deux mots et trois chiffres, comme `PIRATE-ETRAVE-772`), un compte et un avatar pour toutes les applications. Un·e enseignant·e a **un seul code** (trois mots et quatre chiffres) pour ses classes, ses élèves et les tableaux de bord. La base : les fonctions `commun_…` du projet Supabase (SQL `supabase/0007-compte-commun.sql` et `0008-enseignants-communs.sql`, en base depuis le 24/11/2026).

## Les pages du site

| Page | Pour qui | Ce qu'on y fait |
|---|---|---|
| `eleve/` (« Ma planque ») | l'élève | créer son code (seul·e ou par le lien de classe `eleve/?classe=ABCD`), entrer avec son code, « Mon avatar », ses hauts faits, sa classe, la carte de son code à imprimer, « Ce n'est pas moi », « Effacer mes données » |
| `enseignant/` | l'enseignant·e | créer son espace (le code est montré une seule fois), ses classes (lien et QR code faits dans la page), ses élèves (avatar, hauts faits, nouveau code), le mode projection, les tableaux de bord des applications, supprimer son espace |

Le réglage `COMPTE_COMMUN_EN_LIGNE` de `reglages.js` choisit le mode : `false`, une démonstration en mémoire (rien n'est envoyé) ; `true`, la base. Trois réglages taisent ce qui n'existe pas encore, et s'allument chacun après sa migration :
- `COMPTE_COMMUN_NIVEAU` : le choix du niveau (migration du niveau) ;
- `COMPTE_COMMUN_APPLICATIONS` : les codes et les espaces des applications, les crédits qu'elles donnent (première application branchée) ;
- `COMPTE_COMMUN_CATALOGUE` : « Offrir un trophée » et « Archiver la classe » (migration 0010), à mettre à `true` une fois 0010 en base.

La boutique, les hauts faits, les trophées et les pièces libres de la loge (kishali, bandana) suivent, eux, le catalogue lu en base, sans réglage : avant 0010, ils sont annoncés pour bientôt, sans être proposés (`commun_porter` refuserait les pièces) ; après, la boutique dit que, pour l'instant, seul·e l'enseignant·e donne des crédits (l'XP attribuée et les hauts faits accordés), et les hauts faits des applications qui ne lisent pas encore le compte restent marqués « Bientôt ».

## Les règles que le module garantit

- **Jamais de code ni de jeton dans une adresse.** Les appels partent en `POST`, dans le corps. Un `?code=` ou un `?jeton=` trouvé dans l'adresse est retiré et ignoré. Seul le code de classe (4 lettres, public) peut être dans un lien.
- **La garde du jeton** : dans l'onglet seulement (`sessionStorage`, 1 jour au plus) ; avec « C'est mon téléphone », dans le navigateur (`localStorage`, 30 jours après l'entrée du code sur l'appareil ; la base, elle, accepte le jeton jusqu'à 30 jours après son dernier usage). Tous les sites de `babash.github.io` ont la même origine : une application lit le jeton posé par une autre.
- **Le code de l'enseignant·e** reste en mémoire de la page ; avec « Rester ouvert dans cet onglet », dans l'onglet. Jamais dans le navigateur.
- **Lecture tolérante d'un code** : majuscules ou minuscules, espaces, tirets ou rien, accents : `pirate etrave 772` vaut `PIRATE-ETRAVE-772`.
- **Jamais d'exception** : chaque appel rend une promesse `{ ok: true, … }` ou `{ ok: false, message }`, avec un message en français (code faux, trop d'essais, hors ligne, base injoignable). Une page ne s'arrête jamais à cause du compte commun.
- **Une seule clé** : la clé publique (« publishable ») du projet. Le module refuse une clé « secret » ou « service_role ».
- **Aucune dépendance**, aucune requête vers un autre hôte que la base (et le site pour l'avatar).

## Brancher une application (exemple de 15 lignes)

```html
<div id="mon-compte"></div>
<script src="https://babash.github.io/Babash-NSI-SNT/assets/compte-commun.js"></script>
<script>
  if (window.CompteCommun) {                         // le site peut être injoignable : le jeu continue
    CompteCommun.configurer({ en_ligne: true, url: 'https://cukahpyqkljiddmimpyi.supabase.co',
                              cle_publique: 'sb_publishable_…' });   // la clé de reglages.js du site
    CompteCommun.bandeau(document.getElementById('mon-compte'), { application: 'quizz_nsi' });
    var qui = CompteCommun.qui();                    // { pseudo } si un compte est ouvert sur l'appareil
    if (qui) {
      CompteCommun.reprendre().then(function (r) {   // la fiche : pseudo, avatar, hauts faits
        if (r.ok) demarrer(r.fiche.pseudo, r.fiche.avatar);   // « Continuer en tant que Zoé ? »
        else demarrer(null);                         // session expirée : on joue avec un pseudo
      });
    } else demarrer(null);
  }
</script>
```

## L'interface

| Appel | Rend |
|---|---|
| `configurer(reglages)` | le mode, `'demo'` ou `'supabase'` |
| `creer(pseudo, { appareil, niveau })` | `{ ok, code_affiche, fiche }` (le jeton reste dans le module) |
| `entrer(code, { appareil })`, `reprendre()`, `quitter()` | la fiche ; `quitter` ferme le compte sur l'appareil (« Ce n'est pas moi ») |
| `qui()`, `connecte()` | le pseudo gardé avec le jeton, sans appel |
| `porter(avatar)`, `renommer(pseudo)`, `lierCode(code)`, `effacerMoi('EFFACER')` | le résultat |
| `classeParCode(code)`, `rejoindre(code)`, `maClasse()` | la classe ; ses camarades (pseudo, avatar, hauts faits ; jamais d'XP, de crédits ni de codes) |
| `evenementPage('td', 'feuille_validee', cle)` | les crédits du barème (feuilles de TD seulement : un téléphone de QuizzNSI ne se donne rien) |
| `bandeau(element, { application })` | le bandeau « Zoé · mes applications » |
| `dessinerAvatar(element, avatar, options)` | l'avatar, par le moteur `assets/equipage.js` |
| `prof.creerEspace`, `prof.ouvrir`, `prof.creerClasse`, `prof.modifierClasse`, `prof.classe`, `prof.nouveauCodeEleve`, `prof.supprimerEspace`… | l'espace enseignant·e |
| `disponible(fonction)` | faux pour une fonction d'une migration à venir (`commun_prof_offrir` : 0010 ; le niveau : T132e) |

## Essayer

- La démonstration : `reglages.js` à `false`, puis `eleve/` et `enseignant/` (codes `DEMO-…`). Test : `scripts/tests/test_compte_commun.py`.
- En ligne, sur une base **locale** (jamais la base réelle) : `python3 -I -B scripts/tests/test_compte_commun_en_ligne.py --psql "psql -h … -p … -U postgres"` reconstruit la base avec les fichiers de `supabase/`, imite l'API (`scripts/calendrier_serveur_essai.py`) et joue les parcours à 320, 768 et 1440 px, en clair et en obscur.
