# Pilot decision — 2026-11-07

**Current decision (2026-11-08 after neutrino-reconstruction feasibility pilot): conditional GO for only a source-matched production-yield and low-tanbeta UV-consistency screen; NO-GO for a standalone a1-plot manuscript or LHC sensitivity claim. Analytic + MG5 WZ/Wgamma and full 2->4 signed interference PASS scoped. User-run low/high scalar branches pass the tree-level doublet D-term mass gate; UV viability UNKNOWN. The min-|pz| truth-MET toy retains opposite a1 signs but dilutes |a1| to ~0.042 at M500; 3σ signal-only contrast needs ~2556 selected trileptons and >77.8 fb effective production at ε=1, or >778 fb at ε=0.1, before backgrounds. Coarse/refined runs do not isolate integration convergence.**

## Established result

The source-matched Python/Mathematica implementation calculates nominal tree-level scalar charged squirkonium amplitudes for \(W^+Z\) and \(W^+\gamma\), including scalar exchanges, seagull, virtual W*. Helicity-summed widths reproduce source integrated rates, and photon Ward tests pass. The 2026 erratum D-term splitting \(\Delta=m_W^2\cos2\beta/M\) yields dramatic WZ fraction changes, e.g., \(f_{00}=0.001938\) (tanβ=1) versus \(0.935846\) (tanβ=10) at M=500 GeV. The wavefunction factor cancels from this fixed-state LO ratio.

**Caution:** The published Eq. (A.7) already contains the two squared terms whose transverse/longitudinal identification we established with an independent tensor contraction. The new plot and the polarization mapping alone are *probably insufficient* as a distinct phenomenology paper. The pre-erratum splitting used in earlier literature cannot be reused as unconstrained free physics.

## Novelty

- **Known:** integrated scalar Wγ/WZ rates and splitting sensitivity were published in Burdman et al. (2008), Forsyth et al. (2025), and a related thesis *Characterizing Quirky Signals*.
- **Newly derived in this pilot:** explicit physical-state helicity projection, f00 versus erratum-corrected tanβ and the ideal W→ℓν normalized angular marginal, with benchmark tests.
- **Now derived as a pilot result, but not demonstrated novel relative to all literature:** the ideal on-shell two-vector joint lepton-angle density and the (a_1cos\Phi) (longitudinal–transverse) and (a_2cos2\Phi) interference terms. **Still missing:** comparative scalar-versus-fermion observable and experimental/fiducial treatment.
- INSPIRE backward/forward citation graph **not completed**, so no novelty certification.

## Validation gates

See validation/VALIDATION_REPORT.md. Local 9 tests pass and the independent rate expression matches the diagram implementation. Non-Abelian general-gauge STI, UFO-level independence, physical model parameter-space viability and state-population effects are **not certified**. No detector simulation or paper-level likelihood is attempted.

## Smallest scientifically meaningful expansion

1. Complete the canonical INSPIRE references/citations audit, including the 2024/25 *Characterizing Quirky Signals* thesis, and explicitly screen for full joint WZ polarization/azimuth observables.
2. Independently regenerate one amplitude with FeynRules/MG5, and verify nonabelian identity in general gauge if making a gauge-independent field-theory claim.
3. Derive joint \(W^+\to\ell^+\nu,\,Z\to\ell^+\ell^-\) spin-density and azimuthal interference, then quantify **nontrivial** differences with an honestly allowed second theory scenario; keep missing angular resolution/unknown formation as uncertainty/limitations.
4. If the joint observables are already published, too small experimentally, or require arbitrary production spin fractions: **NO-GO**, redirect to another quirk idea.

## Publication referee risk

A severe referee objection is: 'You have only plotted a helicity decomposition that is already implicitly fixed by Forsyth Eq. (A.7), with no nontrivial second model or realistic observable.' This objection is presently valid. A modest EPJC/PTEP publication requires something beyond the current plots and validation.

**Do not misdescribe this pilot as a detector study, validated sensitivity, proof of novelty, or finished manuscript.**


## Joint-angle result (new within this pilot)

