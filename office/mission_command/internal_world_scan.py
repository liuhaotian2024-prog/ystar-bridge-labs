from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List

from .research_capability import FORBIDDEN_MARKERS


SCAN_TARGETS = [
    "README.md",
    "AGENTS.md",
    "OPERATIONS.md",
    "DIRECTIVE_TRACKER.md",
    "governance/ACTIVE_OPERATING_CHARTER.md",
    "directive_retriage.json",
    "sales",
    "content",
    "reports/integration",
    "knowledge/ceo/wisdom",
    "office/aiden_meeting_room",
    "office/mission_command",
]


def _safe(path: Path) -> bool:
    lowered = str(path).lower()
    return "__pycache__" not in path.parts and not any(marker in lowered for marker in FORBIDDEN_MARKERS)


def _iter_safe_files(root: Path, target: str, limit: int = 80) -> Iterable[Path]:
    path = root / target
    if not _safe(path) or not path.exists():
        return []
    if path.is_file():
        return [path]
    files: List[Path] = []
    for candidate in sorted(path.rglob("*")):
        if len(files) >= limit:
            break
        if candidate.is_file() and _safe(candidate):
            files.append(candidate)
    return files


def _read_snippet(path: Path, max_chars: int = 500) -> str:
    if not _safe(path):
        return ""
    return " ".join(path.read_text(encoding="utf-8", errors="replace")[:max_chars].split())


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def build_internal_world_scan(repo_root: Path) -> Dict[str, object]:
    files_by_target: Dict[str, List[str]] = {}
    snippets: Dict[str, str] = {}
    for target in SCAN_TARGETS:
        files = list(_iter_safe_files(repo_root, target))
        files_by_target[target] = [_rel(repo_root, path) for path in files[:40]]
        for path in files[:15]:
            snippets[_rel(repo_root, path)] = _read_snippet(path)

    sales_files = files_by_target.get("sales", [])
    content_files = files_by_target.get("content", [])
    integration_reports = files_by_target.get("reports/integration", [])
    knowledge_files = files_by_target.get("knowledge/ceo/wisdom", [])

    money_paths = [
        {
            "path": "Founder AI Workflow Audit / CEO Command Brief",
            "internal_asset_match": ["M Triangle", "WORK_METHODOLOGY", "Mission Command", "sales/prospect history"],
            "evidence_refs": ["knowledge/ceo/wisdom/M_TRIANGLE.md", "knowledge/ceo/wisdom/WORK_METHODOLOGY.md", *sales_files[:3]],
        },
        {
            "path": "AI Company Cockpit Setup",
            "internal_asset_match": ["Aiden CEO Meeting Room", "Mission Command", "Active Operating Charter"],
            "evidence_refs": ["office/aiden_meeting_room", "office/mission_command", "governance/ACTIVE_OPERATING_CHARTER.md"],
        },
        {
            "path": "Coding-Agent Governance Audit",
            "internal_asset_match": ["Y-star-gov governance kernel", "gov-mcp preflight", "CIEU/audit language"],
            "evidence_refs": ["governance/ACTIVE_OPERATING_CHARTER.md", *content_files[:3]],
        },
        {
            "path": "Agent Workflow Bottleneck Diagnosis",
            "internal_asset_match": ["WORK_METHODOLOGY", "directive/admin rationalization", "Mission Command task split"],
            "evidence_refs": ["DIRECTIVE_TRACKER.md", "directive_retriage.json", "office/mission_command"],
        },
        {
            "path": "Runtime Setup Advisory",
            "internal_asset_match": ["Mission Command operating spine", "Aiden Meeting Room", "company_runtime/gov-mcp bridge"],
            "evidence_refs": ["office/mission_command", *integration_reports[:3]],
        },
        {
            "path": "Governance Template Paid Support",
            "internal_asset_match": ["content/product assets", "governance templates", "active charter"],
            "evidence_refs": ["content/product", "governance/ACTIVE_OPERATING_CHARTER.md"],
        },
    ]

    return {
        "safe_scan_targets": SCAN_TARGETS,
        "files_by_target": files_by_target,
        "snippets": snippets,
        "internal_assets": [
            "Aiden CEO Meeting Room",
            "Mission Command",
            "Active Operating Charter",
            "directive_retriage.json",
            "M Triangle",
            "WORK_METHODOLOGY",
            "sales/prospect files",
            "content/product and article assets",
        ],
        "current_capabilities": [
            "evidence-grounded repo context loading",
            "active vs historical governance/admin distinction",
            "team task split",
            "Y-star-gov/gov-mcp preflight bridge",
            "approval-needed action separation",
        ],
        "old_commercial_assets": sales_files[:20],
        "old_content_assets": content_files[:20],
        "current_governance_capability": [
            "M Triangle",
            "Active Operating Charter",
            "company_runtime permission tiers",
            "gov-mcp action preflight",
        ],
        "execution_boundary": [
            "no external sending",
            "no customer contact",
            "no email",
            "no publication",
            "no payment",
            "no core DB/brain/memory/CIEU writeback",
        ],
        "internal_constraints": [
            "external live market evidence is not available unless configured live read-only research is enabled",
            "old sales/content artifacts are historical evidence, not current market validation",
            "any outreach or publication requires owner approval",
        ],
        "money_paths": money_paths,
    }


def render_internal_world_scan_markdown(scan: Dict[str, object]) -> str:
    lines = ["# Internal World Scan — 2026-05-01", ""]
    lines.append("## Internal Assets")
    lines.extend(f"- {item}" for item in scan["internal_assets"])  # type: ignore[index]
    lines.append("")
    lines.append("## Current Capabilities")
    lines.extend(f"- {item}" for item in scan["current_capabilities"])  # type: ignore[index]
    lines.append("")
    lines.append("## Old Commercial Assets")
    lines.extend(f"- {item}" for item in scan["old_commercial_assets"])  # type: ignore[index]
    lines.append("")
    lines.append("## Old Content Assets")
    lines.extend(f"- {item}" for item in scan["old_content_assets"])  # type: ignore[index]
    lines.append("")
    lines.append("## Governance / Execution Boundary")
    lines.extend(f"- {item}" for item in scan["current_governance_capability"])  # type: ignore[index]
    lines.extend(f"- {item}" for item in scan["execution_boundary"])  # type: ignore[index]
    lines.append("")
    lines.append("## Internal Constraints")
    lines.extend(f"- {item}" for item in scan["internal_constraints"])  # type: ignore[index]
    lines.append("")
    lines.append("## Internal Assets Mapped To Money Paths")
    for path in scan["money_paths"]:  # type: ignore[index]
        lines.append(f"### {path['path']}")
        lines.append(f"- Asset match: {', '.join(path['internal_asset_match'])}")
        lines.append(f"- Evidence refs: {', '.join(path['evidence_refs'])}")
    lines.append("")
    lines.append("## File Coverage Snapshot")
    lines.append("```json")
    lines.append(json.dumps(scan["files_by_target"], ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    lines.append("Safety: skipped secrets/env, DB/WAL/SHM, private logs, and active-agent marker contents.")
    return "\n".join(lines)
