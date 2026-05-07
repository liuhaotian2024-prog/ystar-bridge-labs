import json
from pathlib import Path

from office.mission_command.e79_ceo_strategic_judgment_upgrade import evaluate_ceo_output_quality


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e79_quality_gate_passes_selected_thesis_and_fails_generic_output():
    gate = _load("operations/external_validation/e79_ceo_judgment_quality_gate.json")

    assert gate["gate_passed_for_E79"] is True
    assert gate["E79_selected_thesis_quality"]["passed"] is True
    assert gate["generic_output_example"]["result"]["passed"] is False
    assert "could_have_been_written_without_project_artifacts" in gate["generic_output_example"]["result"]["failure_reasons"]


def test_quality_gate_function_rejects_banal_market_summary():
    result = evaluate_ceo_output_quality({
        "one_sentence_claim": "AI teams need better governance and observability",
        "generic_only": True,
    })

    assert result["passed"] is False
    assert "missing_target_buyer" in result["failure_reasons"]
    assert "missing_trigger_event" in result["failure_reasons"]


def test_quality_gate_has_failure_rules_against_construction_drift():
    gate = _load("operations/external_validation/e79_ceo_judgment_quality_gate.json")

    assert "fails_if_recommends_more_construction_when_real_work_is_possible" in gate["failure_rules"]
    assert "fails_if_safety_language_replaces_strategic_judgment" in gate["failure_rules"]
    assert gate["E78_classification"]["classification"] == "process_success_but_requires_E79_strategic_correction_before_L4_packet_is_trusted"

