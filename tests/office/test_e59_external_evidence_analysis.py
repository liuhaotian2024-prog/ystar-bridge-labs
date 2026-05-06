from office.mission_command.e59_external_evidence_analysis import run_external_evidence_analysis


def test_external_evidence_analysis_has_credibility_freshness_and_gap_labels():
    data = run_external_evidence_analysis()
    assert data["credibility_labels_present"] is True
    assert data["freshness_labels_present"] is True
    assert data["contradiction_gap_labels_present"] is True
    assert data["analyzed_atoms"]

