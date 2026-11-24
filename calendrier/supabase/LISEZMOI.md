# Calendrier des vacances : la base

*T105, version de Noël 2026. **`vacances_0001_calendrier` et `base_unique_0009_registre_vacances` sont appliquées le 20/11 (15:31 et 15:33, version `0ecbb1d`) ; `vacances_0002_index_resultats` est appliquée le 24/11 à 13:30 (version 20261124103014), par le chef d'orchestre.** L'enseignant a vu le fichier et délégué (20/11, 14:55, au chef d'orchestre) ; le Gardien relit, puis le chef d'orchestre applique (`apply_migration`). Spécification : `architecture-calendrier-vacances.md` (livrable T105).*

- **Projet :** `cukahpyqkljiddmimpyi` (« Babash - applications »), la base unique.
- **Schéma :** `vacances`. Il n'est pas exposé à l'API, et `anon` comme `authenticated` n'y ont aucun droit.
- **Préfixe des fonctions d'entrée :** `cv_`.
- **Liste de mots :** « les jeux et les loisirs », 64 mots. Elle a été contrôlée contre les cinq listes en service et contre celle du compte commun (T101, « la ville et le réseau ») : aucun recouvrement, aucun mot qui soit le début d'un autre. SKATE, ROLLER, VELO et MANETTE, déjà pris par T101, ont été remplacés par TAQUIN, RALLYE, HOCKEY et SQUASH.
- **Les thèmes (précision de l'enseignant, 20/11, 15:20) :** un calendrier se compose de 1 à 20 thèmes (chapitres ou notions), cochés librement, sans lien avec le niveau de la classe ; les cases alternent entre eux (`mode = 'alternance'`, par défaut), ou une case par thème et par jour (`chaque_theme`). Colonnes `calendriers.themes` et `cases.theme`.
- **Le score :** les étoiles, les cases faites, les rattrapages et les **jours différents** où l'élève a réussi au moins une case. Il n'y a ni série, ni classement, ni rang.

## Les fichiers, dans l'ordre

| Fichier | Nom de migration | Ce qu'il fait |
|---|---|---|
| `calendrier/supabase/0001-calendrier.sql` | `vacances_0001_calendrier` | Crée le schéma, 9 tables, 15 fonctions internes et les 22 fonctions d'entrée. |
| `calendrier/supabase/0001-calendrier-inverse.sql` | — | Retire tout. **Efface les comptes et les résultats** : l'enseignant exporte d'abord les tables (M8). |
| `calendrier/supabase/schema.sql` | — | Le script complet de l'application, pour installer une copie (après le `schema.sql` du socle) : aujourd'hui, le même texte que `0001`. |
| `calendrier/supabase/0002-index-resultats.sql` (et son inverse) | `vacances_0002_index_resultats` | Ajoute l'index `vacances.resultats_case (calendrier_id, numero)`, qui couvre la clé étrangère des résultats vers les cases (conseiller de performance 0001, relevé après l'application du 20/11). **Appliqué le 24/11 à 13:30 (version 20261124103014)** ; vérifié en lecture : l'index et son commentaire sont en base, identiques au fichier. L'inverse retire l'index sans rien effacer. |
| `supabase/0009-registre-vacances.sql` | `base_unique_0009_registre_vacances` | Ajoute le schéma `vacances` et le préfixe `cv_` à la vue `commun.registre`. Il passe avant ou après `0001`, et avant ou après `0007` et `0008` du compte commun (T101), qu'il ne touche pas. |
| `supabase/0009-registre-vacances-inverse.sql` | — | Remet la vue de `0006`, sans rien effacer. |

**Ordre proposé :** `vacances_0001_calendrier`, puis `base_unique_0009_registre_vacances`.

**Le numéro 0009 :** `0006` est le dernier du socle appliqué (`list_migrations`, 20/11). `0007` et `0008` sont écrits par T101 (branche `archi/t101-compte-commun`) et ne sont pas appliqués. `0009` ne se heurte donc à rien.

Par `apply_migration`, on retire seulement les lignes `begin;` et `commit;`.

## Les fonctions d'entrée (attendues au conseiller 0028)

**Élèves (10) :**
- `cv_calendrier_par_code(text)`
- `cv_inscription(text, text)`
- `cv_connexion(text)`
- `cv_rejoindre(uuid, text)`
- `cv_reprise(uuid)`
- `cv_calendrier(uuid, uuid)`
- `cv_resultat(uuid, uuid, integer, integer, boolean, integer, integer, integer, integer)`
- `cv_classe(uuid, uuid)`
- `cv_deconnexion(uuid)`
- `cv_effacer_moi(uuid)`

**Enseignant·e·s (12) :**
- `cv_prof_creer_espace(text)`
- `cv_prof_ouvrir(text)`
- `cv_prof_creer_calendrier(text, text, date, date, text[], text, text)`
- `cv_prof_modifier_calendrier(text, uuid, text, date, date, text[], text, text)`
- `cv_prof_tableau(text, uuid)`
- `cv_prof_inscriptions(text, uuid, boolean)`
- `cv_prof_nouveau_code_eleve(text, uuid, uuid)`
- `cv_prof_renommer_eleve(text, uuid, uuid, text)`
- `cv_prof_retirer_eleve(text, uuid, uuid, text)`
- `cv_prof_supprimer_calendrier(text, uuid, text)`
- `cv_prof_debloquer_reseau(text)`
- `cv_prof_nouveau_code(text)`

Toutes sont `security definer`, avec `search_path = ''`, propriétaire `postgres` et appelables par `anon` seul. Leurs règles communes :
- elles bornent chaque paramètre ;
- elles répondent `{ "ok": false, "message" }` plutôt que de lever une exception ;
- elles comptent les échecs de code dans `commun.essais`, avec l'application `vacances`.

Les seuils, par heure et par réseau :

| Échec ou création | Seuil |
|---|---|
| Code d'élève faux | 20 |
| Code d'enseignant·e faux | 10 |
| Code de calendrier faux | 30 |
| Création de compte | 60 |

## Les données gardées, et combien de temps

- **Pour chaque élève :**
  - un prénom ou un pseudo (2 à 24 caractères, jamais le nom de famille) ;
  - le code ;
  - un jeton par appareil (5 au plus) ;
  - les calendriers rejoints ;
  - pour chaque case jouée et chaque niveau : réussite, étoiles, nombre d'essais, nombre de coups de pouce, durée, date, et « avant ou après le corrigé ».

  **Jamais les réponses tapées**, ni le nom de famille, ni l'adresse électronique, ni l'adresse IP en clair : seulement son empreinte du jour, dans `commun.essais`, effacée après 24 h.
- **Pour chaque enseignant·e :** le nom affiché (un exemple neutre : « Mme N. ») et l'empreinte du code.
- **Les durées.** Le ménage passe au plus une fois par heure, **au premier usage de l'application après l'échéance** : rien ne s'efface tant que personne n'ouvre l'application.

  | Données | Effacées au premier usage de l'application après… |
  |---|---|
  | Le compte d'un·e élève, ses inscriptions et ses résultats | 12 mois sans visite |
  | Un calendrier, ses cases et ses résultats | 12 mois après sa fin |
  | Un espace d'enseignant·e, avec ses calendriers | 24 mois sans ouverture |
  | Une session | 30 jours sans usage |
- **Effacer avant :**
  - l'élève : « Effacer mes données » (`cv_effacer_moi`) ;
  - l'enseignant·e : retirer un·e élève ou supprimer un calendrier ;
  - en dernier recours : le tableau de bord de Supabase.
- **Sur l'appareil de l'élève** (le stockage du navigateur, clés `cv:`), rien d'autre que :
  - la session : le jeton, le prénom ou pseudo et le code, pour les montrer dans « Mon compte » ;
  - la partie en cours (les réponses de la partie pas finie, pour la reprendre) ;
  - les résultats pas encore reçus par la base (envoi différé, quand le réseau manque) ;
  - le calendrier choisi, et le fait que le code a été noté.

  Tout, sauf la session, est rattaché à l'élève par une **empreinte de son code** (pas le code lui-même). Un résultat en attente n'est envoyé qu'avec la session de l'élève qui l'a produit : si Lou joue sans réseau, quitte (« Ce n'est pas moi »), puis Sam entre sur le même téléphone, le résultat de Lou n'est ni montré à Sam ni envoyé avec son jeton ; il partira si Lou revient sur ce téléphone avec son code avant l'échéance.

  **L'échéance :** 1 jour après l'écriture, ou 30 jours si l'élève a coché « C'est mon téléphone » (la session : 1 jour ou 30 jours après l'entrée). Après l'échéance, rien n'est plus lu, et tout est effacé à l'ouverture suivante de la page sur cet appareil (une page fermée ne peut rien effacer). « Effacer mes données » efface aussi tout ce que l'appareil garde de l'élève ; « Ce n'est pas moi » ferme la session et laisse seulement les résultats en attente, jusqu'à leur échéance. L'état du calendrier n'est gardé qu'en mémoire, le temps que la page est ouverte. Le choix clair ou obscur (clé `theme`, la même que sur le reste du site depuis T135) n'est rattaché à personne.
- **Les essais au hasard.** Un code faux, un lien de calendrier faux et **un prénom déjà pris** comptent comme des essais. Les seuils, par heure et par réseau : 20 essais pour un code d'élève, 10 pour un code d'enseignant·e, 30 pour un calendrier (lien ou prénom), 60 créations.

### Le texte du champ `donnees_eleves` de la fiche (à transmettre au Bibliothécaire)

> Le Calendrier des vacances garde en ligne, dans la base de l'enseignant (Supabase, schéma `vacances`), le prénom ou le pseudo choisi par l'élève (jamais le nom de famille), son code d'accès et, pour chaque case jouée, le niveau, la réussite, les étoiles, le nombre d'essais et de coups de pouce, la durée et la date. Les réponses tapées ne sont jamais envoyées. Un compte est effacé au premier usage de l'application après 12 mois sans visite ; un calendrier et ses résultats, au premier usage après 12 mois suivant sa fin. Sur le téléphone ou l'ordinateur de l'élève, la page garde la session, la partie en cours et les résultats pas encore envoyés (quand le réseau manque), rattachés à l'élève par une empreinte de son code : un résultat n'est jamais envoyé pour un·e autre élève. Ces données ne sont plus lues après 1 jour (30 jours si l'élève a coché « C'est mon téléphone »), et elles sont effacées à l'ouverture suivante de la page. L'élève peut tout effacer à tout moment, en ligne et sur l'appareil (« Effacer mes données ») ; l'enseignant·e peut retirer un·e élève ou supprimer un calendrier. Aucun classement : la classe ne voit que des nombres, sans aucun nom, et seulement si l'enseignant·e a choisi de les montrer.

## Vérifier après l'application (métadonnées seulement)

Les requêtes a à f du § 6 des règles des bases, plus celles-ci :

```sql
-- les 9 tables ont la RLS, et aucun droit pour anon ni authenticated (attendu : 9 lignes, rls = true, droits = false)
select c.relname, c.relrowsecurity as rls,
       has_table_privilege('anon', c.oid, 'select') or has_table_privilege('authenticated', c.oid, 'select') as droits
from pg_class c where c.relnamespace = 'vacances'::regnamespace and c.relkind = 'r' order by 1;
-- le schéma est fermé (attendu : false)
select has_schema_privilege('anon', 'vacances', 'usage');
-- 22 fonctions cv_ appelables par anon seul (attendu : 22)
select count(*) from pg_proc p where p.pronamespace = 'public'::regnamespace and p.proname like 'cv\_%'
  and has_function_privilege('anon', p.oid, 'execute') and not has_function_privilege('authenticated', p.oid, 'execute');
-- 64 mots ; 0 compte juste après l'application (count(*) seulement)
select (select count(*) from vacances.mots) as mots, (select count(*) from vacances.eleves) as comptes;
```

**Conseillers attendus :**
- 0008 (RLS sans règle) pour les 9 tables ;
- 0028 pour les 22 fonctions `cv_`.

Rien d'autre.

## Essayé en local

Les essais ont été faits le 20/11, et rejoués après les corrections de l'après-midi (jours différents, liste de mots, numéro 0009), sur Postgres 16, avec les migrations `0001` et `0003` du site. Le droit `maintain`, qui n'existe qu'en Postgres 17, a été retiré pour ces essais seulement. Le script d'essai est `essais-locaux.sql` (à lancer dans une base locale qui a le socle, jamais sur la base en ligne). Ce qui a été vérifié :
- la migration se relance sans erreur, et l'inverse retire tout ;
- les codes ont leur forme, et ils sont lus avec tolérance ;
- les refus marchent : doublon de prénom, caractère invisible, 31 jours, case à venir, étoiles impossibles ;
- au jour 5, les cases sont dans le bon état : deux corrigées, trois ouvertes, les autres à venir ;
- un rattrapage est compté à part, et un moins bon résultat ne remplace pas le meilleur ;
- une modification après le début ne touche pas aux cases déjà ouvertes ;
- en mode « chaque thème », trois cases au plus sont à faire, et les autres attendent ;
- un nouveau code ferme les anciennes sessions ;
- la suppression demande une confirmation ;
- le compteur bloque après 20 échecs ;
- `anon` ne lit aucune table.

Aucune base Supabase n'a été modifiée.
