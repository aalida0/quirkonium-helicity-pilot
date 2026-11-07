# Joint WZ lepton angular density and interference moments

**Scope:** \(\Psi^+(0^+)\to W^+Z\to(\ell^+\nu)(\ell^-\ell^+)\), on-shell narrow-width W,Z, massless leptons, tree-level electroweak, no cuts or detector effects. The amplitude \(H_{\lambda\lambda}\) comes from src/scalar_threshold_amplitudes.py (all exchange, seagull and W* diagrams) and is contracted in src/joint_wz_angles.py.

## Frame and helicity choices

Work in the parent rest frame with W moving +z and Z moving −z. Each daughter defines a right-handed helicity coordinate system: \((x_W,y_W)=(x,y)\) and \((x_Z,y_Z)=(-x,y)\). \(\theta_W\) is the W+ charged-lepton angle relative to W flight axis, and \(\theta_Z\) is the Z negative-lepton angle relative to Z flight axis, all measured in their respective boson rest frames. Let \(\Phi=\phi_W+\phi_Z\). We use metric (+−−−) and outgoing transverse vectors \(e_W(+)=-[x+iy]/\sqrt2\), \(e_Z(+)=[x-iy]/\sqrt2\), with complex conjugation in amplitudes. These choices imply \(H_{++}=H_{--}=-{\cal M}_{xx}\), \(H_{00}={\cal M}_{00}\).

## Differential density

For spin-1 Wigner functions \(d^1_{\lambda h}(\theta)\) and \(\lambda=\pm1,0\), define
\[
D^W_{\lambda\lambda'}=d^1_{\lambda,+1}(\theta_W)d^1_{\lambda',+1}(\theta_W),
\]
\[
D^Z_{\lambda\lambda'}=\sum_{h=\pm1}w_h d^1_{\lambda,h}(\theta_Z)d^1_{\lambda',h}(\theta_Z)
\]
with \(w_{+1}=g_R^2/(g_L^2+g_R^2)\), \(w_{-1}=g_L^2/(g_L^2+g_R^2)\), \(g_L=-1/2+s_W^2\), \(g_R=s_W^2\).

Writing \(N=\sum_\lambda |H_{\lambda\lambda}|^2\), the **normalized** joint three-angle probability density (after integrating the global unobservable azimuth) is
\[
P(c_W,c_Z,\Phi)=\frac{9}{8\pi N}
\sum_{\lambda,\lambda'}
H_{\lambda\lambda}H^*_{\lambda'\lambda'}
D^W_{\lambda\lambda'}D^Z_{\lambda\lambda'}
\exp[i(\lambda-\lambda')\Phi],
\quad c_{W,Z}=\cos\theta_{W,Z}.
\]
The expression is real by hermiticity. Physical range \(c_W,c_Z\in[-1,1],\ \Phi\in[0,2\pi)\). Normalization \(\int d c_W d c_Z d\Phi\,P=1\).

After polar-angle integration:
\[
\frac{1}{\Gamma}\frac{d\Gamma}{d\Phi}
=\frac{1}{2\pi}\left[1+a_1\cos\Phi+a_2\cos(2\Phi)\right],
\]
\[
a_1=\frac{9\pi^2}{32}
\frac{g_R^2-g_L^2}{g_R^2+g_L^2}
\frac{\mathrm{Re}(H_{++}H^*_{00})}{N},\qquad
a_2=\frac{\mathrm{Re}(H_{++}H^*_{--})}{2N}=\frac{1-f_{00}}4
\]
for this real parity-even scalar threshold amplitude. The moments are
\(\langle\cos\Phi\rangle=a_1/2\), \(\langle\cos2\Phi\rangle=a_2/2\).

**Why \(a_1\) matters:** unlike the integrated WZ width, it retains the relative longitudinal–transverse **sign/phase**, with a suppression by the Standard Model Z charged-lepton parity asymmetry. Its sign depends on the stated decay-frame convention; the prediction is physically meaningful only when this convention is used consistently for data and templates. This is not a proven new paper result; earlier complete amplitude analyses may already imply it.

## Numerical benchmarks

At \(M=500\) GeV and 2026-erratum \(\Delta=m_W^2\cos2\beta/M\):

| tanβ | f00 | a1 | a2 |
|---:|---:|---:|---:|
| 0.1 | 0.949905 | +0.091375 | 0.012524 |
| 1 | 0.001938 | −0.018423 | 0.249515 |
| 3 | 0.909281 | −0.120305 | 0.022680 |
| 10 | 0.935846 | −0.102636 | 0.016038 |

The two-dimensional polar-angle integration was checked numerically (see tests/test_joint_wz_angles.py): normalized total within 7e-4 and moments within 5e-4 of the derived coefficients on a deliberately finite midpoint grid. Check against finer quadrature or an independent spin-helicity generator before higher-precision claims.

## Boundaries

No \(\Gamma\)-dependent acceptance corrections, W/Z off-shell interference, photon radiation, tau decays, detector angles, neutrino-solution ambiguities, formation fractions, or full experimental likelihood are modeled. The current \(a_1,a_2\) are **conditional ideal theory predictions**, not fiducial LHC observables or certified new literature.
