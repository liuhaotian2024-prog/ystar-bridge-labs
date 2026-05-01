from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .directive_retriage_analyzer import analyze_directive_tracker
from .governance_burden_analyzer import analyze_governance_burden
from .operations_admin_analyzer import analyze_operations_admin
from .repo_evidence_index import RepoEvidenceIndex, build_repo_evidence_index


SAFE_CONTEXT_FILES = [
    "README.md",
    "AGENTS.md",
    "OPERATIONS.md",
    "DIRECTIVE_TRACKER.md",
    "governance/ACTIVE_OPERATING_CHARTER.md",
    "governance/INTERNAL_GOVERNANCE.md",
    "governance/WORKING_STYLE.md",
    "knowledge/ceo/wisdom/M_TRIANGLE.md",
    "knowledge/ceo/wisdom/WORK_METHODOLOGY.md",
    "knowledge/ceo/wisdom/AIDEN_META_DEVELOPMENT_METHOD_KERNEL.md",
    "scripts/gov_order.py",
]

FORBIDDEN_PATH_MARKERS = (
    ".env",
    "secret",
    ".db",
    ".db-wal",
    ".db-shm",
    ".log",
    "active_agent",
    ".ystar_active_agent",
)


@dataclass
class CompanyContext:
    repo_root: Path
    source_texts: Dict[str, str] = field(default_factory=dict)
    missing_files: List[str] = field(default_factory=list)
    evidence_index: RepoEvidenceIndex | None = None
    governance_findings: List[Any] = field(default_factory=list)
    directive_findings: List[Any] = field(default_factory=list)
    operations_findings: List[Any] = field(default_factory=list)
    team_roster: List[str] = field(default_factory=list)
    m_triangle_summary: str = ""
    methodology_summary: str = ""
    operations_summary: str = ""
    no_action_boundary: List[str] = field(default_factory=list)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _safe_read(path: Path, max_chars: int = 30000) -> str:
    lowered = str(path).lower()
    if any(marker in lowered for marker in FORBIDDEN_PATH_MARKERS):
        return ""
    return path.read_text(encoding="utf-8", errors="replace")[:max_chars]


def _contains(texts: Dict[str, str], needle: str) -> bool:
    return any(needle.lower() in text.lower() for text in texts.values())


def load_company_context(repo_root: Path | None = None) -> CompanyContext:
    root = (repo_root or _repo_root()).resolve()
    ctx = CompanyContext(repo_root=root)
    for rel in SAFE_CONTEXT_FILES:
        path = root / rel
        if path.exists() and path.is_file():
            ctx.source_texts[rel] = _safe_read(path)
        else:
            ctx.missing_files.append(rel)

    ctx.team_roster = [
        "Haotian Liu — Board / Founder",
        "Aiden Liu — CEO",
        "Ethan Wright — CTO",
        "Sofia Blake — CMO",
        "Marco Rivera — CFO",
        "Zara Johnson — CSO",
        "Samantha Lin — Secretary",
        "Leo / Maya / Ryan / Jordan — Engineers",
        "Jinjin / K9 Scout — Research",
    ]
    ctx.m_triangle_summary = (
        "M Triangle: M-1 survivability, M-2 governability, M-3 value production. "
        "M-3 means real product, real customers, real revenue, and real industry impact."
    )
    ctx.methodology_summary = (
        "WORK_METHODOLOGY says plan is not done; every task must trace M -> U -> action -> empirical result. "
        "AIDEN_META_DEVELOPMENT_METHOD_KERNEL adds observe/compare/capability/opportunity/experiment/residual discipline."
    )
    ctx.operations_summary = (
        "OPERATIONS shows CEO session rhythm, directive tracking, sales/content cadence, and a historical risk of report-heavy autonomous work."
    )
    ctx.no_action_boundary = [
        "no external sending",
        "no customer contact",
        "no email",
        "no publication",
        "no payment",
        "no form submission",
        "no account creation",
        "no core DB/brain/memory/CIEU writeback",
    ]

    if not _contains(ctx.source_texts, "COO"):
        ctx.no_action_boundary.append("no COO invented")
    ctx.evidence_index = build_repo_evidence_index(root)
    ctx.governance_findings = analyze_governance_burden(ctx.evidence_index)
    ctx.directive_findings = analyze_directive_tracker(root)
    ctx.operations_findings = analyze_operations_admin(root)
    return ctx