An on-shell narrow-width W+Z three-angle density was constructed from the LO scalar helicity amplitudes and leptonic W/Z decay currents, including transverse–longitudinal interference. Analytic polar-angle-integrated coefficients \(a_1,a_2\) were derived and tested by independent numeric quadrature; \(a_1\) changes sign across erratum-restricted tanβ. In particular, at M=500 GeV, \(a_1=-0.120305\) for tanβ=3, compared with \(+0.091375\) for tanβ=0.1. Unlike integrated rates, \(a_1\) retains relative helicity sign information. **This remains a conditional pilot result, not a demonstrated novel EPJC contribution.** Prior analytic amplitudes in the 2023 Forsyth thesis and possible already published angular methods remain an explicit referee risk. Detector-level viability and the exact full INSPIRE graph remain unknown.


## Independent generator countercheck — MUST RESOLVE

On 2026-11-07, user-run MG5_aMC 3.5.1 MSSM_SLHA2 matrix2py returned numerical, color-averaged matrix elements at M=500 GeV, tanbeta=3: WZ = 142350088.3299091 and Wgamma = 772.9807959512825. Both differ sharply from the assumed color-averaged analytic prediction (0.005317520079460985 and 0.001680692474251963), by factors 2.677e10 and 4.599e5 respectively. The numerical benchmark **FAILS**, but whether the problem is momentum indexing/phase space, MSSM model inputs/diagrams, or the analytic amplitudes remains UNKNOWN. The Python/Mathematica internal validation does NOT supersede these independent results. Pause physical interpretation, headline plots and publication claims; use the read-only MG5 discrepancy audit to identify the cause. Original code and parameter cards are preserved.


## 2026-11-07 update: parameter isolation locates EW change; full-review nonreproduction

User ran the generated standalone MG5 factor-isolation diagnostic. Results (all ME2):

| case | WZ | Wgamma |
|---|---:|---:|
| original | 0.01292073817016226 | 0.001589724882844365 |
| squarks_only | 0.0683286862353484 | 0.00172528605269909 |
| ew_only | 7593.18744541589 | 29.0411384331647 |
| full_except_ew | 0.06832867993250016 | 0.00172528613695433 |
| widths_only | 0.0128912020347695 | 0.00158972488379714 |
| full_review reconstructed from original | 6805310.983732369 | 173.7348371282458 |

This establishes an **electroweak-input dependence**: the huge growth occurs when the group containing SMINPUTS[1] (aEWM1), MASS[24] (MW) and MASS[23] (MZ) changes, while squark masses/widths alone do not. It does NOT yet establish why the EW change causes huge enhancement or whether the model/implementation is wrong.

**Additional consistency failure:** The group-reconstructed full_review does not reproduce the independently evaluated actual preflight review card at the same benchmark and momenta (WZ 142350088.3299091; Wgamma 772.9807959512825). Reconstructed/full ratio differences are ~20.9 and ~4.45. Before assigning physics significance to one factor, verify reconstructed SLHA card fields and parser behavior. It is not scientifically acceptable to classify the group reconstruction as an exact full-review equivalent until it matches numerically. The original MSSM model card reproduces its directly measured ME2 in the factor scan.

New script scripts/mg5_ew_input_audit.py and tests/test_mg5_ew_input_audit.py isolate SMINPUTS[1] and MASS[24] individually and together, compare **exact** preflight review against group reconstruction and all-scalar-key reconstruction, and save the full numeric/diff evidence. Run in the existing virtualenv, without editing any canonical cards:

    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v
    .venv-mg5-f2py/bin/python scripts/mg5_ew_input_audit.py --mass 500 --tanbeta 3 --probe

Output: validation/local_logs/threshold_benchmarks/M500_tanbeta3_ew_isolation.json. All substituted SLHA cards are diagnostic, not physically consistent MSSM spectra. Stop gate remains NO-GO until exact card and model input consistency is established and independent ME2 comparison agrees.


## 2026-11-07: Strong numerical evidence of SLHA fixed-field exponent truncation

