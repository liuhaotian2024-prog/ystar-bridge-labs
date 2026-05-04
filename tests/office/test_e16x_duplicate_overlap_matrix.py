from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load() -> dict:
    return json.loads((ROOT / "operations/external_validation/e16x_duplicate_overlap_matrix.json").read_text())


def test_e16x_duplicate_matrix_covers_required_overlaps() -> None:
    overlaps = {item["overlap_id"]: item for item in load()["overlaps"]}
    required = {
        "e8_risk_model_vs_b2r_capability_domains",
        "e8_preflight_vs_action_authorization_router",
        "action_authorization_router_vs_c2_decision_control",
        "b2r_gov_mcp_contract_vs_c2_execution_control",
        "c2_c3_e15a_feedback_vs_e12_e14_feedback",
        "e15d_outbound_policy_vs_b2r_external_validation_message_domain",
        "e15d_adapter_contract_vs_real_gov_mcp_surface",
        "e15d_safety_guards_vs_e9_suppression_e8_stop_conditions",
        "e15d_send_gated_queue_vs_e15a_owner_console",
    }
    assert required <= set(overlaps)


def test_e16x_duplicate_matrix_flags_harmful_parallel_logic() -> None:
    overlaps = load()["overlaps"]
    high_risk = [item for item in overlaps if item["risk_level"] == "high"]
    assert any(item["duplicate_type"] == "harmful_parallel_logic" for item in high_risk)
    assert "e15d_adapter_contract_vs_real_gov_mcp_surface" in load()["highest_risk_overlaps"]
