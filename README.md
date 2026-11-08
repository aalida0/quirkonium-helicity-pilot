# Charged quirkonium polarization — scalar helicity feasibility pilot

**Research date:** 2026-11-07. **Branch:** research/pilot1-literature-model-gate.
**Status (updated 2026-11-07 after expanded pilot): 66 Python tests PASS; six-point independent MG5 WZ/Wgamma benchmark grid PASS 12/12 (maximum relative error 1.21e-10); independent longitudinal/transverse squared-amplitude check PASS at M500/tanbeta3. The 21-character SLHA formatting artifact is resolved. Seven LO pairs with equal f00 and normalized BR(WZ) but opposite signed a1 PASS mathematically. Complex helicity relative phases, tanbeta<1 model viability, literature novelty and collider reach remain UNKNOWN. No paper-ready claim.**

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
    python src/make_joint_figures.py

Plots generated: figures/f00_vs_tanbeta.png, figures/w_lepton_angle.png, figures/published_width_validation.png, figures/a1_cosPhi_vs_tanbeta.png, figures/joint_decay_plane_azimuth.png. The figures folder is generated output (not required for the source code).

## Docs and gatekeepers
- MODEL_SPECIFICATION.md — field content, couplings, mass splitting, non-viability caveats
- theory/amplitudes.md — explicit tree diagram sum, phase space and source formula
- theory/helicity_conventions.md — definitions and ideal W lepton polar angle
- theory/joint_angular_interference.md — complete ideal WZ angular density and interference moments
- literature/PRIOR_ART_MATRIX.md — including Forsyth 2023 MS thesis
- literature/CITATION_AUDIT.md — literature coverage and honest API/quota blockers
- literature/NOVELTY_VERDICT.md — incomplete novelty status
- validation/VALIDATION_REPORT.md — PASS/UNKNOWN gates and benchmark evidence
- PILOT_DECISION.md — referee-risk assessment and conditional GO/NO-GO

Source: Forsyth et al. (2025), arXiv:2504.02940, Appendix A.3, and 2026 erratum DOI:10.1103/lwnc-cmpn.

## What has **not** been finished

No direct complete two-hop INSPIRE citation graph (API unavailable, scholarly connector quota); no independently generated UFO/MadGraph calculation or arbitrary Rξ Goldstone/Slavnov–Taylor verification; no complete scalar potential/vacuum and collider-constraint validation; no fermionic comparison or detector simulation. The ideal joint W/Z angular density **has been computed**, but its independence from existing prior art and experimental usefulness remain unverified. The **current polarization decomposition is implicitly encoded in the prior published integrated width**, so by itself it is unlikely to constitute a paper.


## Additional joint-decay calculation

The on-shell WZ helicity amplitudes have now been propagated through the SM W and Z chiral leptonic currents. See theory/joint_angular_interference.md and src/joint_wz_angles.py. The normalized decay-plane azimuth density is \((1+a_1\cos\Phi+a_2\cos2\Phi)/(2\pi)\). The \(a_1\) term retains the sign of transverse–longitudinal interference and is not reconstructible from helicity-summed **rate values alone**. At M=500 GeV and tanβ=0.1,1,3,10, \(a_1=(+0.091375,-0.018423,-0.120305,-0.102636)\). The calculation, its positivity, normalization and two harmonics are covered by five additional tests in tests/test_joint_wz_angles.py, and plotted with src/make_joint_figures.py. Total local test count is **14** (9 threshold + 5 joint-angle). This is an *idealized theoretical* angular result; paper novelty and detector observability remain unverified.


## Independent Wolfram/MG5 and INSPIRE phase (2026-11-07)

The research branch now contains **prepared, not yet executed** cross-validation tools:

- `mathematica/validate_scalar_WZ.wl`: independent rank-two tree tensor with Wγ photon Ward tests, source WZ/Wγ width comparisons and Wigner-d angular Fourier moments.
- `madgraph/mssm_ew_procs.mg5`: two standalone processes for a pure-left up/down MSSM squark EW control (not the full hidden-color squirk model).
- `scripts/inspire_twohop.py`: live INSPIRE canonical DOI/arXiv seed resolver with paginated first-hop and relevance-selected second-hop citation graph, error logging and raw JSON caching.
- `scripts/compare_wolfram.py` and `scripts/run_local_checks.sh`: run and compare independent numerical benchmarks.
- `validation/INDEPENDENT_VALIDATION_GATE.md`: detailed acceptance criteria and version/card/evidence requirements.

Run on a machine with Mathematica (from the repository root):

    mkdir -p validation/local_logs
    wolframscript -file mathematica/validate_scalar_WZ.wl | tee validation/local_logs/mathematica.log
    python scripts/compare_wolfram.py validation/local_logs/mathematica.log

