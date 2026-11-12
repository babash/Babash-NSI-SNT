#!/usr/bin/env node
/* Tests du moteur de recherche (assets/recherche.js), avec le vrai thésaurus et des fiches fabriquées.

   Usage (depuis la racine du dépôt) :  node scripts/tests/test_recherche.js [DOSSIER_DU_DEPOT]
   Code de retour : 0 si tous les cas passent, 1 sinon. Node seul, sans dépendance. */
'use strict';
const fs = require('fs');
const path = require('path');

const racine = path.resolve(process.argv[2] || path.join(__dirname, '..', '..'));
const R = require(path.join(racine, 'assets', 'recherche.js'));
const notions = JSON.parse(fs.readFileSync(path.join(racine, 'donnees', 'referentiels', 'notions.json'), 'utf8'));
const valeurs = JSON.parse(fs.readFileSync(path.join(racine, 'donnees', 'referentiels', 'valeurs.json'), 'utf8'));

let n = 0, echecs = 0;
function cas(titre, ok, detail) {
  n++;
  if (ok) console.log('  ok     ' + titre);
  else { echecs++; console.log('  ÉCHEC  ' + titre + (detail ? '\n         ' + detail : '')); }
}

/* Des fiches fabriquées : champs de recherche et notions */
const FICHES = [
  ['boucles-for', { titre: 'Les boucles for en Python', resume: 'Répéter un nombre de fois connu avec range.' }],
  ['tant-que', { titre: 'Tant que : la boucle while', resume: 'Répéter tant qu\'une condition est vraie.' }],
  ['robot', { titre: 'Un robot qui avance', resume: 'Avancer jusqu\'au mur.' },
    { enseignees: ['prog.boucle.non-bornee'] }],
  ['sql', { titre: 'Bases de données et SQL', resume: 'Interroger une base avec SELECT et WHERE.' }],
  ['objets', { titre: 'Premiers pas', resume: 'Une voiture, sa couleur, sa vitesse.' }, { enseignees: ['prog.poo.classe'] }],
  ['dicho', { titre: 'Recherche dichotomique dans un tableau trié', presentation: 'On coupe en deux à chaque étape.' }],
  ['debranche', { titre: 'Le crêpier psychorigide', mots: ['Activité débranchée', 'Débranché'] }],
  ['reseau', { titre: 'Réseaux : TCP/IP et routage', bo: ['Protocole TCP/IP : paquets, routage des paquets'] }],
  ['journaux', { titre: 'Les journaux et les animaux', resume: 'Pluriels en -aux.' }],
];

function index() {
  const ix = new R.Index({ notions });
  ix.ajouterSynonymes(['types', 'usages', 'langages', 'roles'].flatMap(l => valeurs[l].map(v => [v.libelle].concat(v.alternatifs || []))));
  FICHES.forEach(([id, champs, nts]) => ix.ajouter(id, champs, nts));
  ix.preparer();
  return ix;
}
const ix = index();
const ids = q => ix.chercher(q).resultats.map(r => r.id);
const contient = (q, attendus) => { const t = ids(q); return attendus.every(a => t.includes(a)); };

console.log('Mots');
cas('« Boucles » et « boucle » ont la même racine', R.racine(R.normaliser('Boucles')) === R.racine(R.normaliser('boucle')));
cas('« données » et « donnée » ont la même racine', R.racine('donnees') === R.racine('donnee'));
cas('« réseaux » et « réseau » ont la même racine', R.racine(R.normaliser('Réseaux')) === R.racine(R.normaliser('réseau')));
cas('« journaux » et « journal » ont la même racine', R.racine('journaux') === R.racine('journal'));
cas('« class » garde son s', R.racine('class') === 'class');
cas('accents, majuscules et ligatures', R.normaliser('Œuvre ÉLÈVE Cœur') === 'oeuvre eleve coeur');
cas('découpage : apostrophe et ponctuation', R.decouper("l'algorithme, TCP/IP").map(x => x.forme).join(' ') === 'l algorithme tcp ip');
cas('distance : une lettre échangée compte 1', R.distance('dichotomie', 'dichotmoie', 2) === 1);

