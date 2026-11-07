# Independent validation handoff — 2026-11-07

## Status (do not promote prepared checks to PASS)
- Existing Python physics: **14 local tests PASS** (source width, physical Wgamma Ward, ideal joint spin density).
- Preflight rank-two tensor equivalence checked separately with NumPy at 4 masses × 4 tanbeta × WZ/Wgamma and all physical polarizations: **PASS internally**. This uses the same intended gauge structure; it is **not** Wolfram or an independent generator.
- Mathematica rank-two tensor (mathematica/validate_scalar_WZ.wl): **USER EXECUTED (2026-11-07)**; printed `PASS Mathematica tensor / published rates / Ward` for the 9 WZ benchmark points, but `N::meprec` warnings occurred for M=250 GeV. The log-based Python comparison originally failed with `ImportError: polarization_fraction`, a comparator-interface bug rather than a physics mismatch. I independently parsed the 9 user-log rows and evaluated the Python reference: all 27 quantities `f00,a1,a2` agreed, maximum absolute residual **1.82e-14**. The corrected GitHub checker now imports `f00` and accepts Wolfram precision suffixes. **A clean Mathematica precision rerun is still required** before claiming the 1e-22 Mathematica arithmetic target.
- MadGraph5 MSSM left-squark EW control (madgraph/mssm_ew_procs.mg5): **PREPARED / NOT EXECUTED**. User confirmed executable at `$HOME/codes/Herwig/herwigpp/opt/MG5_aMC_v3_5_1/bin/mg5_aMC`, version directory MG5_aMC_v3_5_1; executable and version have not been checked by a tool.
- INSPIRE two-hop automated traversal (scripts/inspire_twohop.py): **PREPARED / NOT LIVE-EXECUTED** here; real citation graph and full-text novelty still UNKNOWN.

## Run on the machine with Mathematica and MG5

From a clone of this branch:

    git checkout research/pilot1-literature-model-gate
    mkdir -p validation/local_logs
    wolframscript -file mathematica/validate_scalar_WZ.wl | tee validation/local_logs/mathematica.log
    python scripts/compare_wolfram.py validation/local_logs/mathematica.log

Or within a Mathematica kernel: Get["mathematica/validate_scalar_WZ.wl"].
A **PASS** marker plus the Python cross-validator are required; merely opening Mathematica is not a test.

MadGraph (user-supplied executable path):

    export MG5_BIN="$HOME/codes/Herwig/herwigpp/opt/MG5_aMC_v3_5_1/bin/mg5_aMC"
    test -x "$MG5_BIN" && "$MG5_BIN" --version
    ( cd validation/local_logs && "$MG5_BIN" ../../madgraph/mssm_ew_procs.mg5 ) |& tee validation/local_logs/madgraph_generation.log

The second command generates standalone code. **Generation alone is not a matrix-element comparison.** Inspect diagram structure and obtain fixed-color matrix elements at nonzero constituent relative velocity, extrapolate to threshold, document exact MSSM card and pure-left first-generation squarks, and compare with scalar quirkonium kinematics. Hidden IC color ≠ MSSM QCD color; no direct cross-section equivalence. The MG benchmark cannot be called PASS until matching numerical outputs exist.

A semiautomated runner is scripts/run_local_checks.sh (set MG5_BIN first). The updated Mathematica script uses 60-digit numeric EW inputs and caches exact elementary Wigner-`d` integrals to avoid enormous exact-radical expressions. **The updated Wolfram script has not been rerun**; do not assume the warnings are eliminated until verified.

## INSPIRE audit (requires internet)

    python scripts/inspire_twohop.py --output validation/inspire_audit

This retrieves entire first-hop cited/citing lists for core sources and relevance-selected second-hop edges. For *all* second-hop nodes:

    python scripts/inspire_twohop.py --output validation/inspire_audit_full --expand-all

The unrestricted option can mean many API requests. The script caches requests, throttles to respect the public API (15 requests/5s), logs pagination, incomplete edges and failures. Exit 2 means incomplete coverage; never mark novelty closed if errors, partial pages or unresolved core sources remain. **The graph itself cannot substitute for checking the full-text calculations**.

## Evidence preserved

