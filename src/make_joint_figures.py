"""Plots of ideal charged scalar WZ decay-plane harmonics (no detector cuts)."""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scalar_threshold_amplitudes import Setup,splitting
from joint_wz_angles import azimuthal_cos1_amplitude,azimuthal_density

out=Path(__file__).resolve().parents[1]/'figures'
out.mkdir(exist_ok=True)
ts=np.linspace(0.1,10.,300)
fig,ax=plt.subplots(figsize=(7.4,4.5))
for M in (250.,500.,1000.):
    ax.plot(ts,[azimuthal_cos1_amplitude(Setup(M,splitting(M,t),'Z')) for t in ts],
            label=f'M={M:.0f} GeV')
ax.axhline(0.,color='gray',linewidth=.8)
ax.set(xlabel=r'$\tan\beta$',ylabel=r'$a_1$ coefficient of $\cos\Phi$',
       title='Scalar charged quirkonium: WZ decay-plane interference')
ax.legend();fig.tight_layout();fig.savefig(out/'a1_cosPhi_vs_tanbeta.png',dpi=180)
plt.close(fig)
fig,ax=plt.subplots(figsize=(7.4,4.5))
ph=np.linspace(0,2*np.pi,300)
for t in (.1,1.,3.,10.):
    b=Setup(500.,splitting(500.,t),'Z')
    ax.plot(ph,[azimuthal_density(b,x) for x in ph],label=rf'$\tan\beta={t:g}$')
ax.set(xlabel=r'$\Phi$ [rad]',ylabel=r'$(1/\Gamma)d\Gamma/d\Phi$',
       title='Ideal WZ decay-plane azimuth at M=500 GeV')
ax.legend();fig.tight_layout()
fig.savefig(out/'joint_decay_plane_azimuth.png',dpi=180)
plt.close(fig)