The user ran exact-vs-rebuilt review card and one-at-a-time EW-input audit.
- Original aEWM1=127.934: WZ=0.01292073817016226, Wgamma=0.001589724882844365.
- Changing ONLY SMINPUTS[1] to 132.6638757554207: WZ=120.15834045063525, Wgamma=14.783884727018979.
- Ratios: 9299.64982407 and 9299.64982403. Both agree closely with (127.934/1.326638757554207)^2 = 9299.64982404.
- The old Python SLHA writer formatted aEWM1 as 1.326638757554207E+02, LENGTH 21. A Fortran 20-character field would clip its final digit 2, leaving 1.326638757554207E+0 and hence an effective inverse electromagnetic coupling of 1.326638757554207 rather than 132.6638757554207. This explains the shared enormous squared-amplitude factor *if* the generated reader truncates at 20 characters.
- MW-only and full-card results may also be badly affected by the same issue, since other updated masses were serialized with 21-character scientific fields.
- Group-reconstructed wide-format preview and exact wide-format preview produced different MEs even though the internal Python scalar SLHA parser reported equal numeric entries; this reinforces the need to validate Fortran input parsing.

This is a **high-confidence hypothesis of an SLHA numeric serialization defect**, not yet independently confirmed by a controlled Fortran parser A/B test. It does NOT justify claiming the published amplitudes are correct without rerunning the corrected external ME comparisons.

Fix: scripts/mg5_threshold_preflight.py now uses at most 20 characters per written numeric field (format .12E). It writes a NEW param_card_quirkonium_review_compact.dat, preserving the former 21-character param_card_quirkonium_review.dat as historical evidence. scripts/mg5_matrix2py_compare.py requires compact; tests/test_mg5_slha_fieldwidth.py prevents regression.

Decisive test: scripts/mg5_slha_fieldwidth_gate.py uses IDENTICAL original MSSM inputs and exact momenta with three cards: (1) original file, (2) identical numeric aEWM1 rewritten as an 18-character field, (3) identical numeric aEWM1 rewritten as 21-character field. If the old reader clips the E+02 to E+0, the third-to-first squared-amplitude ratio should equal exactly 10000, while the second equals 1. It then evaluates old long-format and new compact preview at the same benchmark momenta.

Commands:
    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v
    python scripts/mg5_threshold_preflight.py --mass 500 --tanbeta 3 --write-cards
    .venv-mg5-f2py/bin/python scripts/mg5_slha_fieldwidth_gate.py --mass 500 --tanbeta 3 --channel both

Output: validation/local_logs/threshold_benchmarks/M500_tanbeta3_slha_width_gate.json.
All original model, Fortran source and SLHA cards preserved.

NO-GO status remains until a genuinely corrected MG5 ME matches the analytic color-averaged target and electroweak model dependence is checked. Novelty/literature risk remains independent.


## Final update: the independent MG5 amplitude stop gate is CLOSED (scoped)

Correctly serialized compact SLHA cards remove the apparent 10^5-10^10
MadGraph/Python disagreement. Controlled identical-physics SLHA formatting
A/B tests demonstrate exactly a factor 10000 artificial increase with
legacy 21-character fields. Both WZ and Wgamma independently generated MG5
helicity-summed tree-level ME2 match the analytic targets at M=500 GeV,
tanbeta=3 to about 3e-13 relative.

Source: validation/MG5_INDEPENDENT_NUMERIC_2026-11-07.md. Chronological
earlier "NO-GO until the mismatch is resolved" notes are superseded as
amplitude validation statements. They should NOT be interpreted as
physical discrepancies. This is one benchmark and does not independently
establish complex helicity relative phases or general-gauge invariance.

Publication verdict REMAINS NO-GO for now due to novelty: part of the
helicity fraction result is implicit in published Forsyth et al. squared
amplitudes. Priority: (1) reproduce independent MG5 checks on a modest
mass/splitting grid; (2) verify complex helicity phase/interference directly;
(3) complete forward/backward citation-network audit and identify a clearly
distinct scalar-vs-fermion or related observable. Do not begin a broad scan
until those gates support a new claim.


