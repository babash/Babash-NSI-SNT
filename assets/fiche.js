/* ═══════════════════════════════════════════════════════════════
   Documents imprimables : boutons de la barre d'outils et mise à
   l'échelle à l'écran. Rien à modifier ici.

   Dans la barre d'outils du document :
     <button type="button" data-action="imprimer">Imprimer</button>
     <button type="button" data-action="projeter">Projeter</button>
   Touche P : projeter / revenir. La feuille garde sa mise en page
   A4 ; on l'agrandit (projection) ou on la réduit (téléphone).
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  var A4 = 793.7; // largeur d'une feuille A4 en pixels CSS (210 mm)
  var html = document.documentElement;

  function ajuster() {
    var dispo = html.clientWidth;
    var z = 1;
    if (html.classList.contains('projeter')) z = Math.min(2.4, dispo / A4);
    else if (dispo < A4 + 24) z = (dispo - 16) / A4;
    html.style.setProperty('--ajuste', z.toFixed(3));
  }

  function projeter(oui) {
    html.classList.toggle('projeter', oui);
    var b = document.querySelector('[data-action="projeter"]');
    if (b) {
      b.setAttribute('aria-pressed', oui ? 'true' : 'false');
      var t = b.querySelector('.libelle');
      if (t) t.textContent = oui ? 'Quitter la projection' : 'Projeter';
    }
    ajuster();
  }

  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-action]');
    if (!b) return;
    var a = b.getAttribute('data-action');
    if (a === 'imprimer') window.print();
    if (a === 'projeter') projeter(!html.classList.contains('projeter'));
  });

  document.addEventListener('keydown', function (e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    var t = e.target.tagName;
    if (t === 'INPUT' || t === 'TEXTAREA') return;
    if (e.key === 'p' || e.key === 'P') projeter(!html.classList.contains('projeter'));
    if (e.key === 'Escape' && html.classList.contains('projeter')) projeter(false);
  });

  window.addEventListener('resize', ajuster);
  window.addEventListener('beforeprint', function () { html.style.setProperty('--ajuste', '1'); });
  window.addEventListener('afterprint', ajuster);
  ajuster();
})();
