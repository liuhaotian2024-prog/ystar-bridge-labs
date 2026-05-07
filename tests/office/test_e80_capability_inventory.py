import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e80_capability_inventory_is_classified_after_discovery():
    inventory = _load("operations/external_validation/e80_whole_ecosystem_capability_inventory.json")

    assert inventory["method"] == "classification_after_discovered_capability_candidates_not_prompt_memory"
    assert inventory["capability_count"] > 1000
    assert inventory["repository_discovered_not_prompt_hinted_count"] > 0
    assert inventory["prompt_hinted_unverified_count"] > 0
    assert len(inventory["capability_domain_counts"]) >= 8
    assert "prompt_hint_unverified" in inventory["activation_state_counts"]


def test_e80_inventory_preserves_cross_repo_ownership_boundaries():
    inventory = _load("operations/external_validation/e80_whole_ecosystem_capability_inventory.json")
    owners = {cap["canonical_owner"] for cap in inventory["capabilities"]}

    assert "K9Audit" in owners
    assert "Y-star-gov" in owners
    assert "gov-mcp" in owners
    assert "bridge-labs" in owners
