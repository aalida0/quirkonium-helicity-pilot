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
if [ -n "${MG5_BIN:-}" ] && [ -x "${MG5_BIN}" ]; then
  ( cd validation/local_logs && "${MG5_BIN}" ../../madgraph/mssm_ew_procs.mg5 ) |& tee validation/local_logs/madgraph_generation.log
else
  echo "NOT EXECUTED: set MG5_BIN=/absolute/path/to/bin/mg5_aMC" >&2
fi
