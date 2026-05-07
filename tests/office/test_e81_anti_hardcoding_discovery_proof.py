import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e81_contract_is_derived_from_e80_repository_evidence_not_prompt_hints():
    proof = _load("operations/external_validation/e81_anti_hardcoding_discovery_proof.json")

    assert proof["E80_capability_candidates_loaded"] > 1000
    assert proof["capabilities_considered_for_CEO_cognition"] > 100
    assert proof["capabilities_selected_from_repository_evidence"] > 0
    assert proof["evidence_paths_for_every_selected_capability_present"] is True
    assert proof["loop_stage_prompt_invented_count"] == 0
    assert proof["anti_hardcoding_rule_passed"] is True


def test_e81_prompt_hints_and_repository_discovered_capabilities_are_reported():
    proof = _load("operations/external_validation/e81_anti_hardcoding_discovery_proof.json")

    assert "capabilities_named_in_prompt_but_not_verified" in proof
    assert "repository_discovered_capabilities_not_named_in_prompt_but_included" in proof
    assert proof["selected_capabilities"]
    assert all(item["evidence_paths"] for item in proof["selected_capabilities"])
