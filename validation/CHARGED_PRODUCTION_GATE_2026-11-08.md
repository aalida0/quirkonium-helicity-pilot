# Charged squirkonium production ceiling gate — Forsyth Eq. (A.2)

**Date:** 2026-11-08. **Purpose:** compare user-run *ideal* sign-discrimination trilepton requirements against a real PDF-convoluted charged scalar-pair production rate, WITHOUT SM QCD squark production, showering, detector simulation, or fabricated survival probabilities.

## Inputs already observed (user's fixed-ensemble 12x24 toy)

M = 500 GeV, tanbeta(low)=0.394724021524, tanbeta(high)=3.
Truth a1=+0.1203701/-0.1203701.
With the smaller absolute neutrino-pz root:
a1 low = +0.0394985, high = -0.0386140,
Delta a1 = +0.078112.
3sigma selected-signal count for the specific background-free
2cosPhi simple-moment estimator = 2979, corresponding to a
minimum effective charged-pair production sigma=90.71 fb at
sqrt(s) unspecified in the toy, L=3000/fb and perfect acceptance.
At assumed epsilon=0.3: required sigma~302.37 fb;
at epsilon=0.1: required sigma~907.1 fb,
BEFORE SM WZ background and all systematic uncertainties.

The original same-ensemble 5x12,8x16,12x24 integrations gave
Delta a1=0.098015,0.090099,0.078112 and required clean selected
N=1892,2239,2979, respectively. The toy coefficient has NOT
demonstrated numerical convergence! The sign persists across the
tested integration resolutions only.

## Source-matched production formula

Forsyth et al., *Visible collider signals of natural quirks*,
Phys. Rev. D 111, 115021 (2025), Appendix A.2 Eqs. (A.2)-(A.3):
for u dbar -> tilde{u}_L tilde{d}_L^* through an off-shell W+,

  hat_sigma = pi alpha_W^2/(32 hat_s) *
      beta^3 / (1-mW^2/hat_s)^2,
  beta = sqrt[(1-M^2/hat_s)(1-Delta^2/hat_s)].

M=m_u+m_d, Delta=m_u-m_d. The charge-conjugate partonic W-
process has the same hat_sigma. This is a scalar pair with hidden
SU(3) confining color, not SM color QCD squark production.

At fixed M, the rate is EXACTLY EVEN under Delta -> -Delta
within Eq. (A.2). Our two f00-degenerate branches have DIFFERENT
magnitudes of Delta, ~+9.44 and -10.34 GeV, so their rates will
not be mathematically identical but should be very close at the
squared-splitting level. The physically discriminating absolute
rate is expected to depend more strongly on the subsequent
beta-decay-versus-deexcitation survival probability; that remains
unknown.

LO proton convolution:
  sigma_pp = sum_flavors integral dx1 dx2 f_a(x1,Q) f_b(x2,Q)
        hat_sigma(x1*x2*s) theta(x1*x2*s-M^2),
where a,b permutations for proton beams and W± are counted
explicitly. The repository script uses y_i=ln(x_i) with
Gauss-Legendre quadrature, thus needing only x f(x,Q)
values from LHAPDF.

**Conventions needing audit before a publication plot:**
- Eq A.2 normalization: no additional hidden SU(3) multiplicity
  inserted. Check whether the source's displayed result already
  includes the hidden color factor before changing it.
- The displayed formula is for u dbar. The script's optional
  --flavor-mode full-ckm adds CKM-weighted 2x3 quark channels,
  an explicitly labelled extension beyond that displayed term.
  Run --flavor-mode ud as the formula-only control.
- PDF set, member, perturbative order and factorization scale must
  be recorded. The 2009 Martin et al. citation indicates an
  MSTW2008-family input, but the exact PDF run card for the
  published MadGraph curves was not provided. Using the
  available MSTW2008lo68cl set is a *documented reference
  choice*, not proven identical to their original setup.
- The Python code uses the repo's alphaW=0.0338 and mW=80.379 GeV;
  validate input scheme differences before precision predictions.
- The original paper plotted 13 TeV pp collisions; user intends
  13.6 and potentially 14 TeV. These are not directly comparable.
- No QCD correction, PDF uncertainty or electroweak higher orders.
- The differential charged-state survival rate could depend on
  charge and sign of Delta. Do not replace it by 1 for a paper.
- "Source production" is the newly produced charged constituent
  pair; formation and prompt charged annihilation are distinct
  physical stages. The inclusive pair rate is a maximal bound,
  not an observed WZ resonance production rate.

## Code committed; results not yet user-run

Source: scripts/quirkonium_production_pdf_gate.py
Offline tests: tests/test_quirkonium_production_pdf_gate.py

The optional Python LHAPDF module and a locally installed PDF set
are needed only for real cross sections. The assistant environment
does not have LHAPDF; no PDF production result has been calculated
and no rate PASS/FAIL exists yet.

Check local dependencies:

    which lhapdf-config || true
    command -v lhapdf || true
    python -c "import lhapdf; print('LHAPDF import works')" || true

After installing or activating bindings and the installed LO set:

    python scripts/quirkonium_production_pdf_gate.py \
      --pdf-set MSTW2008lo68cl \
      --energies 13.6 14 \
      --masses 500 \
      --nodes 48 72 \
      --flavor-mode ud \
      --required-fb 90.71 \
      --output validation/local_logs/charged_prod_ud_LO.json

    python scripts/quirkonium_production_pdf_gate.py \
      --pdf-set MSTW2008lo68cl \
      --energies 13.6 14 \
      --masses 500 \
      --nodes 48 72 \
      --flavor-mode full-ckm \
      --required-fb 90.71 \
      --output validation/local_logs/charged_prod_fullckm_LO.json

The two integration orders must agree to <1% or output is flagged
NOT_CONVERGED. Explicit PDF installation requirements are documented
at https://www.lhapdf.org/install.html and official PDF sets at
https://www.lhapdf.org/pdfsets.

## Interpretation, no paper GO

For each branch and pp energy, assess sigma_pair against
sigma_required = 90.71 fb (perfect acceptance), then against
90.71/(P_survival*epsilon) for any actually justified P_survival
and epsilon.

- If even the *maximal inclusive charged-pair rate* is below the
  required sigma for this toy moment, the chosen toy test with
  P_survival<=1 and acceptance<=1 is not statistically achievable
  under its own assumptions; a different estimator could improve.
- If sigma_pair exceeds it, this is at most a NECESSARY condition.
  Charged survival, realistic acceptance, neutrino smearing,
  background contamination, PDFs and NLO uncertainties may destroy
  feasibility.
- The toy rapidity and orientation choices are not a pp
  production model. Before a final research decision, use the
  calculated charged-pair differential production kinematics rather
  than an arbitrary uniform boost grid.

No LHC reach, exclusion or publication readiness claim is justified
from the PDF-integral number alone.
