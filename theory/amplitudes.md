# Tree scalar threshold amplitudes and reference-rate comparison

**Metric:** (+---). **State:** \(\Psi^+\sim\widetilde u\widetilde d^*\), \(J^P=0^+\), weak doublet scalar with charges (+2/3,-1/3). The incoming constituents are at rest, \(p_u=m_ut\), \(p_d=m_dt\), \(t=(1,0,0,0)\), \(M=m_u+m_d\), \(\Delta=m_u-m_d\), \(P=(M,0,0,0)\), and the outgoing W,V momenta are \(k_W,k_V\). Common S-wave normalization is factored out.

Define \(g_W=g/\sqrt2\), \(a=g_{Vu}\), \(b=g_{Vd}\), \(c=g_{WWV}\), and final physical polarizations \(e_W,e_V\). The **complete physical tree** amplitude (up to a common overall phase) is a sum of four terms:
\[
{\cal M}_c=g_W(a+b)(e_W\cdot e_V),
\]
\[
{\cal M}_u=-g_Wa\,{[(\Delta t-k_V)\cdot e_W][(2m_ut-k_V)\cdot e_V]\over m_V^2-2m_u E_V},
\quad
{\cal M}_d=+g_Wb\,{[(\Delta t+k_V)\cdot e_W][(2m_dt-k_V)\cdot e_V]\over m_V^2-2m_d E_V},
\]
\[
{\cal M}_s=-{g_Wc\Delta\over m_W^2}\left[e_W^0(-P-k_W)\cdot e_V+(e_W\cdot e_V)(E_W-E_V)+e_V^0(k_V+P)\cdot e_W\right].
\]
The contributions are, respectively, the scalar seagull, two scalar exchanges and virtual W with SM WWV vertex. The last is essential at \(\Delta\neq0\). Couplings follow the gauge-covariant kinetic term, not anomalous placeholders. See src/scalar_threshold_amplitudes.py.

For \(WZ\), use transverse x and y linear polarization vectors for the transverse trace and longitudinal vectors
\[
e_W^{(0)}=(p/m_W,0,0,E_W/m_W),\quad
e_Z^{(0)}=(p/m_Z,0,0,-E_Z/m_Z).
\]
Only WZ helicity pairs (0,0),(+,+),(-,-) can contribute for spin zero. Let \(A_T^2=|M_{xx}|^2+|M_{yy}|^2\), \(A_L^2=|M_{00}|^2\). Width and fraction:
\[
\Gamma={3|R(0)|^2\over 32\pi^2 M^2}\beta_{WV}(A_T^2+A_L^2),\qquad f_{00}=A_L^2/(A_T^2+A_L^2).
\]
\(A_L=0\) for on-shell Wγ. The leading fixed-state normalized fraction cancels \(|R(0)|^2\).

## Independently compared published rate

Forsyth et al. (arXiv:2504.02940, Appendix A.3, Eq. (A.7)) integrated WZ width is expressible as
\[
\Gamma_{WZ}=K\left[D^2+\frac{M^4F^2}{8m_W^2m_Z^2}\right],\
K=\frac{3\alpha_W^2s_W^4|R(0)|^2}{2c_W^2M^2}\beta_{WZ},\
D=Q_u+Q_d-\Delta/M,
\]
\[
F=(1-\Delta^2/M^2)\beta_{WZ}^2A_{WZ}-D(1-w-z),
\quad
A_{WZ}=\frac{(Q_u+Q_d)(1-w-z)+(c_W^2/s_W^2)(\Delta/M)(1+z-w)}
{(1-w-z)^2-(\Delta/M)^2(1+z-w)^2},
\]
where \(w=m_W^2/M^2\) and \(z=m_Z^2/M^2\). The independent diagram-level polarization contraction identifies the \(D^2\) and \(F^2\) pieces with transverse and longitudinal contributions. Both WZ and Wγ summed widths match the reference expressions.

At \(\Delta=0\) the exact fraction becomes
\[
f_{00}=\frac{m_W^2m_Z^2}{2K_0^2+m_W^2m_Z^2}, \quad K_0=(M^2-m_W^2-m_Z^2)/2.
\]
For erratum-constrained \(\Delta=m_W^2\cos2\beta/M\), the large-M limit is
\[
f_{00}\to \frac{r}{1+r}, \quad r=\frac{c_W^2\cos^2(2\beta)}{8s_W^4(Q_u+Q_d)^2}.
\]
This explains why nonzero tiny splitting at high mass can still give O(1) longitudinal fraction.

## Validation scope

Diagram contraction and published rate comparison are independent algebraic pathways, but **no independent UFO/MG5, arbitrary-gauge Rξ Goldstone STI, NLO bound-state treatment or fermionic model comparison was performed**. Photon Ward identity and spin/helicity limits were checked. Do not interpret reference agreement as a fully certified collider-level simulation.
