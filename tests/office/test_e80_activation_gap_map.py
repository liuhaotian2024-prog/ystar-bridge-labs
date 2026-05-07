import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e80_activation_gap_map_has_required_buckets():
    gap = _load("operations/external_validation/e80_capability_activation_gap_map.json")

    for bucket in [
        "active_and_useful",
        "active_but_shallow",
        "readback_only",
        "dormant_high_value",
        "dormant_low_value",
        "design_only",
        "duplicate_conflicting",
        "stale_quarantined",
        "prompt_hinted_but_unverified",
        "repository_discovered_but_previously_ignored",
    ]:
        assert bucket in gap["bucket_counts"]

    assert gap["bucket_counts"]["repository_discovered_but_previously_ignored"] > 0
    assert gap["high_value_dormant_or_shallow_activation_targets"]


def test_e80_gap_map_records_how_high_value_assets_enter_cognition_loop():
    gap = _load("operations/external_validation/e80_capability_activation_gap_map.json")

    target = gap["high_value_dormant_or_shallow_activation_targets"][0]
    assert target["current_CEO_failure_addressed"]
    assert target["where_enters_CEO_cognition_loop"]
    assert target["activation_mode"]
    assert target["test_required"].endswith("test_e80_high_value_capability_activation.py")