Run the INSPIRE graph retrieval (Internet required):

    python scripts/inspire_twohop.py --output validation/inspire_audit

Generate the MadGraph standalone *EW control* from the repository root:

    export MG5_BIN="$HOME/codes/Herwig/herwigpp/opt/MG5_aMC_v3_5_1/bin/mg5_aMC"
    ( cd validation/local_logs && "$MG5_BIN" ../../madgraph/mssm_ew_procs.mg5 ) |& tee validation/local_logs/madgraph_generation.log

**Important:** successful MG process generation does not demonstrate the amplitude is correct. A fixed-color, fixed-helicity matrix-element benchmark, parameter card and threshold extrapolation must be compared numerically and logged before the MG gate can be PASS. Never equate QCD-colored MSSM squarks with infracolor squirks for production.

The user executed the original Mathematica tensor/width/Ward script on 2026-11-07: it printed PASS but also `N::meprec` precision warnings. Nine `f00,a1,a2` rows were independently compared against the Python implementation (largest absolute deviation `1.82e-14`). This establishes a **scoped numerical Mathematica/Python comparison**, not a clean 1e-22 precision certification or an independent MG5 generator check. The original comparator crashed because it tried importing `polarization_fraction` rather than the actual `f00` API; fixed, with Mathematica precision-suffix handling and a regression fixture. The revised 60-digit Wolfram script still needs a clean rerun. MG5 and live INSPIRE runs remain UNKNOWN. Running `python -m unittest discover -s tests -v` now also checks the stored nine-point Mathematica fixture.

## MadGraph 3.5.1 compatibility fix

The user's first MG5 run failed solely during `import model mssm`, which was replaced by `MSSM_SLHA2` in this installation. The corrected card uses `import model MSSM_SLHA2` and retains `ul dl~ > w+ z/a QCD=0 QED=2`.

```bash
git pull --ff-only origin research/pilot1-literature-model-gate
mkdir -p validation/local_logs
(
  cd validation/local_logs
  set -o pipefail
  "$HOME/codes/Herwig/herwigpp/opt/MG5_aMC_v3_5_1/bin/mg5_aMC" ../../madgraph/mssm_ew_procs.mg5 2>&1 | tee madgraph_generation.log
)
python scripts/check_mg5_generation.py validation/local_logs/madgraph_generation.log
```

Do not mistake the script returning to a shell for generation success: the checker verifies both standalone matrix outputs and the absence of MadGraph error markers. Passing this check is **generation only**, not a matrix-element physics validation.


## 2026-11-07: Standalone generation PASS, actual matrix-element comparison next

The user ran MG5_aMC **3.5.1** with `MSSM_SLHA2`. Generated:
- `validation/local_logs/MG5_UL_DL_WZ/SubProcesses/P1_uldlx_wpz/matrix.f`
- `validation/local_logs/MG5_UL_DL_WA/SubProcesses/P1_uldlx_wpa/matrix.f`

`scripts/check_mg5_generation.py` reported **PASS** for generation. This is *not* the numeric matrix-element validation yet.

Read-only benchmark and color/parameter preflight (no change to default cards):

```bash
git pull --ff-only origin research/pilot1-literature-model-gate
python -m unittest discover -s tests -v
python scripts/mg5_threshold_preflight.py --mass 500 --tanbeta 3
```

The preflight writes `PS.input` and a JSON report. Before using its optional `--write-cards --apply` mode, check the generated MSSM model mass, gauge input and first-generation squark mixing conventions. If `check_sa.f` supports `READPS`, `scripts/mg5_evaluate_threshold.py` can compile/run a reproducible single-point check and save its raw result. No independent amplitude PASS is assigned until actual MadGraph values are inspected, including the generated initial-color denominator. See `madgraph/README.md` for full instructions and benchmark targets.


## MG5 exact four-momentum comparison without READPS or overwriting cards

The user confirmed the generated MSSM_SLHA2 Source/MODEL/param_read.inc reads aEWM1 and mdl_MW, while GF is not an external SMINPUTS entry in the produced cards. Source/internal coupling relations must still be checked. The old check_sa.f READPS gate is unavailable for this generated code.

Use MadGraph's documented make matrix2py.so API instead. At M=500 GeV, tanβ=3:

    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v
    python scripts/mg5_threshold_preflight.py --mass 500 --tanbeta 3 --write-cards
    python scripts/mg5_matrix2py_compare.py --channel Z --mass 500 --tanbeta 3
    python scripts/mg5_matrix2py_compare.py --channel gamma --mass 500 --tanbeta 3

