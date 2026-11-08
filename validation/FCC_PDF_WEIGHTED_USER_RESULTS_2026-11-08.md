# User-run FCC-hh PDF-weighted W+ angular-sign pilot: initial result

**Date:** 2026-11-08. **Status:** NEW PDF-INTEGRATION COORDINATE CHECK PASS, ANGULAR NUMERICAL-CONVERGENCE PENDING, COLLIDER FEASIBILITY CONDITIONAL.
**Run:** UChicago AF Key4HEP release 2026-02-01, Python 3.13.8, LHAPDF 6.5.5, MSTW2008lo68cl member 0 (LHAPDF ID 21000).
**Code:** scripts/quirkonium_fcc_pdf_rapidity_gate.py (charge mode W+ only).
**Parameters:** M=500 GeV, tanbeta_high=3, tanbeta_low=0.39472402, full CKM, 5 polar Gauss nodes, 12 Phi points, 5 orientation nodes, 24 PDF rapidity nodes, 40 log-shat nodes, 72 independent source x1/x2 reference nodes.
**User result path on AF:** /data/aalida/quirkonium-production/fcc_pdf_rapidity_pilot.json. The JSON exists on the user's AF node but was NOT supplied as an attachment; the following facts are grounded in the terminal output pasted by the user.

## Numerical results

| Observable | 85 TeV, L=20000/fb | 100 TeV, L=30000/fb |
| --- | ---: | ---: |
| Low-branch W+ constituent pair rate (fb) | 562.17 | 691.48 |
| High-branch W+ pair rate (fb) | 562.14 | 691.45 |
| Charge-summed low-branch pair rate (fb) | 951.87 | 1179.6 |
| Relative independent ln-x PDF cross-check | 0.002% | 0.003% |
| Truth a1, low branch | +0.121089 | +0.121089 |
| Truth a1, high branch | -0.121089 | -0.121089 |
| min-abs-pz a1, low branch | +0.028833 | +0.026530 |
| min-abs-pz a1, high branch | -0.027639 | -0.025333 |
| min-abs-pz delta a1 | +0.056472 | +0.051863 |
| min-abs-pz true-root fraction | 0.579 | 0.568 |
| Truth simple-moment 3sigma selected N | 309 | 309 |
| min-abs-pz simple-moment 3sigma selected N | **5703** | **6761** |
| min-abs-pz required P_charged_survival * epsilon | **0.046336** | **0.029773** |
| equal-root moment delta a1 | +0.023507 | +0.023507 |
| equal-root moment 3sigma selected N | 32923 | 32923 |
| equal-root required P_charged_survival*epsilon | 0.26749 | 0.14498 |
| Oracle known-M moment 3sigma selected N | 309 | 309 |
| Oracle known-M required P_charged_survival*epsilon | 0.0025106 | 0.0013607 |

At hypothetical epsilon=0.1 (excluding charged survival),
the min-abs-pz approach would need charged survival at least
0.46336 (85 TeV) and 0.29773 (100 TeV), respectively, in the
signal-only toy. Whether those conditions can be physically
realized is UNKNOWN. W- contribution not included in the
signed-angle significance because the signed Phi convention
was only validated for W+Z; do not multiply the yield by
the full W+W- rate unless validating the CP-conjugate
observable and charge-sensitive angular inference.

The rapidity spectrum is the **initial constituent-pair CM**,
not a demonstrated final resonant state boost: deexcitation,
ISR recoil and constituent beta decay are absent.

## Gates

- Independent PDF production formula vs original triangular
  x1,x2 convolution: PASS at 0.002% (85) / 0.003% (100).
  This checks the integrated total, NOT the differential
  rapidity distribution against an independent generator.
- Opposite-sign a1 truth: PASS in the 5x12 analytic grid.
- Opposite-sign a1 after small-|pz| root: PASS in this 5x12 toy.
- Collider-specific angular-grid convergence: **UNKNOWN**.
  A previous 5x12->8x16->12x24 *uniform y* test changed
  the min-|pz| coefficient materially; the current PDF y
  test must be refined before quoting stable dilution numbers.
- Absolute bound-state survival: UNKNOWN.
- Low-tanbeta UV physical model: UNKNOWN.
- Full signal with lepton acceptance and SM WZ continuum: UNKNOWN.
- CP-conjugate W- angular interference: NOT_EVALUATED.
- Source Eq A.2 hidden-infracolor normalization:
  SOURCE-MATCHED_AS_PRINTED, independent color audit still PENDING.

## Controlled angular-only and PDF-only refinement

Run EXACTLY the same input PDF and same 85/100 TeV scenarios
as the first pilot, and keep PDF rapidity/shat quadrature
fixed while changing ONLY the angular integration:

    cd ~/quirkonium-helicity-pilot

    python scripts/quirkonium_fcc_pdf_rapidity_gate.py \
      --pdf-set MSTW2008lo68cl \
      --scenarios 85:20000 100:30000 \
      --mass 500 --tanbeta-high 3 \
      --polar-nodes 8 --phis 16 --orientations 5 \
      --rapidity-nodes 24 --shat-nodes 40 \
      --reference-nodes 72 --flavor-mode full-ckm \
      --charge-mode wplus \
      --output /data/aalida/quirkonium-production/fcc_pdf_rapidity_ang8x16.json

If angular results are stable enough in the first controlled
refinement, re-run with ONLY PDF numerical quadrature varied:
  polar=8, phi=16, orientations=5,
  rapidity=40, shat=64, reference=72.
Save to a DIFFERENT output path and compare sigma, a1, and N.

The smaller-|pz| root selection is discontinuous. Convergence
of a1 is not guaranteed to be monotonic, so require more than
one numerical resolution comparison and do not assume that
0.002% inclusive PDF agreement validates the decay-plane
moment itself.

## Next physical phase only after numerical check

Source-matched survival P_deexc = exp(-t_deexc/tau_beta),
integrated over physically weighted production E_T/hat{s}
with explicit hidden glueball mass/cooling assumptions;
keep initial-pair-to-final-resonance boost a controlled
approximation. Then apply generator-level acceptance and
source-matched parton-level SM WZ background; do not
claim formal collider reach until then.

Sources: Forsyth et al arXiv:2504.02940 Sec 2/3 and
Appendix A.2. LHAPDF 6 arXiv:1412.7420.
