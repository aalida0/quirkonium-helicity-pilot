# Pilot decision — 2026-11-07

**Current decision (revised after MG5 2026-11-07): NO-GO for quantitative physics conclusions or manuscript development until the independent matrix-element discrepancy is resolved. Diagnostic validation work only.**

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