Each generated process is run in its own Python process (matrix2py shares the same extension module name). Review cards are loaded by initialisemodel; the default param_card.dat is not overwritten. NumPy with f2py, GNU Fortran and a C compiler are required. Both raw matrix elements, the assumed /3 color-normalized analytic targets, ratios and input reader evidence are written to threshold_benchmarks/*/matrix2py_result.json.

Do **not** run the old --apply or mg5_evaluate_threshold.py path. The new program saves a diagnostic comparison, not a publication-grade validation without independently checking generated color and mixing conventions.


### Isolated fix for MG5 3.5.1 f2py3.10 loader (2026-11-07)

The first WZ matrix2py build failed before Fortran compilation: the generated standalone Makefile invokes stale /usr/bin/f2py3.10 (NumPy 1.21.5 console-entrypoint), while the active interpreter has NumPy 2.2.6. This is a toolchain issue, not an amplitude mismatch.

Recommended isolated and reversible fix:

    python3.10 -m venv .venv-mg5-f2py
    .venv-mg5-f2py/bin/python -m pip install -r requirements-mg5-f2py.txt
    .venv-mg5-f2py/bin/python scripts/fix_mg5_f2py_makefile.py --apply
    .venv-mg5-f2py/bin/python scripts/mg5_matrix2py_compare.py --channel Z --mass 500 --tanbeta 3
    .venv-mg5-f2py/bin/python scripts/mg5_matrix2py_compare.py --channel gamma --mass 500 --tanbeta 3

Only generated standalone P*/makefile files are changed, and backups are preserved. The MG5 installation, original cards and all physics sources remain unchanged. Run the f2py extension with the SAME venv Python used for compilation; a NumPy1.x-built module cannot safely be imported into the active NumPy2.x interpreter. See madgraph/README.md.


### Correction to MG5 f2py recovery helper

If the previous helper printed /usr/bin/python3.10 and then raised No f2py3.10 launcher found despite installing NumPy 1.26.4 in .venv-mg5-f2py: these were two bugs in our helper, now addressed. The fix preserves the venv symlink and supports variable-derived f2py3.10 commands via a shim local to the venv.

    git pull --ff-only origin research/pilot1-literature-model-gate
    .venv-mg5-f2py/bin/python scripts/fix_mg5_f2py_makefile.py --apply
    .venv-mg5-f2py/bin/f2py3.10 -v
    .venv-mg5-f2py/bin/python scripts/mg5_matrix2py_compare.py --channel Z --mass 500 --tanbeta 3

No global Python packages, MG5 installation or original parameter cards are changed. This is a tooling fix, not yet an independent numerical ME validation.


### matrix2py initialization / ident_card.dat (2026-11-07)

Both MG5 standalone Fortran extensions compile under the isolated NumPy 1.26.4 venv, but user-run initialisemodel printed a warning about missing ident_card.dat in parent directories and terminated without a matrix element. The wrapper originally ran from the repository root, rather than the generated P* working directory.

The updated evaluator finds the genuine generated ident_card.dat and stages a symlink in the P* working directory if necessary, then runs initialisemodel/get_value in a child process with that cwd. A fresh worker result file is mandatory, preventing a Fortran STOP with exit code 0 from being reported as successful physics.

    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v
    .venv-mg5-f2py/bin/python scripts/mg5_matrix2py_compare.py --channel Z --mass 500 --tanbeta 3
    .venv-mg5-f2py/bin/python scripts/mg5_matrix2py_compare.py --channel gamma --mass 500 --tanbeta 3

If the standalone has no ident_card.dat, the script stops with an explicit find command; do not create an empty mapping. The independent numerical matrix-element gate remains UNKNOWN.


### Stop gate: independent MG5 amplitude discrepancy

The user ran both compiled MSSM_SLHA2 standalone MEs at M=500 GeV, tanbeta=3. Observed MG5 ME2: WZ = 142350088.3299091; Wgamma = 772.9807959512825, versus our conditional color-averaged analytic targets 0.005317520079460985 and 0.001680692474251963. These are observed failed numeric checks; no rescaling to force agreement is authorized.

Reproduce the diagnostic scan and generated-source audit (does not alter model, cards, or physics):

    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v
    .venv-mg5-f2py/bin/python scripts/mg5_discrepancy_audit.py --mass 500 --tanbeta 3 --probe

The read-only audit extracts original/review SLHA masses and mixing, generated diagrams/color factors and direct MG5 ME values at q=0 (both final-state orientations), q=0.1, 1 GeV and the unmodified original MSSM card. It writes validation/local_logs/threshold_benchmarks/M500_tanbeta3_discrepancy_audit.json. Do not claim physical helicity fractions from this model as externally validated until this countercheck is reconciled.


### 2026-11-07: Narrowed MG5 discrepancy after rotation/color/model audit

