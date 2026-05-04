import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_open_monetization_paths_are_multi_path_and_evidence_grounded():
    data = json.loads((ROOT / "operations/external_validation/e32_open_monetization_paths.json").read_text())
    assert data["monetization_path_count"] >= 8
    paths = {p["path_id"]: p for p in data["paths"]}
    assert "path_paid_readiness_review_service" in paths
    assert "path_governance_evidence_audit_pack" in paths
    assert "path_ceo_agent_strategy_runtime_product" in paths
    assert all(p["evidence_supporting_it"] for p in data["paths"])
