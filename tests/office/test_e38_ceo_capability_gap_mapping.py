from office.mission_command.e38_ceo_capability_gap_mapping import build_ceo_capability_gap_mapping
from office.mission_command.e35_one_brain_integration_guard import get_artifact


def test_ceo_capability_gap_mapping_targets_repos_and_preserves_evidence_boundaries():
    mapping = build_ceo_capability_gap_mapping()
    assert mapping["gap_count"] >= 15
    assert mapping["external_tool_integration_occurred"] is False
    assert mapping["provider_api_execution_occurred"] is False
    assert mapping["customer_validation_claimed"] is False
    assert mapping["paid_signal_claimed"] is False
    targets = {gap["target_repo"] for gap in mapping["gaps"]}
    assert "bridge-labs" in targets
    assert "gov-mcp" in targets
    for gap in mapping["gaps"]:
        assert gap["frontier_capability_that_may_address_it"]
        assert gap["proposed_import_pattern"]
        assert gap["target_repo"] in {"bridge-labs", "Y-star-gov", "gov-mcp", "future repo", "no action"}
        assert gap["not_customer_validation"] is True
        assert gap["not_paid_signal"] is True


def test_ceo_brain_update_includes_frontier_capability_awareness():
    brain = get_artifact("e38_ceo_brain_public_evidence_update")
    summary = brain["frontier_capability_import_scan_summary"]
    assert summary["categories_inspected"] >= 10
    assert summary["external_integration_occurred"] is False
    assert brain["external_tool_integration_occurred"] is False
    assert brain["provider_api_execution_occurred"] is False
    assert brain["must_remain_blocked_until_owner_approval"]
