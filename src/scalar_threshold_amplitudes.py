"""Tree-level scalar quirk-pair annihilation at threshold.

The model is a colorless-SM, SU(3)_IC scalar weak doublet with charges
(2/3,-1/3), matching Forsyth et al. arXiv:2504.02940, Sec. 3.
The amplitude includes the W-V seagull, u/d exchange and W* channel.
Reference: Forsyth et al., Appendix A.3, Eqs. (A.4)-(A.8).
The restricted D-term splitting is from PRD 113, 079901 (2026) erratum.
No detector response or bound-state formation model is implied.
"""
from dataclasses import dataclass
from math import sqrt, pi

MW = 80.379
MZ = 91.1876
ALPHA_W = 0.0338
S2 = 1 - MW**2/MZ**2
C2 = 1 - S2
QU, QD = 2/3, -1/3

def dot(a,b):
    return a[0]*b[0]-sum(x*y for x,y in zip(a[1:],b[1:]))

def add(a,b):
    return tuple(x+y for x,y in zip(a,b))

def scale(c,a):
    return tuple(c*x for x in a)

def sub(a,b):
    return add(a,scale(-1,b))

def splitting(M,tanbeta):
    return MW**2/M*(1-tanbeta**2)/(1+tanbeta**2)

@dataclass(frozen=True)
class Setup:
    M: float
    delta: float
    V: str

    def __post_init__(self):
        if self.V not in ('Z','gamma'):
            raise ValueError('V must be Z or gamma')
        if self.M<=MW+(MZ if self.V=='Z' else 0):
            raise ValueError('two-body final state closed')
        if abs(self.delta)>=self.M:
            raise ValueError('nonpositive constituent mass')

    @property
    def mv(self):
        return MZ if self.V=='Z' else 0.

    @property
    def mu(self):
        return (self.M+self.delta)/2

    @property
    def md(self):
        return (self.M-self.delta)/2

    @property
    def beta(self):
        w=MW**2/self.M**2
        z=self.mv**2/self.M**2
        return sqrt((1-w-z)**2-4*w*z)

    def vectors(self):
        M, m = self.M,self.mv
        ew=(M*M+MW*MW-m*m)/(2*M)
        ev=(M*M+m*m-MW*MW)/(2*M)
        p=sqrt(max(0.,ew*ew-MW*MW))
        return ((M,0.,0.,0.),(ew,0.,0.,p),(ev,0.,0.,-p))

    def couplings(self):
        g=sqrt(4*pi*ALPHA_W)
        gw=g/sqrt(2)
        if self.V=='gamma':
            return gw,g*sqrt(S2)*QU,g*sqrt(S2)*QD,g*sqrt(S2)
        return (gw,g/sqrt(C2)*(0.5-S2*QU),
                g/sqrt(C2)*(-0.5-S2*QD),g*sqrt(C2))

def amplitude(b,ew,ev):
    """Covariant diagram sum contracted with final-vector polarizations.

    All vectors are contravariant and dot is (+,-,-,-).
    Incoming u and dbar are at rest, masses (M+delta)/2 and (M-delta)/2.
    """
    P,kw,kv=b.vectors()
    t=(1.,0.,0.,0.)
    gw,zu,zd,gv=b.couplings()
    mu,md=b.mu,b.md
    denu=b.mv**2-2*mu*kv[0]
    dend=b.mv**2-2*md*kv[0]
    contact=gw*(zu+zd)*dot(ew,ev)
    u=-gw*zu*dot(sub(scale(b.delta,t),kv),ew)*dot(sub(scale(2*mu,t),kv),ev)/denu
    d=+gw*zd*dot(add(scale(b.delta,t),kv),ew)*dot(sub(scale(2*md,t),kv),ev)/dend
    V=(ew[0]*dot(sub(scale(-1,P),kw),ev)
       +dot(ew,ev)*(kw[0]-kv[0])
       +ev[0]*dot(add(kv,P),ew))
    # Unitary-gauge propagator contracted with (p_u-p_d)^mu=delta*t^mu:
    # (g_0^beta-P_0 P^beta/MW^2)/(M^2-MW^2) = -t^beta/MW^2
    schannel=-gw*gv*b.delta/MW**2*V
    return contact+u+d+schannel

def helicities(b):
    _,kw,kv=b.vectors()
    ex=(0.,1.,0.,0.)
    ey=(0.,0.,1.,0.)
    trans=(amplitude(b,ex,ex),amplitude(b,ey,ey))
    if b.V=='gamma':
        return trans,None
    p=kw[3]
    ew=(p/MW,0.,0.,kw[0]/MW)
    ev=(p/b.mv,0.,0.,-kv[0]/b.mv)
    return trans,amplitude(b,ew,ev)

def amplitude_width(b,R2=1.):
    T,L=helicities(b)
    ampsq=sum(a*a for a in T)+(0 if L is None else L*L)
    # Eq. (A.4), unlike final states, |R(0)|^2=R2 GeV^3
    return 3/(32*pi*pi)*(R2/b.M**2)*b.beta*ampsq

def published_pieces(b):
    """Independent algebraic implementation of Forsyth A.6-A.8."""
    M,delta=b.M,b.delta
    D=QU+QD-delta/M
    if b.V=='gamma':
        pref=3*ALPHA_W**2*S2/(2*M*M)*(1-MW**2/M**2)
        return pref,D*D,0.
    w,z=MW**2/M**2,MZ**2/M**2
    den=(1-w-z)**2-(delta/M)**2*(1+z-w)**2
    AW=((QU+QD)*(1-w-z)+C2*delta/(S2*M)*(1+z-w))/den
    F=(1-(delta/M)**2)*b.beta**2*AW-D*(1-w-z)
    T=D**2
    L=M**4/(8*MW**2*MZ**2)*F**2
    pref=3*ALPHA_W**2*S2**2/(2*C2*M*M)*b.beta
    return pref,T,L

def published_width(b,R2=1.):
    pref,T,L=published_pieces(b)
    return pref*(T+L)*R2

def f00(b):
    T,L=helicities(b)
    if L is None:
        return 0.
    return L*L/(sum(a*a for a in T)+L*L)

def ward_photon(b):
    """Max normalized |M(epsW,k_gamma)|: photon Ward identity."""
    if b.V!='gamma':
        raise ValueError('photon required')
    _,kw,kg=b.vectors()
    p=kw[3]
    pol=((0.,1.,0.,0.),(0.,0.,1.,0.),(p/MW,0.,0.,kw[0]/MW))
    gw,_,_,e=b.couplings()
    return max(abs(amplitude(b,ew,kg)) for ew in pol)/(gw*e*b.M)

def w_lepton_density(c,f):
    """Ideal W+ helicity-frame polar-angle marginal, equal T+ and T-."""
    if not -1<=c<=1:
        raise ValueError('cos(theta) out of range')
    return 0.75*f*(1-c*c)+0.375*(1-f)*(1+c*c)

if __name__=='__main__':
    for M in (250.,500.,1000.):
        for tb in (1.,3.,10.):
            d=splitting(M,tb)
            z=Setup(M,d,'Z')
            ph=Setup(M,d,'gamma')
            print(f'M={M:.0f}, tanbeta={tb:g}, delta={d:.6f}, f00={f00(z):.8f}, '
                  f'WZratio={amplitude_width(z)/published_width(z):.12f}, '
                  f'Wgratio={amplitude_width(ph)/published_width(ph):.12f}, '
                  f'Ward={ward_photon(ph):.3g}')