User's generated MSSM_SLHA2 matrix.f has NGRAPHS=4 with the expected scalar-contact, W*, up/down scalar-exchange HELAS calls. For both channels: IDEN=9, CF=3, HELAVGFACTOR=1, so for the single color-diagonal amplitude the initial-color average is 1/3. First-generation USQMIX and DSQMIX are unmixed. The exact threshold ME is rotation invariant and varies smoothly at q=0.1 and 1 GeV; those checks eliminate several normalization/kinematic suspicions, but not the very large physical-model discrepancy.

User-reported original MSSM card result: WZ ME2 0.01292073817 and Wgamma ME2 0.00158972488. At the modified M=500 GeV/tanbeta=3 review card: WZ 142350088.3299091; Wgamma 772.9807959512825. The original and review inputs have different mass scales, so this is a clue only, NOT a controlled same-kinematics comparison.

The new read-only parameter-factor experiment isolates which type of card edit triggers the enhancement using the same exact MadGraph generator and transient SLHA copies. It varies squark masses, EW inputs, particle widths and tanbeta independently, using correct on-shell scattering kinematics for each modified spectrum:

    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v
    .venv-mg5-f2py/bin/python scripts/mg5_parameter_isolation.py --mass 500 --tanbeta 3 --channel both

Output: validation/local_logs/threshold_benchmarks/M500_tanbeta3_parameter_isolation.json. The resulting temporary MSSM spectra may be inconsistent and are used ONLY to diagnose the generated amplitude. This does not alter original cards or establish physical viability. Publication/quantitative physics gates remain NO-GO pending resolution.


### 2026-11-07: EW-input anomaly, and a second card-reconstruction discrepancy

MG5 factor study: original WZ/Wgamma ME² = 0.01292 / 0.001590; squark-masses-only = 0.06833 / 0.001725; EW-only (SMINPUTS[1], MASS[24]/[23]) = 7593 / 29.04. Full excluding EW returns ~0.06833 / 0.001725. Thus EW changes are essential to the large enhancement.

But the factor-study's reconstructed full-review card yields WZ/Wgamma = 6.805e6 / 173.735, while the directly evaluated exact preflight review card yields 1.4235e8 / 772.981. These values are NOT reconciled and must not be treated as identical setups. The input parser/card layout needs an exact-vs-reconstructed audit.

A focused script, using temporary cards and existing matrix2py, now splits electroweak changes into independent SMINPUTS[1] (aEWM1), MASS[24] (MW), their combination, and the unmodified MZ case. It also runs exact preflight review vs two reconstructed versions at matched 4-momenta, reports numerical differences in all supported SLHA scalar entries, and saves text diffs. It does not edit physics source/model or canonical cards.

    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v
    .venv-mg5-f2py/bin/python scripts/mg5_ew_input_audit.py --mass 500 --tanbeta 3 --probe

Output: validation/local_logs/threshold_benchmarks/M500_tanbeta3_ew_isolation.json. Physics validation decision remains NO-GO until a genuine common-setup ME agreement is established.


### Potential root cause found: too-long numeric fields in generated SLHA preview (2026-11-07)

The one-at-a-time EW-input audit gives a striking result: changing only aEWM1 from 127.934 to 132.6638757554207 multiplied the MG5 ME2 in BOTH WZ and Wgamma by 9299.649824 (same to better than 1e-10 relative). This is numerically equal to the fourth power of the gauge-coupling ratio if the 21-character field 1.326638757554207E+02 were incorrectly interpreted as 1.326638757554207E+0 due to a 20-column truncation. This is a strong input-parsing hypothesis, NOT yet a directly demonstrated parser defect.

The previous Python serializer wrote 21-character values using .15E. The corrected serializer writes <=20-character .12E fields, retaining roughly 13 significant digits, and saves new Cards/param_card_quirkonium_review_compact.dat for each process, preserving old Cards/param_card_quirkonium_review.dat for the A/B test. The ME comparator now requires the new compact card.

Run the decisive controlled same-physics A/B test (legacy wide alpha field vs compact field at the same original MSSM momenta) and new benchmark:

    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v
    python scripts/mg5_threshold_preflight.py --mass 500 --tanbeta 3 --write-cards
    .venv-mg5-f2py/bin/python scripts/mg5_slha_fieldwidth_gate.py --mass 500 --tanbeta 3 --channel both

Then, only after confirming numerical input handling, retry the matrix element comparison using the compact benchmark cards:

    .venv-mg5-f2py/bin/python scripts/mg5_matrix2py_compare.py --channel Z --mass 500 --tanbeta 3
    .venv-mg5-f2py/bin/python scripts/mg5_matrix2py_compare.py --channel gamma --mass 500 --tanbeta 3

