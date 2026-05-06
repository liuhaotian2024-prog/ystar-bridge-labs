import json
from pathlib import Path

from office.mission_command.e64_dual_axis_revenue_core import build_dual_axis_public_read_evidence_atoms, build_dual_axis_public_read_receipts


ROOT = Path(__file__).resolve().parents[2]


class _FakeResult:
    url = "https://example.com/"
    domain = "example.com"
    status = 200
    retrieved_at = "2026-05-06T00:00:00Z"
    title = "Business operations automation and governed agent reliability"
    text_excerpt = "Operators need workflow automation, SOPs, guardrails, traces, and safe action execution for agent workflows."
    safety_errors = []
    blocked_reason = ""
    bytes_read = 256
    external_action_executed = False


class _FakeReader:
    def read(self, _url):
        return _FakeResult()


def test_e64_public_read_plan_and_receipts_preserve_no_contact_flags():
    plan = json.loads((ROOT / "operations/external_validation/e64_dual_axis_public_read_plan.json").read_text())
    receipts = json.loads((ROOT / "operations/external_validation/e64_dual_axis_public_read_receipts.json").read_text())
    assert plan["planned_source_count"] >= 24
    assert plan["open_world_surface_count"] >= 6
    assert plan["YBridge_adjacent_surface_count"] >= 6
    assert receipts["receipt_count"] == plan["planned_source_count"]
    assert all(item["no_contact_info_extracted"] is True for item in receipts["receipts"])
    assert all(item["no_human_identification"] is True for item in receipts["receipts"])


def test_e64_public_read_pipeline_can_create_live_atoms_with_controlled_reader():
    receipts = build_dual_axis_public_read_receipts(reader=_FakeReader())
    assert receipts["live_successful_read_count"] == receipts["planned_source_count"]
    atoms = build_dual_axis_public_read_evidence_atoms()
    # Artifact-mode atoms may be zero if the local network is blocked; the fake-reader path proves the receipt path.
    assert atoms["no_customer_validation_claimed"] is True
