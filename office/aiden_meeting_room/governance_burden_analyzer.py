from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .repo_evidence_index import RepoEvidenceIndex


@dataclass(frozen=True)
class GovernanceFinding:
    title: str
    classification: str
    reason: str
    evidence_refs: List[str]


def _refs(items: Iterable[object]) -> List[str]:
    return [getattr(item, "ref") for item in items if getattr(item, "ref", None)]


def analyze_governance_burden(index: RepoEvidenceIndex) -> List[GovernanceFinding]:
    findings: List[GovernanceFinding] = []

    core_items = index.by_classification("core_constitutional")
    if core_items:
        findings.append(
            GovernanceFinding(
                title="M Triangle / deterministic governance / CIEU stay active",
                classification="core_constitutional",
                reason=(
                    "These rules protect survivability and governability; the repair should reduce ceremony, "
                    "not weaken the safety kernel."
                ),
                evidence_refs=_refs(core_items[:6]),
            )
        )

    choice_items = index.by_label("Iron Rule 0 choice rule")
    if choice_items:
        findings.append(
            GovernanceFinding(
                title="Over-broad no-choice rule should become recommendation-plus-approval",
                classification="replace_with_permission_tier",
                reason=(
                    "Aiden should not dump unanalyzed choices on the owner, but approval gates still need explicit "
                    "approve/reject/revise/hold controls for external side effects and strategic authorization."
                ),
                evidence_refs=_refs(choice_items),
            )
        )

    ceremony_items = index.by_label("Unified work protocol")
    if ceremony_items:
        findings.append(
            GovernanceFinding(
                title="12-layer / 5-tuple ceremony can slow small M-3 work",
                classification="administrative_burden",
                reason=(
                    "The full protocol is useful for serious obligations, but applying it mechanically to every "
                    "small task turns execution into paperwork."
                ),
                evidence_refs=_refs(ceremony_items),
            )
        )

    report_items = index.search("nightly", "daily report", "autonomous_daily_report", "weekly_board_summary")
    if report_items:
        findings.append(
            GovernanceFinding(
                title="Nightly/daily/weekly reporting is only useful when mission-bound",
                classification="administrative_burden",
                reason=(
                    "Routine reporting without an active mission or decision need competes with M-3 value production."
                ),
                evidence_refs=_refs(report_items[:6]),
            )
        )

    idle_items = index.by_label("Idle learning loop")
    if idle_items:
        findings.append(
            GovernanceFinding(
                title="Idle learning loops need a value-production stop condition",
                classification="simplify_active_runtime_rule",
                reason=(
                    "Learning is useful when it feeds a mission, customer signal, or product decision; otherwise it "
                    "can become a self-loop."
                ),
                evidence_refs=_refs(idle_items),
            )
        )

    social_items = index.by_label("Social media approval")
    if social_items:
        findings.append(
            GovernanceFinding(
                title="Social/publication rules belong in permission tiers",
                classification="replace_with_permission_tier",
                reason=(
                    "Publication should not be a hidden admin ritual; it should be a Tier 2/3 owner-approved action "
                    "with explicit content and risk boundary."
                ),
                evidence_refs=_refs(social_items),
            )
        )

    return findings


def burden_findings(index: RepoEvidenceIndex) -> List[GovernanceFinding]:
    return [
        finding
        for finding in analyze_governance_burden(index)
        if finding.classification in {"administrative_burden", "simplify_active_runtime_rule"}
    ]


def permission_tier_replacement_findings(index: RepoEvidenceIndex) -> List[GovernanceFinding]:
    return [
        finding
        for finding in analyze_governance_burden(index)
        if finding.classification == "replace_with_permission_tier"
    ]
