# Alien Python – entraînement en ligne

Site statique (HTML/JS) pour s'entraîner sur les 78 exercices d'[Alien-Python](https://forge.apps.education.fr/DegrangeM/alien-python) (M. Degrange, licence MIT) : validation, coups de pouce, correction, badges, avancement de la classe, et tableau de bord enseignant. La progression est stockée dans Supabase.

## Mise en route (10 minutes)
1. **Supabase** : déjà fait pour le projet « SNT-1er Jour » (tables `alien_*` créées à côté des tables existantes, `config.js` renseigné). Pour un autre projet : *SQL Editor* → coller `supabase.sql` → *Run*, puis mettre l'URL et la clé « anon public » dans `config.js`.
3. **GitHub Pages** : *Settings > Pages* → source « Deploy from a branch », branche `main`, dossier `/ (root)`.
4. **Enseignant** : ouvrir `…/index.html#prof` → « Créer une classe » (nom + code enseignant secret). On obtient un **code classe** à donner aux élèves.
5. **Élèves** : « Nouvel élève » (code classe + prénom) → un **code personnel à 4 chiffres** leur est donné ; ils le réutilisent avec « J'ai déjà un code ». L'enseignant voit tous les codes dans son tableau de bord.

## Sécurité (à connaître)
- Les tables sont verrouillées (RLS) ; le site passe uniquement par des fonctions qui vérifient les codes. Le code enseignant est haché.
- Les codes élèves (4 chiffres) sont faits pour la simplicité, pas pour protéger des données sensibles : ne saisir que des **prénoms**, pas de noms de famille.
- N'importe qui connaissant l'adresse du site peut créer une classe ; si besoin, surveiller le tableau `classes` dans Supabase.

## Limites actuelles
- Exercices 1–62 : réponse = clic sur la case d'arrivée. Séries A/B : le programme complété est comparé à la solution (espaces ignorés) ; une solution équivalente mais écrite autrement sera refusée (la correction reste disponible).
- Pas de mot de passe élève, pas de suppression d'élève depuis le site (à faire dans Supabase > Table Editor).
