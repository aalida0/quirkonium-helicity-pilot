# Feasibility pilot — user-run numerical results and reviewer decision

**Date:** 2026-11-08
**Source:** Ubuntu terminal logs pasted by user. No underlying ignored JSONs were attached.
**Model:** charged scalar quirkonium in the restricted doublet D-term model, **not** a validated full folded-SUSY UV completion.
**Scope:** analytic angular-density weighted 2->4 on-shell kinematics, exact neutrino missing pT, illustrative boost ensembles and NO detector response/backgrounds.
**Latest phase check from previous stage:** user-run independent full spin-correlated MG5 2->4 signed a1 PASS. The current reconstruction is a *separate analytic weighted toy*, not independent matrix-element validation.

## Automated tests: diagnosed and patched

The original 81-test run had one failure:
test_toy_ensemble_closes_truth_analytic_phase produced
  numerical 3-node Gauss-Legendre/8-Phi result = 0.12351554002339352
  analytic closed coefficient                = 0.12030511054331107
  absolute difference                        = 0.00321042948008245
while the hard-coded numerical tolerance was 0.003.

**Cause:** inadequate 3-node angular quadrature for the particular
cosPhi interference integral, not an observed physics failure. In the
user's denser 8-node/16-Phi run, the truth coefficient is 0.1205134,
only ~2.08e-4 from the analytic closed form. An intermediate
5-node/12-Phi calculation gives 0.1210891, ~7.84e-4 from closed.

Correction committed to
tests/test_quirkonium_feasibility_gates.py:
explicitly evaluate both 3-node and 5-node quadratures with the
*same other settings*, require the 5-node rule to reduce the actual
error vs the closed analytic coefficient and require <0.0015
absolute error. **Do NOT merely widen the old tolerance to .004.**
The repaired suite has not yet been user-rerun, so no new PASS claimed.

## Model-domain numerical results (user-run, PASS scoped tree-level)

| M (GeV) | matched low tanbeta | weak-scale type-II-assumed low y_t (m_t=163 GeV) | Γ(WZ) low/high at fixed |R(0)|² | ideal 3σ required σ_prod ε=1 (fb), before pz dilution |
|---:|---:|---:|---:|---:|
| 250 | 0.49081362 | 2.1249 | 0.4215 | 8.16 |
| 500 | 0.39472402 | 2.5499 | 0.7890 | 9.53 |
| 1000 | 0.35084620 | 2.8279 | 0.9406 | 9.97 |
| 2000 | 0.33787417 | 2.9248 | 0.9847 | 10.09 |

All four common left-doublet soft-mass tree tests **PASS**.
This checks only the original D-term mass relation. It does NOT
test Yukawa running, the folded-SUSY cutoff, Higgs sector,
scalar mixing, loop corrections, confinement, cooling, beta decay
or realistic production. **UV viability UNKNOWN**.
At M500 and common wavefunction normalization the two solutions
have unequal absolute widths (low/high ~0.789), while their normalized
BR(WZ) and f00 match. Thus there is no absolute-rate degeneracy
claim.

## Neutrino-pz ambiguity (M=500 GeV; observed)

Full on-shell truth-angle closure passed. Both toy ensembles
preserve the opposite signs when choosing the smaller |pz| root.
However the coefficient is strongly diluted.

| Scenario | low a1 | high a1 | Δa1 | ideal N_selected 3σ | minimum σ_prod ε=1 at L=3000 fb^-1 |
|---|---:|---:|---:|---:|---:|
| coarse (5 nodes, 12 Φ, 5 orient; y=-1,0,1), TRUE pz | +0.1210891 | -0.1210891 | 0.242178 | 309 | 9.41 fb |
| coarse, min |pz| | +0.0494202 | -0.0485950 | 0.098015 | 1892 | 57.61 fb |
| coarse, equal-root moment | +0.0124455 | -0.0110614 | 0.023507 | 32923 | 1002.46 fb |
| refined (8 nodes, 16 Φ, 7 orient; y=-1.5,-.5,0,.5,1.5), TRUE pz | +0.1205134 | -0.1205134 | 0.241027 | 312 | 9.50 fb |
| refined, min |pz| | +0.0425996 | -0.0417345 | 0.084334 | **2556** | **77.83 fb** |
| refined, equal-root moment | +0.0135580 | -0.0122036 | 0.025762 | **27414** | **834.72 fb** |
| refined, known mass chooses pz | +0.1205134 | -0.1205134 | 0.241027 | 312 | 9.50 fb |

The "known-M" solver always chose the truth root in this **exact on-shell,
perfectly measured** toy. It is an *optimistic oracle-like upper-bound
diagnostic*, not a demonstrated detector/analysis reconstruction algorithm.

In refined min-|pz|:
- retained |a1| is ~35% of truth;
- required 3σ selected events rise from 312 to 2556, factor ~8.19;
- at ε=0.3, minimum necessary σ_prod ~259.4 fb;
- at ε=0.1, minimum necessary σ_prod ~778.3 fb.
For refined equal-root averaging at ε=0.1, the threshold would exceed
8 pb at 3σ before any backgrounds. These are **conditional
signal-only moment-estimator counts**, not universal sensitivity lower
bounds, not a signal-rate forecast and not statistical likelihood claims.

**Important:** the coarse and refined runs changed simultaneously:
polar quadrature, azimuthal sampling, orientation sampling AND the
synthetic rapidity ensemble. Their min-|pz| shifts therefore
**do not prove numerical convergence**. Separate the axes before
quoting stable coefficients.

### Minimal controlled reruns (no new code needed)

