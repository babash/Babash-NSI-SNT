import sys
def lum(h):
    h=h.lstrip('#'); r,g,b=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    f=lambda c: c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)
def cr(a,b):
    la,lb=sorted([lum(a),lum(b)],reverse=True); return (la+0.05)/(lb+0.05)
def gray(h):
    return round(lum(h)**(1/2.2)*100)
if __name__=='__main__':
    pairs=[l.split() for l in sys.stdin if l.strip() and not l.startswith('#')]
    for p in pairs:
        name,fg,bg=p[0],p[1],p[2]
        c=cr(fg,bg); print(f"{name:28s} {fg} sur {bg}: {c:5.2f}  {'AAA' if c>=7 else 'AA' if c>=4.5 else 'AA-grand/UI' if c>=3 else 'ÉCHEC'}  gris={gray(fg)}")
