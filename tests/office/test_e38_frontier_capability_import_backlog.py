from office.mission_command.e35_one_brain_integration_guard import get_artifact


def test_frontier_capability_import_backlog_is_prepared_only_and_layered():
    backlog = get_artifact("e38_frontier_capability_import_backlog")
    summary = backlog["summary"]
    assert backlog["item_count"] >= 10
    assert summary["bridge_labs_items"] >= 5
    assert summary["Y-star-gov_primitive_proposal_items"] >= 1
    assert summary["gov_mcp_adapter_proposal_items"] >= 1
    assert summary["owner_decision_items"] >= 1
    assert summary["external_integrations_implemented"] == 0
    assert backlog["provider_api_execution_occurred"] is False
    assert backlog["customer_validation_claimed"] is False
    assert backlog["paid_signal_claimed"] is False
    for item in backlog["items"]:
        assert item["no_rebuild_check"] is True
        assert item["external_side_effect"] is False
        assert item["status"] == "prepared_only_not_implemented"
        assert item["repo_target"] in {"bridge-labs", "Y-star-gov", "gov-mcp", "future repo"}
        if item["repo_target"] in {"Y-star-gov", "gov-mcp"}:
            assert "proposal" in item["proposed_implementation_type"]
