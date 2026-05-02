from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "integration"


def test_duplicate_cluster_report_has_evidence_backed_clusters():
    text = (REPORTS / "e11_duplicate_overlap_cluster_report.md").read_text(encoding="utf-8")
    assert "clusters_found_from_evidence: yes" in text
    assert "cluster_target_lifecycle" in text
    assert "cluster_action_authorization_chain" in text


def test_duplicate_cluster_report_does_not_use_only_prompt_seed_categories():
    text = (REPORTS / "e11_duplicate_overlap_cluster_report.md").read_text(encoding="utf-8")
    assert "prompt_seed_categories_used_as_search_terms_only: yes" in text
    assert "cluster_incubated_company_runtime" in text


def test_conflict_matrix_flags_high_risk_evidence_and_approval_risks():
    text = (REPORTS / "e11_conflict_risk_matrix.md").read_text(encoding="utf-8")
    assert "E10 proposed target seed is treated as contact approval" in text
    assert "Public target discovery evidence is treated as validation feedback or paid signal" in text
    assert "Bridge-labs execution gate bypasses Y-star-gov/gov-mcp semantics" in text

