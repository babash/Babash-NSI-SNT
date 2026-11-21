"""Contrastes des couples de couleurs utilisés par le site (maquette T126), clair et obscur."""
def lum(h):
    h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    c=[x/12.92 if x<=0.03928 else ((x+0.055)/1.055)**2.4 for x in c]
    return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
def ratio(a,b):
    la,lb=sorted([lum(a),lum(b)],reverse=True); return (la+0.05)/(lb+0.05)
CLAIR=dict(fond='#FFFFFF',panneau='#FFFFFF',p2='#F5F4F7',encre='#121016',douce='#45414D',trait='#8C8796',accent='#00566E',focus='#C2006A',pf='#121016',pe='#FFFFFF')
OBSCUR=dict(fond='#0E0C14',panneau='#14111C',p2='#1C1826',encre='#ECE8F5',douce='#C9C3D6',trait='#7A7390',accent='#5EE6FF',focus='#FF7AC0',pf='#ECE8F5',pe='#0E0C14')
COUPLES=[('texte courant','encre','fond',7),('texte sur panneau','encre','panneau',7),('texte sur note (panneau-2)','encre','p2',7),
 ('petit texte doux (chemins, nombres, mentions)','douce','fond',4.5),('petit texte doux sur panneau-2','douce','p2',4.5),
 ('liens (accent)','accent','fond',7),('liens sur panneau-2','accent','p2',4.5),('bouton principal','pe','pf',7),
 ('trait fin (filets, cases vides)','trait','fond',3),('contour du focus','focus','fond',3)]
ok=True
for nom,pal in (('clair',CLAIR),('obscur',OBSCUR)):
    for lib,a,b,mini in COUPLES:
        r=ratio(pal[a],pal[b]); f = r>=mini; ok&=f
        print(f'{nom:7} {lib:48} {r:5.2f}:1  (mini {mini})  {"ok" if f else "NON"}')
print('TOUT EST CONFORME' if ok else 'À CORRIGER')
