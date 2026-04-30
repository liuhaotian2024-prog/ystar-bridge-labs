#!/usr/bin/env bash
set -euo pipefail

MODE="build"
if [[ "${1:-}" == "--mode" ]]; then
  MODE="${2:-build}"
elif [[ -n "${1:-}" ]]; then
  echo "usage: bash scripts/run_l7_3_offer_validation_workflow.sh [--mode build|status]" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ "$(basename "${REPO_ROOT}")" != "ystar-company" ]]; then
  echo "Refusing to run outside ystar-company." >&2
  exit 1
fi

cd "${REPO_ROOT}"

SUMMARY="l7_approval_ready_offer_validation_workflow/l7_3_summary.json"

case "${MODE}" in
  build)
    PYTHONDONTWRITEBYTECODE=1 python3 scripts/l7_3/build_l7_3_offer_validation_workflow.py
    ;;
  status)
    if [[ ! -f "${SUMMARY}" ]]; then
      echo "L7.3 status: missing"
      echo "next_command: bash scripts/run_l7_3_offer_validation_workflow.sh --mode build"
      exit 0
    fi
    python3 - <<'PY'
import json
from pathlib import Path

summary = json.loads(Path("l7_approval_ready_offer_validation_workflow/l7_3_summary.json").read_text(encoding="utf-8"))
print(f"L7.3 status: ready")
print(f"selected_offer: {summary['selected_offer']}")
print(f"recommended_outreach_draft: {summary['recommended_outreach_draft']}")
print("approval_request_path: l7_approval_ready_offer_validation_workflow/human_approval_request/l7_3_outreach_approval_request.md")
print(f"owner_review_packet_path: {summary['owner_review_packet_path']}")
print(f"execution_allowed: {str(summary['execution_allowed']).lower()}")
print(f"next_command: {summary['next_one_command_action']}")
PY
    ;;
  *)
    echo "Unknown mode: ${MODE}" >&2
    echo "usage: bash scripts/run_l7_3_offer_validation_workflow.sh [--mode build|status]" >&2
    exit 2
    ;;
esac
