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


## Preferred method after 2026-11-07 preflight: matrix2py, NOT check_sa / READPS

The user has now run the preflight on the generated MG5_aMC 3.5.1 standalones:
- 24 Python tests passed.
- Source/MODEL/param_read.inc directly loads **aEWM1** and **mdl_MW**.
- Original external card has SMINPUTS keys **[1,3]**, and original MASS[24]=79.82901 GeV, differing from the target MW=80.379 GeV.
- The standalone check_sa.f did **not** expose the READPS interface. Thus the older mg5_evaluate_threshold.py path is **not usable on this generated version**.
- Read-only preflight and --write-cards review copies passed. The original cards were not overwritten.

The exact external scheme still needs checking against generated model's internal coupling relations, but **GF is not required simply because generic SLHA2 convention calls it SMINPUTS[2]**. Do not invent GF. Our preview cards match external alpha_EM = alpha_W sin²(thetaW) and independent MW,MZ and the two squark masses; the model must derive the corresponding weak-angle and weak gauge coupling for a physical apples-to-apples comparison.

MadGraph's official standalone documentation gives a direct method: compile a Python-wrapped Fortran extension with make matrix2py.so, load a parameter card using matrix2py.initialisemodel, and evaluate matrix2py.get_value(P, alpha_s, -1). See https://cp3.irmp.ucl.ac.be/projects/madgraph/wiki/FAQ-General-4. This uses our **review** card and does not modify the generated default.

From the repository root:

    git pull --ff-only origin research/pilot1-literature-model-gate
    python -m unittest discover -s tests -v
    python scripts/mg5_threshold_preflight.py --mass 500 --tanbeta 3 --write-cards
    python scripts/mg5_matrix2py_compare.py --channel Z --mass 500 --tanbeta 3
    python scripts/mg5_matrix2py_compare.py --channel gamma --mass 500 --tanbeta 3

NumPy, NumPy f2py compatible with the active Python, GNU Fortran and a C compiler are needed to compile the shared library. Each channel is evaluated in a separate Python process to avoid colliding shared-library module names. The result is stored at:
    validation/local_logs/threshold_benchmarks/M500_tanbeta3_Z/matrix2py_result.json
    validation/local_logs/threshold_benchmarks/M500_tanbeta3_gamma/matrix2py_result.json

The first two analytical **targets if MG5 averages over three initial squark colors** are:
- WZ: 0.005317520079460985
- Wgamma: 0.0016806924742519627

These are not MG5 results. If ratios differ, investigate color averaging, squark mixings, EW external input dependencies, exact generated diagrams, and width/gauge conventions. Do not tune couplings to force agreement. Even ratio 1 in both channels is a scoped matrix element cross-check, not a physical allowed bound-state benchmark.

Important: the older documented --apply / mg5_evaluate_threshold.py path should **not** be used for these outputs, because it requires READPS and edits original param cards. Keep the generated defaults intact.


## 2026-11-07 matrix2py build failed — compiler diagnosis required

User completed 27 unit tests and preflight for both channels. The first WZ make matrix2py.so returned a nonzero exit code and stopped **before any numerical matrix-element calculation**. The wrapper originally stored the complete build stderr/stdout in:

    validation/local_logs/threshold_benchmarks/M500_tanbeta3_Z/matrix2py_build.log

But only printed a generic traceback. The wrapper now prints the relevant error lines and last 70 lines of the build log and records Python/NumPy/f2py/make/gcc/gfortran executables in matrix2py_environment.json. **No root cause is yet known from the user-provided traceback alone.**

Recover the exact compiler error without rerunning:

    LOG=validation/local_logs/threshold_benchmarks/M500_tanbeta3_Z/matrix2py_build.log
    grep -nEi 'error|fatal|not found|no rule|python.h|distutils|f2py|traceback|undefined reference|cannot find' "$LOG" | tail -n 35
    tail -n 70 "$LOG"
    python --version
    python -m numpy.f2py -v
    command -v gfortran; command -v f2py; command -v make

MadGraph's official standalone Python API documents make matrix2py.so in the process-specific SubProcesses/P* directory, followed by matrix2py.initialisemodel(path) and matrix2py.get_value(p,alphas,-1). See https://cp3.irmp.ucl.ac.be/projects/madgraph/wiki/FAQ-General-4. The build needs compatible NumPy/f2py, Python headers and Fortran tools. Do not guess which dependency is broken, install random packages, or change the physics card until the log is inspected.

The numerical MG5 gate is still **UNKNOWN**; 27 passing tests do not substitute for the independent generator ME.


## 2026-11-07: f2py3.10 / NumPy version mismatch — ROOT CAUSE FOUND

User's exact `matrix2py_build.log` showed:

    f2py3.10 -L../../lib/ -ldhelas -lmodel -c matrix.f -m matrix2py --f77exec=gfortran
    File "/usr/bin/f2py3.10", line 33
      sys.exit(load_entry_point('numpy==1.21.5', 'console_scripts', 'f2py3.10')())
    StopIteration
    make: *** [makefile:27: matrix2py.so] Error 1

System Python is 3.10.12, with active `python -m numpy.f2py -v` = 2.2.6, `f2py` at ~/.local/bin/f2py. gfortran and gcc exist. The legacy f2py3.10 entry-point launcher is stale; no Fortran compiler error has occurred yet.

The generated Makefile uses a legacy f2py invocation with `--f77exec=gfortran`. For a reproducible Python 3.10 build, prefer an ISOLATED venv with NumPy 1.26.4 and setuptools 68.2.2, preserving the older distutils build interface. Do NOT overwrite the system numpy, Athena, or global MadGraph installation. NumPy 2.x can use a Meson backend but that may require changing the legacy f2py flags; do not combine separate solutions without testing.

From repository root:

    git pull --ff-only origin research/pilot1-literature-model-gate
    python3.10 -m venv .venv-mg5-f2py
    .venv-mg5-f2py/bin/python -m pip install -r requirements-mg5-f2py.txt
    .venv-mg5-f2py/bin/python -m numpy.f2py -v
    .venv-mg5-f2py/bin/python scripts/fix_mg5_f2py_makefile.py
    .venv-mg5-f2py/bin/python scripts/fix_mg5_f2py_makefile.py --apply
    .venv-mg5-f2py/bin/python scripts/mg5_matrix2py_compare.py --channel Z --mass 500 --tanbeta 3
    .venv-mg5-f2py/bin/python scripts/mg5_matrix2py_compare.py --channel gamma --mass 500 --tanbeta 3

The patch changes ONLY generated standalone `SubProcesses/P*/makefile` files; each original saved as `makefile.before_quirkonium_f2py`. It substitutes the broken `f2py3.10` invocation with the venv interpreter's `python -m numpy.f2py`. It does not edit `matrix.f`, model UFO files, EW input cards, or system symlinks. Use the **same interpreter** for compiling and importing a NumPy extension to avoid 1.x/2.x ABI mismatch.

The next build may expose an actual compiler problem. The wrapper prints full diagnostic errors and writes `matrix2py_environment.json`. Do not claim independent ME validation until it produces **numeric results** and the color/mixing/coupling conventions are audited.
