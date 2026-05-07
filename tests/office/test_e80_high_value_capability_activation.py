import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e80_high_value_activation_plan_uses_repository_evidence_without_new_brain():
    plan = _load("operations/external_validation/e80_high_value_capability_activation_plan.json")

    assert plan["activation_basis"] == "selected_after_repository_discovery_and_activation_gap_classification"
    assert plan["activation_count"] > 0
    assert plan["not_a_parallel_CEO_brain"] is True
    assert plan["external_action_allowed"] is False
    assert all(item["source_evidence"]["paths"] or item["source_evidence"]["symbols"] for item in plan["activated_capabilities"])


def test_e80_activation_plan_blocks_duplicate_core_implementations():
    plan = _load("operations/external_validation/e80_high_value_capability_activation_plan.json")

    assert "production_CIEU_ledger_in_bridge_labs" in plan["blocked_capabilities"]
    assert "duplicate_Y_star_gov_governance_engine" in plan["blocked_capabilities"]
    assert "duplicate_gov_mcp_executor" in plan["blocked_capabilities"]