Expected mathematical signature for a clipped original aEWM1 127.934: unsafe 21-character rewrite produces 10000 times the original amplitude squared, while the compact rewrite produces the same value. This signature requires verification with the actual Fortran code; no numeric MG5 PASS or publication claim is yet authorized. Outputs stored at validation/local_logs/threshold_benchmarks/M500_tanbeta3_slha_width_gate.json.


### Resolution of the previous MG5 discrepancy (supersedes earlier diagnostic status)

The former 10^5-10^10 failures and NO-GO statements in the chronological
debugging notes below refer to legacy, misparsed, 21-character SLHA cards
and **do not describe the current compact-card amplitudes**. A controlled
same-input, same-kinematics test demonstrated exactly 10000x numerical
enhancement from long scientific-notation fields. The compact SLHA writer
and the independent MG5 matrix2py calculations now agree at the
M=500 GeV, tanbeta=3 benchmark:

- WZ: MG5 5.3175200794627446e-3 vs analytic 5.317520079460985e-3.
- Wgamma: MG5 1.6806924742524885e-3 vs analytic 1.680692474251963e-3.

Full provenance is frozen in validation/MG5_INDEPENDENT_NUMERIC_2026-11-07.md.
The first post-change suite had 50 tests with two stale synthetic fixtures
(failure and error); fixture repairs and an additional regression were pushed
but have not been rerun locally. This is a narrow theoretical validation,
NOT proof of novelty, realistic quirks spectrum, helicity-phase fidelity,
or a publishable result.


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


### 2026-11-07 next phase: 2-to-4 decay-chain amplitude (not yet run)

To independently validate the SIGN of a1, the helicity-summed and
LL/TT-squared MG5 checks are insufficient. A new, separate standalone
MG5 generator process with full resonant spin correlation was added:

    madgraph/mssm_wz_spin_correlated.mg5

    cd ~/quirkonium-helicity-pilot
    git pull --ff-only origin research/pilot1-literature-model-gate
    cd validation/local_logs
    "$HOME/codes/Herwig/herwigpp/opt/MG5_aMC_v3_5_1/bin/mg5_aMC"       "$HOME/quirkonium-helicity-pilot/madgraph/mssm_wz_spin_correlated.mg5"
    find MG5_UL_DL_WZ_3LNU -name matrix.f -o -name param_card.dat

Output: a NEW standalone MG5_UL_DL_WZ_3LNU. It is a resonant
W+Z -> e+ ve mu+ mu- matrix element, NOT detector simulation.
**WARNING:** The 2-to-2 reviewed card has ZERO W/Z widths. For the
2-to-4 on-shell W/Z amplitude, use a separate compact SLHA card with
nonzero physical W/Z Breit-Wigner widths. Do not overwrite original
or 2-to-2 review cards. Full stage-by-stage procedure, including
charged-lepton angular frames and exact momentum validation, is at
madgraph/SPIN_CORRELATED_3LNU_PLAN.md. The current tool only generates
the process; a successful generation is NOT an external a1 PASS.

The local INSPIRE graph's 2008 zero-citation 'complete' status
contradicts the actual 2025 APS bibliography (reference 51).
Updated crawler has explicit seed-identifier and known-edge integrity
tests; rerun is required and publication-novelty certification remains
UNKNOWN.


### Latest execution outcome and next commands (2026-11-07)

User-run 69 Python tests all PASS; independent 12/12 two-to-two MG5
checks PASS; fixed-helicity LL and TT squared amplitudes PASS; 7/7
two-branch normalized-rate degeneracy tests PASS. The new full
WZ -> e+ ve mu+ mu- decay-chain standalone generated successfully
(4 production EW diagrams and two decay vertices); it has NOT YET
been numerically evaluated. Signed interference a1 is still UNKNOWN
by an independently generated complete 6-leg amplitude.

INSPIRE first-hop audit reports 2008 paper 67 metadata citations yet
0 forward results. A code bug was identified: earlier recid search
used arXiv lookup aliases, e.g. 2504.02940, instead of INSPIRE's
numeric metadata.control_number. The crawler and regression tests
were corrected; re-run required. A response without API error is
not proof that a query was semantically correct.

    cd ~/quirkonium-helicity-pilot
    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v
    python scripts/inspire_quirkonium_citations.py --depth 1
    .venv-mg5-f2py/bin/python scripts/mg5_spin_correlated_angles.py         --mass 500 --tanbeta-high 3 --nodes 10 --phis 8

The 6-leg runner compiles a separate matrix2py extension in the
generated 6-leg standalone; uses new compact cards with NONZERO
Breit-Wigner W/Z widths; verifies all six external HELAS legs,
massless outgoing leptons and exact on-shell six-body kinematics;
evaluates both low/high tanbeta branches on an angular grid.
It then compares normalized full-MG5 and analytic Phi distributions,
including signed a1. No original MG5 cards, legacy 2-to-2
validations or analytic source are overwritten.

