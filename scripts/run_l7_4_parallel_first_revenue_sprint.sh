#!/usr/bin/env bash
set -euo pipefail

MODE="local-parallel"
if [[ "${1:-}" == "--mode" ]]; then
  MODE="${2:-local-parallel}"
elif [[ -n "${1:-}" ]]; then
  echo "usage: bash scripts/run_l7_4_parallel_first_revenue_sprint.sh [--mode build|local-parallel|status]" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ "$(basename "${REPO_ROOT}")" != "ystar-company" ]]; then
  echo "Refusing to run outside ystar-company." >&2
  exit 1
fi

cd "${REPO_ROOT}"

OUT_DIR="l7_parallel_first_revenue_readiness_sprint"
SUMMARY="${OUT_DIR}/l7_4_summary.json"
LANE_EXIT_CODES="${OUT_DIR}/l7_4_lane_exit_codes.json"

LANE_IDS=(L7.4A L7.4B L7.4C L7.4D L7.4E L7.4F)
LANE_SCRIPTS=(
  scripts/l7_4_lanes/build_l7_4a_target_customer_discovery.py
  scripts/l7_4_lanes/build_l7_4b_outreach_execution_pipeline.py
  scripts/l7_4_lanes/build_l7_4c_service_delivery_dry_run.py
  scripts/l7_4_lanes/build_l7_4d_trust_proof_pack.py
  scripts/l7_4_lanes/build_l7_4e_payment_contract_preflight.py
  scripts/l7_4_lanes/build_l7_4f_cockpit_and_debt_batch.py
)

write_empty_exit_codes() {
  mkdir -p "${OUT_DIR}"
  python3 - <<'PY'
import json
from pathlib import Path
Path("l7_parallel_first_revenue_readiness_sprint/l7_4_lane_exit_codes.json").write_text(json.dumps({}, indent=2) + "\n")
PY
}

run_integration() {
  PYTHONDONTWRITEBYTECODE=1 python3 scripts/l7_4_lanes/build_l7_4_integration.py
}

print_summary() {
  python3 - <<'PY'
import json
from pathlib import Path

summary_path = Path("l7_parallel_first_revenue_readiness_sprint/l7_4_summary.json")
if not summary_path.exists():
    print("L7.4 status: missing")
    print("next_command: bash scripts/run_l7_4_parallel_first_revenue_sprint.sh --mode local-parallel")
    raise SystemExit(0)
summary = json.loads(summary_path.read_text(encoding="utf-8"))
print("L7.4 status: ready")
print(f"customer_discovery_generated: {summary['target_customer_archetypes_generated'] > 0}")
print(f"approval_pipeline_generated: {summary['approval_pipeline_ready']}")
print(f"delivery_dry_run_generated: {summary['delivery_dry_run_ready']}")
print(f"trust_pack_generated: {summary['trust_proof_pack_ready']}")
print(f"payment_contract_preflight_generated: {summary['pricing_payment_contract_preflight_ready']}")
print(f"cockpit_updated: {summary['owner_cockpit_v3_ready']}")
print(f"first_revenue_readiness_score: {summary['first_revenue_readiness_score']}")
print(f"next_command: {summary['next_one_command_action']}")
PY
}

case "${MODE}" in
  build)
    write_empty_exit_codes
    for script in "${LANE_SCRIPTS[@]}"; do
      PYTHONDONTWRITEBYTECODE=1 python3 "${script}"
    done
    run_integration
    print_summary
    ;;
  local-parallel)
    mkdir -p "${OUT_DIR}"
    TMP_STATUS="${OUT_DIR}/l7_4_lane_exit_codes.tmp"
    : > "${TMP_STATUS}"
    pids=""
    index=0
    for script in "${LANE_SCRIPTS[@]}"; do
      lane_id="${LANE_IDS[$index]}"
      (
        set +e
        PYTHONDONTWRITEBYTECODE=1 python3 "${script}"
        code=$?
        printf '%s %s\n' "${lane_id}" "${code}" >> "${TMP_STATUS}"
        exit "${code}"
      ) &
      pids="${pids} $!"
      index=$((index + 1))
    done

    failed=0
    for pid in ${pids}; do
      if ! wait "${pid}"; then
        failed=1
      fi
    done

    python3 - "${TMP_STATUS}" "${LANE_EXIT_CODES}" <<'PY'
import json
import sys
from pathlib import Path

tmp = Path(sys.argv[1])
out = Path(sys.argv[2])
codes = {}
for line in tmp.read_text(encoding="utf-8").splitlines():
    parts = line.split()
    if len(parts) == 2:
        codes[parts[0]] = int(parts[1])
out.write_text(json.dumps(codes, indent=2, sort_keys=True) + "\n", encoding="utf-8")
tmp.unlink(missing_ok=True)
PY

    if [[ "${failed}" -ne 0 ]]; then
      echo "One or more L7.4 lanes failed." >&2
      exit 1
    fi
    run_integration
    print_summary
    ;;
  status)
    print_summary
    ;;
  *)
    echo "Unknown mode: ${MODE}" >&2
    echo "usage: bash scripts/run_l7_4_parallel_first_revenue_sprint.sh [--mode build|local-parallel|status]" >&2
    exit 2
    ;;
esac
