from pathlib import Path

from office.mission_command.e13r_buyer_pain_evidence import (
    build_default_e13r_request,
    build_e13r_evidence_record,
    classify_e13r_quality,
    e13r_blocks_external_side_effects,
    public_evidence_can_be_validation_feedback,
    public_readiness_can_be_revenue,
    validate_e13r_request,
)
from office.mission_command.e13r_offer_revision import diagnose_e13_result, generate_revised_offer_candidates
from office.mission_command.e13r_owner_decision_packet import build_e13r_owner_decision_packet
from office.mission_command.e13r_readiness_gate import build_e13r_readiness_report


def test_e13r_loads_e13_result_and_detects_needs_offer_revision():
    diagnosis = diagnose_e13_result(Path("."))
    assert diagnosis.e13_classification == "needs_offer_revision"
    assert diagnosis.direct_buyer_pain_count == 0
    assert diagnosis.pricing_or_budget_count > 0


def test_e13r_refuses_e14_when_direct_buyer_pain_zero():
    report = build_e13r_readiness_report([])
    assert report.e14_entry_allowed is False
    assert report.paid_signal_readiness_rt1 == 1
    assert report.buyer_pain_evidence_rt1 == 1


def test_e13r_generates_multiple_revised_offer_candidates():
    candidates = generate_revised_offer_candidates()
    names = {item.offer_name for item in candidates}
    assert len(candidates) >= 5
    assert "48h Coding-Agent Governance Audit" in names
    assert "48h AI Agent Workflow Recovery Room" in names


def test_e13r_evidence_queries_target_buyer_pain_not_only_pricing():
    request = build_default_e13r_request().to_dict()
    assert validate_e13r_request(request) == []
    queries = " ".join(request["queries"]).lower()
    assert "unsafe code" in queries
    assert "broke production workflow" in queries
    assert len([query for query in request["queries"] if "pricing" in query.lower()]) < len(request["queries"])


def test_e13r_distinguishes_buyer_pain_from_pricing_and_substitute():
    assert classify_e13r_quality("public_buyer_pain_article", "AI agents broke production workflow and created governance risk") == "direct_buyer_pain"
    assert classify_e13r_quality("public_pricing_page", "pricing package $1500") == "pricing_or_budget"
    assert classify_e13r_quality("public_substitute_or_competitor_page", "AI governance audit service") == "substitute_or_comparable"


def test_e13r_paid_signal_ready_requires_pain_pricing_and_substitute():
    pain = build_e13r_evidence_record(
        "pain",
        "coding_agent_governance_audit",
        "https://example.com/pain",
        "public_buyer_pain_article",
        "coding agent generated unsafe code and created production governance risk",
        "buyer pain",
    )
    pricing = build_e13r_evidence_record(
        "pricing",
        "coding_agent_governance_audit",
        "https://example.com/pricing",
        "public_pricing_page",
        "pricing package cost $1500",
        "pricing",
    )
    substitute = build_e13r_evidence_record(
        "substitute",
        "coding_agent_governance_audit",
        "https://example.com/audit",
        "public_substitute_or_competitor_page",
        "AI governance audit service",
        "substitute",
    )
    incomplete = build_e13r_readiness_report([pain, pricing])
    assert incomplete.classification != "paid_signal_ready"
    complete = build_e13r_readiness_report([pain, pricing, substitute])
    assert complete.classification == "paid_signal_ready"
    assert complete.e14_entry_allowed is True


def test_e13r_public_evidence_is_not_validation_feedback_or_revenue():
    assert public_evidence_can_be_validation_feedback() is False
    assert public_readiness_can_be_revenue() is False


def test_e13r_blocks_all_external_side_effects():
    request = build_default_e13r_request().to_dict()
    for action in [
        "customer_contact",
        "email_or_message",
        "publication",
        "payment",
        "account_creation",
        "form_submission",
        "login",
        "core_brain_cieu_memory_writeback",
    ]:
        assert action in request["forbidden_actions"]
    assert e13r_blocks_external_side_effects() is True


def test_e13r_owner_packet_includes_exact_approval_boundary():
    report = build_e13r_readiness_report([])
    packet = build_e13r_owner_decision_packet(report)
    assert "does not approve outreach" in packet.exact_approval_boundary
    assert "Aiden autonomous sending" in packet.not_approved


def test_e13r_counterfactual_gate_can_choose_coding_agent_governance():
    records = [
        build_e13r_evidence_record("p", "coding_agent_governance_audit", "https://e/p", "public_buyer_pain_article", "unsafe code production risk", "pain"),
        build_e13r_evidence_record("b", "coding_agent_governance_audit", "https://e/b", "public_pricing_page", "pricing package $1000", "pricing"),
        build_e13r_evidence_record("s", "coding_agent_governance_audit", "https://e/s", "public_substitute_or_competitor_page", "AI governance audit service", "substitute"),
    ]
    report = build_e13r_readiness_report(records)
    assert report.top_revised_offer_id == "coding_agent_governance_audit"
    assert report.counterfactual_changed_default is True


def test_e13r_residual_stays_nonzero_when_evidence_insufficient():
    pain = build_e13r_evidence_record("p", "ai_agent_workflow_recovery_room", "https://e/p", "public_buyer_pain_article", "AI agents break in production workflow", "pain")
    report = build_e13r_readiness_report([pain])
    assert report.paid_signal_readiness_rt1 == 1


def test_e13r_repository_delivery_uses_host_side_bridge():
    request_path = Path("operations/repository_delivery/delivery_requests/e13r_offer_revision_delivery.json")
    assert request_path.as_posix().endswith("e13r_offer_revision_delivery.json")


def test_e13r_produces_one_host_bootstrap_command():
    command = "python3.11 /tmp/e13r_offer_revision_bootstrap.py"
    assert command.count("python3.11") == 1
    assert "&&" not in command
