// Calendrier des vacances : configuration.
// La base est le projet Supabase partagé des applications du site (schéma vacances,
// calendrier/supabase/0001-calendrier.sql). La clé ci-dessous est la clé « publishable »
// du projet : elle est publique par conception (envoyée dans l'en-tête apikey).
// EN_LIGNE : true seulement quand la migration vacances_0001_calendrier est appliquée dans la base
// (règle M7 : la page n'appelle que des fonctions qui existent). Tant que c'est false, les pages le disent.
// Pour installer ta copie : l'adresse et la clé publique de ton propre projet, après le schema.sql du socle
// (supabase/schema.sql) puis celui de l'application (calendrier/supabase/schema.sql).
window.CV_CONFIG = {
  SUPABASE_URL: 'https://cukahpyqkljiddmimpyi.supabase.co',
  SUPABASE_KEY: 'sb_publishable_dYwCrwaqiDOm8knczJu3Kw_5InHwyPB',
  EN_LIGNE: false,
  DEPOT: 'https://github.com/babash/Babash-NSI-SNT',
  // Les dates proposées par défaut à l'enseignant·e (vacances de Noël 2026-2027 à Mayotte :
  // du samedi 12/12/2026 au lundi 11/01/2027, reprise le matin). À tenir à jour chaque année.
  VACANCES: [
    { nom: 'Vacances de Noël 2026-2027', debut: '2026-12-12', fin: '2027-01-10' },
    { nom: 'Vacances de février 2027', debut: '2027-02-20', fin: '2027-03-07' }
  ]
};
