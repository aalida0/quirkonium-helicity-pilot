#!/usr/bin/env bash
# One-shot no-Condor FCC scalar-quirkonium source audit.
# All execution, logs, and physics reports are in the user's HOME checkout.
# Invocation: bash scripts/run_fcc_survival_local.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$REPO/results/fcc_survival_one_shot_20261108"
mkdir -p "$OUT"
cd "$REPO"

# Record ALL setup messages and exceptions, including Key4HEP failures.
# A fresh local.log is created before sourcing external environment scripts.
exec > >(tee "$OUT/local.log") 2>&1

# Reports from an earlier failed/successful attempt should not be
# mistaken for the outcome of the current run. Keep previous logs.
rm -f "$OUT/fcc_survival_all.json" "$OUT/fcc_survival_all.md"

on_exit() {
  exitcode=$?
  if [[ "$exitcode" -eq 0 ]]; then
    return 0
  fi
  printf '\nLOCAL FCC SURVIVAL JOB FAILED (exit %s)\n' "$exitcode" >&2
  printf 'Read the last traceback/error in: %s\n' "$OUT/local.log" >&2
  if [[ ! -s "$OUT/fcc_survival_all.md" ]]; then
    printf '# FCC local survival audit: FAILED\n\nExit code: %s. No completed physics result. Inspect local.log.\n' \
      "$exitcode" > "$OUT/fcc_survival_all.md"
  fi
  if [[ ! -s "$OUT/fcc_survival_all.json" ]]; then
    printf '{"status":"FAILED","exit_code":%s,"message":"No completed physics result; see local.log"}\n' \
      "$exitcode" > "$OUT/fcc_survival_all.json"
  fi
}
# EXIT runs once, including early failures; ERR with errtrace duplicated notices.
trap on_exit EXIT

# Keep CPU library thread counts controlled on a shared login host.
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

# Key4HEP's setup script accesses unset shell variables (e.g. compiler);
# temporarily disable nounset only while loading this external environment.
set +u
source /cvmfs/sw.hsf.org/key4hep/setup.sh
set -u
export LHAPDF_DATA_PATH="/cvmfs/sft.cern.ch/lcg/external/lhapdfsets/current:$(lhapdf-config --datadir)"

echo "Running locally (NO Condor); repo: $REPO"
echo "Results directory: $OUT"
echo "Host: $(hostname)"
echo "Python: $(command -v python)"
python - <<'PY'
import sys, numpy, lhapdf
p=lhapdf.mkPDF("MSTW2008lo68cl",0)
print("Python:",sys.version.split()[0],
      "| NumPy:",numpy.__version__,
      "| LHAPDF:",lhapdf.version(),
      "| PDF:",p.set().name)
PY

# All output, including tests and Python exceptions, is already captured
# by the shell-wide tee initialized before Key4HEP. Python -u avoids buffering.
nice -n 10 python -u scripts/quirkonium_fcc_survival_one_shot.py \
  --run-tests \
  --pdf-set MSTW2008lo68cl \
  --scenarios 85:20000 100:30000 \
  --mass 500 --tanbeta-high 3 \
  --lambda-grid 1 2 3 5 10 \
  --rapidity-nodes 40 --shat-nodes 64 \
  --reference-nodes 72 \
  --polar-nodes 8 --phis 16 --orientations 5 \
  --flavor-mode full-ckm \
  --output "$OUT/fcc_survival_all.json"

echo
echo "SUCCESS: local one-shot completed without Condor."
echo "JSON: $OUT/fcc_survival_all.json"
echo "REPORT: $OUT/fcc_survival_all.md"
echo "LOG: $OUT/local.log"
