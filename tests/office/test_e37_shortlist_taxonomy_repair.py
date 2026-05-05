from office.mission_command.e37_shortlist_taxonomy_repair import build_shortlist_taxonomy_repair


def test_shortlist_taxonomy_repair_detects_and_repairs_mismatches():
    data = build_shortlist_taxonomy_repair()
    assert data["repair_status"] == "passed"
    assert data["mismatches_found"] > 0
    assert data["evidence_route_design_unblocked"] is True
    assert data["final_product_selected"] is False
    issue_types = {issue for row in data["detected_taxonomy_issues"] for issue in row["issue_types"]}
    assert "AI productivity label used for non-AI-productivity opportunity" in issue_types
