# L'équipage : six avatars originaux (2 femmes, 2 hommes, 2 indéterminés)
HEX = '<path d="M32 3 57 17.5v29L32 61 7 46.5v-29z" stroke-width="1.6"/>'
BUST = '<path d="M15 52c1-8 8-11.5 17-11.5S48 44 49 52"/>'
A = 'style="stroke:var(--acc,#0B6378)"'
AF = 'style="fill:var(--acc,#0B6378);stroke:none"'
EQUIPAGE = [
 ("kestrel", "Kestrel", "elle", "Cheveux longs, oreillette",
  BUST + '<circle cx="32" cy="27" r="8"/>'
  '<path d="M23.2 39c-1.6-7-1.8-14 .4-18.6C25.7 16 29 14.6 32 14.6s6.3 1.4 8.4 5.8c2.2 4.6 2 11.6.4 18.6"/>'
  '<path d="M24.6 22.6c3.4 1.6 9.6.4 14-3.2"/>'
  f'<circle cx="24.2" cy="28.4" r="1.6" {AF}/><path d="M24.2 30v3.4l3 1.4" {A}/>'),
 ("nova", "Nova", "elle", "Cheveux crépus, bandeau",
  BUST + '<path d="M22.2 33.6A2.2 2.2 0 0 1 20.1 29.6A2.2 2.2 0 0 1 19.6 25.0A2.2 2.2 0 0 1 20.9 20.6A2.2 2.2 0 0 1 23.6 16.9A2.2 2.2 0 0 1 27.5 14.4A2.2 2.2 0 0 1 32.0 13.6A2.2 2.2 0 0 1 36.5 14.4A2.2 2.2 0 0 1 40.4 16.9A2.2 2.2 0 0 1 43.1 20.6A2.2 2.2 0 0 1 44.4 25.0A2.2 2.2 0 0 1 43.9 29.6A2.2 2.2 0 0 1 41.8 33.6"/>'
  '<circle cx="32" cy="28.4" r="7.6" fill="var(--fond,#fff)"/>'
  f'<path d="M24.6 22.4c4.6-2.6 10.2-2.6 14.8 0" stroke-width="2.6" {A}/>'),
 ("vector", "Vector", "il", "Cheveux courts, barbe, œil augmenté",
  BUST + '<circle cx="32" cy="27" r="8"/>'
  '<path d="M24.2 25c.2-6 3.6-9.2 7.8-9.2s7.6 3.2 7.8 9.2c-1.6-2.4-4.6-3.6-7.8-3.6s-6.2 1.2-7.8 3.6z"/>'
  '<path d="M24.4 28.6c.6 5.8 3.6 9 7.6 9s7-3.2 7.6-9"/><path d="M29 32.4c2-.8 4-.8 6 0"/>'
  f'<path d="M34.4 26.2h4.2" {A}/>'),
 ("byte", "Byte", "il", "Coupe dégradée, lunettes",
  BUST + '<circle cx="32" cy="27.4" r="8"/>'
  '<path d="M24.4 24c.6-6 4.6-9 9.4-8.6 3.4.3 6.2 2.6 7.2 5.8-3.6-1-8.6-.6-12.6 1.6"/>'
  f'<rect x="25.4" y="25.6" width="5.6" height="3.6" rx=".6" {A}/><rect x="33" y="25.6" width="5.6" height="3.6" rx=".6" {A}/><path d="M31 27.2h2" {A}/>'),
 ("zero", "Zéro", None, "Capuche, visière",
  BUST + '<path d="M20.6 41c-1.4-11.8.4-25.8 11.4-25.8S44.8 29.2 43.4 41"/>'
  '<path d="M25 37.6c-1.2-6.4-.6-15 7-15s8.2 8.6 7 15"/>'
  f'<path d="M26.4 28.6h11.2" stroke-width="3.2" {A}/>'),
 ("glitch", "Glitch", None, "Casque, antenne",
  BUST + '<path d="M22.4 34.6V26a9.6 9.6 0 0 1 19.2 0v8.6z"/>'
  f'<rect x="25.2" y="24.4" width="13.6" height="5.2" {A}/>'
  '<path d="M38.6 18.6 44 11"/><circle cx="44.6" cy="10.2" r="1.4"/>'
  f'<path d="M27 33h10" {A}/>'),
]
def svg(key, extra_class="avatar", title=None):
    for k, nom, pron, desc, body in EQUIPAGE:
        if k == key:
            t = f'<title>{title or nom}</title>' if title is not False else ''
            return (f'<svg class="{extra_class}" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" '
                    f'stroke-linecap="round" stroke-linejoin="round" role="img" aria-label="{nom}">{t}{HEX}{body}</svg>')
    raise KeyError(key)
