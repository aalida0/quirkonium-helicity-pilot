#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p validation/local_logs
if command -v wolframscript >/dev/null 2>&1; then
  wolframscript -file mathematica/validate_scalar_WZ.wl | tee validation/local_logs/mathematica.log
  python scripts/compare_wolfram.py validation/local_logs/mathematica.log
else
  echo "NOT EXECUTED: wolframscript unavailable; use Mathematica Get[...]" >&2
fi
# Default to the user's installed MG5_aMC v3.5.1; an explicit MG5_BIN overrides it.
MG5_BIN="${MG5_BIN:-$HOME/codes/Herwig/herwigpp/opt/MG5_aMC_v3_5_1/bin/mg5_aMC}"
if [ -x "${MG5_BIN}" ]; then
  ( cd validation/local_logs && "${MG5_BIN}" ../../madgraph/mssm_ew_procs.mg5 ) |& tee validation/local_logs/madgraph_generation.log
else
  echo "NOT EXECUTED: MadGraph executable not found at $MG5_BIN; override MG5_BIN" >&2
fi
