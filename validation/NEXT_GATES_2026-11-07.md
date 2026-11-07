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


## 2026-11-07 — User-run continuation results (66-test PASS)

Direct Ubuntu terminal output establishes:

* Python: **66 tests PASS** in 3.633 seconds.
* Mathematical D-term two-branch gate: **7/7 masses PASS**, M=250,300,
  400,500,800,1200,2000 GeV; for tanbeta_high=3 matched low-tanbeta
  solutions are 0.490813616081, 0.463905016580, 0.421083863861,
  0.394724021524, 0.359987245098, 0.345674525124, 0.337874169952.
  Identical LO f00 and normalized two-channel BR(WZ), but opposite signed
  a1 at each mass, IN THE SPECIFIED amplitude model. No new physics
  parameter-space viability gate was completed.
* Ideal azimuthal moment at M=500,tanbeta=3: a1=-0.120305, a2=0.02268.
  Approx. 1249/3469 CLEAN selected signal events for 3/5 sigma nonzero
  moment with full reconstruction, no backgrounds; NOT collider reach.
* Independent MG5 summed MEs: **12/12 PASS** (WZ and Wgamma at six
  masses/tanbeta points). Maximum absolute relative deviation
  1.2025731282032518e-10 at WZ M=2000,tanbeta=3.
* Independent MG5 helicity-SQUARED results at M=500,tanbeta=3:
  WZ transverse 0.0004823977211492944 vs 0.0004823977211491437
  analytic; longitudinal 0.004835122358313449 vs
  0.004835122358311841 analytic.
  f00(MG5)=0.9092814481298518 vs f00(analytic)=0.9092814481298503.
  Wgamma all-transverse 0.0016806924742524885 vs
  0.0016806924742519627; longitudinal and unphysical parts zero.
  COMPLEX relative H++/H00 phase needed for signed a1 is NOT
  checked by these squares.
* INSPIRE first-hop script reported scalar_2008=0, fermionic_2011=4,
  spin_bound_states_2011=406, scalar_2025=2 forward papers and
  complete_requested_scope=True.

**Critical INSPIRE integrity inconsistency:** The published 2025 Forsyth
paper (PRD 111 115021, DOI:10.1103/34xj-vz82) explicitly cites the
2008 Burdman paper (PRD 78 075028) as ref. 51. Thus zero forward
citations for the 2008 seed is NOT a trustworthy complete graph.
Whether the cause is INSPIRE curation, ID mapping or query errors is
UNKNOWN. Previously returned complete_requested_scope=True only
signified paginated response completion, not source corroboration.
A new source-backed forward-edge and identifier consistency guard
in scripts/inspire_quirkonium_citations.py flags the graph as inconsistent
until the known edge is recovered. Run the crawler again.

Validation status: analytic/summed amplitudes PASS 12 external points;
squared helicities PASS 1 point; signed complex phase UNKNOWN;
tanbeta<1 physical model viability UNKNOWN; full citation-network
integrity/novelty UNKNOWN; paper readiness NOT ESTABLISHED.

    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v
    python scripts/inspire_quirkonium_citations.py --depth 1

No changes to the original matrices, model sources or original cards.
