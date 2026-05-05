from office.mission_command.e36_gov_mcp_execution_boundary_alignment import build_gov_mcp_execution_boundary_alignment


def test_gov_mcp_alignment_is_read_only_and_blocks_execution():
    data = build_gov_mcp_execution_boundary_alignment()
    assert data["inspection_mode"] == "read_only"
    assert len(data["entries"]) >= 60
    assert data["summary"]["gov_mcp_files_modified"] is False
    assert data["summary"]["labs_only_or_no_execution_yet"] > 0
    assert data["summary"]["blocked_action_count"] > 0
    assert all(entry["owner_approval_required_before_execution"] is True for entry in data["entries"])
