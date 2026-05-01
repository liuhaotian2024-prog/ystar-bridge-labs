from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from .evidence_extractor import safe_read_lines


@dataclass(frozen=True)
class OperationsFinding:
    title: str
    classification: str
    reason: str
    evidence_ref: str


def _classify(line: str) -> tuple[str, str]:
    text = line.lower()
    if "hacker news" in text or " hn " in f" {text} " or "linkedin" in text:
        return (
            "historical_or_stale_admin",
            "Content cadence is historical/admin by default; it should be reactivated only for a current evidence-backed money path.",
        )
    if any(k in text for k in ["daily", "weekly", "nightly", "autonomous_daily_report", "weekly_board_summary"]):
        return (
            "stale_admin",
            "Time-based reporting should not bind agents unless attached to a live mission, obligation, or owner-approved cadence.",
        )
    if "enterprise" in text or "sales" in text:
        return (
            "owner_decision_required",
            "Sales/enterprise plans may be revenue-relevant but require current evidence before becoming active operations.",
        )
    if "legacy" in text or "dispatch" in text:
        return (
            "historical",
            "Legacy dispatch material should remain available as history, not operate as a current mandate.",
        )
    return (
        "owner_decision_required",
        "The operations item needs explicit reactivation before it is treated as current.",
    )


def analyze_operations_admin(repo_root: Path) -> List[OperationsFinding]:
    lines = safe_read_lines(repo_root, "OPERATIONS.md")
    findings: List[OperationsFinding] = []
    keywords = [
        "daily",
        "weekly",
        "nightly",
        "hacker news",
        "linkedin",
        "enterprise",
        "sales",
        "legacy",
        "dispatch",
        "autonomous_daily_report",
        "weekly_board_summary",
    ]
    for line_number, line in enumerate(lines, start=1):
        raw = line.strip()
        if not raw or not any(keyword in raw.lower() for keyword in keywords):
            continue
        classification, reason = _classify(raw)
        findings.append(
            OperationsFinding(
                title=raw[:120],
                classification=classification,
                reason=reason,
                evidence_ref=f"OPERATIONS.md:{line_number}",
            )
        )
    return findings
