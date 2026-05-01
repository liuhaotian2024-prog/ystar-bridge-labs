from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from .evidence_extractor import safe_read_lines


@dataclass(frozen=True)
class DirectiveFinding:
    directive_id: str
    task_id: str
    task: str
    old_status: str
    new_status: str
    reason: str
    m_triangle_alignment: str
    evidence_ref: str


def _classify(task: str, status: str) -> tuple[str, str, str]:
    text = f"{task} {status}".lower()
    if any(k in text for k in ["linkedin", "hacker news", "hn", "podcast", "content calendar", "内容", "article"]):
        return (
            "ARCHIVE_LEGACY",
            "Old content/social cadence should not stay active unless owner reactivates it for a current money-path mission.",
            "weak_m3_unless_reactivated",
        )
    if any(k in text for k in ["enterprise", "warm intro", "pilot", "sales phase", "sales intelligence"]):
        return (
            "OWNER_DECISION_REQUIRED",
            "Enterprise sales work may be revenue-relevant, but it needs current evidence and owner authorization before becoming active.",
            "possible_m3_but_needs_evidence",
        )
    if any(k in text for k in ["three-repo", "3-repo", "三仓库", "integration", "backflow"]):
        return (
            "SUPERSEDED_BY_RUNTIME",
            "Recent backflow architecture makes the old integration directive a source of evidence, not an always-active task list.",
            "m2_to_m3_bridge",
        )
    if any(k in text for k in ["notebooklm", "books", "patent", "uspto", "lawyer"]):
        return (
            "OWNER_DECISION_REQUIRED",
            "This is potentially strategic but not automatically value-producing; owner must decide whether to reactivate.",
            "strategic_optional",
        )
    if any(k in text for k in ["test", "coverage", "pytest", "baseline", "smoke", "测试", "覆盖率", "基线"]):
        return (
            "REVENUE_RELEVANT_NOW",
            "Testing baseline supports usable delivery and prevents governance/runtime regressions that block paid work.",
            "m1_m2_supports_m3",
        )
    if any(k in text for k in ["daily", "weekly", "nightly", "report", "cadence", "summary"]):
        return (
            "ADMIN_BURDEN",
            "Reporting cadence is useful only when tied to a live mission or owner decision.",
            "low_m3_when_unbound",
        )
    if any(k in text for k in ["gov_order", "obligation", "mcp", "y*gov", "governance"]):
        return (
            "ACTIVE_NOW",
            "Governance pipeline work remains active when it directly supports safer mission execution.",
            "m2_supports_m3",
        )
    return (
        "OWNER_DECISION_REQUIRED",
        "The tracker entry is not clearly current from file evidence alone; it should be re-triaged before execution.",
        "unclear",
    )


def analyze_directive_tracker(repo_root: Path) -> List[DirectiveFinding]:
    lines = safe_read_lines(repo_root, "DIRECTIVE_TRACKER.md")
    findings: List[DirectiveFinding] = []
    current_directive = ""
    for line_number, line in enumerate(lines, start=1):
        raw = line.strip()
        if raw.startswith("## ") and "D-" in raw:
            current_directive = raw.lstrip("# ").strip()
        if not raw.startswith("|"):
            continue
        if "---" in raw or "Task ID" in raw:
            continue
        cells = [cell.strip() for cell in raw.strip("|").split("|")]
        if len(cells) < 5:
            continue
        task_id, task, owner, due, status = cells[:5]
        if not task_id or not task:
            continue
        new_status, reason, alignment = _classify(task, status)
        findings.append(
            DirectiveFinding(
                directive_id=current_directive or "unknown",
                task_id=task_id,
                task=task,
                old_status=status,
                new_status=new_status,
                reason=reason,
                m_triangle_alignment=alignment,
                evidence_ref=f"DIRECTIVE_TRACKER.md:{line_number}",
            )
        )
    return findings


def grouped_directive_summary(findings: List[DirectiveFinding]) -> dict[str, List[DirectiveFinding]]:
    grouped: dict[str, List[DirectiveFinding]] = {}
    for finding in findings:
        grouped.setdefault(finding.new_status, []).append(finding)
    return grouped
