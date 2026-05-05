import json
from pathlib import Path

from office.mission_command.e35_cross_repo_governance_execution_alignment import build_cross_repo_governance_execution_alignment


ROOT = Path(__file__).resolve().parents[2]


def test_cross_repo_alignment_keeps_repo_roles_separate():
    artifact = build_cross_repo_governance_execution_alignment()
    assert artifact["alignment_status"] == "passed"
    assert artifact["repos_inspected"]["Y-star-gov"]["inspection_mode"] == "read_only"
    assert artifact["repos_inspected"]["gov-mcp"]["inspection_mode"] == "read_only"
    roles = artifact["repo_role_map"]
    assert "IntentContract" in roles["Y-star-gov"]["owns"]
    assert "gov_check / gov_enforce MCP tool boundary" in roles["gov-mcp"]["owns"]
    assert "CEO brain and CEO KG deltas" in roles["ystar-bridge-labs"]["owns"]
    no_conflict = artifact["no_conflict_result"]
    assert no_conflict["duplicate_governance_kernel_created"] is False
    assert no_conflict["duplicate_mcp_execution_layer_created"] is False
    assert no_conflict["duplicate_cieu_czl_contract_semantics_created"] is False
    assert no_conflict["labs_ceo_brain_remained_strategy_opportunity_layer"] is True


def test_alignment_contains_primitive_and_execution_mappings():
    artifact = build_cross_repo_governance_execution_alignment()
    assert artifact["governance_primitive_alignment"]
    assert artifact["gov_mcp_execution_alignment"]
    assert any(item["classification"] == "existing IntentContract primitive" for item in artifact["governance_primitive_alignment"])
    assert any(item["classification"] == "must remain blocked until owner approval" for item in artifact["gov_mcp_execution_alignment"])
    assert artifact["external_side_effects"]["customer_contact_occurred"] is False
    assert artifact["external_side_effects"]["provider_api_called"] is False
    assert artifact["no_conflict_result"]["product_answer_hardcoded"] is False


def test_ceo_brain_records_cross_repo_awareness():
    brain = json.loads((ROOT / "operations/external_validation/e35_ceo_brain_unified_six_dimensional_update.json").read_text())
    awareness = brain["cross_repo_awareness"]
    assert awareness["Y-star-gov_role"].startswith("governance kernel")
    assert awareness["gov-mcp_role"].startswith("execution boundary")
    assert awareness["future_labs_outputs_require_governance_primitive_alignment"] is True
    assert awareness["future_labs_routes_require_gov_mcp_execution_boundary_alignment"] is True
    assert awareness["labs_artifacts_may_not_claim_runtime_authority_without_y_star_gov_or_gov_mcp_evidence"] is True
