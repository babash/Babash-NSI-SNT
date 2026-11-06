/* ═══════════════════════════════════════════════════════════════
   L'équipage : neuf runners originaux, trois profils, et dans
   chaque profil une femme, un homme et une personne indéterminée.
   Dessin original (aucun personnage de jeu existant).
   Portraits : assets/equipage/<id>-nuit.svg (écran) et -trait.svg (papier).
   Utilisé par la page d'accueil (section « L'équipage »).
   Rien à modifier ici sans passer par l'agent de design.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  var RUNNERS = [
 {
  "id": "kestrel",
  "nom": "Kestrel",
  "profil": "Architecte",
  "glyphe": "Ar",
  "neon": "#22D3EE",
  "encre": "#0B6378",
  "specialite": "Algorithmes et boucles",
  "capacite": "Quand un programme tourne en rond, Kestrel déroule chaque tour de boucle à la main.",
  "replique": "« Un bon plan vaut mille lignes de code. »",
  "stats": {
   "Algo": 3,
   "Réseau": 1,
   "Données": 2
  }
 },
 {
  "id": "vector",
  "nom": "Vector",
  "profil": "Architecte",
  "glyphe": "Ar",
  "neon": "#22D3EE",
  "encre": "#0B6378",
  "specialite": "Programmation objet",
  "capacite": "Vector découpe tout problème en classes et en méthodes avant d'écrire la moindre ligne.",
  "replique": "« Chaque objet a sa place. »",
  "stats": {
   "Algo": 3,
   "Réseau": 1,
   "Données": 2
  }
 },
 {
  "id": "pixel",
  "nom": "Pixel",
  "profil": "Architecte",
  "glyphe": "Ar",
  "neon": "#22D3EE",
  "encre": "#0B6378",
  "specialite": "Web et interfaces",
  "capacite": "Pixel teste chaque page sur trois écrans avant de la mettre en ligne.",
  "replique": "« Si ça ne s'affiche pas, ça n'existe pas. »",
  "stats": {
   "Algo": 2,
   "Réseau": 2,
   "Données": 2
  }
 },
 {
  "id": "nova",
  "nom": "Nova",
  "profil": "Analyste",
  "glyphe": "An",
  "neon": "#A78BFA",
  "encre": "#5B2BB5",
  "specialite": "Données et bases de données",
  "capacite": "Nova trouve la bonne requête du premier coup en lisant d'abord le schéma.",
  "replique": "« Les données ne mentent pas. Les requêtes, parfois. »",
  "stats": {
   "Algo": 2,
   "Réseau": 1,
   "Données": 3
  }
 },
 {
  "id": "byte",
  "nom": "Byte",
  "profil": "Analyste",
  "glyphe": "An",
  "neon": "#A78BFA",
  "encre": "#5B2BB5",
  "specialite": "Représentation des données",
  "capacite": "Byte convertit de tête du binaire, de l'hexadécimal et du texte encodé.",
  "replique": "« Tout finit en 0 et en 1. »",
  "stats": {
   "Algo": 2,
   "Réseau": 2,
   "Données": 3
  }
 },
 {
  "id": "mwezi",
  "nom": "Mwezi",
  "profil": "Analyste",
  "glyphe": "An",
  "neon": "#A78BFA",
  "encre": "#5B2BB5",
  "specialite": "Réseaux et protocoles",
  "capacite": "Mwezi suit un paquet de données de routeur en routeur sans jamais le perdre.",
  "replique": "« Toute route mène quelque part. »",
  "stats": {
   "Algo": 1,
   "Réseau": 3,
   "Données": 2
  }
 },
 {
  "id": "nyota",
  "nom": "Nyota",
  "profil": "Hacker",
  "glyphe": "Hk",
  "neon": "#FF5CA8",
  "encre": "#A3155C",
  "specialite": "Débogage",
  "capacite": "Nyota lit un message d'erreur jusqu'au bout, puis trouve la ligne fautive.",
  "replique": "« Une erreur, c'est un indice. »",
  "stats": {
   "Algo": 2,
   "Réseau": 2,
   "Données": 1
  }
 },
 {
  "id": "mistral",
  "nom": "Mistral",
  "profil": "Hacker",
  "glyphe": "Hk",
  "neon": "#FF5CA8",
  "encre": "#A3155C",
  "specialite": "Systèmes et ligne de commande",
  "capacite": "Mistral fait en trois commandes ce que d'autres font en trente clics.",
  "replique": "« Le terminal, c'est la liberté. »",
  "stats": {
   "Algo": 2,
   "Réseau": 3,
   "Données": 1
  }
 },
 {
  "id": "zero",
  "nom": "Zéro",
  "profil": "Hacker",
  "glyphe": "Hk",
  "neon": "#FF5CA8",
  "encre": "#A3155C",
  "specialite": "Sécurité et cryptographie",
  "capacite": "Zéro repère un mot de passe faible avant même qu'on le tape.",
  "replique": "« Personne n'est à l'abri. Surtout pas moi. »",
  "stats": {
   "Algo": 2,
   "Réseau": 2,
   "Données": 2
  }
 }
];
  var PROFILS = {"architecte": {"nom": "Architecte", "devise": "Construire des programmes solides", "neon": "#22D3EE", "encre": "#0B6378"}, "analyste": {"nom": "Analyste", "devise": "Faire parler les données et les réseaux", "neon": "#A78BFA", "encre": "#5B2BB5"}, "hacker": {"nom": "Hacker", "devise": "Trouver la faille, puis la réparer", "neon": "#FF5CA8", "encre": "#A3155C"}};

  function jauge(n) {
    var s = '';
    for (var i = 0; i < 3; i++) s += i < n ? '◆' : '◇';
    return s;
  }

  function carte(r, racine) {
    var a = document.createElement('article');
    a.className = 'carte-runner';
    a.style.setProperty('--prof', r.neon);
    a.style.setProperty('--prof-encre', r.encre);
    var stats = Object.keys(r.stats).map(function (k) {
      return '<span>' + k + ' <b aria-label="' + r.stats[k] + ' sur 3">' + jauge(r.stats[k]) + '</b></span>';
    }).join('');
    a.innerHTML =
      '<header class="cr-tete"><span class="cr-glyphe" aria-hidden="true">' + r.glyphe + '</span>' +
      '<h3 class="cr-nom">' + r.nom + '</h3></header>' +
      '<div class="cr-art"><img src="' + racine + 'assets/equipage/' + r.id + '-nuit.svg" alt="Portrait de ' + r.nom + '" width="300" height="360" loading="lazy"></div>' +
      '<p class="cr-type">Runner · ' + r.profil + '</p>' +
      '<div class="cr-texte"><p class="cr-spe">' + r.specialite + '</p><p>' + r.capacite + '</p>' +
      '<p class="cr-replique">' + r.replique + '</p></div>' +
      '<p class="cr-jauges">' + stats + '</p>';
    return a;
  }

  /* Section de la page d'accueil */
  window.sectionEquipage = function (racine) {
    var s = document.createElement('section');
    s.className = 'equipage';
    s.setAttribute('aria-labelledby', 'equipage-titre');
    var profils = Object.keys(PROFILS).map(function (k) {
      var p = PROFILS[k];
      return '<li style="--prof:' + p.neon + ';--prof-encre:' + p.encre + '"><b>' + p.nom + '</b> ' + p.devise + '</li>';
    }).join('');
    s.innerHTML =
      '<div class="equipage-intro"><p class="invite" aria-hidden="true">~/equipage</p>' +
      '<h2 id="equipage-titre">L\'équipage</h2>' +
      '<p>Neuf runners, trois profils. Ils signent les coups de pouce des fiches. Lequel te ressemble ? ' +
      'Ou crée ta propre carte de runner.</p><ul class="profils">' + profils + '</ul></div>';
    var grille = document.createElement('div');
    grille.className = 'cartes-runners';
    RUNNERS.forEach(function (r) { grille.appendChild(carte(r, racine)); });
    s.appendChild(grille);
    return s;
  };
  window.EQUIPAGE = RUNNERS;
})();
