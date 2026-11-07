"""Generate three theory-only PNG figures (requires numpy, matplotlib)."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from scalar_threshold_amplitudes import *
import numpy as np
import matplotlib.pyplot as plt
out=Path(__file__).resolve().parents[1]/'figures'
out.mkdir(exist_ok=True)
ts=np.linspace(0.1,10.,240)
fig,ax=plt.subplots(figsize=(7.2,4.4))
for M in (250.,500.,1000.):
    ax.plot(ts,[f00(Setup(M,splitting(M,t),'Z')) for t in ts],label=f'M={M:.0f} GeV')
ax.set(xlabel=r'$\tan\beta$',ylabel=r'$f_{00}(WZ)$',ylim=(0,1),
       title='Scalar charged quirkonium: LO WZ polarization')
ax.legend();fig.tight_layout();fig.savefig(out/'f00_vs_tanbeta.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(7.2,4.4))
x=np.linspace(-1.,1.,250)
for t in (1.,3.,10.):
    f=f00(Setup(500.,splitting(500.,t),'Z'))
    ax.plot(x,[w_lepton_density(c,f) for c in x],
            label=rf'$\tan\beta={t:g}$, $f_{{00}}={f:.3f}$')
ax.set(xlabel=r'$\cos\theta_\ell$ (W helicity frame)',ylabel='Normalized density',
       title='Ideal W+ lepton polar angle, M=500 GeV')
ax.legend();fig.tight_layout();fig.savefig(out/'w_lepton_angle.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(7.2,4.4))
ms=np.linspace(180.,2000.,100)
for t in (1.,10.):
    for V in ('Z','gamma'):
        residuals=[]
        for m in ms:
            b=Setup(float(m),splitting(float(m),t),V)
            residuals.append(amplitude_width(b)/published_width(b)-1)
        ax.plot(ms,residuals,label=f'{V}, tanbeta={t:g}')
ax.set(xlabel='Parent mass M [GeV]',
       ylabel=r'$\Gamma_{\rm amplitude}/\Gamma_{\rm published}-1$',
       title='Published-width validation: floating-point residual')
ax.legend();fig.tight_layout()
fig.savefig(out/'published_width_validation.png',dpi=180);plt.close(fig)
print('Wrote PNG plots to',out)
