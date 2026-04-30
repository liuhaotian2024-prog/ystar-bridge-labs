import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCHEDULER_OUT = ROOT / "l7_labs_team_self_work_scheduler"
SCRIPT_DIR = ROOT / "scripts/l7_labs_office_web"
RUNNER = ROOT / "scripts/run_l7_labs_office_web.sh"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SCRIPT_DIR))

from l7_labs_team_self_work_scheduler.capability_classifier import classify_work_item  # noqa: E402
from l7_labs_team_self_work_scheduler.scheduler import run_bounded, run_once, scheduler_status  # noqa: E402
from l7_labs_team_self_work_scheduler.work_item_loader import select_eligible_work_items  # noqa: E402
from office_web_builder import build  # noqa: E402
from whiteboard_store import PACKET_ROOT, create_work_item, load_agent_replies, load_completion_reports  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def build_runtime():
    build()


@pytest.fixture()
def packet_root():
    root = PACKET_ROOT / "_test_l7_6_packets"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    yield root
    if root.exists():
        shutil.rmtree(root)


def test_classifier_allows_internal_offer_refinement():
    decision = classify_work_item("refine offer package and produce owner review packet locally")
    assert decision["classification"] == "autonomous_internal_allowed"
    assert decision["autonomous_allowed"] is True
    assert decision["external_side_effects"] is False


def test_classifier_requires_approval_for_email_or_customer_contact():
    decision = classify_work_item("send email to customer and contact buyer")
    assert decision["classification"] == "approval_required_external_action"
    assert decision["approval_required"] is True
    assert decision["external_side_effects"] is True


def test_classifier_ignores_explicit_no_go_boundary_text():
    decision = classify_work_item("refine offer package locally. Do not send email or contact customers.")
    assert decision["classification"] == "autonomous_internal_allowed"
    assert decision["external_side_effects"] is False


def test_classifier_requires_approval_for_core_writeback():
    decision = classify_work_item("perform actual memory writeback and canonical strategy update")
    assert decision["classification"] == "approval_required_core_writeback"
    assert decision["approval_required"] is True
    assert decision["core_writeback"] is True


def test_scheduler_selects_pending_work_item(packet_root):
    item = create_work_item(
        "Refine offer package",
        "refine offer package and improve delivery workflow locally",
        None,
        packet_root=packet_root,
    )
    selected = select_eligible_work_items(packet_root, limit=1)
    assert selected[0]["work_item_id"] == item["work_item_id"]


def test_scheduler_respects_cycle_limit(packet_root):
    create_work_item("Refine offer", "refine offer package locally", None, packet_root=packet_root)
    result = run_bounded(packet_root=packet_root, max_work_items=1, max_cycles=1)
    assert result["ok"] is True
    assert result["results"][0]["cycles_run"] == 1


def test_scheduler_writes_progress_heartbeats(packet_root):
    create_work_item("Improve delivery workflow", "improve delivery workflow with internal analysis", None, packet_root=packet_root)
    run_once(packet_root=packet_root, max_cycles=1)
    assert list((packet_root / "progress_heartbeats").glob("*.json"))


def test_scheduler_writes_agent_replies(packet_root):
    create_work_item("Compare customer segments", "compare customer segments internally", None, packet_root=packet_root)
    run_once(packet_root=packet_root, max_cycles=1)
    assert load_agent_replies(packet_root)


def test_scheduler_generates_completion_report(packet_root):
    create_work_item("Owner review packet", "produce owner review packet locally", None, packet_root=packet_root)
    run_once(packet_root=packet_root, max_cycles=1)
    assert load_completion_reports(packet_root)


def test_scheduler_creates_approval_interrupt_for_external_action(packet_root):
    create_work_item("Send customer email", "send email to customer", None, packet_root=packet_root)
    result = run_once(packet_root=packet_root, max_cycles=1)
    assert result["status"] == "interrupted"
    assert result["approval_interrupt"]["scheduler_stopped"] is True
    assert list((packet_root / "approval_interrupts").glob("*.json"))


def test_scheduler_does_not_execute_external_side_effects(packet_root):
    create_work_item("Publish update", "publish content externally", None, packet_root=packet_root)
    result = run_once(packet_root=packet_root, max_cycles=1)
    assert result["approval_interrupt"]["external_side_effects_executed"] is False
    assert result["approval_interrupt"]["core_writeback_executed"] is False


def test_office_api_scheduler_status():
    source = (SCRIPT_DIR / "office_web_server.py").read_text(encoding="utf-8")
    for endpoint in [
        "/api/scheduler/status",
        "/api/scheduler/run_once",
        "/api/scheduler/run_bounded",
        "/api/autonomous_runs",
        "/api/progress_heartbeats",
        "/api/approval_interrupts",
    ]:
        assert endpoint in source
    status = scheduler_status()
    assert status["scheduler_ready"] is True


def test_office_api_run_once_or_bounded(packet_root):
    create_work_item("Summarize local packets", "summarize existing local packets", None, packet_root=packet_root)
    result = run_bounded(packet_root=packet_root, max_work_items=1, max_cycles=1)
    assert result["ok"] is True
    assert result["items_processed"] == 1


def test_runner_build_status_demo_smoke():
    runner_source = RUNNER.read_text(encoding="utf-8")
    for mode in ["build", "status", "demo", "smoke", "serve"]:
        assert mode in runner_source
    assert "L7.6 scheduler ready" in runner_source
    assert "/api/scheduler/status" in runner_source


def test_scheduler_outputs_and_no_secret_serialization():
    required = [
        "l7_6_summary.json",
        "l7_6_summary.md",
        "whiteboard_runtime_state.json",
        "whiteboard_no_action_receipt.json",
        "README.md",
        "demo_scenarios/demo_autonomous_first_cash_path_offer_package.json",
        "demo_scenarios/demo_autonomous_first_cash_path_offer_package.md",
    ]
    for relative in required:
        assert (SCHEDULER_OUT / relative).exists()
    summary = json.loads((SCHEDULER_OUT / "l7_6_summary.json").read_text(encoding="utf-8"))
    assert summary["scheduler_created"] is True
    assert summary["coo_invented"] is False
    receipt = json.loads((SCHEDULER_OUT / "whiteboard_no_action_receipt.json").read_text(encoding="utf-8"))
    assert receipt["customer_contacted"] is False
    scoped_text = "\n".join(path.read_text(encoding="utf-8") for path in SCHEDULER_OUT.rglob("*") if path.is_file())
    lowered = scoped_text.lower()
    assert "tvly-" not in lowered
    assert "bearer " not in lowered
    assert "api_key=" not in lowered


def test_runner_build_and_status_modes_are_safe():
    for mode in ["build", "status"]:
        result = subprocess.run(
            ["bash", str(RUNNER), "--mode", mode],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
            timeout=30,
        )
        assert "error" not in result.stderr.lower()
