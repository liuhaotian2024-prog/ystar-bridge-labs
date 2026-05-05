from office.mission_command.e37_evidence_route_gov_mcp_alignment import build_evidence_route_gov_mcp_alignment


def test_gov_mcp_alignment_is_read_only_and_blocks_execution():
    data = build_evidence_route_gov_mcp_alignment()
    assert data["inspection_mode"] == "read_only"
    assert data["summary"]["gov_mcp_files_modified"] is False
    assert data["summary"]["adapter_candidates"]
    assert data["summary"]["blocked_actions"]
    assert all(entry["owner_approval_required_before_execution"] is True for entry in data["entries"])
