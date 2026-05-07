import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e80_capability_candidates_are_discovered_from_multiple_repository_signals():
    candidates = _load("operations/external_validation/e80_discovered_capability_candidates.json")

    assert candidates["candidate_count"] > 1000
    assert candidates["repository_discovered_count"] > 100
    assert candidates["prompt_hint_used_count"] > 0
    assert set(candidates["signals_used"]) == {
        "path_signal",
        "symbol_signal",
        "content_signal",
        "test_signal",
        "dependency_signal",
        "cross_repo_owner_signal",
    }


def test_e80_candidates_include_repository_discovered_non_prompt_capabilities():
    candidates = _load("operations/external_validation/e80_discovered_capability_candidates.json")

    repository_discovered = [item for item in candidates["candidates"] if item["repository_discovered"]]
    assert repository_discovered
    assert any("test_signal" in item["discovered_from"] or "symbol_signal" in item["discovered_from"] for item in repository_discovered)
    assert all(item["evidence_paths"] or item["dependency_relationships"] for item in candidates["candidates"][:50])
