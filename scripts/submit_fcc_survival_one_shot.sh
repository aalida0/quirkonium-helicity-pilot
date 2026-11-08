#!/usr/bin/env bash
# UChicago AF: Condor submission/logs HOME, physics JSON/MD DATA.
# Transfer tracked source snapshot to worker scratch. No shared-FS requirement.
set -Eeuo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
JOB_DIR="$REPO/condor/fcc_survival_one_shot_20261108"
OUTPUT_DIR="/data/$USER/quirkonium-production/fcc_survival_one_shot_20261108"
mkdir -p "$JOB_DIR" "$OUTPUT_DIR"

# Only git-tracked source: no .git, local outputs, secrets or /data.
ARCHIVE="$JOB_DIR/source.tar.gz"
git -C "$REPO" archive --format=tar.gz \
  --prefix=quirkonium-helicity-pilot/ --output="$ARCHIVE" HEAD

WORKER="$JOB_DIR/worker.sh"
cat >"$WORKER" <<'WORKER_EOF'
#!/usr/bin/env bash
set -Eeuo pipefail
RESULT_DIR="$PWD"
status_file="$RESULT_DIR/fcc_survival_all.json"
summary_file="$RESULT_DIR/fcc_survival_all.md"
on_exit() {
  code=$?
  if [[ "$code" -ne 0 ]]; then
    if [[ ! -s "$status_file" ]]; then
      printf '{"status":"FAILED","exit_code":%d,"message":"See Condor stderr and stdout for the cause; no physics results were established."}\n' \
        "$code" > "$status_file"
    fi
    if [[ ! -s "$summary_file" ]]; then
      printf '# FCC one-shot survival audit FAILED\n\nExit code: %d. See Condor stderr/stdout.\n' \
        "$code" > "$summary_file"
    fi
  fi
}
trap on_exit EXIT

source /cvmfs/sw.hsf.org/key4hep/setup.sh
export LHAPDF_DATA_PATH="/cvmfs/sft.cern.ch/lcg/external/lhapdfsets/current:$(lhapdf-config --datadir)"
echo "WORKER_HOST=$(hostname)"
echo "PYTHON=$(command -v python)"
echo "SCRATCH=$PWD"
python - <<'PY'
import lhapdf, numpy
pdf=lhapdf.mkPDF("MSTW2008lo68cl",0)
print("LHAPDF",lhapdf.version(),"PDF",pdf.set().name)
PY

tar -xzf source.tar.gz
cd quirkonium-helicity-pilot
python scripts/quirkonium_fcc_survival_one_shot.py \
  --run-tests \
  --pdf-set MSTW2008lo68cl \
  --scenarios 85:20000 100:30000 \
  --mass 500 --tanbeta-high 3 \
  --lambda-grid 1 2 3 5 10 \
  --rapidity-nodes 40 --shat-nodes 64 \
  --reference-nodes 72 \
  --polar-nodes 8 --phis 16 --orientations 5 \
  --flavor-mode full-ckm \
  --output "$RESULT_DIR/fcc_survival_all.json"
echo "SUCCESS: source-weighted survival and W+ angular reports written"
WORKER_EOF
chmod 750 "$WORKER"

if [[ "$#" -gt 0 && "$1" == "--local" ]]; then
  echo "CAUTION: --local only for an ALLOCATED worker, not shared login"
  (cd "$JOB_DIR" && bash "$WORKER") 2>&1 | tee "$JOB_DIR/local.log"
  exit $?
fi
if ! command -v condor_submit >/dev/null 2>&1; then
  echo "ERROR: condor_submit unavailable; no job submitted" >&2
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
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files = $ARCHIVE
transfer_output_files = fcc_survival_all.json, fcc_survival_all.md
transfer_output_remaps = "fcc_survival_all.json=$OUTPUT_DIR/fcc_survival_all.json;fcc_survival_all.md=$OUTPUT_DIR/fcc_survival_all.md"
getenv = False
queue 1
EOF

echo "REPOSITORY=$REPO"
echo "JOB_DIR=$JOB_DIR"
echo "OUTPUT_DIR=$OUTPUT_DIR"
echo "SOURCE_ARCHIVE=$(du -h "$ARCHIVE" | awk '{print $1}')"
echo "SUBMITTING ONE TRANSFER-ENABLED CONDOR JOB"
(cd "$JOB_DIR" && condor_submit submit.sub)
echo "After completion:"
echo "  $OUTPUT_DIR/fcc_survival_all.md"
echo "  $OUTPUT_DIR/fcc_survival_all.json"
echo "  $JOB_DIR/stdout.<cluster>.<proc>.log"
echo "Check queue with: condor_q $USER -better-analyze"
