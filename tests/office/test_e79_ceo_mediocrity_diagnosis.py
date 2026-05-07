import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e79_acknowledges_e78_process_success_but_strategic_weakness():
    diagnosis = _load("operations/external_validation/e79_ceo_mediocrity_diagnosis.json")
    gate = _load("operations/external_validation/e79_ceo_judgment_quality_gate.json")

    assert "owner-approved L3 public-read pilot executed safely" in diagnosis["E78_process_success"]
    assert diagnosis["diagnosis"] == "E78 proved process safety but not founder-grade strategic judgment."
    assert gate["E78_classification"]["process_execution"] == "acceptable_process_execution"
    assert gate["E78_classification"]["strategic_sharpness"] == "insufficient_strategic_sharpness"
    assert gate["E78_classification"]["passed"] is False


def test_e79_mediocrity_diagnosis_names_root_causes_and_required_changes():
    diagnosis = _load("operations/external_validation/e79_ceo_mediocrity_diagnosis.json")

    assert "failure to isolate a painful wedge" in diagnosis["generic_output_symptoms"]
    assert "completion-gate optimized instead of insight-gate optimized" in diagnosis["root_causes"]
    assert "recent-memory overdependence" in diagnosis["root_causes"]
    assert "CEO must mark generic conclusions as failures" in diagnosis["what_must_change"]
    assert diagnosis["no_external_action"] is True