Numerical results will appear in
validation/local_logs/threshold_benchmarks/spin_correlated_3lnu/summary.json.
If generated external masses/order differ from this narrow setup,
the runner must fail safely and be corrected from actual source,
not by post-hoc phase or normalization fitting.

The sign-sensitive two-branch mechanism is LO/scoped. UV viability
for tanbeta<1, full model-state populations, novel prior art and
measurability at the LHC remain UNKNOWN. See
madgraph/SPIN_CORRELATED_3LNU_PLAN.md.


### 2026-11-08 — focused feasibility stop gates (new code; local rerun pending)

The novelty review established that generic spin-zero diboson helicity
interference is prior art. For a credible quirk-specific parameter-inference
claim, we must test (1) whether the low-tanbeta branch has at least a
coherent scalar-doublet mass origin, and (2) whether its opposite signed
a1 can survive the neutrino two-root ambiguity without detector simulation.

New code and documentation:
- scripts/quirkonium_model_domain_gate.py: reconstructs a common
  first-generation SU(2) left-doublet soft mass using original 2025
  D-term equations plus corrected 2026 splitting; provides a stated
  weak-scale type-II top-Yukawa diagnostic; conditional absolute-width
  ratios and necessary clean trilepton production thresholds. This
  does NOT establish UV viability, which remains UNKNOWN.
- scripts/quirkonium_neutrino_pz_gate.py: weighs the analytical
  spin-correlated WZ -> e+nu mu+mu- angular density, rotates W direction
  relative to beam and applies illustrative longitudinal parent boosts,
  solves both neutrino-pz roots from perfect missing pT and mW, and
  reconstructs the charge-labelled joint Phi in helicity frames.
  Compares truth, smaller |pz|, reconstructed WZ mass closest to known
  M (optimistic), and equal-root average, and reports coefficient
  dilution and conditional selected signal/production requirements.
  No detector, production rapidity distribution, backgrounds or
  physical UV checks are included.
- tests/test_quirkonium_feasibility_gates.py: source-convention checks,
  mass relation, pz quadratic solutions and known-neutrino angular closure.
- validation/FEASIBILITY_STOP_GATES_2026-11-08.md: source equations,
  clear physics STOP/UNKNOWN gates, complete commands.

    cd ~/quirkonium-helicity-pilot
    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v
    python scripts/quirkonium_model_domain_gate.py --masses 250 500 1000 2000
    python scripts/quirkonium_neutrino_pz_gate.py \
        --mass 500 --high-tanbeta 3 --nodes 5 --phis 12 \
        --orientations 5 --rapidities=-1,0,1

A separate assistant-side exploratory integration of the same ideal
helicity distribution (NOT the committed script or physical pp
production) found min-|pz| retained opposite interference signs
but reduced |a1| from about 0.12 to roughly 0.04--0.05. This varied
with coarse angular quadrature; DO NOT treat it as robust sensitivity
or a user-run validation. Needed clean trilepton event counts could
increase dramatically. A denser quadrature and multiple boost
ensembles must be compared.

The user's 69-test and independent spin-correlated six-leg MG5
validation PASS remain. The new feasibility scripts and new regression
tests are COMMITTED but NOT YET RUN on the user's workstation.


### 2026-11-08: user-run feasibility evidence and corrected convergence regression

The 81-test run had 80 passes and **one failure due to coarse
angular integration**: three Gauss–Legendre polar nodes and eight
Phi angles yield a1=0.1235155400 vs the analytic closed
0.1203051105, absolute error 0.00321043 > the old .003 tolerance.
A denser user-run 5-node/12-Phi result gave 0.1210891 and the
8-node/16-Phi result 0.1205134. This is **numerical quadrature
accuracy**, not a physics-amplitude failure. The test now requires
explicit 3-to-5 node error improvement and a .0015 absolute
fine-grid tolerance, rather than simply loosening the original
tolerance. Local retest is PENDING.

The user-run model-domain gate PASS is limited to the common
first-generation scalar SU(2)L doublet D-term mass relation at
M250/500/1000/2000 GeV. For M500 the low branch has an assumed
weak-scale type-II y_t=2.5499 and unequal absolute partial
widths relative to the high branch (WZ low/high=0.789 for equal
wavefunction normalization). UV consistency is UNKNOWN.

