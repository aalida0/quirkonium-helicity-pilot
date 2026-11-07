# A discrete LO ambiguity in charged scalar quirkonium WZ polarization

**Status: mathematical amplitude-level mechanism identified; physical viability and
novelty UNKNOWN.** Date 2026-11-07. See scripts/quirkonium_branch_degeneracy.py
and tests/test_quirkonium_branch_degeneracy.py. No detector simulation.

## Statement

Consider a fixed charged spin-zero scalar quirkonium state of mass M, with
up-/down-constituent masses (M+Delta)/2 and (M-Delta)/2, and the restricted
D-term splitting Delta = mW^2 cos(2 beta)/M. Assume the **only** open decay
modes of this charged ground state are WZ and Wgamma, as in the simplified
source model. Use on-shell tree-level amplitudes and the narrow-width
approximation for W and Z.

Let T = sum over both WZ transverse helicities |H++|^2+|H--|^2 and
L = |H00|^2. Then

    f00 = L/(T+L),
    Gamma(WZ)/Gamma(Wgamma)
        = tan^2(thetaW) * beta_WZ/beta_Wgamma * 1/(1-f00),

where beta_WV is the corresponding on-shell 2-body phase-space factor.
This relation follows from the common transverse coupling factors in
Forsyth et al. (2025) Appendix A.3 Eqs. (A.6)-(A.8); it can also be
checked directly in src/scalar_threshold_amplitudes.py. The formula
is valid **within this model**, not as a universal relation for all
charged resonances. In particular, the branching ratio is

    BR(WZ) = R/(1+R),  R = Gamma(WZ)/Gamma(Wgamma)

if and only if those are the only decay channels. At fixed M, Gamma(WZ)/
Gamma(Wgamma) and f00 contain the **same normalized information**.

But the azimuthal decay-plane distribution of the leptonically decaying
W and Z may retain a relative helicity sign:

    dP/dPhi = [1 + a1 cos Phi + a2 cos(2 Phi)]/(2 pi)
    a1 = (9 pi^2/32) * (gR^2-gL^2)/(gR^2+gL^2)
         * Re(H++ H00*) / (|H++|^2+|H--|^2+|H00|^2)
    a2 = (1-f00)/4.

Here H++ and H00 refer to the particular helicity-frame definitions in
theory/joint_angular_interference.md. a1 is sign-sensitive but the sign
is convention-dependent unless that frame is held fixed for both
hypotheses and their reconstructed leptons.

## Concrete two-solution example

Solving f00(M=500 GeV,tanbeta_low) = f00(M=500 GeV,tanbeta_high=3)
in the interval 0.1<tanbeta_low<1 gives:

| Quantity | positive-splitting branch | negative-splitting branch |
|---|---:|---:|
| M (GeV) | 500 | 500 |
| tanbeta | 0.394724021524... | 3.000000 |
| Delta (GeV) | +9.4378 | -10.3373 |
| f00 | 0.9092814481 | 0.9092814481 |
| BR(WZ), only WZ/Wgamma | 0.7530816453 | 0.7530816453 |
| a1 | +0.1203051105 | -0.1203051105 |
| a2 | 0.0226796 | 0.0226796 |

This is a **discrete normalized-rate degeneracy broken by the signed
interference** within the leading-order model. Numerically finding two
points is NOT a claim that this degeneracy survives a full scalar
potential, extra decay modes, production-state mixtures or collider
reconstruction.

## Statistical caveat

The simple ideal moment estimator a1hat = (2/N) sum cos Phi has

    Var(a1hat) = [2 + a2 - a1^2]/N.

At M=500 GeV, tanbeta=3, measuring a1 significantly nonzero needs
approximately 1,250 (3 sigma) or 3,470 (5 sigma) fully selected,
background-free, perfectly angularly reconstructed decays. Binary
discrimination of **two known opposite-sign hypotheses** using the
difference Delta a1=2|a1| is statistically easier: approximately
313 selected clean events (3 sigma) or 868 (5 sigma) for this
specific moment-based asymptotic estimator. Neither number includes
branching fractions for W/Z leptonic decays, acceptance, W-neutrino
reconstruction ambiguities, background, off-shell effects or
systematic errors. It is NOT an LHC reach projection or universal
likelihood sensitivity; specific tests may attain different power.

## Mandatory physics and novelty caveats

1. **Model domain:** The 2025 source study discusses the SUSY construction
   with tanbeta>1, while the 2026 erratum explores 0.1<=tanbeta<=10.
   Whether tanbeta=0.395 has a viable, perturbative, correctly matched
   scalar model (including Higgs/Yukawa sector and flavor) is **UNKNOWN**.
   If the low branch is not viable, the two-solution *physical*
   phenomenological mechanism fails for that model. One may not
   substitute an unconstrained arbitrary Delta for the erratum
   expression to revive it.
2. **Literature:** cos Phi and cos 2 Phi angular terms are generic
   helicity interference observables known in diboson/Higgs studies.
   Our implementation is not their first derivation. Prior quirk
   papers contain WZ/Wgamma decay-rate and splitting formulas.
   Whether this *model-specific rates-degenerate, sign-sensitive*
   ambiguity was previously explicitly identified is NOT
   certified absent; see literature/SCOPED_NOVELTY_GATE_2026-11-07.md.
3. **External validation:** MG5's independent summed ME2 agrees at
   one benchmark (M500,tanbeta3) after fixing 21-character SLHA
   fields. This validates the sum, not independent complex phases,
   and so a1 retains an explicit external phase-validation gate.
   scripts/mg5_fixed_helicity_audit.py checks squared LL/TT portions,
   not relative helicity signs; its result is not yet executed.
4. **Experimental:** Phi uses both W and Z leptonic decay frames, and
   the W neutrino is unmeasured longitudinally. A claim that a1 is
   observable requires a tested reconstruction prescription or
   explicit ideal truth-level scope; this pilot is the latter only.
5. **Model inference:** Opposite-sign a1 distinguishes amplitudes
   **within a specified physical model**, not necessarily quirk
   constituent spin. Fermionic alternative hypotheses may have
   different J^P and source couplings.

## Near-term falsification criteria

Stop this specific candidate if:
- the tanbeta<1 benchmark cannot exist in the intended consistent model;
- the relative complex phase does not pass an independent amplitude
  check, or cancels once physical state populations are included;
- identical physics is clearly already published; or
- even an ideal reconstruction proxy makes the interference contrast
  effectively unmeasurable for any meaningful experimental scope.

Sources:
- Forsyth, Low, Tenney, Verhaaren, Phys Rev D 111, 115021 (2025),
  arXiv:2504.02940, Appendix A.3.
- 2026 erratum, Phys Rev D 113, 079901, corrected Delta relation.
- Fok and Kribs, Chiral Quirkonium Decays, Phys Rev D 84, 035001
  (2011), arXiv:1106.3101.
- Burdman et al., The Quirky Collider Signals of Folded Supersymmetry,
  arXiv:0805.4667.
- Choi, Jeong, Kang, Vetoing all the Higgs imposters in
  H -> l-l+ Z, Eur Phys J C 84 (2024) 1095: general angular methods.
