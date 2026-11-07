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
  var RUNNERS = /*DONNEES*/[];
  var PROFILS = /*PROFILS*/{};

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
