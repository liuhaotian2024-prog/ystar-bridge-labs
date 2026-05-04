import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_evidence_needs_drive_public_observation():
    data = json.loads((ROOT / "operations/external_validation/e31_ceo_kg_real_world_evidence_needs.json").read_text())
    assert data["selected_route"] == "paid_readiness_review_signal_package"
    assert data["evidence_need_count"] == 4
    assert "unsupported claims are excluded" in data["package_update_rule"].lower()
