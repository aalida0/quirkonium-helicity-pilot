#!/usr/bin/env bash
# Single-command AF task: create one HTCondor worker job, fixed audit paths.
# Usage: bash scripts/submit_fcc_survival_one_shot.sh
# Optional on an allocated worker: bash scripts/submit_fcc_survival_one_shot.sh --local

set -Eeuo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JOB_DIR="${HOME}/quirkonium-helicity-pilot/condor/fcc_survival_one_shot_20261108"
OUTPUT_DIR="/data/${USER}/quirkonium-production/fcc_survival_one_shot_20261108"
mkdir -p "$JOB_DIR" "$OUTPUT_DIR"

WORKER="$JOB_DIR/worker.sh"
cat >"$WORKER" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail
source /cvmfs/sw.hsf.org/key4hep/setup.sh
export LHAPDF_DATA_PATH="/cvmfs/sft.cern.ch/lcg/external/lhapdfsets/current:\$(lhapdf-config --datadir)"
cd "$REPO"
echo "HOST=\$(hostname)"
echo "PYTHON=\$(which python)"
python - <<'PY'
import lhapdf, numpy
pdf=lhapdf.mkPDF("MSTW2008lo68cl",0)
print("LHAPDF",lhapdf.version(),"PDF",pdf.set().name)
PY
python scripts/quirkonium_fcc_survival_one_shot.py \\
  --run-tests \\
  --pdf-set MSTW2008lo68cl \\
  --scenarios 85:20000 100:30000 \\
  --mass 500 --tanbeta-high 3 \\
  --lambda-grid 1 2 3 5 10 \\
  --rapidity-nodes 40 --shat-nodes 64 \\
  --reference-nodes 72 \\
  --polar-nodes 8 --phis 16 --orientations 5 \\
  --flavor-mode full-ckm \\
  --output "$OUTPUT_DIR/fcc_survival_all.json"
EOF
chmod 750 "$WORKER"

if [[ "${1:-}" == "--local" ]]; then
  echo "RUNNING LOCALLY (avoid on a busy shared login node)"
  bash "$WORKER" 2>&1 | tee "$JOB_DIR/local.log"
  exit "${PIPESTATUS[0]}"
fi

if ! command -v condor_submit >/dev/null 2>&1; then
  echo "ERROR: condor_submit unavailable. No job submitted."
  echo "Use on UChicago AF or call with --local on an allocated worker."
  exit 3
fi

SUBMIT="$JOB_DIR/submit.sub"
cat >"$SUBMIT" <<EOF
universe = vanilla
executable = $WORKER
initialdir = $JOB_DIR
output = $JOB_DIR/stdout.\$(ClusterId).\$(ProcId).log
error = $JOB_DIR/stderr.\$(ClusterId).\$(ProcId).log
log = $JOB_DIR/condor-events.log
request_cpus = 1
request_memory = 4GB
request_disk = 2GB
should_transfer_files = NO
getenv = False
queue 1
EOF
echo "REPOSITORY=$REPO"
echo "JOB_DIR=$JOB_DIR"
echo "OUTPUT_DIR=$OUTPUT_DIR"
echo "SUBMITTING ONE CONDOR WORKER JOB"
(cd "$JOB_DIR" && condor_submit submit.sub)
echo
echo "After completion:"
echo "  $OUTPUT_DIR/fcc_survival_all.md"
echo "  $OUTPUT_DIR/fcc_survival_all.json"
echo "  $JOB_DIR/stdout.<cluster>.<proc>.log"
echo "Inspect your user-owned Condor jobs with: condor_q $USER"
echo "If submission still fails, run: condor_submit -debug $SUBMIT"
