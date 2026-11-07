# Research pilot continuation — execution and decision gates
Date: 2026-11-07. Branch: research/pilot1-literature-model-gate.

## Established before this continuation
- 51/51 Python tests PASS, user run.
- Independent MG5_aMC 3.5.1 WZ and Wgamma helicity-SUMMED ME2
  PASS at M500/tanbeta3 to ~3e-13 relative after correcting the SLHA
  21-character field-truncation defect.
- Published partial widths and independent Mathematica checks PASS scoped.
- Relative complex helicity phases, novelty and model viability UNKNOWN.

## New mathematical mechanism (code committed; user execution pending)

For a single charged spin-0 scalar quirkonium state, only Wgamma and
WZ open, LO on shell, at fixed mass:
Gamma(WZ)/Gamma(Wgamma) = (sW^2/cW^2)
  * beta_WZ/beta_Wgamma / (1-f00).
Thus rate ratio and f00 are redundant normalized data, whereas signed
a1 proportional to Re(H++ H00*) carries phase information.

At M=500 GeV, the two ideal scalar branches tanbeta approximately
0.394724021524 and 3.0 have the same f00=0.9092814481 and
BR(WZ)=0.7530816453 but opposite a1 approximately +/-0.1203051105.
This is a mathematical observation requiring source/model admissibility
and prior-art screening; it is not yet a publishable phenomenology result.

## Run in order (not yet executed on user workstation)

    cd ~/quirkonium-helicity-pilot
    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v

    python scripts/quirkonium_branch_degeneracy.py
    python scripts/ideal_a1_statistical_gate.py

    .venv-mg5-f2py/bin/python scripts/mg5_benchmark_grid.py
    .venv-mg5-f2py/bin/python scripts/mg5_fixed_helicity_audit.py

    python scripts/inspire_quirkonium_citations.py --depth 1

The networked INSPIRE step may return INCOMPLETE due to connectivity;
failure does not imply no prior literature. The benchmark grid and
helicity scripts require existing local generated standalone outputs.
No canonical SLHA cards, model UFO, matrix.f or original analytical
amplitudes are edited by these programs.

### Evidence files
- validation/local_logs/branch_degeneracy_pilot.json
- validation/local_logs/ideal_a1_statistical_gate.json
- validation/local_logs/threshold_benchmarks/independent_grid/summary.json
- validation/local_logs/threshold_benchmarks/M500_tanbeta3_Z/fixed_helicity/summary.json
- validation/local_logs/threshold_benchmarks/M500_tanbeta3_gamma/fixed_helicity/summary.json
- validation/local_logs/inspire_quirkonium_citation_graph.json

## Explicit PASS/UNKNOWN gates

| Claim | Current status | Decisive test |
|---|---|---|
| Published scalar WZ/Wgamma amplitudes | PASS scoped one benchmark | Multi-mass independent MG5 grid |
| Complex relative phase a1 | UNKNOWN external | Direct complex helicity amplitude extraction, not only LL/TT squares |
| Signed-a1 two-branch ambiguity | MATHEMATICAL PILOT pending local run | Low/high tanbeta solve; normalized rates and phase signs |
| Model viability at tanbeta ~0.395 | UNKNOWN | Confront original model (tanbeta>1 SUSY description) with erratum's 0.1-10 treatment; perturbativity/spectrum analysis |
| Observable strength | UNKNOWN | Ideal event-cost estimate is only necessary diagnostic, not LHC reach |
| Literature novelty | UNKNOWN | Exact source formula comparison and INSPIRE citations (scope and pagination recorded) |
| EPJC/PTEP readiness | NO-GO | Demonstrate distinct and sufficiently substantive model mechanism and applicability |

The 2026 erratum considers 0.1<=tanbeta<=10 in its corrected physical
plots, but that alone is not a full perturbativity or UV-completion gate.

## Publication stop criteria
- Same angular mechanism explicitly established in source literature;
- one of the two branches not viable in the model claimed;
- independent helicity-phase check fails;
- a1 inference evaporates after required model-state mixtures;
- no plausible event-level observational meaning even at truth level.

If stop criteria hold, archive reproducible physics checks and pivot to
another quirk idea rather than extending an incremental f00-only paper.
