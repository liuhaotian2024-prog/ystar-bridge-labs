#!/usr/bin/env bash
set -euo pipefail

MODE="serve"
if [[ "${1:-}" == "--mode" ]]; then
  MODE="${2:-serve}"
elif [[ -n "${1:-}" ]]; then
  echo "Usage: bash scripts/run_l7_labs_office_web.sh [--mode build|serve|status|smoke|demo]" >&2
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
whiteboard_threads = list(Path("l7_real_labs_office_web_ui/runtime_packets/whiteboard_threads").glob("*.json"))
work_items = list(Path("l7_real_labs_office_web_ui/runtime_packets/work_items").glob("*.json"))
scheduler_ticks = list(Path("l7_real_labs_office_web_ui/runtime_packets/scheduler_ticks").glob("*.json"))
heartbeats = list(Path("l7_real_labs_office_web_ui/runtime_packets/progress_heartbeats").glob("*.json"))
approval_interrupts = list(Path("l7_real_labs_office_web_ui/runtime_packets/approval_interrupts").glob("*.json"))
sys_path = Path("l7_labs_team_self_work_scheduler")
print("Y*Bridge Labs Office Web UI")
print(f"- URL: {state['local_url']}")
print(f"- agents: {state['agent_count']}")
print(f"- queued owner messages: {len(owner_messages)}")
print(f"- queued team tasks: {len(team_tasks)}")
print(f"- whiteboard threads: {len(whiteboard_threads)}")
print(f"- work items: {len(work_items)}")
print(f"- L7.6 scheduler ready: {sys_path.exists()}")
print(f"- scheduler ticks: {len(scheduler_ticks)}")
print(f"- progress heartbeats: {len(heartbeats)}")
print(f"- approval interruptions: {len(approval_interrupts)}")
print(f"- pending approvals: {', '.join(state.get('pending_approvals', []))}")
print(f"- next command: bash scripts/run_l7_labs_office_web.sh --mode serve")
PY
}

run_demo() {
  build_office >/dev/null
  python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path("scripts/l7_labs_office_web").resolve()))
sys.path.insert(0, str(Path(".").resolve()))
from l7_labs_team_self_work_scheduler.scheduler import create_demo_work_item, run_bounded
item = create_demo_work_item()
result = run_bounded(max_work_items=1, max_cycles=2)
report = None
if result.get("results"):
    report = result["results"][0].get("completion_report", {}).get("completion_report_id")
print("demo_ok: L7.6 autonomous first-cash-path offer package work item created and processed locally")
print(f"work_item: {item['work_item_id']}")
print(f"completion_report: {report or 'not_created'}")
print("next_command: bash scripts/run_l7_labs_office_web.sh --mode serve")
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
    if "whiteboard-message-form" not in html or "work-board" not in html:
        raise SystemExit("HTML missing forms")
    roster = json.loads(get("/api/roster"))
    if roster.get("agent_count", 0) < 12:
        raise SystemExit("roster missing recovered agents")
    status = json.loads(get("/api/status"))
    if status.get("local_url") != "http://127.0.0.1:8765":
        raise SystemExit("status URL mismatch")
    scheduler = json.loads(get("/api/scheduler/status"))
    if not scheduler.get("scheduler_ready"):
        raise SystemExit("scheduler status not ready")
    print("smoke_ok: GET /, /api/roster, /api/status, /api/scheduler/status")
except URLError as exc:
    if "Operation not permitted" not in str(exc):
        raise
    html = Path("l7_real_labs_office_web_ui/templates/index.html").read_text(encoding="utf-8")
    state = json.loads(Path("l7_real_labs_office_web_ui/office_runtime_state.json").read_text(encoding="utf-8"))
    if "whiteboard-message-form" not in html or "work-board" not in html:
        raise SystemExit("HTML missing forms")
    if state.get("agent_count", 0) < 12:
        raise SystemExit("runtime state missing recovered agents")
    summary = json.loads(Path("l7_labs_team_self_work_scheduler/l7_6_summary.json").read_text(encoding="utf-8"))
    if not summary.get("scheduler_created"):
        raise SystemExit("scheduler summary missing")
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
  demo)
    run_demo
    ;;
  *)
    echo "Unknown mode: ${MODE}" >&2
    echo "Usage: bash scripts/run_l7_labs_office_web.sh [--mode build|serve|status|smoke|demo]" >&2
    exit 2
    ;;
esac
