# FCC-hh charged scalar quirkonium: ONE-STEP full source-matched survival task

**Date:** 2026-11-08.
**Status:** CODE AND TESTS COMMITTED; this new combined job has NOT yet been user-executed on AF.
**Branch:** research/pilot1-literature-model-gate.
**Paper status:** NOT ESTABLISHED; source-level beta-lifetime discrepancy is a material scientific stop gate.

## The single AF action

After the GitHub branch is updated, run:

    cd ~/quirkonium-helicity-pilot && git pull --ff-only origin research/pilot1-literature-model-gate && bash scripts/submit_fcc_survival_one_shot.sh

This submits ONE user-owned HTCondor vanilla job, 1 CPU, 4 GB memory,
2 GB requested disk on UChicago AF. The script:
- sources Key4HEP and sets the known functional CVMFS LHAPDF PDF path,
- checks the PDF load (MSTW2008lo68cl member 0),
- runs the COMPLETE repository unittest suite first, and aborts
  the physics calculation on any regression failure,
- runs 85 TeV, L20 ab^-1 and 100 TeV, L30 ab^-1 scenarios,
- scans LambdaPrime [1,2,3,5,10] GeV, separately for positive
  and negative Delta (low/high tanbeta), W+ signal by default,
- computes sourced beta width, photon cooling, PDF-weighted
  charged survival and survival-reweighted W+ lepton angles,
- writes a JSON plus a short Markdown report and Condor logs.

Fixed output directory:

    /data/aalida/quirkonium-production/fcc_survival_one_shot_20261108/

Expected files after successful completion:
    fcc_survival_all.json
    fcc_survival_all.md
    stdout.<cluster>.<proc>.log
    stderr.<cluster>.<proc>.log
    condor-events.log

This operation is entirely on the USER's AF/HTCondor account:
ChatGPT did not start the job. If condor_submit is unavailable,
the launcher stops safely. Optional --local is intended only for
an allocated worker, not a busy shared login node.

## Source-matched equations and serious inconsistency

Original primary source: Forsyth, Low, Tenney, Verhaaren,
*Visible collider signals of natural quirks*,
Phys Rev D 111 115021 (2025), arXiv:2504.02940,
https://doi.org/10.1103/34xj-vz82.
Erratum PRD 113 079901 (2026),
https://doi.org/10.1103/lwnc-cmpn.

The model assumes a charged scalar-doublet pair under hidden
confining SU(3), with total pair mass M and splitting Delta,
NOT the macroscopic string regime of the user's ATLAS quirk
trajectory search. The production model is W*-mediated,
source Eq A.2/A.3, with both quark/antiquark proton beam
assignments and full approximate 2x3 CKM initial channels.
No SM QCD color production; no extra unverified N_IC=3 factor.

Infracolor string tension (Eq 2.1 discussion):
    sigma_string ≈ 3.6 (LambdaPrime)^2   [GeV^2].

Photon-only deexcitation time (Eq 2.11):
    t_deexc [natural units] =
        [3 M^3 / (64*pi*alpha_EM*sigma_string^2)] *
        [E_T/M-1] * [(1-(Delta/M)^2)^2/(1+(Delta/M)^2)].
Here E_T=sqrt(shat), the INITIAL pair invariant-mass energy.
Multiply by hbar=6.582119569e-25 GeV*s.
The source calls this an upper (conservative) cooling time
when hidden glueball deexcitation radiation is neglected.

The source Appendix A.1 gives an exact one-dimensional
three-body beta width Gamma_beta with GF^2*Delta^5,
including finite W propagator corrections. For
Delta/M ->0 and Delta/mW ->0 the dimensionless integral
approaches 2/5. We perform 96-node Gauss quadrature and
compare this analytical limiting identity.

Eq (3.6):
    P_deexc(E_T) = exp[-t_deexc(E_T)/tau_beta]
with tau_beta=hbar/Gamma_beta.

**A major source-level discrepancy:** Eq 3.5 states the
rough scaling tau_beta~10^-12 s*(10GeV/|Delta|)^5.
But numerical integration of the printed Eq A.1 at
M=1000 GeV and |Delta|=10 GeV gives approximately
tau_beta=2.22e-17 seconds, i.e. ~45,000 times shorter!
The physical origin of this discrepancy is NOT resolved;
it may reflect an error in the rough estimate, a
missing normalization/convention, or another assumption.
The pilot explicitly records BOTH and flags this
as a scientific review gate. It uses the printed
integral for the quantitative survival scan, never
silently swaps to the rough estimate.
**DO NOT present the survival results as certified**
until this source issue is independently investigated
and, if needed, queried with the authors. Do not
override either formula to force agreement.

A caveat independent of the lifetime discrepancy:
Eq 2.11 follows the source's simplified photon cooling
normalization; charge-weighted photon emission, multiple
channels, nonperturbative glueball radiation, excited
state angular momentum and environmental effects
are not independently calculated here.

