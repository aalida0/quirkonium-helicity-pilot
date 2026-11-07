# Charged quirkonium polarization — scalar helicity feasibility pilot

**Research date:** 2026-11-07. **Branch:** research/pilot1-literature-model-gate.
**Status:** scoped scalar tree-level helicity and source-width validation PASS; complete literature novelty and physical benchmark viability UNKNOWN. No paper or experimental-reach claim.

## What has been calculated

Scalar SU(2) weak-doublet squirks of component charge (+2/3,-1/3) form a fixed charged \(0^+\) S-wave quirkonium. The complete tree-level threshold \(\widetilde u\widetilde d^*\to W^+ Z,W^+\gamma\) amplitude is implemented with scalar t/u exchange, four-point seagull and virtual W*. Photon Ward identity, spin-zero selection rules, limiting cases and published integrated partial-width comparison are checked.

The **2026 erratum** to Forsyth et al. requires the restricted \(D\)-term splitting \(\Delta=m_W^2\cos(2\beta)/M\). Within this limit, the longitudinal fraction \(f_{00}(WZ)\) varies strongly with tanβ, even at high M. For M=500 GeV: tanβ=1 → 0.00193812, tanβ=10 → 0.93584632. These are **ideal leading-order theory ratios, not detector predictions**.

## Reproduce

Python 3.11+ standard library suffices for the physics checks:

    python -m unittest discover -s tests -v
    python src/scalar_threshold_amplitudes.py

Local verification in Python 3.13.5: **14 tests PASS**, including 70 WZ/Wγ published-width configurations and 20 photon Ward configurations. All source-width ratios tested agree at floating-point precision. For PNG plots:

    python -m pip install -r requirements-figures.txt
    python src/make_figures.py

Plots generated: figures/f00_vs_tanbeta.png, figures/w_lepton_angle.png, figures/published_width_validation.png. The figures folder is generated output (not required for the source code).

## Docs and gatekeepers
- MODEL_SPECIFICATION.md — field content, couplings, mass splitting, non-viability caveats
- theory/amplitudes.md — explicit tree diagram sum, phase space and source formula
- theory/helicity_conventions.md — definitions and ideal W lepton polar angle
- literature/PRIOR_ART_MATRIX.md — including Forsyth 2023 MS thesis
- literature/CITATION_AUDIT.md — literature coverage and honest API/quota blockers
- literature/NOVELTY_VERDICT.md — incomplete novelty status
- validation/VALIDATION_REPORT.md — PASS/UNKNOWN gates and benchmark evidence
- PILOT_DECISION.md — referee-risk assessment and conditional GO/NO-GO

Source: Forsyth et al. (2025), arXiv:2504.02940, Appendix A.3, and 2026 erratum DOI:10.1103/lwnc-cmpn.

## What has **not** been finished

No direct complete two-hop INSPIRE citation graph (API unavailable, scholarly connector quota); no independently generated UFO/MadGraph calculation or arbitrary Rξ Goldstone/Slavnov–Taylor verification; no complete scalar potential/vacuum and collider-constraint validation; no fermionic comparison; a *calculated but not literature-novelty-certified* ideal joint W/Z leptonic azimuthal-interference observable or detector simulation. The **current polarization decomposition is implicitly encoded in the prior published integrated width**, so by itself it is unlikely to constitute a paper.


## Additional joint-decay calculation

The on-shell WZ helicity amplitudes have now been propagated through the SM W and Z chiral leptonic currents. See theory/joint_angular_interference.md and src/joint_wz_angles.py. The normalized decay-plane azimuth density is \((1+a_1\cos\Phi+a_2\cos2\Phi)/(2\pi)\). The \(a_1\) term retains the sign of transverse–longitudinal interference and is not reconstructible from helicity-summed **rate values alone**. At M=500 GeV and tanβ=0.1,1,3,10, \(a_1=(+0.091375,-0.018423,-0.120305,-0.102636)\). The calculation, its positivity, normalization and two harmonics are covered by five additional tests in tests/test_joint_wz_angles.py, and plotted with src/make_joint_figures.py. Total local test count is **14** (9 threshold + 5 joint-angle). This is an *idealized theoretical* angular result; paper novelty and detector observability remain unverified.