## 2026-11-07 continuation: explicit two-branch interference mechanism

The physics pilot has identified a narrowly scoped potential result:
the published tree-level scalar quirkonium WZ and Wgamma rates imply
Gamma(WZ)/Gamma(Wgamma) =
[tan^2(thetaW) beta_WZ / beta_Wgamma]/(1-f00).
At fixed M, the WZ/Wgamma normalized rates and f00 thus carry the
same information; the longitudinal/transverse relative phase does not
appear in either. The ideal lepton decay-plane signed interference
a1 proportional to Re(H++ H00*) can distinguish amplitude branches
sharing the same f00.

For M=500 GeV, tanbeta=3 and tanbeta_low approximately 0.394724021524:
f00=0.9092814481, BR(WZ) under the two-channel assumption=0.7530816453,
while a1 approximately -0.1203051105 and +0.1203051105 respectively.
The discrete sign ambiguity is a **mathematical LO model feature**,
not yet demonstrated physically realizable in the original SUSY
construction. The 2025 paper discusses tanbeta>1 in its SUSY context;
the 2026 erratum plots a wider interval 0.1--10. Both facts must be
reconciled before claiming a viable low-tanbeta branch.

This is more specific than generic cosPhi/cos2Phi angles, which are
known from diboson resonance angular analyses; novelty still UNKNOWN.
The external MG5 helicity-summed matrix-element benchmark is scoped
PASS at M=500, tanbeta=3, but independent complex amplitude phases and
multi-benchmark pass are PENDING. Nor has the user yet run new ideal
moment-statistics or branch-degeneracy tests.

New self-contained sources:
- theory/branch_degeneracy.md (derivation, signs, caveats);
- scripts/quirkonium_branch_degeneracy.py (seven-mass bisection scan);
- scripts/ideal_a1_statistical_gate.py (perfect-reconstruction
  statistics, not event yield or sensitivity);
- scripts/mg5_benchmark_grid.py (six-M/tanbeta independent ME grid);
- scripts/mg5_fixed_helicity_audit.py (MG5 LL/TT squared components,
  NOT complex phase);
- scripts/inspire_quirkonium_citations.py (networked INSPIRE
  reference/citing metadata with explicit incomplete-status fallback).

Decision: Conditional GO for mathematical/validation pilot only.
NO-GO for a manuscript, physical tanbeta-branch claim, experimental
sensitivity, or novelty assertion until the remaining gates are closed.


### 2026-11-07 latest user-run gate: mathematics validated, paper gate open

The original 66 Python tests PASS, six independent MG5 points per two
channels PASS 12/12 at worst relative difference 1.2026e-10, the
independent fixed-helicity squares PASS (including f00 at M500/tb3),
and the 7-point LO two-branch a1 sign flip passes. These are user-run
results, not a new assistant-run MG5 execution.

The 2008 INSPIRE citing list returned zero even though the 2025 APS paper
explicitly cites it as ref. 51; the original graph completeness flag
is therefore not reliable. The crawler now checks this known edge.
Signed a1 depends on a complex relative helicity phase not independently
checked by the squared results. Neither branch physical viability
nor the novelty and collider feasibility of the sign ambiguity have
been certified. Conditional GO for narrowly testing those gaps only.


## Decision stage launched 2026-11-08: UV-vs-reconstruction feasibility, no detector

The primary-source novelty audit (literature/NOVELTY_AUDIT_INDEPENDENT_2026-11-07.md)
found generic spin-zero diboson azimuthal interference ALREADY published.
The exact two-branch charged scalar quirkonium application remains
a plausible *incremental model-specific* effect, not an independently
established paper contribution.

A small independent **assistant-side numerical prototype**, NOT the
newly committed user-local scripts, indicates a nontrivial practical
warning: exact true-neutrino reconstruction gives |a1|~0.12 at M500,
but choosing the common smaller-|pz(nu)| W-mass root reduces |a1|
to ~0.04--0.05 on tested discrete ideal-kinematics ensembles. The
sign contrast appeared to survive in this exploratory test, but the
numbers were sensitive to finite angular integration and use no
production, detector, background, or fiducial model. This is
PRELIMINARY and **not validated signal reach**.

