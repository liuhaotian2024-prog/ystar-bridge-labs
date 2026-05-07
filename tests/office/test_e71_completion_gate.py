import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e71_completion_gate_passes_for_legacy_resurrection():
    data = json.loads((ROOT / "operations/external_validation/e71_completion_gate_result.json").read_text())
    assert data["gate_passed"] is True
    assert data["final_status"] == "e71_legacy_high_value_asset_resurrection_completed"
    assert data["top_cluster"] == "k9_cieu_hash_chain_spec_cluster"
    assert data["promoted_count"] > 0
    assert data["quarantined_count"] > 0
    assert data["recommended_next_milestone"] == "E72_integrate_K9_CIEU_hash_chain_context_into_CIEU_audit_module"
    assert data["read_only_repo_status_unchanged"] is True
    assert data["external_action_allowed"] is False