Nine Mathematica `f00,a1,a2` benchmark lines from the user-executed output are stored in `validation/wolfram_benchmark_20261107.txt`. The record explicitly notes the `N::meprec` warnings in the original full log. `tests/test_wolfram_log_regression.py` checks all nine entries with the fixed comparator. Agreement supports the physical tensor and angular conventions within double-precision accuracy; it is **not** an independent FeynRules/MG5 diagram-generation or collider-model validation.

## Acceptance criteria

1. Mathematica 18 source-width comparisons and 9 independent angular benchmark lines, photon Ward residual < 1e-22 at exact rational EW inputs. Numeric tolerance is a high-precision algebra check, not physical theory precision. If it fails, first inspect conventions rather than simply loosening the threshold.
2. MadGraph genuine independent amplitude comparison at M=250, 500 GeV, tanbeta=1,3,10, with identical EW input, correct pure-left couplings, complete gauge diagrams and ≥3 nonzero relative velocities; extrapolated threshold agreement target <1e-3 (refine after seeing finite-v corrections).
3. All INSPIRE primary records resolved and every first-hop edge counted, second-hop coverage stated, high-scoring matches read equation-by-equation. Do not certify novel if any material unmatched paper remains.
4. All gate statuses recorded PASS/FAIL/UNKNOWN with logs, versions, model cards and comparison residuals. No physics scan, official ATLAS sensitivity or manuscript claim until prerequisites close.

## Why this matters for the paper

The 2023 Forsyth thesis already has the charged scalar Wgamma/WZ **analytic amplitudes** (Eqs. 4.2.4–4.2.12). Fok and Kribs (2011), Appendix B, explicitly discuss double-longitudinal WZ modes in charged fermionic quirkonium. Existing ATLAS WZ joint-polarization measurements show the formal observable is measurable in SM production, but are not a validation of a quirkonium signal's experimental sensitivity. The pilot cosine-Phi term is derived from existing scalar amplitudes and standard spin-one decays; its novelty/discrimination is therefore unproven. 

Refs: https://physics.byu.edu/docs/thesis/1674; https://arxiv.org/abs/1106.3101; https://atlas-public.web.cern.ch/Updates/Physics-Briefing/WZ-Polarisation

**Review decision:** GO for restricted independent validation; NO-GO for expansion to scan/manuscript until independent physics and citation gates close.

## Revalidation on user machine (2026-11-07)

**Mathematica:** After precision mitigation, the user reran `wolframscript -file mathematica/validate_scalar_WZ.wl` and `scripts/compare_wolfram.py`. The full 9-point WZ grid printed `PASS Mathematica tensor / published rates / Ward` without `N::meprec` warnings. The comparator evaluated all 27 quantities `f00,a1,a2` with **0 failures**, maximum absolute difference **1.817e-14**. Upgrade the independent numeric *Mathematica–Python cross-check* to PASS (within double-precision numerical scope). This does not constitute MG5/UFO diagram-level validation or physical model viability.

**MadGraph:** User's MG5_aMC 3.5.1 executable was found and started. Original `import model mssm` failed because this MG5 version requires `MSSM_SLHA2`; all generation commands were skipped. The model card now uses `MSSM_SLHA2`; a postflight checker requires both `SubProcesses/P*/matrix*.f` outputs and fails if error diagnostics appear. **MG5 independent amplitude check: UNKNOWN**, not executed successfully; first retry process generation, then implement a fixed-color numerical matrix-element and threshold comparison.

For source-backed model naming, see ATLAS JobOption/DOxygen examples using `import model MSSM_SLHA2-full` and public MG5 3.x model output. **No claim that the replacement card has already run successfully.**


### Updated numerical-MG5 path (2026-11-07)

User has completed process generation (WZ and Wgamma standalones) and preflight with 24 unit tests. Default MSSM_SLHA2 parameter cards contain SMINPUTS[1,3], read AEWM1 and mdl_MW and omit GF. The old READPS-based check_sa evaluator is not compatible with the generated files (READPS=False). Use the documented make matrix2py.so binding via scripts/mg5_matrix2py_compare.py and the read-only review parameter card. Confirm that the UFO's internal SW/CW/GW definitions are consistent with our on-shell EW scheme before final PASS. Report both raw ME values and generated color-denominator lines. Never rewrite original cards or manufacture absent GF, and do not promote process generation to matrix-element validation.
