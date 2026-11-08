# FCC-hh no-detector pilot: PDF-weighted production rapidity and signed WZ interference

**Date:** 2026-11-08. **Branch:** research/pilot1-literature-model-gate.
**Status:** CODE IMPLEMENTED; LHAPDF run on AF not yet performed for this NEW differential workflow.

## Research target

At M=500 GeV, a tree-level common SU(2) scalar-doublet D-term
relation supports a low-tanbeta branch (~0.394724) and a high one
(tanbeta=3) with almost equal normalized WZ helicity fractions and
WZ/Wgamma BRs, yet opposite signed ideal W+Z cos(Phi) interference:
low a1~+0.1203, high a1~-0.1203.
The amplitudes and exact spin-correlated 2->4 matrix elements were
previously checked independently with MG5. However the W-neutrino
pz root ambiguity dilutes the signed coefficient strongly.

HL-LHC production vs toy moment yield: full CKM LO charge-summed
sigma_pair=65.022 fb at 14 TeV; with the *nonconverged*
fixed-boost 12x24 moment estimator the clean-signal yield would
require >90.71 fb at P_survival=efficiency=1, even before backgrounds.

User-run AF full-CKM production (M500):
- 27 TeV: W+-sum=188.76 fb, 15 ab-1;
- 85 TeV: W+-sum=951.85 fb, 20 ab-1;
- 100 TeV: W+-sum=1179.7 fb, 30 ab-1;
all MSTW2008lo68cl member0, LO, numerical integration drift <=0.003%.
These numbers alone support only a PRODUCTION-CEILING conditional FCC GO;
they do not yield a valid FCC signal significance.

## New work package A: physical PDF-weighted initial-pair rapidity

Code: scripts/quirkonium_fcc_pdf_rapidity_gate.py

Uses the LO partonic source formula (Forsyth PRD111, 2025,
Appendix A.2) and unmodified PDF+EW conventions from
scripts/quirkonium_production_pdf_gate.py.

Derivation:
  x1 = exp(t/2+y), x2=exp(t/2-y)
  t = ln(x1 x2) = ln(hat{s}/s)
  y = (ln x1 - ln x2)/2
  t_min = ln(M^2/s), t_max=-2|y|
  -ln(sqrt(s)/M) < y < +ln(sqrt(s)/M)
  d x1 d x2 f_a(x1,Q) f_b(x2,Q)
    = d t d y [x1 f_a(x1,Q)] [x2 f_b(x2,Q)].

This Jacobian is exactly ONE. Each positive Gauss-Legendre
quadrature node in y gets an integrated W+ and W- differential
cross section after an independent t quadrature. The original
triangular ln(x1)-ln(x2) PDF integration is separately recomputed;
the independent factorization must agree within 2% in total
charged-pair cross section or the run FAILS. Note: a 2% comparison
tolerance is a preliminary integration check, NOT a 2% physics
uncertainty. Rerun different PDF node numbers for convergence.
PDFs are cached per flavor,x,Q for efficiency.

Both incoming pp beam configurations and both W charge
cross sections are recorded; a pp beam symmetry check expects
d sigma(W+)/dy and d sigma(W-)/dy each to be even in y.

**CRITICAL interpretation:** this is the longitudinal rapidity
of the INITIAL hard-scattering squirk PAIR CM. It is not
demonstrated to equal the final s-wave charged ground-state
resonance boost, because deexcitation glueball recoil, ISR,
state mixing and beta decay are NOT simulated. We assume the
initial pair CM rapidity is inherited by the WZ decaying
state for this deliberately restricted pilot. This must
remain named as an *approximation* in any presentation/paper.

## New work package B: preserve validated angular conventions

Existing code:
  scripts/quirkonium_neutrino_pz_gate.py::run_one
now has optional rapidity_weights. Default uniform rapidity
weights are unchanged; previous fixed-y toy is backward
compatible. Large grids are evaluated by O(1)-memory streaming
moment accumulation (no giant list of event dictionaries).
For each PDF-sourced y node:
  - analytically weighted exact on-shell W+Z->e+nu mu+mu-
    three-angle joint spin density,
  - isotropic orientation of the W direction in parent rest frame,
  - longitudinal boost y, exact neutrino transverse momentum,
  - quadratic W mass pz roots,
  - compare truth, smaller-|pz|, known-M and average roots,
  - a1,a2, truth root fraction, and 3sigma/5sigma signal-only
    simple-moment event cost per *specified pair* of hypotheses.

