# Calendrier des vacances : la base

*T105, version de Noël 2026 (20/11/2026). **Rien n'est appliqué.** L'enseignant a vu le fichier et délégué (20/11, 14:55, au chef d'orchestre) ; le Gardien relit, puis le chef d'orchestre applique (`apply_migration`). Spécification : `architecture-calendrier-vacances.md` (livrable T105).*

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
