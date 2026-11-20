/* Zone de code des contrôles de notions : une zone de plusieurs lignes, en
   police à chasse fixe, où la touche Tab indente (4 espaces), Maj + Tab
   désindente, et Entrée garde l'indentation de la ligne (un niveau de plus
   après « : »). Aucune dépendance. Échap puis Tab sort de la zone (clavier seul).
   S'applique à toute <textarea class="zone-code">, même ajoutée plus tard.
   Babash - NSI Tani Malandi · MIT */

(function () {
  'use strict';
  var IND = '    ', libre = null;

  function remplacer(z, debut, fin, texte, curseur) {
    z.setRangeText(texte, debut, fin, 'end');
    if (curseur !== undefined) z.setSelectionRange(curseur, curseur);
    z.dispatchEvent(new Event('input', { bubbles: true }));
  }

  document.addEventListener('keydown', function (ev) {
    var z = ev.target;
    if (!z || z.tagName !== 'TEXTAREA' || !z.classList.contains('zone-code')) return;
    if (ev.key === 'Escape') { libre = z; return; }
    var v = z.value, a = z.selectionStart, b = z.selectionEnd;
    var debutLigne = v.lastIndexOf('\n', a - 1) + 1;
    if (ev.key === 'Tab' && !ev.ctrlKey && !ev.altKey && !ev.metaKey) {
      if (libre === z) { libre = null; return; } /* Échap puis Tab : on laisse sortir */
      ev.preventDefault();
      if (!ev.shiftKey && a === b) { remplacer(z, a, b, IND); return; }
      /* Plusieurs lignes, ou Maj + Tab : (dés)indenter les lignes sélectionnées */
      var fin = v.indexOf('\n', b); if (fin < 0) fin = v.length;
      var bloc = v.slice(debutLigne, fin).split('\n').map(function (l) {
        return ev.shiftKey ? l.replace(/^ {1,4}/, '') : IND + l;
      }).join('\n');
      z.setRangeText(bloc, debutLigne, fin, 'select');
      z.dispatchEvent(new Event('input', { bubbles: true }));
      return;
    }
    libre = null;
    if (ev.key === 'Enter' && !ev.shiftKey && !ev.ctrlKey && !ev.isComposing) {
      ev.preventDefault();
      var ligne = v.slice(debutLigne, a), ind = /^ */.exec(ligne)[0];
      if (/:\s*$/.test(ligne)) ind += IND;
      remplacer(z, a, b, '\n' + ind);
    } else if (ev.key === 'Backspace' && a === b && a > debutLigne) {
      /* Effacer dans l'indentation : un niveau entier */
      var avant = v.slice(debutLigne, a);
      if (/^ +$/.test(avant)) {
        ev.preventDefault();
        var n = avant.length % 4 || 4;
        remplacer(z, a - n, a, '');
      }
    }
  });
})();
