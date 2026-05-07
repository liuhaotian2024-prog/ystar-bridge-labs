import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e78_evidence_synthesis_answers_required_sections():
    synthesis = json.loads((ROOT / "operations/external_validation/e78_l3_evidence_synthesis.json").read_text())

    for key in [
        "buyer_problem_evidence",
        "product_offer_evidence",
        "CIEU_audit_module_relevance",
        "first_cash_route_implications",
        "pricing_packaging_public_analogs",
        "contradictions_and_weak_signals",
        "evidence_quality",
        "what_remains_unproven",
    ]:
        assert key in synthesis
    assert synthesis["buyer_problem_evidence"]["finding"].startswith("Public evidence strengthens")
    assert synthesis["evidence_quality"]["classification"] == "L3_public_read_non_contact_public_proxy_evidence"
    assert "no customer conversations" in synthesis["evidence_quality"]["limits"]

