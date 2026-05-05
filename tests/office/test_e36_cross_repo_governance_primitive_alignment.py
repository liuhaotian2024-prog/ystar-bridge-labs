from office.mission_command.e36_cross_repo_governance_primitive_alignment import build_cross_repo_governance_primitive_alignment


def test_y_star_gov_alignment_is_read_only_and_complete():
    data = build_cross_repo_governance_primitive_alignment()
    assert data["inspection_mode"] == "read_only"
    assert len(data["entries"]) >= 60
    assert data["summary"]["Y-star-gov_files_modified"] is False
    assert data["summary"]["uses_existing_primitives"] > 0
    assert "candidate new Y-star-gov primitive" in {item for entry in data["entries"] for item in entry["alignment"]}
