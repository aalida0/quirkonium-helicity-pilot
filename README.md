# Charged quirkonium polarization — scalar helicity feasibility pilot

**Research date:** 2026-11-07. **Branch:** research/pilot1-literature-model-gate.
**Status (revised after MG5 2026-11-07): published-width and Mathematica/Python numerical checks PASS scoped, but independent MG5 numerical matrix-element benchmark FAILS by factors 2.677e10 (WZ) and 4.599e5 (Wgamma) at M=500 GeV, tanbeta=3; root cause UNKNOWN. All physics interpretation/plot release PAUSED. No paper or experimental-reach claim.**

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