W+ versus W- **must not be silently combined**:
the existing six-leg amplitude and signed azimuth definition
are specifically for W+Z->e+nu mu+mu-.
Default --charge-mode wplus uses only W+ production
spectrum and rates, so the new result is conservative and
does not assume CP-conjugate angular mapping.
Optional --charge-mode both_cp_assumed uses both charges
but does NOT constitute a validated W- spin-density derivation;
never promote it to a physical quoted rate without an
independent charge-conjugate MG5 test and consistent angle sign.

The original 2979-event / 90.71-fb toy figure assumed the
total W+ + W- charge-summed rate and earlier uniform rapidity
grid. We MUST recompute the threshold for each W+ only
FCC weighted ensemble; those old cross-section thresholds
are NOT universal and cannot be transferred directly.

## Commands for UChicago AF with Key4HEP

After sourcing the existing functional Key4HEP environment
(Python 3.13.8, NumPy 2.2.6, LHAPDF 6.5.5) and configuring
LHAPDF_DATA_PATH to include MSTW2008lo68cl through CVMFS:

    cd ~/quirkonium-helicity-pilot
    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v

Small pilot, two FCC energies, W+ only, 85/100 TeV:

    mkdir -p /data/aalida/quirkonium-production

    python scripts/quirkonium_fcc_pdf_rapidity_gate.py \
        --pdf-set MSTW2008lo68cl \
        --scenarios 85:20000 100:30000 \
        --mass 500 --tanbeta-high 3 \
        --polar-nodes 5 --phis 12 --orientations 5 \
        --rapidity-nodes 24 --shat-nodes 40 \
        --reference-nodes 72 --flavor-mode full-ckm \
        --charge-mode wplus \
        --output /data/aalida/quirkonium-production/fcc_pdf_rapidity_pilot.json

**Controlled refinement:** keep same two FCC scenarios and W+ only;
vary the quadrature with two separately identifiable dimensions.

  [angular only]: polar=8, Phi=16, orient=5, y=24, shat=40.
  [rapidity only]: polar=5, Phi=12, orient=5, y=40, shat=64.
  [both]:         polar=8, Phi=16, orient=5, y=40, shat=64.

No need to run both advanced configurations until the small pilot
has PASSED the independent PDF cross-section normalization check.

To compare HE-LHC optionally:
  --scenarios 27:15000
(This is a separate invocation with an independent output filename.)

## Necessary checks before passing the gate

1. Every report writes an actual JSON (no tuples; no NaN), and
   reproduces previous full CKM charge-summed LO cross sections
   near 951.85 fb (85 TeV) and 1179.7 fb (100 TeV),
   at same source inputs, within 2%.
2. d sigma(W+)/dy and d sigma(W-)/dy even in y for pp beams;
   normalized rapidity weights sum to one; W+ and W- are distinct.
3. Truth reconstructed a1 matches its source analytic closed
   coefficient to angular quadrature error, with opposite signs.
4. The smaller-|pz| signed a1 **may** survive or fail.
   If it fails, record failure, not just the positive truth result.
5. At least one additional angular and rapidity quadrature
   comparison before quantifying min-|pz| damping or Nselected.
   Root-switching is a discontinuous map; monotonic convergence
   is NOT expected. A single 5x12x24 result is not final.
6. Account separately for charged survival, W+ -> e/mu nu,
   Z -> e+e-/mu+mu-, fiducial selection, and SM WZ background.
   No detector-level simulation is required for this scoped
   study, but any sensitivity statement needs an honest
   background and selection model.
7. Physically consistent low tanbeta model and source hidden
   SU(3) color counting remain UNKNOWN.

## Go/no-go criteria

- If the PDF-rate crosscheck fails: METHOD_BLOCKED, do not
  quote angular results. Fix integration/numerics first.
- If opposite signs vanish at min-|pz| after controlled
  convergence: NO GO for this specific reconstruction; do
  NOT claim no alternative full-likelihood can work.
- If signs survive with enough yield at Psurv*eff ~ .01 to
  .1: CONDITIONAL GO for deexcitation survival and
  generator-level fiducial WZ-background work, NOT a paper GO.
- If positive/negative branches are not both viable in a
  source-consistent folded-SUSY-like model: degeneracy/sign
  comparison loses its direct model interpretation.

### Sources
- Forsyth et al, arXiv:2504.02940, Phys Rev D 111 115021 (2025),
  production Eq A.2, deexcitation/constituent beta-decay Eq 3.6.
- Eq A.2 color counting and MadGraph cross section normalization
  remain an explicit separate source audit.
- Existing 2026-11-08 result record:
  validation/FUTURE_COLLIDER_PRODUCTION_GATE_2026-11-08.md
