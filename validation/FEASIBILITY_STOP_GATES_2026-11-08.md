# Charged scalar quirkonium WZ angular-sign feasibility: decisive pilot
Date: 2026-11-08. Branch: research/pilot1-literature-model-gate.

## Purpose and release gate
The exact two-branch WZ normalized-rate degeneracy and ±a1 sign are
already independently checked in MG5 spin-correlated six-body MEs.
This pilot tests whether (A) the low-tanbeta branch is at least
TREE-LEVEL mass-compatible with the restricted scalar-doublet model
and (B) the a1 sign is retained by a specific truth-MET, two-solution
W-neutrino longitudinal-momentum reconstruction, *without*
using detector simulation, experimental efficiency or a pp production
model.

The pilot CANNOT prove an accessible physically consistent UV model or
collider sensitivity. Keep statuses scoped. A failure in the toy
reconstruction is a problem for the chosen prescription, NOT a proof
that no better observable or reconstruction exists.

## Gate A — D-term model and leading-order Yukawa scale

Source: Forsyth et al., PRD 111 115021 (2025), Sec 3 Eqs 3.1–3.4;
2026 erratum PRD 113 079901 corrected Eq 3.4.

Neglect first-generation SM quark masses, lift right-handed squarks,
and assume a common unbroken SU(2)L doublet soft m_Q². Then
m_uL² = m_Q² + (1/2 - 2sW²/3) mZ² cos(2β)
m_dL² = m_Q² - (1/2 - sW²/3) mZ² cos(2β)
and so (m_uL² - m_dL²) = mW² cos(2β).
If M = m_uL + m_dL, Delta = mW² cos(2β)/M.
Both low/high tanbeta branches can satisfy this identical tree-level
mass relation; they have different m_Q² inputs.

At M=500 GeV:
- tβ_low=0.394724021524: Delta=+9.43781744 GeV, m_uL=254.71890872,
  m_dL=245.28109128, reconstructed common m_Q²=62748.0075 GeV².
- tβ_high=3: Delta=-10.33725383 GeV, m_uL=244.83137309,
  m_dL=255.16862691, reconstructed common m_Q²=62279.4621 GeV².

For the additional **assumption** of a conventional type-II top-Yukawa
relation, y_t(tree,weak) = sqrt(2)*m_t/(v sinβ).
With v=246.22 GeV and running m_t(m_t)=163 GeV input (not an RGE
computation), low gives y_t≈2.550, high ≈0.987.
With pole mass 172.5 GeV, low ≈2.699, high ≈1.044.
Even a value below sqrt(4π) is only an initial-scale heuristic;
it is NOT a proof of perturbativity up to the cutoff. No SUSY RGE,
Higgs mass, EWSB, tachyon/mixing, EWPO, vacuum, or cosmology tests
were performed. The 2026 erratum studies .1<=tanbeta<=10, but does
not certify a folded-SUSY UV-complete low-tanbeta branch.

A **new fact that matters for identifiability**: at fixed M and equal
wavefunction normalization |R(0)|², the absolute Wγ (and WZ)
partial widths are different even though their normalized
BR(WZ) and f00 match. The Wγ width contains
D²=[Q_u+Q_d-Delta/M]²; the M500 low/high ratio is
[(1/3-9.43781744/500)/(1/3+10.33725383/500)]² ≈ 0.789.
Do not claim same absolute partial width or signal production rate
without an independent normalisation argument.

The source's beta-decay lifetime Eq 3.5 is only an *approximate*
function of |Delta|. A full cooling vs beta-decay comparison needs
a source-matched t_deexc, boost, species and energy distribution.
It remains UNKNOWN.

## Gate B — ideal no-detector neutrino pz roots

For each generated 2-to-4 on-shell W+Z decay:
- Weight (cosθ_W,cosθ_Z,Phi) by the fully correlated analytic
  joint density for each scalar bound-state branch.
- Rotate W direction relative to proton beam with an isotropic angular
  quadrature, and apply an **explicit illustrative** longitudinal
  parent boost set. This is NOT a simulated rapidity distribution.
- Use exact missing transverse momentum from the neutrino, and
  the known mW constraint to solve its two quadratic pz roots.
