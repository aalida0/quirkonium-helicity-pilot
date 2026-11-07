# Independent signed-WZ helicity interference pilot

Status: generator process definition COMMITTED, **NOT YET GENERATED OR EVALUATED**.
Date: 2026-11-07. Exact target is an external test of the relative phase
between scalar charged quirkonium H++ and H00 that controls the signed
cos(Phi) coefficient a1. The helicity-SQUARED MG5 tests cannot do this.

## Proposed independent method (no detector simulation)

Use MadGraph5_aMC v3.5.1 in standalone mode to generate

    ul dl~ > w+ z QCD=0 QED=2, w+ > e+ ve, z > mu+ mu-

via madgraph/mssm_wz_spin_correlated.mg5. MadGraph's documented decay-chain
syntax retains spin correlations in the W and Z decay and finite-width
Breit-Wigner propagators, in contrast to replacing decay by uncorrelated
branching fractions. Source:
https://cp3.irmp.ucl.ac.be/projects/madgraph/wiki/FAQ-General-6

MSSM_SLHA2 first-generation unmixed left squarks provide only a
source-level electroweak matrix-element proxy for the infracolor scalar
doublet. The external squark masses must match M and tanbeta of the LO
benchmark; use compact <=20-character SLHA numeric fields, as proven
necessary by the standalone parser A/B test.

The 2-to-2 validation's review card has zero internal W/Z widths.
**Do not feed those zero widths to the on-shell 2-to-4 process.**
Use a separate temporary 2-to-4 review card with nonzero physical
Breit-Wigner widths (and record their values); keep original input and
2-to-2 compact review cards unchanged.

## Stage A: Generate only; no physics conclusion yet

    cd ~/quirkonium-helicity-pilot
    git pull --ff-only origin research/pilot1-literature-model-gate
    cd validation/local_logs
    MG5=$HOME/codes/Herwig/herwigpp/opt/MG5_aMC_v3_5_1/bin/mg5_aMC
    "$MG5" "$HOME/quirkonium-helicity-pilot/madgraph/mssm_wz_spin_correlated.mg5"
    find MG5_UL_DL_WZ_3LNU -name matrix.f -o -name param_card.dat

Do not compile and call nhel=get_value until generated external-leg
order, nhel spectrum, model electroweak inputs and on-shell propagator
widths have been audited. This process is different from the original
2->2 results; a successful generator exit is a software-generation
result, NOT a phase-validation PASS.

## Stage B: Invariant differential angular test (next code stage)

At initial relative momentum q=0 and fixed M, construct exactly
conserved on-shell 4-vectors for W+Z, then decay:

- W+ -> e+ nu_e with the charged e+ at thetaW, phiW in the W+ helicity frame.
- Z -> mu+ mu- with the mu- at thetaZ, phiZ in the Z helicity frame.
- Define zW along W flight (+z), zZ along Z flight (-z);
  (xW,yW)=(x,y), (xZ,yZ)=(-x,y), Phi=phiW+phiZ.
- Boost each massless lepton from its parent boson rest frame to the
  2-scalar rest frame. The 4 final momenta must sum to exactly the two
  initial scalar 4-momenta; all final leptons massless on shell.
- Verify the actual matrix.f outgoing leg order matches the call inputs;
  do not assume a specific 6-leg ordering from the handwritten command.
- At fixed cos(thetaW),cos(thetaZ), take several Phi values, including
  Phi=0 and Phi=pi. Calculate the ratios ME2(Phi)/ME2(0) from the
  spin-correlated 2->4 matrix and from theory/joint_angular_interference.md.
  The common Breit-Wigner and phase-space normalization cancels.
- Repeat for tanbeta_hi=3 and the LO f00-degenerate low-tanbeta solution
  ~0.394724 at M=500 GeV; test whether the Phi -> Phi+pi asymmetry
  actually changes sign with rate-degenerate inputs.

