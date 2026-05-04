import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_suppression_proof_uses_fixture_only_and_blocks():
    data = load("operations/external_validation/e22_suppression_proof.json")
    assert data["proof_type"] == "local_test_fixture_only_not_production_target"
    assert data["suppressed_target_passed_dry_run"] is False
    assert data["production_artifact_uses_synthetic_target"] is False
