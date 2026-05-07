import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e79_produces_multiple_non_banal_theses_and_required_variants():
    thesis = _load("operations/external_validation/e79_non_banal_strategic_thesis.json")
    theses = thesis["theses"]

    assert thesis["thesis_count"] >= 5
    assert any(item.get("contrarian") for item in theses)
    assert any(item.get("argues_against_leading_with_ai_governance") for item in theses)
    assert any("founder/operator" in item["target_buyer"] for item in theses)
    assert any("control room" in item["one_sentence_claim"].lower() or "control-room" in item["how_blueprint_fits"].lower() for item in theses)
    assert any("audit-readiness" in item["one_sentence_claim"].lower() or "audit-readiness" in item["likely_first_paid_package"].lower() for item in theses)


def test_selected_thesis_is_specific_falsifiable_and_not_generic():
    thesis = _load("operations/external_validation/e79_non_banal_strategic_thesis.json")
    selected = thesis["selected_primary_thesis"]

    assert selected["thesis_id"] == "T1_founder_operator_agent_ops_control_review"
    assert "do not first buy governance" in selected["one_sentence_claim"]
    assert selected["target_buyer"]
    assert selected["trigger_event"]
    assert selected["painful_problem"]
    assert selected["why_now"]
    assert selected["why_existing_alternatives_are_insufficient"]
    assert selected["falsification_question"]
    assert selected["evidence_would_kill"]
    assert selected["evidence_would_strengthen"]
    assert selected["quality_gate"]["passed"] is True

