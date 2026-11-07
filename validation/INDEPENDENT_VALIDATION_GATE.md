# Independent validation handoff — 2026-11-07

## Status (do not promote prepared checks to PASS)
- Existing Python physics: **14 local tests PASS** (source width, physical Wgamma Ward, ideal joint spin density).
- Preflight rank-two tensor equivalence checked separately with NumPy at 4 masses × 4 tanbeta × WZ/Wgamma and all physical polarizations: **PASS internally**. This uses the same intended gauge structure; it is **not** Wolfram or an independent generator.
- Mathematica rank-two tensor (mathematica/validate_scalar_WZ.wl): **PREPARED / NOT EXECUTED** in this environment.
- MadGraph5 MSSM left-squark EW control (madgraph/mssm_ew_procs.mg5): **PREPARED / NOT EXECUTED** in this environment.
- INSPIRE two-hop automated traversal (scripts/inspire_twohop.py): **PREPARED / NOT LIVE-EXECUTED** here; real citation graph and full-text novelty still UNKNOWN.

## Run on the machine with Mathematica and MG5

From a clone of this branch:

    git checkout research/pilot1-literature-model-gate
    mkdir -p validation/local_logs
    wolframscript -file mathematica/validate_scalar_WZ.wl | tee validation/local_logs/mathematica.log
    python scripts/compare_wolfram.py validation/local_logs/mathematica.log

Or within a Mathematica kernel: Get["mathematica/validate_scalar_WZ.wl"].
A **PASS** marker plus the Python cross-validator are required; merely opening Mathematica is not a test.

MadGraph (replace the path with the actual installation):

    export MG5_BIN=/path/to/MG5_aMC/bin/mg5_aMC
    ( cd validation/local_logs && "$MG5_BIN" ../../madgraph/mssm_ew_procs.mg5 ) |& tee validation/local_logs/madgraph_generation.log

The second command generates standalone code. **Generation alone is not a matrix-element comparison.** Inspect diagram structure and obtain fixed-color matrix elements at nonzero constituent relative velocity, extrapolate to threshold, document exact MSSM card and pure-left first-generation squarks, and compare with scalar quirkonium kinematics. Hidden IC color ≠ MSSM QCD color; no direct cross-section equivalence. The MG benchmark cannot be called PASS until matching numerical outputs exist.

A semiautomated runner is scripts/run_local_checks.sh (set MG5_BIN first). The original Mathematica version bundled in the downloadable validation kit additionally reports more verbose diagnostics.

## INSPIRE audit (requires internet)

    python scripts/inspire_twohop.py --output validation/inspire_audit

This retrieves entire first-hop cited/citing lists for core sources and relevance-selected second-hop edges. For *all* second-hop nodes:

    python scripts/inspire_twohop.py --output validation/inspire_audit_full --expand-all

The unrestricted option can mean many API requests. The script caches requests, throttles to respect the public API (15 requests/5s), logs pagination, incomplete edges and failures. Exit 2 means incomplete coverage; never mark novelty closed if errors, partial pages or unresolved core sources remain. **The graph itself cannot substitute for checking the full-text calculations**.

## Acceptance criteria

1. Mathematica 18 source-width comparisons and 9 independent angular benchmark lines, photon Ward residual < 1e-22 at exact rational EW inputs. Numeric tolerance is a high-precision algebra check, not physical theory precision. If it fails, first inspect conventions rather than simply loosening the threshold.
2. MadGraph genuine independent amplitude comparison at M=250, 500 GeV, tanbeta=1,3,10, with identical EW input, correct pure-left couplings, complete gauge diagrams and ≥3 nonzero relative velocities; extrapolated threshold agreement target <1e-3 (refine after seeing finite-v corrections).
3. All INSPIRE primary records resolved and every first-hop edge counted, second-hop coverage stated, high-scoring matches read equation-by-equation. Do not certify novel if any material unmatched paper remains.
4. All gate statuses recorded PASS/FAIL/UNKNOWN with logs, versions, model cards and comparison residuals. No physics scan, official ATLAS sensitivity or manuscript claim until prerequisites close.

## Why this matters for the paper

The 2023 Forsyth thesis already has the charged scalar Wgamma/WZ **analytic amplitudes** (Eqs. 4.2.4–4.2.12). Fok and Kribs (2011), Appendix B, explicitly discuss double-longitudinal WZ modes in charged fermionic quirkonium. Existing ATLAS WZ joint-polarization measurements show the formal observable is measurable in SM production, but are not a validation of a quirkonium signal's experimental sensitivity. The pilot cosine-Phi term is derived from existing scalar amplitudes and standard spin-one decays; its novelty/discrimination is therefore unproven. 

Refs: https://physics.byu.edu/docs/thesis/1674; https://arxiv.org/abs/1106.3101; https://atlas-public.web.cern.ch/Updates/Physics-Briefing/WZ-Polarisation

**Review decision:** GO for restricted independent validation; NO-GO for expansion to scan/manuscript until independent physics and citation gates close.
