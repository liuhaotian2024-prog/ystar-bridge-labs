import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_ceo_strategy_control_room_is_owner_facing_and_multi_path():
    data = json.loads((ROOT / "operations/external_validation/e32_ceo_strategy_control_room.json").read_text())
    assert data["researched_source_count"] == 12
    assert data["recommended_primary_path"] == "path_paid_readiness_review_service"
    assert "path_governance_evidence_audit_pack" in data["backup_paths"]
    assert "customer contact" in data["blocked_real_world_actions"]
    assert data["owner_discussion_questions"]
