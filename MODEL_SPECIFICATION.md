# Physics model, scope and assumptions — scalar threshold pilot

**Date:** 2026-11-07. **Calculation status:** tree-level scalar-pair annihilation + leading nonrelativistic S-wave factorization. This is **not** a collider-event simulation or a scan of viable bound states.

## Field content and charges

In the convention Q=T3+Y/2, take an SU(2)_L scalar doublet \(\widetilde Q=(\widetilde u,\widetilde d)^T\), hypercharge \(Y=1/3\), an SU(3)_{IC} fundamental, and an SU(3)_{color} singlet. Component charges are \(Q_u=+2/3\), \(Q_d=-1/3\). Scalar gauge multiplets carry no perturbative chiral gauge anomalies. The quirkonium charged state is \(\Psi^+\sim\widetilde u\,\widetilde d^*\), \(J^P=0^+\) in the \(S\)-wave approximation. Do not assign a charged state \(C\) parity.

The needed renormalizable kinetic term is \((D_\mu\widetilde Q)^\dagger(D^\mu\widetilde Q)\), including non-Abelian covariant-derivative contact interactions. For this calculation only, the spectrum is specified by two physical masses \(m_u=(M+\Delta)/2\), \(m_d=(M-\Delta)/2\), and \(M=m_u+m_d\), ignoring binding energy. The full scalar potential, other heavy superpartners, infracolor spectrum, and formation/de-excitation are **not** constructed here. Thus the benchmark is **conditional** on realizing the source model assumptions.

## Corrected splitting and parameterization

In the limiting case stated by the *erratum* to Forsyth, Low, Tenney and Verhaaren, PRD 113 079901 (2026), the splitting obeys

\[
\Delta={m_W^2\over M}\cos(2\beta)
={m_W^2\over M}{1-\tan^2\beta\over1+\tan^2\beta}.
\]

We evaluate \(\tan\beta\in[0.1,10]\) and open on-shell WZ channels. This is **not** a free \(\Delta\) scan, and it is not proof that every sampled point satisfies vacuum/collider/cosmology constraints. Do not use original 2025 figures that did not enforce the relation.

Inputs used for diagnostic rates and fractions are \(m_W=80.379\) GeV, \(m_Z=91.1876\) GeV, \(\alpha_W=0.0338\) (fixed illustrative scheme), \(s_W^2=1-m_W^2/m_Z^2\), \(c_W^2=1-s_W^2\). Bound-state wavefunction input \(|R(0)|^2\) is unspecified; reported polarization fractions are independent of this common normalization **at leading factorization order for the fixed state**.

## Interactions

Define \(g=\sqrt{4\pi\alpha_W}\), \(g_W=g/\sqrt{2}\); for \(V=\gamma\): \((g_{Vu},g_{Vd},g_{WWV})=(eQ_u,eQ_d,e)\), \(e=gs_W\). For \(V=Z\): \((g_{Vu},g_{Vd},g_{WWV})=(g(c_W)^{-1}(1/2-s_W^2Q_u),\,g(c_W)^{-1}(-1/2-s_W^2 Q_d),\,g c_W)\).

The calculation includes **four** contributions: \(W^+V\) seagull; two scalar-exchange channels; and intermediate \(W\) with the SM \(WWV\) vertex. The latter is crucial for nondegenerate constituent masses.

## Spin and experimental-scope limitations

Only a scalar spin-zero state is evaluated. Unknown quirkonium formation fractions, relativistic corrections, hidden glue radiation, off-shell gauge bosons, detector acceptance, and weak constituent-decay competition are not modeled. This result does not distinguish scalar and fermion models yet. No production sensitivity or physical exclusion is claimed.

References: https://arxiv.org/abs/2504.02940 (Appendix A.3) and https://doi.org/10.1103/lwnc-cmpn (2026 erratum).
