import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e81_ystar_gov_surface_map_exists_and_is_read_only():
    surface = _load("operations/external_validation/e81_ystar_gov_enforcement_surface_map.json")

    assert surface["surface_count"] > 0
    assert surface["Y_star_gov_expected_base_provided"] is False
    assert surface["Y_star_gov_mutated"] is False
    assert surface["mutation_policy"] == "no_mutation_without_explicit_Y_star_gov_expected_base"


def test_e81_ystar_gov_surface_map_finds_enforcement_roles():
    surface = _load("operations/external_validation/e81_ystar_gov_enforcement_surface_map.json")
    roles = surface["role_counts"]

    assert any(role in roles for role in ["hook_contract_enforcement", "pre_action_packet_validation", "ALLOW_DENY_ESCALATE_decision"])
    assert any(item["supports_pre_action_check"] for item in surface["surfaces"])
    assert any(item["bridge_labs_can_safely_sync_contract_to_it"] for item in surface["surfaces"])
