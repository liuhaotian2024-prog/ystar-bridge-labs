import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e80_symbol_artifact_test_dependency_and_provenance_indexes_exist():
    symbols = _load("operations/external_validation/e80_python_symbol_index.json")
    artifacts = _load("operations/external_validation/e80_generated_artifact_index.json")
    tests = _load("operations/external_validation/e80_test_index.json")
    deps = _load("operations/external_validation/e80_import_dependency_map.json")
    provenance = _load("operations/external_validation/e80_artifact_provenance_map.json")
    raw = _load("operations/external_validation/e80_raw_file_inventory.json")

    assert symbols["python_file_count"] > 1000
    assert symbols["total_functions"] > 1000
    assert artifacts["artifact_count"] > 1000
    assert tests["test_file_count"] > 100
    assert tests["assert_count"] > 100
    assert deps["module_count"] > 100
    assert deps["ceo_brain_adapter"]["path"] == "office/mission_command/e46b_ceo_brain_adapter.py"
    assert provenance["record_count"] == raw["bridge_labs_tracked_file_count"]


def test_e80_indexes_have_raw_discovery_phase_markers():
    for rel in [
        "operations/external_validation/e80_python_symbol_index.json",
        "operations/external_validation/e80_generated_artifact_index.json",
        "operations/external_validation/e80_test_index.json",
        "operations/external_validation/e80_import_dependency_map.json",
        "operations/external_validation/e80_artifact_provenance_map.json",
    ]:
        assert _load(rel)["raw_discovery_phase"] is True
