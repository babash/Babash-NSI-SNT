/* Ressources SNT : petits automatismes de la page d'accueil.
   Rien à modifier ici pour ajouter une ressource. */
(function () {
  // 1. Compteur de ressources à côté de chaque thème du sommaire
  document.querySelectorAll('.index a[href^="#"]').forEach(function (lien) {
    var section = document.querySelector(lien.getAttribute('href'));
    if (!section) return;
    var n = section.querySelectorAll('.res').length;
    var nb = lien.querySelector('.nb');
    if (nb) nb.textContent = n;
    if (n === 0) lien.classList.add('est-vide');
  });

  // 2. Liens externes : nouvel onglet + nom du site affiché sous la ressource
  document.querySelectorAll('.res a.titre').forEach(function (lien) {
    var url;
    try { url = new URL(lien.href); } catch (e) { return; }
    if (url.origin === location.origin) return;

    lien.target = '_blank';
    lien.rel = 'noopener';

    var res = lien.closest('.res');
    var tags = res.querySelector('.tags');
    if (!tags) {
      tags = document.createElement('p');
      tags.className = 'tags';
      res.appendChild(tags);
    }
    var site = document.createElement('span');
    site.className = 'site';
    site.textContent = url.hostname.replace(/^www\./, '');
    tags.appendChild(site);
  });

  // 3. Lien vers le dépôt GitHub (seulement une fois en ligne sur github.io)
  var depot = document.querySelector('.lien-depot');
  var hote = location.hostname;
  if (depot && /\.github\.io$/.test(hote)) {
    var compte = hote.replace(/\.github\.io$/, '');
    var dossier = location.pathname.split('/').filter(Boolean)[0];
    var nomDepot = dossier && !/\.html$/.test(dossier) ? dossier : hote;
    depot.href = 'https://github.com/' + compte + '/' + nomDepot + '#readme';
    depot.hidden = false;
  }

  // 4. Date de dernière modification de la page
  var maj = document.querySelector('.maj');
  if (maj && document.lastModified) {
    var d = new Date(document.lastModified);
    if (!isNaN(d)) {
      maj.textContent = 'Page mise à jour le ' + d.toLocaleDateString('fr-FR', {
        day: 'numeric', month: 'long', year: 'numeric'
      }) + '.';
    }
  }
})();