- Reconstruct both W/Z helicity frames from lab charged leptons and
  each neutrino root, defining the signed Phi by the W+ charged lepton
  and the Z negative lepton in the exact same right-handed frames
  used in the analytic matrix element.
- Require exact known-pz closure to original generated Phi.
- Compare four cosPhi moments: true pz; smaller |pz|;
  m(WZ) closest to known M (OPTIMISTIC, uses signal mass);
  equal root average (a toy, not optimal fit).
- Extract a1,a2, and the ideal selected signal count for
  3σ/5σ separation of the TWO specified branches with the
  *same simple cosPhi moment estimator*. These are not universal
  significance estimates or background-aware limits.
- Re-run with more angular nodes and a different boost ensemble
  to gauge numerical convergence and model dependence. A single
  deterministic ensemble is insufficient to claim measurement reach.

This validates a kinematic effect only. No detector smearing, pileup,
FSR, fiducial selection, W/Z off-shell tails, pp production
acceptance, sigma(pp→Ψ), bound-state deexcitation, charge-state mixture,
or irreducible SM WZ background was included.

## Statistical production-rate diagnostic

Only if Ψ± decays into WZ or Wγ, use its model BR(WZ)≈0.7531.
For W→e/μν≈0.216 and Z→ee/μμ≈0.0673, the observed
trilepton channel fraction is ~0.01095 BEFORE acceptance.
At L=3000 fb^-1, ~313 (868) *selected clean* events for 3σ
(5σ) separation of known opposite-sign ideal a1 hypotheses require
at least ~9.5 (~26.4) fb effective charged-bound-state production
for 100% reconstruction/acceptance. If efficiency is 10%, required
cross sections are ~95 (~264) fb, before backgrounds. **The actual
charged bound-state production cross sections are UNKNOWN in this
pilot**, as are the performance and WZ continuum backgrounds.
Do not label the numbers experimental discovery projections.

## Reproduce the NEW code

    cd ~/quirkonium-helicity-pilot
    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v
    python scripts/quirkonium_model_domain_gate.py --masses 250 500 1000 2000
    python scripts/quirkonium_neutrino_pz_gate.py \
        --mass 500 --high-tanbeta 3 --nodes 5 --phis 12 \
        --orientations 5 --rapidities=-1,0,1

If the default toy passes truth closure, test numerical stability:

    python scripts/quirkonium_neutrino_pz_gate.py \
        --mass 500 --high-tanbeta 3 --nodes 8 --phis 16 \
        --orientations 7 --rapidities=-1.5,-0.5,0,0.5,1.5 \
        --output validation/local_logs/neutrino_pz_ambiguity_gate_refined.json

Files:
  validation/local_logs/model_domain_and_yield_gate.json
  validation/local_logs/neutrino_pz_ambiguity_gate.json
  validation/local_logs/neutrino_pz_ambiguity_gate_refined.json

User must run these scripts locally; no local MG5 or
neutrino-response execution was performed by the assistant when
committing this file. The existing independent MG5 2-to-4 phase
check remains PASS as USER-REPORTED evidence.

## Explicit decision branches

* If tree doublet MASS consistency fails => fix model errors before
  considering the benchmark.
* If reconstructed **known-pz truth closure** fails => stop, debug
  angular-frame convention; no angular inference allowed.
* If min-|pz| loses opposite a1 signs => do not claim that prescription
  measures the sign; test another explicit estimator (possibly fully
  leptonic angular functions or mass-constrained likelihood).
* If signs persist only when using exact M to choose pz => the
  result needs a mass-dependent search strategy and cannot be called
  model-independent.
* If robust signs persist at truth-level but selected event requirements
  exceed plausible production rates from a source-matched calculation =>
  the proposed LHC measurement is not a strong paper foundation.
* Even if every toy gate passes, SUSY UV consistency, signal rates,
  actual acceptance and full novelty remain UNKNOWN => no paper GO.

Sources:
- 10.1103/34xj-vz82 and 10.1103/lwnc-cmpn;
- 10.1007/JHEP12(2024)120 (Grossi et al. angular reconstruction);
- 10.1103/PhysRevD.81.075022 (Gao et al., generic angular phases);
- literature/NOVELTY_AUDIT_INDEPENDENT_2026-11-07.md.
