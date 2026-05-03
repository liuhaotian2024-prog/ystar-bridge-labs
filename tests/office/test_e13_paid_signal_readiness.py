from office.mission_command.e13_evidence_records import build_evidence_record
from office.mission_command.e13_paid_signal_readiness import build_paid_signal_readiness_report


def test_e13_does_not_classify_public_evidence_as_validation_feedback():
    record = build_evidence_record(
        "ev1",
        "Agent Workflow Bottleneck Diagnosis",
        "https://example.com/pain",
        "public_forum_or_community",
        "agent workflow bottleneck governance pain",
    )
    report = build_paid_signal_readiness_report([record])
    path = next(item for item in report.path_results if item.opportunity_path == "Agent Workflow Bottleneck Diagnosis")
    assert path.evidence_router_allows_validation_feedback_claim is False


def test_e13_does_not_classify_readiness_as_revenue():
    record = build_evidence_record(
        "ev1",
        "Agent Workflow Bottleneck Diagnosis",
        "https://example.com/pricing",
        "public_pricing_page",
        "pricing package for consulting workflow audit",
    )
    report = build_paid_signal_readiness_report([record])
    path = next(item for item in report.path_results if item.opportunity_path == "Agent Workflow Bottleneck Diagnosis")
    assert path.evidence_router_allows_paid_signal_claim is False


def test_e13_compares_multiple_paths_before_choosing_default():
    records = [
        build_evidence_record("ev1", "Agent Workflow Bottleneck Diagnosis", "https://a.example", "public_blog_post", "market trend"),
        build_evidence_record("ev2", "Coding-Agent Governance Audit", "https://b.example", "public_forum_or_community", "coding agent governance pain bottleneck"),
        build_evidence_record("ev3", "Coding-Agent Governance Audit", "https://c.example", "public_pricing_page", "pricing package audit"),
        build_evidence_record("ev4", "Coding-Agent Governance Audit", "https://d.example", "public_marketplace_or_agency_page", "consulting agency substitute service"),
    ]
    report = build_paid_signal_readiness_report(records)
    assert len(report.path_results) >= 7
    assert report.top_path == "Coding-Agent Governance Audit"


def test_e13_counterfactual_gate_can_change_default():
    records = [
        build_evidence_record("ev1", "Coding-Agent Governance Audit", "https://b.example", "public_forum_or_community", "coding agent governance pain bottleneck"),
        build_evidence_record("ev2", "Coding-Agent Governance Audit", "https://c.example", "public_pricing_page", "pricing package audit"),
        build_evidence_record("ev3", "Coding-Agent Governance Audit", "https://d.example", "public_marketplace_or_agency_page", "consulting agency substitute service"),
    ]
    report = build_paid_signal_readiness_report(records, default_path="Agent Workflow Bottleneck Diagnosis")
    assert report.counterfactual_changed_default is True


def test_e13_paid_signal_readiness_requires_sufficient_evidence():
    weak = [
        build_evidence_record("ev1", "Agent Workflow Bottleneck Diagnosis", "https://a.example", "public_forum_or_community", "workflow bottleneck pain"),
    ]
    strong = [
        build_evidence_record("ev1", "Agent Workflow Bottleneck Diagnosis", "https://a.example", "public_forum_or_community", "workflow bottleneck pain"),
        build_evidence_record("ev2", "Agent Workflow Bottleneck Diagnosis", "https://b.example", "public_pricing_page", "pricing package diagnostic"),
        build_evidence_record("ev3", "Agent Workflow Bottleneck Diagnosis", "https://c.example", "public_marketplace_or_agency_page", "consulting agency substitute"),
    ]
    assert build_paid_signal_readiness_report(weak).paid_signal_readiness_rt1 > 0
    assert build_paid_signal_readiness_report(strong).paid_signal_readiness_rt1 == 0


def test_e13_blocked_no_evidence_keeps_residual_nonzero():
    report = build_paid_signal_readiness_report([])
    assert report.classification == "blocked_no_evidence"
    assert report.paid_signal_readiness_rt1 > 0
