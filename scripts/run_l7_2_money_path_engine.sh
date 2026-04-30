#!/usr/bin/env bash
set -euo pipefail

MODE="build"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    -h|--help)
      echo "Usage: bash scripts/run_l7_2_money_path_engine.sh [--mode build|status]"
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
cd "${REPO_ROOT}"

PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONDONTWRITEBYTECODE=1

run_status() {
  if [[ ! -f "l7_meta_development_money_path_engine/l7_2_summary.json" ]]; then
    echo "L7.2 summary missing. Run: bash scripts/run_l7_2_money_path_engine.sh --mode build"
    exit 0
  fi
  "${PYTHON_BIN}" - <<'PY'
import json
from pathlib import Path
summary = json.loads(Path("l7_meta_development_money_path_engine/l7_2_summary.json").read_text())
print(f"primary_shortest_cash_path: {summary['primary_shortest_cash_path']} - {summary['primary_shortest_cash_path_name']}")
print(f"primary_long_term_strategic_path: {summary['primary_long_term_strategic_path']} - {summary['primary_long_term_strategic_path_name']}")
print(f"bridge_path_between_cash_and_strategy: {summary['bridge_path_between_cash_and_strategy']}")
print(f"first_cash_step: {summary['first_cash_step']}")
print(f"first_possible_buyer: {summary['first_possible_buyer']}")
print(f"next tool to build: {summary['next_tool_to_build']}")
print(f"next one-command action: {summary['next_one_command_action']}")
print("owner review packet: owner_review_packet/l7_2_money_path_owner_review_packet.md")
PY
}

case "${MODE}" in
  build)
    "${PYTHON_BIN}" scripts/l7_2_meta/build_l7_2_money_path_engine.py
    run_status
    ;;
  status)
    run_status
    ;;
  *)
    echo "Unsupported mode: ${MODE}" >&2
    exit 2
    ;;
esac
