import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e71_self_bootstrap_awareness_requires_legacy_check_before_new_work():
    data = json.loads((ROOT / "operations/external_validation/e71_self_bootstrap_legacy_asset_awareness_update.json").read_text())
    assert data["CEO_should_consider_resurrected_assets_before_new_code"] is True
    assert data["Codex_job_proposals_should_check_legacy_registry_first"] is True
    assert data["skill_discovery_should_check_local_legacy_assets_first"] is True
    assert data["stale_quarantined_assets_blocked"] is True
    assert data["promotion_gated_assets_can_become_future_capability_candidates"] is True
    assert data["external_action_allowed"] is False