Next scoped code, awaiting the user's run:
- scripts/quirkonium_model_domain_gate.py (tree D-term doublet
  mass origin, Yukawa initial-scale size; full UV remains UNKNOWN).
- scripts/quirkonium_neutrino_pz_gate.py (exact missing pT two-root
  kinematic Phi reconstruction and differential moment dilution).
- tests/test_quirkonium_feasibility_gates.py.
- validation/FEASIBILITY_STOP_GATES_2026-11-08.md.

The model check is narrowly positive at M500 by independent
algebra: tβ_low≈0.394724 gives m_uL≈254.719, m_dL≈245.281,
common m_Q²≈62748 GeV²; tβ_high=3 gives m_uL≈244.831,
m_dL≈255.169, common m_Q²≈62279 GeV². The user has not yet
run the new script suite, so do NOT promote these analytic checks
to a complete implementation PASS. The tree-level common soft mass
does NOT certify SUSY Higgs/Yukawa RG running or a physically viable
UV model.

Crucially, equal f00 and normalized BR do **not** imply equal
absolute partial widths: at M500 and fixed |R(0)|², the low-branch
Wγ (and WZ) widths have a relative ratio ~0.789 to the high branch.
We must not claim absolute event-rate degeneracy without source-
matched production and wavefunction calculations.

Paper status: NO-GO for manuscript, CONDITIONAL GO only to test
physical low-tanbeta viability, robust charged-sign reconstruction,
and plausible bound-state production rate. Stop early if any of
these decisive gates cannot be supported.


### 2026-11-08 latest user-run feasibility results

- User ran 81 Python tests: 80 PASS and one coarse quadrature
  test failure because a1(3 Legendre nodes, 8 Phi)=0.12351554
  differs from analytic a1=0.12030511 by 0.00321043,
  just above hard tolerance 0.003. The test has been **repaired
  by adding an explicit quadrature convergence check** (3 nodes
  ->5 nodes, strict 0.0015 closure) rather than relaxing tolerance;
  revised suite is NOT YET rerun on user workstation.
- Four tree-level scalar soft-mass points M250/500/1000/2000
  PASS scoped; tβ_low=0.394724 at M500 has weak-scale
  type-II-assumed y_t≈2.55. UV consistency UNKNOWN.
- Fixed wavefunction |R(0)|² at M500 gives low/high
  Γ(WZ) ratio 0.7890; normalized BR equality does not mean
  equal absolute rates.
- Coarse pz toy (5 Legendre nodes, 12 Phi, 5 orientations,
  rapidities [-1,0,1]): low/high a1=+.0494202/-.0485950
  for min-|pz|, 3σ Nselected=1892, necessary σprod>57.61 fb
  at perfect acceptance.
- Refined but DIFFERENT ensemble (8 nodes, 16 Phi,
  7 orientations, rapidities [-1.5,-.5,0,.5,1.5]):
  low/high a1=+.0425996/-.0417345, 3σ Nselected=2556,
  necessary σprod>77.83 fb at perfect acceptance,
  >778.3 fb if ε=10% (both before continuum backgrounds).
  Equal-root average: Δa1=0.025762, Nselected=27414,
  σprod>834.72 fb even at ε=1.
- Exact mass-constrained choice reproduces true a1 under
  PERFECT on-shell masses and momenta; not a detector algorithm.
- Data do **not** demonstrate stable convergence, since both
  integration order and boost ensemble changed. Re-run with
  constant boost/orientation and denser integration before
  promoting a quantitative dilution factor.

The key issue is **not an amplitude disagreement**: amplitude and
spin-correlated phase validation remain PASS. It is whether a
detector-free yet realistic signal production and reconstruction
model could support enough clean trileptons. The 2025 Forsyth
model and its 2026 erratum explicitly find existing WZ resonance
constraints insufficient; this is not a numerical production-rate
bound for our mass pair.

