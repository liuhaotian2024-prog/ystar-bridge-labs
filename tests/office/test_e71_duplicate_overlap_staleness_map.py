import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e71_duplicate_overlap_map_blocks_stale_canonical_promotion():
    data = json.loads((ROOT / "operations/external_validation/e71_legacy_duplicate_overlap_staleness_map.json").read_text())
    assert len(data["rows"]) >= 10
    assert data["old_assets_do_not_override_current_state"] is True
    decisions = {row["old_asset"]: row for row in data["rows"]}
    assert decisions["E24 route portfolio"]["relationship"] == "complementary"
    assert decisions["K9Audit CIEU spec"]["relationship"] == "stronger_for_causal_audit_detail"
    assert decisions["legacy CEO brain"]["relationship"] == "stale_if_promoted_directly"
    assert decisions["ystar-company old sales assets"]["relationship"] == "dangerous_if_promoted_directly"
    assert data["external_action_allowed"] is False

