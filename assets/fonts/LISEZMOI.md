# Polices hébergées sur le site

Les pages qui suivent le style « Signal pirate » (d'abord les TD en ligne, `assets/td-en-ligne.css`) chargent leurs polices d'ici : **aucun appel à un serveur de polices** (ni Google Fonts, ni autre). Les fichiers sont les sous-ensembles « latin » et « latin-ext » des paquets Fontsource 5.3.0, sans modification.

| Famille | Fichiers | Usage | Licence |
|---|---|---|---|
| Atkinson Hyperlegible (Braille Institute of America) | `atkinson-hyperlegible-*` (400, 700, 400 italique) | texte courant | SIL Open Font License 1.1 : `LICENCE-atkinson-hyperlegible.txt` |
| JetBrains Mono (JetBrains) | `jetbrains-mono-*` (400, 700, italiques) | code, consoles, petites étiquettes | SIL Open Font License 1.1 : `LICENCE-jetbrains-mono.txt` |
| Anton (The Anton Project Authors) | `anton-latin-400-normal.woff2` | grands titres | SIL Open Font License 1.1 : `LICENCE-anton.txt` |
| VT323 (The VT323 Project Authors) | `vt323-latin-400-normal.woff2` | accroche du bandeau, étiquettes « sortie », « erreur », « cours-quiz » (13 pt au moins : son œil est petit) | SIL Open Font License 1.1 : `LICENCE-vt323.txt` |
| TD Symboles | `td-symboles-400-normal.woff2` | les signes absents des polices ci-dessus : ← ↑ → ↓ ↔ ⇒ ⇔ ∧ ∨ ¬ × ≠ ≤ ≥ ≈ ≡ Δ Σ π λ √ ∞ ∑ ∈ ∉ ∅ ∩ ∪ ■ □ ▲ ▼ ◆ ★ ☆ ✓ ✗ | sous-ensemble de DejaVu Sans 2.37 (licences Bitstream Vera et Arev, changements de DejaVu dans le domaine public) : `LICENCE-dejavu.txt`, le fichier `LICENSE` d'origine de DejaVu. Renommé « TD Symboles », comme l'exige la licence Bitstream Vera pour une version modifiée. |

Refaire « TD Symboles » (fontTools) :

```
python3 -I charte/symboles-td.py /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf assets/fonts/td-symboles-400-normal.woff2
```
Le script prend le sous-ensemble, garde le copyright et la licence (noms 0 et 13) et renomme la famille (noms 1, 3, 4, 6, 16) en « TD Symboles ».
