from office.mission_command.e38_y_star_gov_alignment_after_evidence import build_y_star_gov_alignment_after_evidence


def test_y_star_gov_alignment_after_evidence_is_read_only():
    data = build_y_star_gov_alignment_after_evidence()
    assert data["inspection_mode"] == "read_only"
    assert data["summary"]["Y-star-gov_files_modified"] is False
    assert data["summary"]["primitives_used"]
    assert data["summary"]["risks"]
