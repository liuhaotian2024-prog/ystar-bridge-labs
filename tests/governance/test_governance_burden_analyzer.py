from pathlib import Path

from office.aiden_meeting_room.governance_burden_analyzer import (
    analyze_governance_burden,
    burden_findings,
    permission_tier_replacement_findings,
)
from office.aiden_meeting_room.repo_evidence_index import build_repo_evidence_index


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_extracts_admin_burden_from_agents():
    index = build_repo_evidence_index(REPO_ROOT)
    findings = burden_findings(index)
    titles = " ".join(finding.title for finding in findings)
    assert "12-layer" in titles or "5-tuple" in titles
    assert "Nightly" in titles or "reporting" in titles


def test_core_governance_rules_are_not_weakened():
    index = build_repo_evidence_index(REPO_ROOT)
    findings = analyze_governance_burden(index)
    core = [finding for finding in findings if finding.classification == "core_constitutional"]
    assert core
    assert "deterministic" in core[0].reason or "governance" in core[0].title.lower()


def test_permission_tier_replacements_are_identified():
    index = build_repo_evidence_index(REPO_ROOT)
    findings = permission_tier_replacement_findings(index)
    text = " ".join(finding.title for finding in findings)
    assert "choice" in text.lower() or "Social" in text