Primary reproducible gate record:
validation/FEASIBILITY_USER_RESULTS_2026-11-08.md.

Publication: NO-GO from signed a1 alone. Small STOP/GO
screen on σ(pp→Ψ±) and source-matched model validity before
any broader theoretical or collider study.


## 2026-11-08: actual Key4HEP/LHAPDF ud-only production gate

On UChicago AF the user ran Key4HEP (Python 3.13.8, LHAPDF 6.5.5,
MSTW2008lo68cl member 0) with the repo's Forsyth-Appendix-A.2
W*-mediated SM-colorless charged-pair cross section and --flavor-mode ud.
Both W charges and proton beam assignments are included.

M=500 GeV, 13.6 TeV: low/high sigma pair = 59.181/59.178 fb.
14.0 TeV: low/high sigma pair = 62.170/62.167 fb.
Numerical quadrature drift (48 -> 72 nodes) = 0.001%.

Given the user's fixed-ensemble 12x24 simple cosPhi toy needs
2979 selected clean trileptons, it requires sigma(pair)>90.71 fb
at L=3000/fb *even if* charged bound-state survival=1,
selection/reconstruction efficiency=1 and background=0.
Consequently the ud-only source-channel LO PDF result is
**FAIL for this specific necessary toy-moment yield criterion**
(required P_survival*epsilon=1.533 at 13.6 TeV,
1.459 at 14 TeV). This is NOT a universal statistical no-go
because the chosen moment is not optimal and full CKM flavor
channels, source normalisation and rapidity dependence are not
yet fully audited.

Mandatory next cheap check: rerun
scripts/quirkonium_production_pdf_gate.py
--flavor-mode full-ckm
with the same MSTW2008lo68cl PDF, masses 500 and energies 13.6/14,
recording output in an independent JSON. Then independently audit
whether Eq(A.2) includes the hidden-SU(3) final-color multiplicity;
do not add an arbitrary x3. No physical UV, deexcitation,
acceptance, or SM WZ background claim is justified.

See validation/CHARGED_PRODUCTION_USER_RESULTS_2026-11-08.md.


## 2026-11-08 AF full-CKM LO production and toy-statistical gate

User-ran Key4HEP LHAPDF 6.5.5 MSTW2008lo68cl member 0,
both beam configurations and both W charges, full 2x3 CKM
initial flavors. M500 charged-pair LO sigma:
13.6 TeV low/high=61.777/61.774 fb;
14 TeV low/high=65.022/65.019 fb.
Both numerical integration drift <=0.001%, compared with earlier
ud-only 59.181/59.178 fb (13.6 TeV) and 62.170/62.167 fb
(14 TeV). Full-CKM adds ~4.4%-4.6% over ud-only.

The 12x24 FIXED BOOST TOY (still not demonstrated quadrature
converged) requires 90.71 fb charged-pair production at
survival=1, efficiency=1, no background, for 3sigma using the
**specific simple cosPhi moment estimator**. Full-CKM
P_survival * efficiency required=1.468 at 13.6 TeV and 1.395
at 14 TeV, impossible under those ideal assumptions.
**FAIL this toy moment necessary-yield gate; NOT a generic
no-go on any full-dimensional likelihood, different selection,
or an alternate quirkonium paper.**

The AF full-CKM cross-section calculation itself printed all
four numerical results but FAILED at JSON serialization:
TypeError keys must be str ... not tuple. The CKM provenance
dictionary used (up,down) tuple keys. The script now converts
it to JSON-safe explicit CKM flavor records; an offline
test checks serialization. The user must pull and rerun to
save the full-CKM JSON, and report current unittest status.

Physics caveats: hidden-color normalisation of source Eq A2
not independently rederived; actual P_survival, realistic
kinematics and backgrounds uncomputed; low-tanbeta folded-SUSY
UV viability UNKNOWN. Do not invest in detector simulation
or repeat amplitudes just to rescue a failing simple moment.

Detailed report:
validation/CHARGED_PRODUCTION_USER_RESULTS_2026-11-08.md
