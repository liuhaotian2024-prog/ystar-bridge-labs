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
l8_root = Path("l8_first_cash_path_operating_loop/runtime_packets")
l8_dirs = {
    "actions": l8_root / "commercial_action_queue",
    "approvals": l8_root / "owner_approval_decisions",
    "manual": l8_root / "manual_send_packets",
    "feedback": l8_root / "customer_feedback",
    "residuals": l8_root / "commercial_residuals",
    "learning": l8_root / "learning_candidates",
}
l9_root = Path("l9_meta_development_opportunity_runtime/runtime_packets")
l9_dirs = {
    "assets": l9_root / "internal_asset_inventory",
    "opportunities": l9_root / "opportunity_candidates",
    "money_paths": l9_root / "money_path_candidates",
    "rankings": l9_root / "opportunity_rankings",
    "reviews": l9_root / "opportunity_review_decisions",
    "plans": l9_root / "execution_plans",
    "bridges": l9_root / "l8_bridge_packets",
    "residuals": l9_root / "portfolio_residuals",
    "learning": l9_root / "portfolio_learning_candidates",
}
l10_root = Path("l10_delegated_live_meta_development_runtime/runtime_packets")
l10_dirs = {
    "missions": l10_root / "missions",
    "evidence": l10_root / "research_evidence_packets",
    "signals": l10_root / "opportunity_signals",
    "briefs": l10_root / "meta_strategy_briefs",
    "escalations": l10_root / "escalation_packets",
    "reports": l10_root / "mission_completion_reports",
}
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
print(f"- L8 package available: {Path('l8_first_cash_path_operating_loop').exists()}")
print(f"- L8 commercial actions: {len(list(l8_dirs['actions'].glob('*.json'))) if l8_dirs['actions'].exists() else 0}")
print(f"- L8 owner approvals: {len(list(l8_dirs['approvals'].glob('*.json'))) if l8_dirs['approvals'].exists() else 0}")
print(f"- L8 manual-send packets: {len(list(l8_dirs['manual'].glob('*.json'))) if l8_dirs['manual'].exists() else 0}")
print(f"- L8 feedback packets: {len(list(l8_dirs['feedback'].glob('*.json'))) if l8_dirs['feedback'].exists() else 0}")
print(f"- L8 residuals: {len(list(l8_dirs['residuals'].glob('*.json'))) if l8_dirs['residuals'].exists() else 0}")
print(f"- L8 learning candidates: {len(list(l8_dirs['learning'].glob('*.json'))) if l8_dirs['learning'].exists() else 0}")
print(f"- L9 package available: {Path('l9_meta_development_opportunity_runtime').exists()}")
print(f"- L9 asset inventory packets: {len(list(l9_dirs['assets'].glob('*.json'))) if l9_dirs['assets'].exists() else 0}")
print(f"- L9 opportunities: {len(list(l9_dirs['opportunities'].glob('*.json'))) if l9_dirs['opportunities'].exists() else 0}")
print(f"- L9 money paths: {len(list(l9_dirs['money_paths'].glob('*.json'))) if l9_dirs['money_paths'].exists() else 0}")
print(f"- L9 rankings: {len(list(l9_dirs['rankings'].glob('*.json'))) if l9_dirs['rankings'].exists() else 0}")
print(f"- L9 selected opportunity count: {sum(1 for p in l9_dirs['money_paths'].glob('*.json') if p.name != '.gitkeep' and json.loads(p.read_text(encoding='utf-8')).get('status') == 'selected_for_execution') if l9_dirs['money_paths'].exists() else 0}")
print(f"- L9 execution plans: {len(list(l9_dirs['plans'].glob('*.json'))) if l9_dirs['plans'].exists() else 0}")
print(f"- L9 L8 bridge packets: {len(list(l9_dirs['bridges'].glob('*.json'))) if l9_dirs['bridges'].exists() else 0}")
print(f"- L9 portfolio residuals: {len(list(l9_dirs['residuals'].glob('*.json'))) if l9_dirs['residuals'].exists() else 0}")
print(f"- L9 learning candidates: {len(list(l9_dirs['learning'].glob('*.json'))) if l9_dirs['learning'].exists() else 0}")
print("- L9 grant/RFP default path: no")
print(f"- L10 package available: {Path('l10_delegated_live_meta_development_runtime').exists()}")
print(f"- L10 missions: {len(list(l10_dirs['missions'].glob('*.json'))) if l10_dirs['missions'].exists() else 0}")
print(f"- L10 evidence packets: {len(list(l10_dirs['evidence'].glob('*.json'))) if l10_dirs['evidence'].exists() else 0}")
print(f"- L10 opportunity signals: {len(list(l10_dirs['signals'].glob('*.json'))) if l10_dirs['signals'].exists() else 0}")
print(f"- L10 strategy briefs: {len(list(l10_dirs['briefs'].glob('*.json'))) if l10_dirs['briefs'].exists() else 0}")
print(f"- L10 escalation packets: {len(list(l10_dirs['escalations'].glob('*.json'))) if l10_dirs['escalations'].exists() else 0}")
print(f"- L10 completion reports: {len(list(l10_dirs['reports'].glob('*.json'))) if l10_dirs['reports'].exists() else 0}")
print("- L10 configured live read-only research: disabled unless explicitly enabled")
print("- L10 fixture demo: available")
print("- external side effects: no")
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
from l8_first_cash_path_operating_loop.commercial_action_builder import build_commercial_actions
from l8_first_cash_path_operating_loop.commercial_residual import build_commercial_residual
from l8_first_cash_path_operating_loop.customer_feedback_intake import record_customer_feedback
from l8_first_cash_path_operating_loop.first_cash_path_loader import initialize_first_cash_path
from l8_first_cash_path_operating_loop.learning_candidate_builder import build_learning_candidate
from l8_first_cash_path_operating_loop.manual_send_packet import mark_manual_send_packet
from l8_first_cash_path_operating_loop.owner_approval_center import decide_action
from l8_first_cash_path_operating_loop.cockpit_model import build_cockpit_snapshot
from l9_meta_development_opportunity_runtime.l9_manifest_builder import build_manifest as build_l9_manifest
from l9_meta_development_opportunity_runtime.owner_decision_packet import list_owner_decision_packets
from l9_meta_development_opportunity_runtime.opportunity_review_center import decide_opportunity
from l9_meta_development_opportunity_runtime.execution_plan_generator import build_execution_plan
from l9_meta_development_opportunity_runtime.l8_action_loop_bridge import build_l8_bridge_packet
from l9_meta_development_opportunity_runtime.portfolio_feedback_ingestor import record_portfolio_feedback
from l9_meta_development_opportunity_runtime.portfolio_residual import build_portfolio_residual
from l9_meta_development_opportunity_runtime.portfolio_learning_candidate import build_portfolio_learning_candidate
from l9_meta_development_opportunity_runtime.meta_development_cockpit import build_meta_cockpit
from l10_delegated_live_meta_development_runtime.l10_manifest_builder import build_manifest as build_l10_manifest
from l10_delegated_live_meta_development_runtime.mission_delegation_center import create_default_mission
from l10_delegated_live_meta_development_runtime.mission_runner import run_bounded_mission
from l10_delegated_live_meta_development_runtime.escalation_review_center import decide_escalation
from l10_delegated_live_meta_development_runtime.escalation_packet_builder import list_escalation_packets
from l10_delegated_live_meta_development_runtime.mission_cockpit_model import build_mission_cockpit
item = create_demo_work_item()
result = run_bounded(max_work_items=1, max_cycles=2)
report = None
if result.get("results"):
    report = result["results"][0].get("completion_report", {}).get("completion_report_id")
