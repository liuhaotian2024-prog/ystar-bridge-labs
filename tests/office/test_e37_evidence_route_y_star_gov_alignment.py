from office.mission_command.e37_evidence_route_y_star_gov_alignment import build_evidence_route_y_star_gov_alignment


def test_y_star_gov_alignment_is_read_only():
    data = build_evidence_route_y_star_gov_alignment()
    assert data["inspection_mode"] == "read_only"
    assert data["summary"]["Y-star-gov_files_modified"] is False
    assert data["summary"]["primitives_used"]
    assert "evidence-boundary risk" in data["summary"]["risks"]
