# 27, 85 and 100 TeV charged squirkonium production: AF results and no-detector next gates

**Date:** 2026-11-08. **Status:** User-run numerical production PASS; research outcome conditional.
**Environment:** UChicago Analysis Facility Key4HEP 2026-02-01, LHAPDF 6.5.5, MSTW2008lo68cl member 0, LHAPDF ID 21000.
**Production:** charged SM-colorless squirk pair via LO s-channel W*, source Forsyth et al., PRD111 (2025) 115021 App A.2 Eqs A.2/A.3. Full 2x3 CKM quark initial-flavor extension, both W charges and both proton-beam orderings. Source formula normalized as printed, with no extra infracolor multiplicity. Cross sections NOT bound-state annihilation yields.

## Saved user-run results

| Collider scenario (illustrative) | sqrt(s) TeV | L (ab^-1) | sigma charge-summed low branch (fb) | sigma high branch (fb) | relative quadrature drift | sigma_required (fb) | P_survival x epsilon minimum |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| HL-LHC reference | 14 | 3 | 65.022 | 65.019 | 0.001% | 90.71 | 1.395 |
| HE-LHC benchmark | 27 | 15 | 188.76 | 188.75 | 0.003% | 18.142 | 0.09611 |
| FCC-hh 85 TeV reference | 85 | 20 | 951.85 | 951.81 | 0.000% | 13.607 | 0.01430 |
| FCC-hh 100 TeV alternate | 100 | 30 | 1179.7 | 1179.6 | 0.001% | 9.071 | 0.007689 |

Outputs that user reported saved on AF:
- /data/aalida/quirkonium-production/charged_27TeV_15ab_LO.json
- /data/aalida/quirkonium-production/charged_85TeV_20ab_LO.json
- /data/aalida/quirkonium-production/charged_100TeV_30ab_LO.json
- /data/aalida/quirkonium-production/charged_prod_fullckm_LO.json

Source user pasted console lines; underlying JSON files are on AF and are not attachments to this conversation. They were not independently opened by assistant.

At M500, low tanbeta=0.394724021524; high=3. Both total pair production rates nearly coincide, as expected because the partonic source formula is even in Delta and the magnitudes |Delta| are close.

The same prior 12x24 toy coefficient from the M500 no-detector reconstruction is reused here unchanged:
- low/high reconstructed min-|p_z^nu| a1=+0.0394985 / -0.0386140.
- moment difference = 0.078112; 3 sigma selected clean signal event count = 2979.
- BR(Psi+ -> W+Z) = 0.753081645 within the ground-state Wgamma/WZ-only approximation.
- BR(W->e/mu nu) = 0.216; BR(Z->ee/mumu)=0.0673.
- no SM WZ background, perfect truth missing transverse momentum, on-shell WZ, chosen simple moment estimator, toy rapidities & isotropic orientations rather than actual collider event weighting. **These angular assumptions have not been validated for new collider energies**.
- Thus sigma_required = 2979/[L_fb * BR_groundstateWZ * BR_Wlep * BR_Zlep] and the minimum product P_survival*epsilon = sigma_required/sigma_pair; none of these quantities is a physical discovery reach.

If epsilon is *independently assumed* 0.1 and charged-state survival is a factor separate from epsilon:
- HE-LHC 27 TeV 15 ab^-1: requires P_survival > 0.9611.
- 85 TeV 20 ab^-1: requires P_survival > 0.1430.
- 100 TeV 30 ab^-1: requires P_survival > 0.07689.
All before continuum SM WZ and possible signal/background distortions. If eps includes survival, do not double count.

## Verdict

**Production ceiling:** HL-LHC FAIL for this toy moment at maximum survival and efficiency; HE-LHC passes bare necessary event-yield gate but fragile at efficiencies ~10%; FCC-hh 85 and 100 TeV PASS bare necessary *production-only* gate with substantial statistical margin.

**Actual FCC-hh measurability:** UNKNOWN. This is NOT a green light for a paper. Current Nselected and required thresholds reuse a not-yet-converged fake rapidity ensemble from the 14 TeV toy, and cannot be assumed stable when sqrt(s) grows.

**Novelty:** generic scalar-to-diboson angular interference is known. Specific opposite sign at two normalized-rate-degenerate D-term scalar branches is a conditional niche result requiring actual low-tanbeta UV viability and a distinct quantitative FCC-hh phenomenology analysis.

## Next minimal no-detector work, in stop/go order

1. **Source normalization cross-check.** Confirm whether published Eq (A.2) already includes sum/average over hidden SU(3) color; check a gauge- and color-matched SM-colorless EW scalar UFO matrix element or derive color factor explicitly. Verify proper CKM flavor factors and PDF choice, then repeat with an up-to-date LO PDF set and scale variations at 27/85/100 TeV. No arbitrary multiplication by 3 and no SM-QCD squark production.
2. **Physically weighted source-level kinematics.** For each pp energy, integrate or sample x1,x2 with PDF/LO matrix element weights, so parent rapidity y=(1/2) ln(x1/x2) is source-derived. For scalar quirkonium rest-frame W direction, use physical scalar isotropy; original toy sampled discrete y uniformly. LO pair total pT is zero under collinear factorization; hidden-glueball deexcitation recoil and initial-state QCD ISR are NOT included and require a transparent model uncertainty. Repeat neutrino pz reconstruction and check convergence in quadrature and PDFs. Record a1 sign/dilution, Nselected and effective rate threshold per collider separately. Do not call present 90.71 fb threshold universal.
3. **Source-matched deexcitation vs beta-decay probability.** Use the original paper's Eq (3.6) evaluated across generated production kinematics, including |Delta| and model glueball mass, not a global P_survival=1 or a collider-independent value. Survival may differ for positive/negative mass order.
4. **Parton-level lepton fiducial acceptance (no detector).** Apply explicit pT and eta thresholds, W/Z leptonic branching fractions, neutrino-root prescription, and a transparent SM WZ continuum estimate from source-matched MG5. No instrumental smearing or Delphes necessary for a carefully labelled parton-level sensitivity pilot, but backgrounds cannot be ignored in a claimed measurement.
5. **Physical low-tanbeta branch.** Check y_t~2.55 at M500 under type-II assumption against matching to folded-SUSY cutoff, perturbativity/electroweak breaking/charged scalar spectrum. Tree-level common SU(2)L doublet soft mass PASS by itself is insufficient.
6. **Paper stop/go.** A credible incremental paper requires genuine model-specific novel collider physics with quantified rate, acceptance, background and a viable two-branch model. If the low branch cannot exist, the claimed degeneracy/sign discrimination loses its motivating physics target.

## Interpretation of published collider design numbers

The 27/15, 85/20 and 100/30 TeV/ab^-1 values used here are *study scenarios supplied to script*, not certified official operating designs. For future papers cite the specific scenario chosen and avoid implying that 85 or 100 TeV and their luminosities are guaranteed.

## Source

Forsyth et al., arXiv:2504.02940 (2025), Appendix A.2 and Sec 3.1, 3.2.2; 2026 erratum for the WZ branching fraction comparison. LHAPDF 6 paper arXiv:1412.7420.