The exact-MET neutrino-pz toy kept a1 signs opposite, but with
substantial dilution for the min-|pz| algorithm. Refined toy:
low a1=+.0425996, high=-.0417345 (truth ±.1205134);
3sigma simple moment required selected trileptons=2556,
requiring effective sigma_prod>77.83 fb at L=3000/fb
with 100% acceptance, >778.3 fb if epsilon=10%.
The equal-root average requires 27414 selected signal events,
>834.72 fb at epsilon=1. No background, detector, realistic
pp rapidity distribution or UV viability is modeled. The
coarse and refined tests changed angular integration AND boost
ensembles simultaneously, therefore a convergence claim is
not justified.

**Paper decision:** NO-GO for just the a1 sign flip or an
HL-LHC trilepton discovery statement. Next scientifically
valuable gate is source-matched sigma(pp→Psi±) and a bounded
model/perturbativity check for tanbeta≈0.395. Do not extend
amplitude infrastructure further. Full numerical results:
validation/FEASIBILITY_USER_RESULTS_2026-11-08.md.


### 2026-11-08: fixed-kinematics 12x24 refinement and LO production ceiling

User-run ideal neutrino-pz reconstruction (M500, fixed 5 orientations
and rapidities [-1,0,1], 12 Legendre nodes, 24 Phi points):
truth a1 low/high +.1203701/-.1203701;
smaller-|pz| low/high +.0394985/-.0386140;
Delta a1=+.078112, 3sigma simple-moment
N(selected clean 3lnu)=2979. Under BR(WZ)=.753082,
W->e/mu nu=.216, Z->ee/mumu=.0673, and L=3000/fb, this needs
at least sigma_charged_pair=90.71 fb at Pcharged_survival=1 and
reconstruction efficiency=1 (or 907.1 fb if efficiency=.1),
all BEFORE SM WZ backgrounds. It is not yet numerically
converged: earlier same-ensemble 5x12 and 8x16 gave
Delta a1=.098015 and .090099, respectively. Sign persists
in all sampled resolutions, but statistical requirement drifts.

A source-matched LO PDF production-ceiling gate is now available:
scripts/quirkonium_production_pdf_gate.py with offline regressions
tests/test_quirkonium_production_pdf_gate.py. Implements the published
Forsyth et al (2025) Appendix A.2 s-channel W* scalar-pair
cross section and both proton beam assignments, W+/W- charges;
mode 'ud' reproduces displayed source flavor channel,
mode 'full-ckm' adds an explicitly labelled LO CKM flavor extension.
Records PDF set/member, scales, two integration orders and a
necessary-only comparison to the 90.71 fb toy threshold.
No QCD squark production, or extra hidden-color factor silently
inserted. Physical bound-state cooling/beta-decay survival is
UNKNOWN. Python LHAPDF and a locally installed PDF set are
required; they are missing from the assistant environment,
so no production-rate number has been calculated.

    cd ~/quirkonium-helicity-pilot
    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v
    command -v lhapdf-config || true
    python -c "import lhapdf; print('LHAPDF import OK')" || true

If the Python module and PDF set exist:

    python scripts/quirkonium_production_pdf_gate.py \
       --pdf-set MSTW2008lo68cl \
       --energies 13.6 14 --masses 500 \
       --nodes 48 72 --flavor-mode ud --required-fb 90.71

    python scripts/quirkonium_production_pdf_gate.py \
       --pdf-set MSTW2008lo68cl \
       --energies 13.6 14 --masses 500 \
       --nodes 48 72 --flavor-mode full-ckm --required-fb 90.71 \
       --output validation/local_logs/charged_prod_fullckm_LO.json

Missing LHAPDF bindings/PDF must report BLOCKED_PDF_DEPENDENCY
or BLOCKED_PDF_SET, not be misreported as zero cross section.
Do not interpret a charged-pair rate above the toy threshold
as proof of a measurable angular effect, since deexcitation
survival and SM WZ backgrounds are missing.

Source details, output interpretation and stop criteria:
validation/CHARGED_PRODUCTION_GATE_2026-11-08.md.


### 2026-11-08: FCC-hh PDF-weighted longitudinal-boost pilot (new code)

Following the user's UChicago AF LHAPDF production results, the
27 TeV (188.76 fb), 85 TeV (951.85 fb), and 100 TeV (1179.7 fb)
full-CKM *charge-summed* LO charged-squirk rates pass the
respective illustrative **production-only** ideal yield thresholds
at 15/20/30 ab^-1. They do NOT establish a physical FCC-hh reach.

