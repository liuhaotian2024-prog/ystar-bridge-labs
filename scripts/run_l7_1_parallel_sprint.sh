#!/usr/bin/env bash
set -euo pipefail

MODE="local-parallel"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    -h|--help)
      echo "Usage: bash scripts/run_l7_1_parallel_sprint.sh [--mode scaffold|local-parallel|status]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ "$(basename "${REPO_ROOT}")" != "ystar-company" ]]; then
  echo "Refusing to run outside ystar-company: ${REPO_ROOT}" >&2
  exit 1
fi

cd "${REPO_ROOT}"

PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONDONTWRITEBYTECODE=1

# Optional repo-external config load. This never prints secret values.
if [[ -r "${HOME}/.ystar-company/controlled_observation.env" ]]; then
  set -a
  # shellcheck disable=SC1090
  . "${HOME}/.ystar-company/controlled_observation.env"
  set +a
fi

LANE_BUILDERS=(
  "scripts/l7_1_lanes/build_l7_1_conservatism_batch.py"
  "scripts/l7_1_lanes/build_l7_1_revenue_radar.py"
  "scripts/l7_1_lanes/build_l7_1_offer_hypotheses.py"
  "scripts/l7_1_lanes/build_l7_1_approval_workflow.py"
  "scripts/l7_1_lanes/build_l7_1_memory_dry_run.py"
  "scripts/l7_1_lanes/build_l7_1_owner_cockpit_v2.py"
)
LANE_SHORTS=("conservatism" "revenue" "offer" "approval" "memory" "cockpit")

print_header() {
  echo "L7.1 Parallel Commercial Autonomy Sprint"
  echo "repo: ${REPO_ROOT}"
  echo "mode: ${MODE}"
  echo "manual URLs: not required"
  echo "external side effects: blocked"
  echo "core writeback: blocked"
  echo "secrets printed: no"
}

run_integration() {
  "${PYTHON_BIN}" scripts/l7_1_lanes/build_l7_1_integration.py
}

run_scaffold() {
  print_header
  for builder in "${LANE_BUILDERS[@]}"; do
    echo "building: ${builder}"
    "${PYTHON_BIN}" "${builder}"
  done
  run_integration
  echo "L7.1 scaffold complete."
}

run_local_parallel() {
  print_header
  local pids=()
  local logs=()
  local idx=0
  for builder in "${LANE_BUILDERS[@]}"; do
    local lane="${LANE_SHORTS[$idx]}"
    local log="/tmp/ystar_l7_1_${lane}_builder.log"
    logs+=("${log}")
    echo "starting lane ${lane}: ${builder}"
    ("${PYTHON_BIN}" "${builder}" >"${log}" 2>&1) &
    pids+=("$!")
    idx=$((idx + 1))
  done

  local failed=0
  idx=0
  for pid in "${pids[@]}"; do
    local lane="${LANE_SHORTS[$idx]}"
    local log="${logs[$idx]}"
    if wait "${pid}"; then
      echo "lane ${lane}: complete"
    else
      echo "lane ${lane}: failed; details in ${log}" >&2
      failed=1
    fi
    idx=$((idx + 1))
  done

  if [[ "${failed}" -ne 0 ]]; then
    exit 1
  fi
  run_integration
  echo "L7.1 local parallel sprint complete."
}

run_status() {
  print_header
  if [[ ! -f "l7_parallel_commercial_autonomy_sprint/l7_1_lane_status.json" ]]; then
    echo "L7.1 lane status missing. Recommended command: bash scripts/run_l7_1_parallel_sprint.sh --mode local-parallel"
    exit 0
  fi
  "${PYTHON_BIN}" - <<'PY'
import json
from pathlib import Path
status = json.loads(Path("l7_parallel_commercial_autonomy_sprint/l7_1_lane_status.json").read_text())
print(f"all lanes complete: {status.get('all_lanes_complete')}")
for lane in status.get("lanes", []):
    print(f"{lane.get('lane_id')} {lane.get('lane_name')}: {lane.get('status')} ({lane.get('output_dir')})")
print("next recommended command: bash scripts/run_l7_1_parallel_sprint.sh --mode local-parallel")
PY
}

case "${MODE}" in
  scaffold)
    run_scaffold
    ;;
  local-parallel)
    run_local_parallel
    ;;
  status)
    run_status
    ;;
  *)
    echo "Unsupported mode: ${MODE}" >&2
    exit 2
    ;;
esac
