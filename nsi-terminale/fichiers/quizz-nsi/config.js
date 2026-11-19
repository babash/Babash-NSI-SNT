// QuizzNSI : configuration (MIT, Babash - NSI Tani Malandi).
// Le mode « tous ensemble » passe par les canaux temps réel (diffusion et présence) du projet Supabase
// partagé des applications du site, sans aucune table : rien n'est enregistré en ligne.
// La clé ci-dessous est la clé publique « publishable » du projet : elle est publique par conception
// (jamais de clé « secret » ou « service_role » ici).
// Pour ta copie : mets l'adresse et la clé publique de ton propre projet Supabase (offre gratuite),
// ou laisse SUPABASE_URL vide : la séance passe alors en mode démo (entre les onglets d'un même navigateur).
window.QUIZZ_CONFIG = {
  SUPABASE_URL: 'https://cukahpyqkljiddmimpyi.supabase.co',
  SUPABASE_KEY: 'sb_publishable_dYwCrwaqiDOm8knczJu3Kw_5InHwyPB',
};
