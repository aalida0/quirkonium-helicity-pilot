# Pilot decision — 2026-11-07

**Current decision: CONDITIONAL GO for a narrow WZ angular-extension pilot; NO-GO for claiming a publishable new result now.**

## Established result

A physical spin-zero scalar charged squirkonium in the Forsyth et al. electroweak charge representation has fully evaluated tree-level physical amplitudes for \(W^+Z\) and \(W^+\gamma\), including scalar exchanges, seagull, virtual W*. Helicity-summed widths reproduce source integrated rates, and photon Ward tests pass. The 2026 erratum D-term splitting \(\Delta=m_W^2\cos2\beta/M\) yields dramatic WZ fraction changes, e.g., \(f_{00}=0.001938\) (tanβ=1) versus \(0.935846\) (tanβ=10) at M=500 GeV. The wavefunction factor cancels from this fixed-state LO ratio.

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