Keep the **same** rapidities and orientation rule to isolate only
angular-integration refinement:

    python scripts/quirkonium_neutrino_pz_gate.py \
       --mass 500 --high-tanbeta 3 --nodes 8 --phis 16 \
       --orientations 5 --rapidities=-1,0,1 \
       --output validation/local_logs/neutrino_pz_fixed_kinematics_fine.json

Then change only the rapidity/orientation model at the SAME angular
integration order. Physical pp rapidity/PDF dependence must be
computed separately before treating the toy dilution as collider reach.

## Literature cross-check

Forsyth et al., PRD 111 115021 (2025), arXiv:2504.02940,
Sec III.B.2 and Fig 5: bound-state production is modeled by
PDF convolutions/MadGraph; WZ searches offered no additional
exclusion in their model, even with Δ up to 40 GeV.
The corrected 2026 erratum DOI:10.1103/lwnc-cmpn updates Fig 5(b)
with the appropriate semileptonic branching fractions and states
that the WZ resonance constraints still do not add bounds.
This is **not** a published numerical σ(pp→Ψ±) value for our
specific ±Δ branches, and must not be used to fabricate one.
The paper's background-free resonance+displaced-glueball
strategy is different from the proposed trilepton angular
measurement with substantial SM WZ continuum.

## Decision register

- Tree-level doublet mass compatibility: PASS, four M; physical UV: UNKNOWN.
- Helicity-summed ME and independent 2->4 signed interference: PASS scoped.
- Neutrino smaller-|pz| opposite-sign *toy*: PASS conditional on
  perfect missing pT/on-shell WZ and selected boost distributions.
- Small-root coefficient stability/pp rapidity: UNKNOWN.
- Actual signal production vs min 77.8 fb optimistic threshold: UNKNOWN.
- Background/fiducial response: UNKNOWN.
- Claim that the model-specific sign flip is enough for standalone
  EPJC/PTEP: not supported.

**Current recommendation:** strong grounds to avoid writing a paper
on the angle calculation alone; do one production-yield screen and a
model-specific UV cutoff check before any new extensive work. If
σ_prod is clearly below the conditional minimum for plausible
acceptances, **do not pursue an LHC discovery claim** based on
this trilepton moment; an alternative model-theory paper would need
additional genuinely distinct results.

## Links
- Phys. Rev. D 111, 115021 (2025), https://doi.org/10.1103/34xj-vz82
- 2026 erratum https://doi.org/10.1103/lwnc-cmpn
- feasibility protocol validation/FEASIBILITY_STOP_GATES_2026-11-08.md


## Follow-up: user-run same-ensemble angular refinement (2026-11-08)

User fixed orientations=5 and rapidities=[-1,0,1], increased
polar Gauss-Legendre nodes 5 -> 8, Phi samples 12 -> 16.
Saved under validation/local_logs/neutrino_pz_fixed_kinematics_fine.json.

| Observable | 5x12 coarse same ensemble | 8x16 fine same ensemble |
|---|---:|---:|
| a1 low/high true | +/-0.1210891 | +/-0.1205134 |
| a1 low min-abs-pz | +0.0494202 | +0.0454307 |
| a1 high min-abs-pz | -0.0485950 | -0.0446683 |
| min-abs-pz Delta a1 | +0.098015 | +0.090099 |
| min-abs-pz correct pz root fraction | 0.663 | 0.645 |
| min-abs-pz N clean selected for 3 sigma | 1892 | 2239 |
| min-abs-pz min effective sigma production, eps=1 | 57.61 fb | 68.17 fb |
| equal-root average N clean 3 sigma | 32923 | 43787 |
| equal-root min sigma production, eps=1 | 1002.46 fb | 1333.25 fb |

The refined same-ensemble study still reports
TOY_OPPOSITE_SIGNS_RETAINED. The high/low sign reversal
survives at the selected reconstruction prescription.
However Delta a1 changes ~8.1 percent, causing an 18.3 percent
increase in signal-only moment count. Thus the numerical
estimate is **not yet converged**: test 12 polar nodes and
24 Phi at the *same* rapidities and orientations.

At M500 and L=3000 fb-1, the new fixed-ensemble 3sigma
minimal production requirement 68.17 fb at perfect efficiency
becomes 227.2 fb at epsilon=0.3 and 681.7 fb at epsilon=0.1,
still BEFORE any irreducible SM WZ background or detector
smearing. This is a selected-signal moment-estimator
diagnostic only, not a collider sensitivity result.

For a different 7-orientation/5-rapidity ensemble, prior
8x16 result 77.83 fb cannot be interpreted as an
angular-convergence change.

### Production caution from original source

Forsyth et al PRD 111 (2025) 115021, Appendix A.2,
provides the charged scalar pair-production parton-level
cross section via s-channel W*. Sec. 4.1.1 Eq. (3.6)
applies bound-state deexcitation probability versus heavy
constituent beta-decay, reducing charged resonance yield.
The April 2026 erratum corrected Fig.5(b) to multiply the
WZ production curves by SEMILEPTONIC branching fractions,
not the fully leptonic 3lnu BR needed here.

Thus actual sigma(pp->charged pair) and the deexcited
charged survival probability have NOT been evaluated by
this pilot; production vs the necessary >68.17 fb is
UNKNOWN. Do not use the MSSM_SLHA2 strong-QCD squark pair
production as a proxy: the target squirks are SM-color
singlets, and only their hidden infracolor SU(3) multiplicity
matches the 3-state bookkeeping. The existing MG5
MSSM_SLHA2 WZ annihilation calculation does not give
the hadronic charged pair production cross section.

The old test failure from 3-point Gauss-Legendre quadrature
was fixed with a strict 3->5 point convergence assertion,
but no user-run post-fix test result has yet been received.
