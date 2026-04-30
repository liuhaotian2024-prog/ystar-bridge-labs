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
      echo "Usage: bash scripts/run_l7_parallel_lanes.sh [--mode scaffold|local-parallel|worktree-setup|status]"
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

LANE_BUILDERS=(
  "scripts/l7_lanes/build_l7a_agent_team_runtime.py"
  "scripts/l7_lanes/build_l7b_revenue_opportunity_radar.py"
  "scripts/l7_lanes/build_l7c_human_approved_external_action_gate.py"
  "scripts/l7_lanes/build_l7d_review_gated_memory_writeback.py"
  "scripts/l7_lanes/build_l7e_owner_runtime_cockpit.py"
)

LANE_SHORTS=("team" "revenue" "action" "memory" "cockpit")
LANE_WORKTREES=(
  "../ystar-company-l7-team"
  "../ystar-company-l7-revenue"
  "../ystar-company-l7-action"
  "../ystar-company-l7-memory"
  "../ystar-company-l7-cockpit"
)
LANE_BRANCHES=(
  "l7/team-runtime"
  "l7/revenue-opportunity-radar"
  "l7/human-approved-action-gate"
  "l7/review-gated-memory-writeback"
  "l7/runtime-cockpit"
)
LANE_PROMPTS=(
  "l7_parallel_lane_specs/l7a_agent_team_runtime.prompt.md"
  "l7_parallel_lane_specs/l7b_revenue_opportunity_radar.prompt.md"
  "l7_parallel_lane_specs/l7c_human_approved_external_action_gate.prompt.md"
  "l7_parallel_lane_specs/l7d_review_gated_memory_writeback.prompt.md"
  "l7_parallel_lane_specs/l7e_owner_runtime_cockpit.prompt.md"
)

print_header() {
  echo "L7.0P Parallel Commercial Agent Team Orchestrator"
  echo "repo: ${REPO_ROOT}"
  echo "mode: ${MODE}"
  echo "network: disabled by default"
  echo "external actions: blocked"
  echo "core writeback: blocked"
}

run_integration() {
  "${PYTHON_BIN}" scripts/l7_lanes/build_l7_integration.py
}

run_scaffold() {
  print_header
  for builder in "${LANE_BUILDERS[@]}"; do
    echo "building: ${builder}"
    "${PYTHON_BIN}" "${builder}"
  done
  run_integration
  echo "L7 scaffold complete."
}

run_local_parallel() {
  print_header
  local pids=()
  local logs=()
  local idx=0
  for builder in "${LANE_BUILDERS[@]}"; do
    local lane="${LANE_SHORTS[$idx]}"
    local log="/tmp/ystar_l7_${lane}_builder.log"
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
  echo "L7 local parallel lane build complete."
}

run_worktree_setup() {
  print_header
  echo "Creating sibling worktrees and branches when missing. No merge is performed."
  local idx=0
  for worktree in "${LANE_WORKTREES[@]}"; do
    local branch="${LANE_BRANCHES[$idx]}"
    local prompt="${LANE_PROMPTS[$idx]}"
    if [[ ! -d "${worktree}/.git" && ! -f "${worktree}/.git" ]]; then
      if git show-ref --verify --quiet "refs/heads/${branch}"; then
        git worktree add "${worktree}" "${branch}"
      else
        git worktree add -b "${branch}" "${worktree}" HEAD
      fi
    fi
    mkdir -p "${worktree}/l7_parallel_lane_specs"
    cp "${prompt}" "${worktree}/l7_parallel_lane_specs/ASSIGNED_LANE_PROMPT.md"
    echo "worktree ready: ${worktree} (${branch})"
    idx=$((idx + 1))
  done
  run_integration
  echo "Worktree setup complete. No branches were merged."
}

run_status() {
  print_header
  if [[ ! -f "l7_parallel_commercial_agent_team_orchestrator/l7_0p_lane_status.json" ]]; then
    echo "Lane status file missing. Recommended command: bash scripts/run_l7_parallel_lanes.sh --mode local-parallel"
    exit 0
  fi
  "${PYTHON_BIN}" - <<'PY'
import json
from pathlib import Path
status = json.loads(Path("l7_parallel_commercial_agent_team_orchestrator/l7_0p_lane_status.json").read_text())
print(f"all lanes complete: {status.get('all_lanes_complete')}")
for lane in status.get("lanes", []):
    print(f"{lane['lane_id']} {lane['lane_name']}: {lane['status']} ({lane['output_dir']})")
print("next recommended command: bash scripts/run_l7_parallel_lanes.sh --mode local-parallel")
PY
}

case "${MODE}" in
  scaffold)
    run_scaffold
    ;;
  local-parallel)
    run_local_parallel
    ;;
  worktree-setup)
    run_worktree_setup
    ;;
  status)
    run_status
    ;;
  *)
    echo "Unsupported mode: ${MODE}" >&2
    exit 2
    ;;
esac
