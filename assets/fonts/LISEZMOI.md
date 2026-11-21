# Polices hébergées sur le site

Les pages qui suivent le style « Signal pirate » (d'abord les TD en ligne, `assets/td-en-ligne.css`) chargent leurs polices d'ici : **aucun appel à un serveur de polices** (ni Google Fonts, ni autre). Les fichiers sont les sous-ensembles « latin » et « latin-ext » des paquets Fontsource 5.3.0, sans modification.

| Famille | Fichiers | Usage | Licence |
|---|---|---|---|
| Atkinson Hyperlegible (Braille Institute of America) | `atkinson-hyperlegible-*` (400, 700, 400 italique) | texte courant | SIL Open Font License 1.1 : `LICENCE-atkinson-hyperlegible.txt` |
| JetBrains Mono (JetBrains) | `jetbrains-mono-*` (400, 700, italiques) | code, consoles, petites étiquettes | SIL Open Font License 1.1 : `LICENCE-jetbrains-mono.txt` |
| Anton (The Anton Project Authors) | `anton-latin-400-normal.woff2` | grands titres | SIL Open Font License 1.1 : `LICENCE-anton.txt` |
| VT323 (The VT323 Project Authors) | `vt323-latin-400-normal.woff2` | accroche du bandeau, étiquettes « sortie », « erreur », « cours-quiz » (13 pt au moins : son œil est petit) | SIL Open Font License 1.1 : `LICENCE-vt323.txt` |
| TD Symboles | `td-symboles-400-normal.woff2` | les signes absents des polices ci-dessus : ← ↑ → ↓ ≠ ≤ ≥ ■ □ ▲ ▼ ◆ ★ ☆ ✓ ✗ | sous-ensemble de DejaVu Sans 2.37 (licences Bitstream Vera et Arev, changements de DejaVu dans le domaine public) : `LICENCE-dejavu.txt`, le fichier `LICENSE` d'origine de DejaVu. Renommé « TD Symboles », comme l'exige la licence Bitstream Vera pour une version modifiée. |

Refaire « TD Symboles » (fontTools) :

```
python3 -m fontTools.subset DejaVuSans.ttf --unicodes="U+2190-2193,U+25A0,U+25A1,U+25B2,U+25BC,U+25C6,U+2605,U+2606,U+2713,U+2717,U+2260,U+2264,U+2265" \
  --flavor=woff2 --output-file=td-symboles-400-normal.woff2 --name-IDs='*'
```
puis renommer la famille (noms 1, 4, 6 et 16) en « TD Symboles ».