Implemented scripts/quirkonium_fcc_pdf_rapidity_gate.py to go beyond
arbitrary resonance-rapidity toy grids: an independently integrated
LO x1,x2 PDF-weighted *initial squirk-pair* rapidity spectrum
y=(ln x1-ln x2)/2 from the published Forsyth partonic production
formula. Its y,ln(s-hat) Jacobian integral crosschecks against
the preexisting triangular ln x1,ln x2 convolution; disagreement
>2% blocks the angular results. Keeps W+ and W- differential rates
separate. The default --charge-mode wplus is conservative because
the validated signed Phi convention is specifically for
W+Z->e+nu mu+mu-; including W- is an unvalidated CP
assumption. The new script uses weighted rapidity nodes with
memory-streamed exact-MET neutrino-pz angular reconstruction,
returns a1,a2 and **new** clean signal moment counts for each
energy. The previous uniform-boost 2979-event threshold must
not be transferred to a different PDF-weighted ensemble.

**Critical conditional approximation:** the rapidity of the initial
hard-scattering charged squirk pair is assumed to be inherited by
the final WZ-annihilating ground state. Infracolor cooling/recoil,
initial-state radiation, state transitions and beta decay are NOT
modeled. There is no detector, background or fiducial selection.
The source Eq A2 hidden-color normalisation audit and low-tanbeta
SUSY-UV model viability are PENDING. Do not call this a
physical sensitivity/reach prediction.

Offline regression tests:
tests/test_quirkonium_fcc_pdf_rapidity_gate.py.
Instructions and STOP/GO gates:
validation/FCC_PDF_WEIGHTED_RAPIDITY_PILOT_2026-11-08.md.

On UChicago AF with Key4HEP 2026-02-01 and
MSTW2008lo68cl PDF visible via LHAPDF_DATA_PATH:

    cd ~/quirkonium-helicity-pilot
    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v

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

This new differential workflow is COMMITTED, **NOT YET USER-RUN**.
Check cross-section closure before interpreting any moments;
repeat at controlled angular/rapidity integration orders to
assess convergence.


### 2026-11-08: ONE-COMMAND FCC-hh quirk survival/deexcitation work package

The source-matched but not UV-certified charged scalar quirkonium
feasibility calculation now has a full one-shot AF Condor task.

**Exactly one command on UChicago AF** (after cloning the branch):

    cd ~/quirkonium-helicity-pilot && git pull --ff-only origin research/pilot1-literature-model-gate && bash scripts/submit_fcc_survival_one_shot.sh

It submits ONE HTCondor worker job, sources Key4HEP and LHAPDF,
runs all regression tests, then calculates BOTH FCC scenarios
(85 TeV/20 ab^-1 and 100 TeV/30 ab^-1), both mass-splitting
branches, and confinement scales LambdaPrime=[1,2,3,5,10] GeV.

The full source-informed calculation now combines:
- EW W*-mediated LO PDF production, both charge cross sections;
- beta three-body width from Forsyth App A.1 Eq (A.1);
- string tension sigma_string=3.6 LambdaPrime^2;
- photon-only deexcitation upper time from Eq (2.11) at
  each partonic E_T=sqrt(shat), and survival Eq (3.6);
- source PDF-weighted survived charged-pair production
  and survival-dependent W+ rapidity distributions;
- one-time per-y W+ leptonic WZ angle reconstruction
  recycled across all Lambda values;
- per scenario and Lambda: charged survival, reconstructed
  signed a1 contrast, background-free simple-moment clean
  3sigma selected signal count, and minimum remaining
  selection epsilon; no detector or SM WZ background;
- independent integrated LO production crosscheck,
  weak-scale top-Yukawa size and tree-level scalar doublet
  mass consistency (not full folded-SUSY UV viability);
- JSON + Markdown report and HTCondor logs under
  /data/aalida/quirkonium-production/fcc_survival_one_shot_20261108/.

**Critical source audit in the same run:** the paper's rough
Eq (3.5) beta lifetime ~1e-12 s at |Delta|=10 GeV
and the printed exact Eq (A.1) width numerically imply
a lifetime ~2.2e-17 s at M1000, Delta10 GeV (factor
~4.5e4 difference). This is a major source/matching
normalization or physics interpretation tension.
Both expressions are recorded side by side, and the
run uses Eq (A.1) integral for survival, WITHOUT
forcing agreement with Eq (3.5). Physical inference
is suspended until the discrepancy is independently
resolved. No paper-reach claim is justified.

This is a compact bound-state-annihilation model
and does NOT simulate the user's ATLAS macroscopic-string
quirk trajectories. W+ angular-sign inference only;
W- CP-conjugate phase unvalidated.

Full technical protocol:
validation/FCC_ONE_SHOT_SURVIVAL_TASK_2026-11-08.md
Code:
scripts/quirkonium_fcc_survival_one_shot.py
Submission:
scripts/submit_fcc_survival_one_shot.sh
Regression tests:
tests/test_quirkonium_fcc_survival_one_shot.py

**Implementation committed, but the new survival job has NOT
yet been run on UChicago AF, so no numerical survival outcome
is asserted here.**
