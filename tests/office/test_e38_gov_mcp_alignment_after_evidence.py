from office.mission_command.e38_gov_mcp_alignment_after_evidence import build_gov_mcp_alignment_after_evidence


def test_gov_mcp_alignment_after_evidence_blocks_execution():
    data = build_gov_mcp_alignment_after_evidence()
    assert data["inspection_mode"] == "read_only"
    assert data["summary"]["gov_mcp_files_modified"] is False
    assert data["summary"]["adapter_candidates"]
    assert data["summary"]["blocked_actions"]