## Physics calculation behind one output table

For every collider, mass-splitting branch and LambdaPrime:
1. Integrate the partonic cross section times LHAPDF
   parton densities over y=.5log(x1/x2) and t=log(shat/s);
   keep W+ and W- production rates separate.
2. At each integration node apply P_deexc(sqrt(shat)),
   obtaining survived W+ and W- production cross sections
   and normalized survived W+ rapidity weights.
3. Independently cross-check RAW charge-summed rate
   against the preexisting triangular log(x1),log(x2)
   convolution; >2% disagreement aborts the job.
4. Compute the exact-MET, W mass-constrained signed
   W+Z->e+nu mu+mu- angular reconstruction ONCE
   per branch and rapidity. Cache moment coefficients
   by y, and reweight by the survived y spectrum
   for all LambdaPrime values without repeated
   expensive 2->4 kinematics calculations.
5. Calculate the existing clean-signal simple-moment
   3sigma/5sigma required events and the minimum
   additional efficiency epsilon after charged survival.
   Note: 3sigma here is an IDEAL discriminant between
   two specified signal-only hypotheses. It is NOT
   observed discovery, exclusion, CLs, or realistic
   signal/background significance.
6. Record weak-scale type-II-assumed yt and
   tree-level doublet mass origin for each branch.
   Neither a viable folded-SUSY UV nor electroweak
   constraints or vacuum proof follows from this.
7. Write full reproducible JSON and concise Markdown.

## Inputs and principal limitations

- M500 and tanbeta_high=3; low ~=.394724.
- 85 TeV (20 ab^-1) and 100 TeV (30 ab^-1)
  are illustrative collider design scenarios.
- LambdaPrime = [1,2,3,5,10] GeV.
  These specify compact, promptly annihilating
  hidden SU(3) string dynamics; NOT long macroscopic
  quirk strings used in the ATLAS search.
- Full 2x3 approximate CKM, MSTW2008lo68cl
  PDF member 0, Q=M, LO EW model as printed.
- Gaussian integration: y=40, ln shat=64,
  independent triangulated x1,x2=72.
- W+Z angular quadrature: 8 polar nodes,
  16 azimuths, 5 parent orientations.
  The min-|pz| moment was still moving by ~6.5%
  between 8x16 and 12x24 at 85 TeV, so a
  published reach requires numerical convergence
  cross-check using another integration scheme.
- No final-quirkonium recoil from radiating the
  initial kinetic energy. We reweight initial
  pair rapidity and assume it is retained.
- No hard initial-state radiation, no fully specified
  excited state/angular momentum distribution,
  no detector response, no trigger/selection/acceptance,
  no SM continuum WZ background, no pileup or fake leptons.
- No charge-conjugate W- signed angle amplitude/observable:
  both charge cross sections are reported, but ONLY
  W+ is used in signed angular significance calculations.
- No hidden-color production normalization independent
  amplitude check or PDF variations yet.

## How to interpret the outcome

Use the Markdown table per LambdaPrime and energy:
  P_survival low/high,
  signed delta a1 after survived-production weighting,
  3sigma clean selected N,
  minimum additional selection epsilon,
  and PASS/FAIL NECESSARY ONLY.

A passed row means only that at the stated exact-model
assumptions, sufficient *raw* charged-pair statistics
survive photon cooling for a signal-only moment with
perfectly measured leptons. It is NOT an experimental
forecast. Source-lifetime disagreement and physical
model consistency keep paper gate NOT ESTABLISHED.

A failed row says the selected moment strategy cannot
reach that signal-only contrast even at epsilon=1,
within the specified source model and its assumptions.
It does not rule out a likelihood or different
charged/neutral channel.

Once this one command completes, audit the reported
A1-vs-Eq3.5 lifetime discrepancy, rather than
starting yet another lengthy amplitude/angles chain.


## 2026-11-08: UChicago AF Condor submission directory correction

User reported that HTCondor submission files belong under
their /home workspace, while bulk outputs should be under /data.
The first launcher put all of its job control, executable,
log and output paths under /data and the user saw:
  ERROR: Failed to commit job submission into the queue.
The scheduler error does NOT prove that the /data placement
was its sole cause.

The launcher now uses:
- Job worker, submit.sub, condor event/stdout/stderr logs:
  /home/aalida/quirkonium-helicity-pilot/condor/fcc_survival_one_shot_20261108/
- Physics JSON and Markdown (results only):
  /data/aalida/quirkonium-production/fcc_survival_one_shot_20261108/

The submitter changes to the job home directory for condor_submit,
and declares initialdir there. It does not use /data as its
Condor submission directory. The exact one-command invocation
remains unchanged (git pull then bash launcher).

If scheduler queue-commit still fails, collect:
  condor_submit -debug ~/quirkonium-helicity-pilot/condor/fcc_survival_one_shot_20261108/submit.sub
and the schedd authorization/connection diagnostics. Do not
claim that changing directories alone fixed the scheduler.