cash_path = initialize_first_cash_path()
actions = build_commercial_actions(force=True)["actions"]
selected = next(action for action in actions if action["action_type"] == "direct_founder_outreach")
decision = decide_action(selected["action_id"], "approve", "Simulated local demo approval only.")
manual_packet = decision["manual_send_packet"]
receipt = mark_manual_send_packet(manual_packet["packet_id"], "marked_sent_by_owner", "Simulated local demo receipt; no email was sent.")
feedback = record_customer_feedback(manual_packet["packet_id"], "interested", "Simulated customer asks for more detail about timeline and sample output.")
residual = build_commercial_residual(feedback["feedback_id"])
candidate = build_learning_candidate(residual["residual_id"])
cockpit = build_cockpit_snapshot()
l9_manifest = build_l9_manifest(force=True)
decision_packets = list_owner_decision_packets()
non_seed_packet = next(packet for packet in decision_packets if "founder_ai_workflow_audit" not in packet["money_path_id"])
l9_decision = decide_opportunity(non_seed_packet["decision_packet_id"], "select_for_execution", "Simulated local demo selection of a non-seed opportunity.")
l9_plan = build_execution_plan(l9_decision["money_path"]["money_path_id"])
l9_bridge = build_l8_bridge_packet(l9_plan["execution_plan_id"])
l9_feedback = record_portfolio_feedback(l9_decision["money_path"]["money_path_id"], "positive_signal", "Simulated portfolio signal for demo; no customer contact occurred.")
l9_residual = build_portfolio_residual(l9_feedback["feedback_id"])
l9_learning = build_portfolio_learning_candidate(l9_residual["residual_id"])
l9_cockpit = build_meta_cockpit()
l10_manifest = build_l10_manifest(force=True)
l10_mission = create_default_mission()
l10_result = run_bounded_mission(l10_mission["mission_id"], max_cycles=2, fixture_research=True)
l10_escalation = next(item for item in list_escalation_packets() if item["mission_id"] == l10_mission["mission_id"])
l10_decision = decide_escalation(l10_escalation["escalation_id"], "hold", "Simulated local demo decision; no action executed.")
l10_cockpit = build_mission_cockpit()
print("demo_ok: L8 first cash path operating loop simulated locally")
print(f"work_item: {item['work_item_id']}")
print(f"completion_report: {report or 'not_created'}")
print(f"selected_offer: {cash_path['selected_offer']}")
print(f"commercial_action: {selected['action_id']}")
print(f"manual_send_packet: {manual_packet['packet_id']}")
print(f"manual_action_receipt: {receipt['receipt_id']}")
print(f"customer_feedback: {feedback['feedback_id']}")
print(f"commercial_residual: {residual['residual_id']}")
print(f"learning_candidate: {candidate['candidate_id']}")
print(f"cockpit_snapshot: {cockpit['cockpit_snapshot_id']}")
print("demo_ok: L9 meta-development portfolio loop simulated locally")
print(f"l9_manifest_opportunities: {l9_manifest['opportunity_count']}")
print(f"l9_selected_non_seed_money_path: {l9_decision['money_path']['money_path_id']}")
print(f"l9_execution_plan: {l9_plan['execution_plan_id']}")
print(f"l9_l8_bridge_packet: {l9_bridge['bridge_packet_id']}")
print(f"l9_portfolio_residual: {l9_residual['residual_id']}")
print(f"l9_learning_candidate: {l9_learning['candidate_id']}")
print(f"l9_cockpit_snapshot: {l9_cockpit['cockpit_snapshot_id']}")
print("demo_ok: L10 delegated meta-development mission simulated locally")
print(f"l10_manifest_missions: {l10_manifest['mission_count']}")
print(f"l10_mission: {l10_mission['mission_id']}")
print(f"l10_completion_report: {l10_result['mission_completion_report']['report_id']}")
print(f"l10_escalation: {l10_escalation['escalation_id']}")
print(f"l10_escalation_decision: {l10_decision['decision_id']}")
print(f"l10_cockpit_snapshot: {l10_cockpit['snapshot_id']}")
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
    l8 = json.loads(get("/api/l8/cockpit"))
    if "Founder AI Workflow Audit" not in l8.get("selected_first_cash_path", {}).get("selected_offer", ""):
        raise SystemExit("L8 cockpit missing selected first cash path")
    l9 = json.loads(get("/api/l9/meta/cockpit"))
    if len(l9.get("opportunity_candidates", [])) < 8:
        raise SystemExit("L9 cockpit missing opportunity portfolio")
    if l9.get("grant_rfp_default_path_status") != "no":
        raise SystemExit("L9 grant/RFP default path unexpectedly enabled")
    l10 = json.loads(get("/api/l10/cockpit"))
    if "fixture_demo_available" not in l10:
        raise SystemExit("L10 cockpit missing fixture demo status")
    print("smoke_ok: GET /, /api/roster, /api/status, /api/scheduler/status, /api/l8/cockpit, /api/l9/meta/cockpit, /api/l10/cockpit")
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
    l8_summary = json.loads(Path("l8_first_cash_path_operating_loop/l8_summary.json").read_text(encoding="utf-8"))
    if not l8_summary.get("first_cash_path_initialized"):
        raise SystemExit("L8 summary missing")
    if "L8 First Cash Path Cockpit" not in html:
        raise SystemExit("HTML missing L8 cockpit")
    l9_summary = json.loads(Path("l9_meta_development_opportunity_runtime/l9_summary.json").read_text(encoding="utf-8"))
    if l9_summary.get("opportunity_count", 0) < 8:
        raise SystemExit("L9 summary missing opportunity portfolio")
    if "L9 Meta-Development Cockpit" not in html:
        raise SystemExit("HTML missing L9 cockpit")
    l10_summary = json.loads(Path("l10_delegated_live_meta_development_runtime/l10_summary.json").read_text(encoding="utf-8"))
    if l10_summary.get("permission_tier_count", 0) < 5:
        raise SystemExit("L10 summary missing permission tiers")
    if "L10 Delegated Mission Cockpit" not in html:
        raise SystemExit("HTML missing L10 cockpit")
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