**An important subtlety:** spin-helicity decay frames, outgoing helicity
polarization signs and charge assignments can reverse Phi signs.
The comparison must use **exactly the same experimentally defined
charged-lepton frame** on both model predictions, not arbitrary amplitude
rephasings. Off-shell/narrow-width corrections, decay-chain resonant
diagram restrictions and an incomplete model must be scoped and recorded.

## Mandatory decision gates

1. Correct generation and charged final-state particle IDs: PENDING.
2. Correct 6-leg kinematics, widths, and legal compact SLHA: PENDING.
3. External generated 2->4 angular shape agrees with analytic joint
   WZ leptonic shape: UNKNOWN.
4. Opposite signed cosPhi interference between two rate-degenerate
   low/high tanbeta branches, at equal mass: UNKNOWN.
5. Physical tanbeta<1 branch and published-literature novelty: UNKNOWN.

No collider sensitivity, UV model viability or paper readiness is
implied by completion of stages A or B.


## 2026-11-07: user generated the complete decay-chain standalone

User executed MG5_aMC 3.5.1 in local_logs; process
ul dl~ > w+ z QCD=0 QED<=2, w+ > e+ ve, z > mu+ mu-
generated 4 EW production diagrams with two one-diagram leptonic decays.
Standalone output is:

    validation/local_logs/MG5_UL_DL_WZ_3LNU/
      SubProcesses/P1_uldlx_wpz_wp_epve_z_mupmum/matrix.f
      Cards/param_card.dat

The FastJet/eMELA/LHAPDF/Ninja/Collier warnings were nonfatal for
this tree-level standalone generation. The output is user-run
generation evidence, NOT yet signed-helicity-phase validation.

### Stage B implemented as independent six-leg angular-shape evaluator

The script scripts/mg5_spin_correlated_angles.py now:

1. Checks the generated subprocess name, all six external HELAS
   wavefunction indices and massless final-lepton assumptions.
2. Compiles the new six-leg matrix2py extension using the existing
   NumPy 1.26.4 f2py virtualenv and the generated standalone makefile.
3. Creates new, COMPACT SLHA cards for M500 and two f00-degenerate
   tanbeta branches; internal W/Z widths are 2.085/2.4952 GeV,
   strictly positive. Original generated and 2-to-2 SLHA cards
   are unmodified.
4. Constructs exact on-shell [E,px,py,pz] momenta for
   (ul, dl~, e+, ve, mu+, mu-), using a fixed W+ charged-lepton
   and Z negative-muon helicity frame. Tests four-momentum,
   mass-shell and intermediate-boson invariants.
5. Evaluates the full SIX-LEG helicity-summed resonant MG5
   matrix element over a Legendre polar-angle grid and 8 Phi
   points, extracts a1,a2 and compares the normalized Phi shape
   to the independently written analytic three-angle density.
6. Requires each branch to agree in angular SHAPE and the two
   branches to exhibit opposite signed a1. A nonzero result at
   correct kinematics is mandatory; no arbitrary normalization,
   phase reversal or tuning is allowed.

Run after pull:

    cd ~/quirkonium-helicity-pilot
    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v
    .venv-mg5-f2py/bin/python scripts/mg5_spin_correlated_angles.py         --mass 500 --tanbeta-high 3 --nodes 10 --phis 8

The new matrix2py build log and angular results are written under

    validation/local_logs/threshold_benchmarks/spin_correlated_3lnu/

including per-branch compact SLHA, complete 6-leg phase-space
inputs, Fortran evaluation output, per-Phi comparison, and a
summary.json. A failure or missing output is an explicit
INCONCLUSIVE/FAIL, never silently a phase PASS.

### Important limitations after this stage

The generator is independent, but uses the same MSSM_SLHA2 EW
proxy. A full 6-leg angular distribution at the physical W/Z pole
compares interference in an on-shell, narrow-width setup. It does
not directly expose the complex H++ H00* amplitude value, reconstruct
neutrino pz at a detector, validate the infracolor bound-state
wavefunction, establish tanbeta<1 parameter consistency, or prove
literature novelty. The result may differ in a real off-shell
treatment; such effects are outside this pilot.
