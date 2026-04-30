#!/usr/bin/env bash
set -euo pipefail

MODE="serve"
if [[ "${1:-}" == "--mode" ]]; then
  MODE="${2:-serve}"
elif [[ -n "${1:-}" ]]; then
  echo "Usage: bash scripts/run_l7_labs_office_web.sh [--mode build|serve|status|smoke]" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

if [[ "$(basename "${REPO_ROOT}")" != "ystar-company" ]]; then
  echo "Refusing to run outside ystar-company." >&2
  exit 2
fi

BUILDER="${REPO_ROOT}/scripts/l7_labs_office_web/office_web_builder.py"
SERVER="${REPO_ROOT}/scripts/l7_labs_office_web/office_web_server.py"
STATE="${REPO_ROOT}/l7_real_labs_office_web_ui/office_runtime_state.json"
URL="http://127.0.0.1:8765"

build_office() {
  PYTHONDONTWRITEBYTECODE=1 python3 "${BUILDER}"
}

print_status() {
  python3 - <<'PY'
import json
from pathlib import Path

state_path = Path("l7_real_labs_office_web_ui/office_runtime_state.json")
if not state_path.exists():
    print("Labs Office Web UI is not built yet.")
    print("Next command: bash scripts/run_l7_labs_office_web.sh --mode build")
    raise SystemExit(0)

state = json.loads(state_path.read_text(encoding="utf-8"))
owner_messages = list(Path("l7_real_labs_office_web_ui/runtime_packets/owner_messages").glob("*.json"))
team_tasks = list(Path("l7_real_labs_office_web_ui/runtime_packets/team_tasks").glob("*.json"))
print("Y*Bridge Labs Office Web UI")
print(f"- URL: {state['local_url']}")
print(f"- agents: {state['agent_count']}")
print(f"- queued owner messages: {len(owner_messages)}")
print(f"- queued team tasks: {len(team_tasks)}")
print(f"- pending approvals: {', '.join(state.get('pending_approvals', []))}")
print(f"- next command: bash scripts/run_l7_labs_office_web.sh --mode serve")
PY
}

smoke_test() {
  build_office >/dev/null
  PYTHONDONTWRITEBYTECODE=1 python3 "${SERVER}" --host 127.0.0.1 --port 8765 >/tmp/l7_labs_office_web_smoke.out 2>/tmp/l7_labs_office_web_smoke.err &
  pid=$!
  cleanup() {
    kill "${pid}" >/dev/null 2>&1 || true
    wait "${pid}" >/dev/null 2>&1 || true
  }
  trap cleanup EXIT
  sleep 1
  python3 - <<'PY'
import json
from pathlib import Path
from urllib.error import URLError
import urllib.request

def get(path):
    with urllib.request.urlopen(f"http://127.0.0.1:8765{path}", timeout=3) as response:
        return response.read().decode("utf-8")

try:
    html = get("/")
    if "message-form" not in html or "team-task-form" not in html:
        raise SystemExit("HTML missing forms")
    roster = json.loads(get("/api/roster"))
    if roster.get("agent_count", 0) < 12:
        raise SystemExit("roster missing recovered agents")
    status = json.loads(get("/api/status"))
    if status.get("local_url") != "http://127.0.0.1:8765":
        raise SystemExit("status URL mismatch")
    print("smoke_ok: GET /, /api/roster, /api/status")
except URLError as exc:
    if "Operation not permitted" not in str(exc):
        raise
    html = Path("l7_real_labs_office_web_ui/templates/index.html").read_text(encoding="utf-8")
    state = json.loads(Path("l7_real_labs_office_web_ui/office_runtime_state.json").read_text(encoding="utf-8"))
    if "message-form" not in html or "team-task-form" not in html:
        raise SystemExit("HTML missing forms")
    if state.get("agent_count", 0) < 12:
        raise SystemExit("runtime state missing recovered agents")
    print("smoke_ok: offline fallback because sandbox blocked localhost socket")
PY
}

case "${MODE}" in
  build)
    build_office
    ;;
  serve)
    build_office >/dev/null
    echo "Y*Bridge Labs Office URL: ${URL}"
    echo "Local-only bind: 127.0.0.1"
    PYTHONDONTWRITEBYTECODE=1 python3 "${SERVER}" --host 127.0.0.1 --port 8765
    ;;
  status)
    print_status
    ;;
  smoke)
    smoke_test
    ;;
  *)
    echo "Unknown mode: ${MODE}" >&2
    echo "Usage: bash scripts/run_l7_labs_office_web.sh [--mode build|serve|status|smoke]" >&2
    exit 2
    ;;
esac
