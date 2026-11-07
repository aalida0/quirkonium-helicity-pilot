"""Ideal W+->l+nu, Z->l+l- correlated angular density for spin-zero squirkonium.

Scalar WZ helicity amplitudes are provided by scalar_threshold_amplitudes.py.
W moves along +z, Z along -z in quirkonium rest frame. Each boson uses a
right-handed helicity frame: (xW,yW)=(x,y), (xZ,yZ)=(-x,y).
The observable Phi=phiW+phiZ. On-shell narrow-W/Z and massless leptons.
No cuts, FSR, production/formation effects, detector response or off-shell tails.
"""
from math import sqrt, pi, cos
from scalar_threshold_amplitudes import Setup, helicities, S2, splitting, f00

LAMS=(1,0,-1)

def d1(lam,h,c):
    """Wigner small d spin-1: m=lam, m'=h, h in +/-1."""
    s=sqrt(max(0.,1-c*c))
    if lam==1:
        return (1+c)/2 if h==1 else ((1-c)/2 if h==-1 else -s/sqrt(2))
    if lam==0:
        return s/sqrt(2) if h==1 else (-s/sqrt(2) if h==-1 else c)
    if lam==-1:
        return (1-c)/2 if h==1 else ((1+c)/2 if h==-1 else s/sqrt(2))
    raise ValueError('lam must be +/-1 or 0')

def components(b:Setup):
    if b.V!='Z':
        raise ValueError('WZ only')
    T,L=helicities(b)
    # Outgoing circular polarizations in the two right-handed helicity frames:
    # eW(+) = -(x+iy)/sqrt2, eZ(+)=(x-iy)/sqrt2.
    # Thus H++=H--=-Mxx and H00=M00, retaining the relative phase.
    return {-1:-T[0],0:L,1:-T[0]}

def joint_density(b:Setup,cw,cz,phi):
    """dP/dcos(thetaW)dcos(thetaZ)dPhi, normalized over [-1,1]^2 x [0,2pi)."""
    if not (-1<=cw<=1 and -1<=cz<=1):
        raise ValueError('cos angle outside physical range')
    H=components(b); N=sum(h*h for h in H.values())
    gl=-.5+S2;gr=S2
    wl=gl*gl/(gl*gl+gr*gr);wr=1-wl
    total=0.
    for a in LAMS:
        for d in LAMS:
            dw=d1(a,1,cw)*d1(d,1,cw) # W+ left-handed current: final-state h=+1
            dz=wr*d1(a,1,cz)*d1(d,1,cz)+wl*d1(a,-1,cz)*d1(d,-1,cz)
            total+=H[a]*H[d]*dw*dz*cos((a-d)*phi)
    return (9/(8*pi))*total/N

def azimuthal_cos2_amplitude(b:Setup):
    """A2 coefficient of cos(2Phi) after polar-angle integration."""
    H=components(b)
    return H[1]*H[-1]/(2*sum(h*h for h in H.values()))

def azimuthal_cos2_moment(b:Setup):
    return azimuthal_cos2_amplitude(b)/2

def azimuthal_cos1_amplitude(b:Setup):
    """A1: longitudinal-transverse interference and Z chiral asymmetry."""
    H=components(b)
    gl=-.5+S2;gr=S2
    az=(gr*gr-gl*gl)/(gr*gr+gl*gl)
    return (9*pi*pi/32)*az*H[1]*H[0]/sum(h*h for h in H.values())

def azimuthal_density(b:Setup,phi):
    """Normalized 1D dP/dPhi; A1 sign assumes stated angular conventions."""
    return (1+azimuthal_cos1_amplitude(b)*cos(phi)
             +azimuthal_cos2_amplitude(b)*cos(2*phi))/(2*pi)

if __name__=='__main__':
    for M,t in ((250.,1.),(500.,.1),(500.,1.),(500.,3.),(500.,10.)):
        b=Setup(M,splitting(M,t),'Z')
        print(f'M={M:.0f} tanbeta={t:g} f00={f00(b):.8f} '
              f'A1={azimuthal_cos1_amplitude(b):+.8f} '
              f'A2={azimuthal_cos2_amplitude(b):+.8f} '
              f'<cosPhi>={azimuthal_cos1_amplitude(b)/2:+.8f}')
