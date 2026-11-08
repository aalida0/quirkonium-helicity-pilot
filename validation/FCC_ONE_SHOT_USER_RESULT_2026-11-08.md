# FCC photon-cooling survival one-shot: verified user run output

Date 2026-11-08. User executed entire no-Condor runner on UChicago AF HOME, with Key4HEP and LHAPDF6.5.5 MSTW2008lo68cl PDF member 0. Internal numerical selfchecks passed. JSON/MD/log saved on user's AF HOME:

  /home/aalida/quirkonium-helicity-pilot/results/fcc_survival_one_shot_20261108/

No result JSON was attached to chat; all values below are transcribed from the user's terminal log. This is NOT a detector-level or publishable sensitivity prediction.

## Real LHAPDF collider production

M=500 GeV, tanbeta low=0.39472402, high=3, charged W+ only for signed angular inference, both W+ and W- LO xsecs evaluated. Full approximate CKM. PDF integration 40x64 (y,log-shat), independent 72-node triangular log-x1/log-x2.

| Energy | L (ab^-1) | sigma LO W+ (fb) | sigma LO W++W- (fb) | independent PDF check |
|---|---:|---:|---:|---:|
| 85 TeV | 20 | ~562.2 | ~951.86 | 0.002% |
| 100 TeV | 30 | ~691.5 | ~1179.6 | printed 0.000% |

## Survival and angular moment table

Survival calculated at each partonic invariant mass sqrt(shat) from photon-only cooling Eq2.11 and EXACT PRINTED constituent beta-decay width EqA.1, with Eq3.6. The signed W+ Z->3lnu min-|pz| a1 is reweighted with surviving y spectrum, no detector/SM WZ background/ISR/deexcitation recoil, ideal toy simple-moment statistic. All rows passed ONLY the necessary no-background epsilon<=1 signal-only count gate.

| sqrts | LambdaPrime GeV | charged Psurv low / high | signed min-|pz| delta a1 | 3sigma clean N | epsilon necessary after survival |
|---|---:|---|---:|---:|---:|
| 85 | 1 | .7161/.6105 | +.054435 | 6137 | .081679 |
| 85 | 2 | .9760/.9626 | +.055370 | 5932 | .050067 |
| 85 | 3 | .9952/.9924 | +.055457 | 5913 | .048411 |
| 85 | 5 | .9994/.9990 | +.055477 | 5909 | .048058 |
| 85 | 10 | 1.0000/.9999 | +.055479 | 5908 | .048005 |
| 100 | 1 | .7149/.6091 | +.053565 | 6338 | .045819 |
| 100 | 2 | .9758/.9624 | +.054470 | 6129 | .028044 |
| 100 | 3 | .9951/.9923 | +.054556 | 6110 | .027113 |
| 100 | 5 | .9994/.9990 | +.054576 | 6106 | .026914 |
| 100 | 10 | 1.0000/.9999 | +.054578 | 6105 | .026885 |

Angular resolution remains polar=8 and phi=16; earlier fixed-PDF 8x16->12x24 changed 85TeV signed moment by ~6.5% and clean event N by ~14.5%. NO convergence certification.

## Material source inconsistency, do not ignore

| Branch | Delta GeV | tau_A1 s | tau_rough_Eq3.5 s | rough/printed exact |
|---|---:|---:|---:|---:|
| low tanbeta | +9.43782 | 2.9410e-17 | 1.3355e-12 | 4.541e4 |
| high tanbeta | -10.33725 | 1.8612e-17 | 8.4718e-13 | 4.552e4 |

The original 2025 paper Sec 4.1.1 explicitly says its simulation used the exact printed Appendix A.1 width, not the Sec 3.5 rough lifetime. The April 2026 erratum corrects model-domain Eq3.4 and other issues but does not specify a correction to this factor ~45,000 lifetime tension. DO NOT claim the authors used the wrong lifetime in their event simulation. Before physical interpretation obtain independent three-body scalar decay validation or author clarification.

Primary: Forsyth et al, Phys Rev D111 115021 (2025) arXiv:2504.02940; erratum Phys Rev D113 079901 (2026).
https://journals.aps.org/prd/abstract/10.1103/34xj-vz82
https://journals.aps.org/prd/abstract/10.1103/lwnc-cmpn

## Fake 13.6 TeV output in unit tests

The run printed a 13.6 TeV sigma(W+) ~700.7 fb in test output. It came from the artificial numerical fixture with x*f(x,Q)=1 for all flavors. This is NOT a physics prediction and is unrelated to actual physical 13.6/14 TeV MSTW2008 rates. The verbose fixture print was suppressed in a follow-up regression-test commit. The actual user-run physical scenarios are the above 85 and 100 TeV blocks only.

## Research decision and limitations

POSITIVE: source-matched LO PDF production closes numerically, photon-only source-model survival is high for LambdaPrime >=2 GeV in this benchmark, and reconstructed W+ signed angular effect survives after deexcitation weighting.

OPEN physics: low tanbeta large weak-scale top Yukawa and UV viability, gluon/glueball cooling, pair-to-final-resonance recoil/boost approximation, hard ISR, dedicated W- CP angle mapping, infracolor SU3 production color normalization, numerical convergence, SM WZ and fake backgrounds, fiducial lepton cuts, detector response. These scalar quirks form promptly annihilating compact bound states, not the user's original ATLAS macroscopic-string quirk regime.

**Publication and true collider significance: NOT ESTABLISHED.** Do not continue scanning grids before independently auditing beta width and moving to acceptance, SM WZ and actual two-hypothesis discrimination.
