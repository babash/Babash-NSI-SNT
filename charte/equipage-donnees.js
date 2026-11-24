#!/usr/bin/env node
/* Les données du moteur d'avatars, tirées de assets/equipage.js (Designer, T133b).

   Usage (à la racine du dépôt) :
     node charte/equipage-donnees.js             écrit les deux fichiers
     node charte/equipage-donnees.js --verifier  sort en erreur si l'un n'est pas à jour

   - assets/equipage/catalogue.json : les valeurs admises dans une description d'avatar
     (lu par scripts/apparences_compte_commun.py, de l'Architecte) ;
   - assets/equipage/applis.json : le fichier versionné des applications : les 20 phrases du
     lobby (liste fermée, envoyée par numéro), les 4 gestes, les états d'usage et les 15 objets
     des applications avec le haut fait qui donne chacun.
   Ne pas modifier ces deux fichiers à la main. */
'use strict';
var fs = require('fs'), path = require('path');
var racine = path.resolve(__dirname, '..');
var E = require(path.join(racine, 'assets', 'equipage.js'));

function catalogue() {
  var modeles = {};
  Object.keys(E.modeles).forEach(function (k) { modeles[k] = { nom: E.modeles[k].nom, description: E.modeles[k].description }; });
  return {
    version: E.version,
    note: 'Généré depuis assets/equipage.js (Equipage.catalogue) : valeurs admises dans une description d’avatar. Ne pas modifier à la main.',
    etats: E.ETATS, defaut: E.defaut(), compat: E.compat, catalogue: E.catalogue, modeles: modeles
  };
}
function applis() {
  return {
    version: E.phrasesVersion,
    equipage_version: E.version,
    note: 'Généré depuis assets/equipage.js par charte/equipage-donnees.js. Les phrases sont une liste FERMÉE, envoyée par numéro (0 à ' +
      (E.phrases.length - 1) + ') : on n’en retire jamais, on n’en change jamais le sens, on ajoute à la fin et la version monte. Ne pas modifier à la main.',
    phrases: E.phrases.map(function (p, i) { return { numero: i, texte: p }; }),
    gestes: E.gestes,
    usages: Object.keys(E.USAGES).map(function (k) { return { id: k, etat: E.USAGES[k] }; }),
    neutre: E.neutre(),
    objets: E.applis
  };
}
var sorties = [
  [path.join(racine, 'assets', 'equipage', 'catalogue.json'), catalogue()],
  [path.join(racine, 'assets', 'equipage', 'applis.json'), applis()]
];
var verifier = process.argv.indexOf('--verifier') >= 0, ko = 0;
sorties.forEach(function (s) {
  var texte = JSON.stringify(s[1], null, 1) + '\n';
  var nom = path.relative(racine, s[0]);
  if (verifier) {
    var actuel = fs.existsSync(s[0]) ? fs.readFileSync(s[0], 'utf8') : '';
    if (actuel !== texte) { console.error('ERREUR : ' + nom + ' n\'est pas à jour : relancer node charte/equipage-donnees.js'); ko = 1; }
    else console.log(nom + ' est à jour.');
  } else { fs.writeFileSync(s[0], texte); console.log(nom + ' écrit.'); }
});
process.exit(ko);
