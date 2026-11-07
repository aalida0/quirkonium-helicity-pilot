# Independent MadGraph5 electroweak control — PREPARED, NOT EXECUTED

MG5's `MSSM_SLHA2` model particle names `ul`, `dl` are left-handed squarks, whose *SM electroweak* W/Z/photon gauge vertices correspond to those of a scalar weak doublet. They carry QCD color rather than infracolor; **do not compare color-averaged production cross sections or bound-state decay rates directly**.

Execute from the research repository root:

```bash
mkdir -p validation/local_logs
cd validation/local_logs
set -o pipefail
"$HOME/codes/Herwig/herwigpp/opt/MG5_aMC_v3_5_1/bin/mg5_aMC" ../../madgraph/mssm_ew_procs.mg5 2>&1 | tee madgraph_generation.log
python ../../scripts/check_mg5_generation.py madgraph_generation.log
```

**Validation requirements:** inspect the generated `SubProcesses/*/matrix.f` and Feynman diagrams. Retain the two scalar exchanges, seagull W/V contact vertex, and s-channel W. Set pure-left first-generation squark mixing and the same EW input scheme as `MODEL_SPECIFICATION.md`; suppress first-generation Yukawa/Higgs contamination. For the mass card choose physically consistent masses and ensure correct CKM. Export numerical fixed-color squared matrix elements with a controlled nonzero incoming relative velocity, extrapolate to threshold, and only then compare with `src/scalar_threshold_amplitudes.py`. Standalone compilation is version dependent; don't treat successful generation as a validated matrix-element match.

This control does not by itself establish an arbitrary-gauge Goldstone Slavnov–Taylor identity. `check lorentz ul dl~ > w+ z QCD=0 QED=2` tests Lorentz invariance, not full gauge identities. In some MG5 versions `check gauge` only checks external gluons. A genuine independent helicity check requires fixed-helicity matrix-element output, not just an unpolarized cross section.

**2026-11-07 run:** The initial card `import model mssm` failed under MadGraph 3.5.1 with the explicit replacement hint `MSSM_SLHA2`. Therefore neither standalone matrix output was created, and **MG5 numerical validation remains NOT RUN**. The card now imports `MSSM_SLHA2` and generates the two outputs without a second import. The postflight command `python ../../scripts/check_mg5_generation.py madgraph_generation.log` from `validation/local_logs` detects error lines and missing matrix output. **Status until a successful new run and numerical fixed-color ME comparison: UNKNOWN.** Log MG5 version, card checksum, diagram count, input masses, relative velocity, MEs, and numerical tolerances. Original particle names: https://madgraph.mi.infn.it/sm_particles.html.


## Threshold-matrix-element phase after generation PASS

The user has confirmed one `matrix.f` for each process and the postflight tool reports PASS. This is process generation only.

**Start with a read-only parameter and color inspection:**

```bash
cd ~/quirkonium-helicity-pilot
git pull --ff-only origin research/pilot1-literature-model-gate
python -m unittest discover -s tests -v

python scripts/mg5_threshold_preflight.py --mass 500 --tanbeta 3
```

The preflight generates exact threshold `PS.input` four-momenta, records the default `MASS`/`SMINPUTS` values, records a few `matrix.f` color-denominator lines, detects whether `check_sa.f` supports explicit `READPS`, and produces an audit manifest at `validation/local_logs/threshold_benchmarks/M500_tanbeta3_preflight.json`. The generated parameter cards are **not modified** by this command.

If the reported MSSM mass/electroweak inputs differ from the scalar benchmark, create matched copies:

```bash
python scripts/mg5_threshold_preflight.py --mass 500 --tanbeta 3 --write-cards
```

After inspecting those copies and confirming that the source model uses the same EW input scheme and first-generation squark mixing, activate the matched cards with backups and attempt exact phase-space evaluation:

```bash
python scripts/mg5_threshold_preflight.py --mass 500 --tanbeta 3 --write-cards --apply
python scripts/mg5_evaluate_threshold.py --mass 500 --tanbeta 3
```

**Important safeguards:** `--apply` changes only the generated standalone `Cards/param_card.dat` files and refuses to replace an existing backup. The evaluator only runs when the installed `check_sa.f` provides the explicit `READPS` and `NPSPOINTS` switches; if these are absent, it stops rather than comparing an unrelated random RAMBO point. Output is saved as raw `madgraph_check.log`, **not** promoted to numerical PASS until its SMATRIX output is parsed and color/spin conventions audited.

At M=500 GeV and tanβ=3: \(m_{\tilde u}=244.8313730872\) GeV, \(m_{\tilde d}=255.1686269128\) GeV. With analytic input MW=80.379 GeV, MZ=91.1876 GeV and αW=0.0338, conditional targets:
- WZ fixed color helicity-summed M² = 0.015952560238382953, corresponding to 0.005317520079460985 **if** MG5's initial-color-averaging is exactly /3.
- Wγ fixed color M² = 0.005042077422755888, corresponding to 0.0016806924742519627 **if** /3.

These numbers are the original analytic prediction, **not independent MG5 observations**. The MSSM_SLHA2 model uses QCD colors unlike the hidden infracolor scalar model. Inspect squark first-generation left/right mixing (e.g. USQMIX, DSQMIX blocks) and all contributing diagrams before treating them as a direct control. Changing external squark masses alone is not enough to establish a consistent full MSSM physical spectrum or an experimental prediction. Use zero-width EW propagators when matching the tree-level analytic amplitudes.


## 2026-11-07: SMINPUTS[2] absent in the generated MSSM_SLHA2 card

User's first threshold preflight hit `RuntimeError: lacks required entries {('SMINPUTS', 2)}`, while all 22 existing Python tests passed. The script incorrectly treated `G_F` at SLHA code `SMINPUTS[2]` as universally mandatory and writable. Conventional SLHA2 assigns `G_F` to this entry, but the **generated model's actual external input basis must be checked before editing it**. This is a parameter-card interface blocker, not a new physics discrepancy.

Fix: the default preflight and `--write-cards` now **succeed without GF**, log `SMINPUTS` codes and short snippets from available `Source/MODEL` files, and create review cards `Cards/param_card_quirkonium_review.dat` without modifying the originals. If GF is absent, **`--apply` remains blocked** until the model's EW input scheme is verified. The review copy may NOT have physically matched electroweak couplings.

Run:

```bash
cd ~/quirkonium-helicity-pilot
git pull --ff-only origin research/pilot1-literature-model-gate
python -m unittest discover -s tests -v
python scripts/mg5_threshold_preflight.py --mass 500 --tanbeta 3
python scripts/mg5_threshold_preflight.py --mass 500 --tanbeta 3 --write-cards
python - <<'PY'
import json
from pathlib import Path
p=Path("validation/local_logs/threshold_benchmarks/M500_tanbeta3_preflight.json")
d=json.loads(p.read_text())
for channel,info in d["channels"].items():
    print("\nCHANNEL",channel)
    print("EW audit:",info["electroweak_input_audit"])
    print("model hints:",info["model_EW_source_hints"][:12])
    print("default masses:",info["default_MASS"])
PY
```

Also inspect the *original* `MG5_UL_DL_WZ/Cards/param_card.dat` `BLOCK SMINPUTS` and generated `Source/MODEL` electroweak parameter handling. Do **not** inject an unregistered external GF value just to satisfy an old preflight assumption, and do **not** run `--apply` or `mg5_evaluate_threshold.py` before EW matching is understood.
