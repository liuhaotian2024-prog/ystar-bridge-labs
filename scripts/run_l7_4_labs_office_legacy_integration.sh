#!/usr/bin/env bash
set -euo pipefail

MODE="build"
if [[ "${1:-}" == "--mode" ]]; then
  MODE="${2:-build}"
elif [[ -n "${1:-}" ]]; then
  echo "Usage: bash scripts/run_l7_4_labs_office_legacy_integration.sh [--mode build|status|roster|rooms]" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

if [[ "$(basename "${REPO_ROOT}")" != "ystar-company" ]]; then
  echo "Refusing to run outside ystar-company." >&2
  exit 2
fi

OUT_DIR="${REPO_ROOT}/l7_labs_office_legacy_integration"
SUMMARY="${OUT_DIR}/l7_4_labs_office_summary.json"
REGISTRY="${OUT_DIR}/original_team_registry/original_team_registry.json"
ROOM_DIR="${OUT_DIR}/agent_rooms"
BUILDER="${REPO_ROOT}/scripts/l7_4_labs_office/build_l7_4_labs_office_legacy_integration.py"

print_status() {
  python3 - <<'PY'
import json
from pathlib import Path

summary_path = Path("l7_labs_office_legacy_integration/l7_4_labs_office_summary.json")
if not summary_path.exists():
    print("Labs Office has not been built yet.")
    print("Next command: bash scripts/run_l7_4_labs_office_legacy_integration.sh --mode build")
    raise SystemExit(0)

summary = json.loads(summary_path.read_text())
print("Y*Bridge Labs Office status")
print(f"- office home: {summary['office_home_path']}")
print(f"- original repo available: {summary['original_repo_available']}")
print(f"- original repo modified by this sprint: {summary['ystar_bridge_labs_modified']}")
print(f"- legacy agents discovered: {summary['legacy_agents_discovered']}")
print(f"- original team members integrated: {summary['original_team_members_integrated']}")
print(f"- COO invented as legacy member: {summary['coo_invented_as_legacy_member']}")
print(f"- agent rooms generated: {summary['agent_rooms_generated']}")
print(f"- next command: {summary['next_one_command_action']}")
PY
}

print_roster() {
  python3 - <<'PY'
import json
from pathlib import Path

path = Path("l7_labs_office_legacy_integration/original_team_registry/original_team_registry.json")
if not path.exists():
    print("Roster is missing. Run: bash scripts/run_l7_4_labs_office_legacy_integration.sh --mode build")
    raise SystemExit(0)
data = json.loads(path.read_text())
print("Legacy Y*Bridge Labs roster")
for agent in data["agents"]:
    print(f"- {agent['display_name']} — {agent['legacy_role']} ({agent['agent_id']})")
PY
}

print_rooms() {
  python3 - <<'PY'
from pathlib import Path

room_dir = Path("l7_labs_office_legacy_integration/agent_rooms")
if not room_dir.exists():
    print("Agent rooms are missing. Run: bash scripts/run_l7_4_labs_office_legacy_integration.sh --mode build")
    raise SystemExit(0)
print("Agent rooms")
for path in sorted(room_dir.glob("*_room.md")):
    print(f"- {path}")
PY
}

case "${MODE}" in
  build)
    PYTHONDONTWRITEBYTECODE=1 python3 "${BUILDER}"
    ;;
  status)
    print_status
    ;;
  roster)
    print_roster
    ;;
  rooms)
    print_rooms
    ;;
  *)
    echo "Unknown mode: ${MODE}" >&2
    echo "Usage: bash scripts/run_l7_4_labs_office_legacy_integration.sh [--mode build|status|roster|rooms]" >&2
    exit 2
    ;;
esac
