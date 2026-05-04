import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_suppression_registry_has_schema_and_one_real_production_suppression():
    schema=load("operations/external_validation/e23_suppression_registry_schema.json")
    data=load("operations/external_validation/e23_suppression_registry.json")
    assert "do_not_contact" in schema["supported_reasons"]
    assert "manual_owner_suppression" in schema["supported_reasons"]
    assert data["production_suppressed_target_count"] == 1
    assert data["template_examples_included"] is False
    assert data["entries"][0]["real_suppression_evidence_fabricated"] is False
