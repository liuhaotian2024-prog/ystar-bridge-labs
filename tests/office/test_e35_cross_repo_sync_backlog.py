from office.mission_command.e35_cross_repo_sync_backlog import build_cross_repo_sync_backlog


def test_cross_repo_sync_backlog_is_targeted_and_safe():
    backlog = build_cross_repo_sync_backlog()
    summary = backlog["summary"]
    assert backlog["backlog_status"] == "created_targeted_followups_only"
    assert summary["sync_items"] >= 8
    assert summary["y_star_gov_items"] >= 1
    assert summary["gov_mcp_items"] >= 1
    assert summary["bridge_labs_only_items"] >= 1
    assert summary["owner_decision_items"] >= 1
    assert summary["external_side_effects_required"] is False
    assert backlog["no_y_star_gov_files_modified"] is True
    assert backlog["no_gov_mcp_files_modified"] is True


def test_backlog_blocks_execution_without_owner_and_boundary_alignment():
    backlog = build_cross_repo_sync_backlog()
    blocked = [item for item in backlog["items"] if item["current_status"] == "blocked"]
    assert blocked
    assert any(item["proposed_action"] == "owner decision required" for item in blocked)
    assert any(item["affected_repo"] == "multiple" for item in backlog["items"])
    for item in backlog["items"]:
        assert item["can_be_done_without_external_side_effects"] is True
