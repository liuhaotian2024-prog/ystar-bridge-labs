from pathlib import Path

from office.mission_command.opportunity_synthesis_engine import (
    compare_generated_opportunities,
    generate_opportunities,
    summarize_opportunity_lenses,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_opportunity_synthesis_generates_multiple_lenses():
    summary = summarize_opportunity_lenses(REPO_ROOT)
    assert len(summary["lenses"]) >= 6
    assert "internal asset lens" in summary["lenses"]
    assert "external pain lens" in summary["lenses"]
    assert "budget/demand lens" in summary["lenses"] or len(summary["opportunities"]) >= 6


def test_opportunity_synthesis_does_not_collapse_to_founder_audit():
    opportunities = generate_opportunities(REPO_ROOT)
    titles = {item["title"] for item in opportunities}
    assert "Founder AI Workflow Audit / CEO Command Brief" in titles
    assert "Agent Workflow Bottleneck Diagnosis" in titles
    assert "Coding-Agent Governance Audit" in titles
    assert len(titles) >= 6


def test_generated_opportunities_include_required_fields():
    opportunity = generate_opportunities(REPO_ROOT)[0]
    for field in [
        "opportunity_id",
        "title",
        "generated_from_lens",
        "buyer",
        "pain",
        "internal_assets",
        "external_unknowns",
        "behavior_capability_required",
        "first_experiment",
        "approval_needed",
        "m_triangle_alignment",
        "owner_burden",
        "confidence",
        "missing_evidence",
    ]:
        assert field in opportunity


def test_compared_opportunities_have_default_candidate():
    opportunities = compare_generated_opportunities(REPO_ROOT)
    assert opportunities[0]["title"] in {
        "Founder AI Workflow Audit / CEO Command Brief",
        "Agent Workflow Bottleneck Diagnosis",
        "Coding-Agent Governance Audit",
    }
    assert opportunities[0]["method_score"] >= opportunities[-1]["method_score"]


def test_no_coo_invented():
    assert "COO" not in str(generate_opportunities(REPO_ROOT))
