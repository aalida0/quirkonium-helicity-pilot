# Source-matched charged-squirk electroweak production: first real LHAPDF result

**Date:** 2026-11-08.
**Machine:** UChicago Analysis Facility login04; Key4HEP release 2026-02-01, Python 3.13.8, numpy 2.2.6, LHAPDF 6.5.5, MSTW2008lo68cl member 0 LHAPDF ID 21000.
**Source:** user terminal output; JSON /data/aalida/quirkonium-production/charged_prod_ud_LO.json exists on AF and was not uploaded to this conversation.
**Script:** scripts/quirkonium_production_pdf_gate.py.
**Command:** --pdf-set MSTW2008lo68cl --energies 13.6 14 --masses 500 --nodes 48 72 --flavor-mode ud --required-fb 90.71
**Physics source:** Forsyth et al PRD 111 (2025) 115021 Eq A.2/A.3: electroweak charged constituent pair u dbar -> tilde u tilde d*; no SM-QCD production.

| sqrt(s) TeV | tanbeta branch | sigma LO W+-sum (fb) | numerical integration drift | needed P_survival x efficiency |
|--:|--|--:|--:|--:|
| 13.6 | low, 0.394724 | 59.181 | 0.001% | 1.533 |
| 13.6 | high, 3 | 59.178 | 0.001% | 1.533 |
| 14.0 | low, 0.394724 | 62.170 | 0.001% | 1.459 |
| 14.0 | high, 3 | 62.167 | 0.001% | 1.459 |

The rate is the charge sum W+/W-, BOTH beam assignments, for the displayed u dbar source flavor channel *only*. It is NOT a validated fully flavor-summed cross section, and the source's hidden-SU(3) color normalization needs explicit review before changing any factors. Do **not** multiply the source formula by hidden color 3 without a matched derivation; the original authors state their Eq A.2 PDF convolution agrees with MadGraph.

For the **specified background-free simple cosPhi moment estimator** using the user's nonconverged fixed-kinematics 12x24 toy, 3sigma requires 2979 *selected* prompt e/mu trileptons. With BR(Psi->WZ)=0.753082 and BR(W->e/mu nu)=0.216, BR(Z->e/mu e/mu)=0.0673, at L=3000/fb, this corresponds to 90.71 fb necessary inclusive charged-pair rate at P_survival=epsilon=1 and no background. The u dbar only rate fails this toy's necessary condition even at P=epsilon=1. It would provide at most about 1,945 such trileptons at 13.6 TeV or 2,043 at 14 TeV, still insufficient for the 2979-event toy criterion. This upper ceiling is valid **for this moment estimator**, not a theorem ruling out the full angular likelihood or an improved neutrino pz estimator.

Interpretation:
- **UD_ONLY_PDF_LO_TOY_MOMENT_NECESSARY_YIELD: FAIL**, with production cross section 59.18/62.17 fb < required 90.71.
- **LHAPDF numerical convergence: PASS scoped**, last-two-node drift 0.001%.
- **Full-CKM flavor sum: NOT_RUN**, must assess additional initial partons with correct CKM factors and scheme. Run the script with '--flavor-mode full-ckm', output with a new filename.
- **Hidden-color normalization independent reproduction: UNKNOWN**, match Forsyth Fig 3 or MadGraph EW 2->2 of SM-colorless scalar model, not MSSM QCD squarks. The authors use N'_c=3 in electroweak precision T parameter Eq 3.9; do not interpret that as proof whether Eq A.2 includes N'_c.
- **Beta-decay vs deexcitation survival: UNKNOWN**, even though their Sec 3.1 gives an illustrative M1000, Delta10, ET2TeV near-100% benchmark. That point is not this M500 production ensemble.
- **Realistic production angular/rapidity distribution, fiducial efficiency, neutrino resolution, SM WZ background: UNKNOWN.**
- **12x24 reconstruction-angle convergence: NOT_DEMONSTRATED**; 5x12->8x16->12x24 fixed-boost toy required 1892,2239,2979 events, respectively.
- **SUSY/Higgs low-tanbeta model viability: UNKNOWN**; tree-level common SU(2) doublet mass relation previously PASS.
- **Publication status: NO-GO on current toy moment, not the full model**.

Next cheap check at AF:

    cd ~/quirkonium-helicity-pilot
    python scripts/quirkonium_production_pdf_gate.py \
        --pdf-set MSTW2008lo68cl \
        --energies 13.6 14 \
        --masses 500 \
        --nodes 48 72 \
        --flavor-mode full-ckm \
        --required-fb 90.71 \
        --output /data/aalida/quirkonium-production/charged_prod_fullckm_LO.json

**STOP:** Do not claim the project impossible based only on ud-only and this one nonoptimal moment; do not undertake another long amplitude validation chain. If full CKM remains below 90.71 fb using validated source normalization, the current HL-LHC simple-angle strategy is not viable even in its optimistic zero-background ideal. Alternative multidimensional likelihood or constrained-mass neutrino reconstruction would need a *separate demonstrably superior method* and source-matched production model, not wishful extrapolation.

Sources:
- Forsyth et al. arXiv:2504.02940 Appendix A.2 Eqs A.2-A.3, Sec 3.2.2 (analytic vs MadGraph agreement), Sec 3.1 beta-decay vs deexcitation, and 2026 erratum.
- LHAPDF paper arXiv:1412.7420.