console.log('Recherche');
cas('« boucle » trouve for, while, et la fiche classée sans le mot', contient('boucle', ['boucles-for', 'tant-que', 'robot']),
    'trouvées : ' + ids('boucle'));
cas('« boucle » : les fiches qui écrivent le mot passent avant', ids('boucle').indexOf('robot') > ids('boucle').indexOf('boucles-for'));
cas('« while » trouve la boucle non bornée et la fiche classée sous elle', contient('while', ['tant-que', 'robot']), 'trouvées : ' + ids('while'));
cas('« while » ne trouve pas la boucle bornée seule', !ids('while').includes('boucles-for') || ids('while').indexOf('boucles-for') > 1);
cas('« BDD » trouve « Bases de données et SQL »', ids('BDD')[0] === 'sql', 'trouvées : ' + ids('BDD'));
cas('« base de donnée » (singulier) trouve SQL', ids('base de donnée')[0] === 'sql');
cas('« objets » trouve la fiche classée sous « classe et instance »', ids('objets').includes('objets'), 'trouvées : ' + ids('objets'));
cas('« POO » aussi', ids('POO').includes('objets'));
cas('début de mot : « dicho »', ids('dicho')[0] === 'dicho');
cas('libellé caché du thésaurus : « dicotomie »', ids('dicotomie').includes('dicho'), 'trouvées : ' + ids('dicotomie'));
const faute = ix.chercher('dichotomei');
cas('faute de frappe : « dichotomei » trouve la dichotomie', faute.resultats.length && faute.resultats[0].id === 'dicho');
cas('… et propose « dichotomie »', faute.suggestion && R.normaliser(faute.suggestion).startsWith('dichotom'), 'suggestion : ' + faute.suggestion);
cas('synonyme d\'une valeur : « sans ordinateur » trouve le débranché', ids('sans ordinateur').includes('debranche'), 'trouvées : ' + ids('sans ordinateur'));
cas('plusieurs mots : tous requis (« réseau tcp »)', JSON.stringify(ids('réseau tcp')) === '["reseau"]', 'trouvées : ' + ids('réseau tcp'));
const partiel = ix.chercher('routage python');
cas('aucune fiche n\'a tous les mots : résultats partiels signalés', partiel.partiel && partiel.resultats.length >= 2);
cas('mot vide seul : aucune clause', ix.chercher('de la').clauses.length === 0);
cas('mot inconnu : rien, et des suggestions proches', ix.chercher('xqzwv').resultats.length === 0 && Array.isArray(ix.suggestions('rezo')));
cas('« rezau » propose « réseau »', ix.suggestions('rezau').some(s => R.normaliser(s).startsWith('reseau')), 'suggestions : ' + ix.suggestions('rezau'));
cas('pluriels en -aux : « journal » trouve « journaux »', ids('journal').includes('journaux'));

console.log('Texte des documents');
const ix2 = index();
ix2.ajouterTextes([{ ressource: 'robot', document: 0, texte: 'Exercice 3 : écrire une fonction récursive qui calcule la factorielle.' }]);
cas('un mot du document hébergé trouve la fiche', ix2.chercher('factorielle').resultats.map(r => r.id).includes('robot'));
const res = ix2.chercher('factorielle').resultats[0];
cas('… avec le champ « texte »', res && res.champs.includes('texte'));
cas('extrait autour du mot', (R.extrait(ix2.docs[ix2.parId.robot].textes[0].texte, res.trouves) || '').includes('factorielle'));

console.log('Surlignage');
const s = R.surligner('Les boucles for en Python', ix.chercher('boucle').resultats.find(r => r.id === 'boucles-for').trouves);
cas('« boucles » est surligné', s.some(x => x.marque && x.texte === 'boucles'), JSON.stringify(s));
cas('le texte est rendu tel quel', s.map(x => x.texte).join('') === 'Les boucles for en Python');
cas('les mots vides ne sont jamais surlignés', !R.surligner('la boucle de la page', ['la', 'boucl']).some(x => x.marque && x.texte === 'la'));

console.log('\n' + n + ' cas, ' + echecs + ' échec(s)');
process.exit(echecs ? 1 : 0);
