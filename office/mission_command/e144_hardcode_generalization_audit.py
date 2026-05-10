from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


MILESTONE_ID = "E144_Hardcode_Generalization_Audit_R1"

RUNTIME_PATH_MARKERS = (
    "office/aiden_meeting_room",
    "office/agent_native_messenger",
    "office/mission_command",
    "ystar/governance",
    "gov_mcp/outbound",
)

LOW_RISK_PATH_MARKERS = (
    "/tests/",
    "tests/",
    "/operations/",
    "operations/",
    "/reports/",
    "reports/",
    "/docs/",
    "docs/",
)

PROCESS_RECEIPT_MARKERS = (
    "CEO Strategy Runtime:",
    "CEO Host Runtime:",
    "CIEU events:",
    "Provider mode:",
    "Selected first-cash path:",
    "Top market-first routes:",
)

ISSUE_SPECIFIC_MARKERS = (
    "STRAT-002",
    "strat002",
    "x402",
    "Mission GO",
    "Agent Payment Intent",
    "Payment Intent Governance",
    "AI security, compliance",
    "construction_bids_first_cash_pack",
    "ai_security_compliance_first_cash_pack",
    "cpa_tax_accounting_first_cash_pack",
)

GENERIC_INTELLIGENCE_REQUIREMENTS = (
    "owner_intent_extraction",
    "evidence_need_inference",
    "existing_capability_recall",
    "class_level_generalization",
    "dynamic_candidate_generation",
    "buyer_or_stakeholder_model",
    "action_packet_if_owner_asks_to_advance",
    "owner_readable_answer_not_machine_receipt",
)


@dataclass(frozen=True)
class HardcodeFinding:
    finding_id: str
    repo: str
    path: str
    line: int
    finding_type: str
    severity: str
    evidence: str
    why_it_matters: str
    correct_path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "repo": self.repo,
            "path": self.path,
            "line": self.line,
            "finding_type": self.finding_type,
            "severity": self.severity,
            "evidence": self.evidence,
            "why_it_matters": self.why_it_matters,
            "correct_path": self.correct_path,
        }


def scan_ecosystem_for_hardcoded_intelligence(
    repo_roots: Mapping[str, str | Path],
    *,
    max_file_size: int = 700_000,
) -> dict[str, Any]:
    """Scan Aiden/Y* runtime code for point-fix/template smells.

    This is an audit, not a proof of intelligence. Its job is to make the class
    of failures visible and repeatable so future milestones cannot keep hiding
    issue-specific patches inside runtime paths.
    """

    findings: list[HardcodeFinding] = []
    scanned_files = 0
    runtime_files = 0
    skipped_large_files = 0

    for repo, root_value in repo_roots.items():
        root = Path(root_value)
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".md", ".json", ".js", ".html"}:
                continue
            rel = str(path.relative_to(root))
            if ".git/" in rel or "__pycache__" in rel:
                continue
            scanned_files += 1
            if any(marker in rel for marker in RUNTIME_PATH_MARKERS):
                runtime_files += 1
            try:
                if path.stat().st_size > max_file_size:
                    skipped_large_files += 1
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if path.suffix == ".py":
                findings.extend(_scan_python_file(repo=repo, rel_path=rel, text=text))
            findings.extend(_scan_text_file(repo=repo, rel_path=rel, text=text))

    high = [item for item in findings if item.severity in {"critical", "high"}]
    return {
        "artifact_id": "e144_hardcode_generalization_audit",
        "milestone_id": MILESTONE_ID,
        "scan_scope": sorted(str(Path(root)) for root in repo_roots.values()),
        "scanned_files": scanned_files,
        "runtime_files": runtime_files,
        "skipped_large_files": skipped_large_files,
        "finding_count": len(findings),
        "critical_or_high_count": len(high),
        "findings": [item.to_dict() for item in findings],
        "class_level_correct_path": build_class_level_correct_path(findings),
        "truth_constraints": {
            "all_hardcoding_removed_claim": False,
            "audit_only_is_runtime_fix": False,
            "specific_issue_patch_claimed_as_general_intelligence": False,
        },
    }


def validate_owner_answer_generalization(owner_text: str, answer_text: str) -> dict[str, Any]:
    """Block owner-facing answers that smell like machine receipts or point-fixes."""

    owner = owner_text or ""
    answer = answer_text or ""
    violations: list[str] = []
    correct_path: list[str] = []

    marker_hits = [marker for marker in PROCESS_RECEIPT_MARKERS if marker in answer]
    if len(marker_hits) >= 2:
        violations.append("machine_receipt_leaked_to_owner")
        correct_path.append("translate runtime receipts into decision content, rationale, tradeoffs, and action packet")

    if _asks_for_action_advancement(owner) and _only_recommends_next_step(answer):
        violations.append("owner_asked_to_advance_but_answer_only_suggested_next_step")
        correct_path.append("build a no-send action advancement packet with buyer/stakeholder, deliverables, validation questions, and internal backlog")

    if _issue_specific_answer_without_owner_topic(owner, answer):
        violations.append("issue_specific_topic_leaked_into_unrelated_answer")
        correct_path.append("derive topic-specific details from owner intent, evidence, and retrieved context instead of fixed literals")

    if _process_ratio(answer) > 0.34 and "我的判断" not in answer[:260]:
        violations.append("process_over_content")
        correct_path.append("lead with CEO judgment; keep governance/process as a short boundary section at the end")

    decision = "ALLOW" if not violations else "REQUIRE_REVISION"
    return {
        "artifact_id": "e144_owner_answer_generalization_gate",
        "decision": decision,
        "passed": decision == "ALLOW",
        "violations": violations,
        "correct_path": correct_path,
        "marker_hits": marker_hits,
        "process_ratio": round(_process_ratio(answer), 3),
    }


def build_owner_answer_revision_guidance(owner_text: str, answer_text: str) -> str:
    gate = validate_owner_answer_generalization(owner_text, answer_text)
    if gate["passed"]:
        return answer_text
    guidance = "\n".join(f"- {item}" for item in gate["correct_path"])
    return (
        "Aiden Owner-Answer Integrity Gate: REQUIRE_REVISION\n"
        "这条回复不能直接给 owner，因为它仍然像模板/机器收据/单点补丁。\n\n"
        "正确方向：\n"
        f"{guidance}\n\n"
        "原始回复已保留在 runtime artifact/CIEU 中，但 owner-facing 层必须重新生成内容判断。"
    )


def build_class_level_correct_path(findings: Iterable[HardcodeFinding]) -> list[dict[str, Any]]:
    by_type: dict[str, int] = {}
    for item in findings:
        by_type[item.finding_type] = by_type.get(item.finding_type, 0) + 1
    return [
        {
            "issue_class": "keyword_router_or_specific_entity_gate",
            "count": by_type.get("keyword_router_branch", 0) + by_type.get("issue_specific_literal", 0),
            "repair": "replace isolated keyword branches with task-context feature extraction, confidence scoring, retrieval planning, and explicit fallback when confidence is low",
        },
        {
            "issue_class": "machine_receipt_as_answer",
            "count": by_type.get("machine_receipt_rendered_to_owner", 0),
            "repair": "owner-facing answers must lead with content judgment; runtime/provenance belongs in a final boundary/proof section",
        },
        {
            "issue_class": "static_route_or_candidate_menu",
            "count": by_type.get("static_route_menu", 0),
            "repair": "candidate routes must be generated from evidence clusters, repo capabilities, buyer model, and explicit constraints rather than fixed route IDs",
        },
        {
            "issue_class": "test_fixture_or_snapshot_used_as_live_intelligence",
            "count": by_type.get("fixture_or_snapshot_runtime_risk", 0),
            "repair": "fixture/snapshot paths must be marked test/historical and cannot satisfy live/current intelligence without an explicit live public-read provider",
        },
    ]


def _scan_python_file(*, repo: str, rel_path: str, text: str) -> list[HardcodeFinding]:
    findings: list[HardcodeFinding] = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return findings
    source_lines = text.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and _if_looks_like_keyword_router(node):
            findings.append(
                _finding(
                    repo,
                    rel_path,
                    getattr(node, "lineno", 1),
                    "keyword_router_branch",
                    "high" if _is_runtime_path(rel_path) else "medium",
                    _line(source_lines, getattr(node, "lineno", 1)),
                    "固定关键词分支会导致换个问法就失效，也会把近期补丁伪装成 CEO 理解。",
                    "Use semantic/task-feature extraction and confidence-scored routing instead of point keyword gates.",
                )
            )
        if isinstance(node, ast.Assign) and _assignment_has_issue_specific_literal(node):
            findings.append(
                _finding(
                    repo,
                    rel_path,
                    getattr(node, "lineno", 1),
                    "issue_specific_literal",
                    "high" if _is_runtime_path(rel_path) else "medium",
                    _line(source_lines, getattr(node, "lineno", 1)),
                    "问题特定常量如果进入 runtime，会把某次事故修复固化成下一次事故。",
                    "Move issue-specific examples into fixtures/artifacts; runtime must infer domain from input and retrieved evidence.",
                )
            )
    return findings


def _scan_text_file(*, repo: str, rel_path: str, text: str) -> list[HardcodeFinding]:
    findings: list[HardcodeFinding] = []
    if _is_low_risk_path(rel_path):
        return findings
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        if any(marker in line for marker in PROCESS_RECEIPT_MARKERS) and _is_runtime_path(rel_path):
            findings.append(
                _finding(
                    repo,
                    rel_path,
                    idx,
                    "machine_receipt_rendered_to_owner",
                    "high",
                    line.strip()[:240],
                    "owner-facing 层输出运行收据，会让 Aiden 看起来只会报流程、不做判断。",
                    "Keep machine receipts in CIEU/runtime artifacts; render owner-facing judgment separately.",
                )
            )
        if any(marker in line for marker in ISSUE_SPECIFIC_MARKERS) and _is_runtime_path(rel_path):
            findings.append(
                _finding(
                    repo,
                    rel_path,
                    idx,
                    "issue_specific_literal",
                    "high",
                    line.strip()[:240],
                    "runtime 中出现具体事故/路线/实体常量，容易形成只会回答这一个 case 的假智能。",
                    "Represent domain hints as evidence-derived features or test fixtures, not as mandatory runtime branches.",
                )
            )
        if re.search(r"(first_cash|route_id|current_best_first_cash_path).*(=|:)", line) and _is_runtime_path(rel_path):
            findings.append(
                _finding(
                    repo,
                    rel_path,
                    idx,
                    "static_route_menu",
                    "medium",
                    line.strip()[:240],
                    "固定路线字段可能是合法结构，也可能是固定候选菜单；必须由候选生成证明支撑。",
                    "Attach candidate_generation_proof and evidence cluster provenance before presenting a route as CEO judgment.",
                )
            )
        if "fixture" in line.lower() or "snapshot" in line.lower():
            if _is_runtime_path(rel_path):
                findings.append(
                    _finding(
                        repo,
                        rel_path,
                        idx,
                        "fixture_or_snapshot_runtime_risk",
                        "medium",
                        line.strip()[:240],
                        "fixture/snapshot 若被当成当前世界，会污染战略判断。",
                        "Mark fixture/snapshot as test or historical; require live/current evidence for non-test strategy.",
                    )
                )
    return findings


def _if_looks_like_keyword_router(node: ast.If) -> bool:
    text = ast.dump(node.test).lower()
    if " in " in text:
        return True
    return ("any" in text and "in" in text and ("text" in text or "message" in text or "owner" in text))


def _assignment_has_issue_specific_literal(node: ast.Assign) -> bool:
    dumped = ast.dump(node.value)
    return any(marker.lower() in dumped.lower() for marker in ISSUE_SPECIFIC_MARKERS)


def _finding(
    repo: str,
    path: str,
    line: int,
    finding_type: str,
    severity: str,
    evidence: str,
    why: str,
    correct_path: str,
) -> HardcodeFinding:
    return HardcodeFinding(
        finding_id=f"{repo}:{path}:{line}:{finding_type}",
        repo=repo,
        path=path,
        line=line,
        finding_type=finding_type,
        severity=severity,
        evidence=evidence,
        why_it_matters=why,
        correct_path=correct_path,
    )


def _line(lines: list[str], line: int) -> str:
    if line <= 0 or line > len(lines):
        return ""
    return lines[line - 1].strip()[:240]


def _is_runtime_path(path: str) -> bool:
    return any(marker in path for marker in RUNTIME_PATH_MARKERS)


def _is_low_risk_path(path: str) -> bool:
    name = Path(path).name
    return (
        any(marker in path for marker in LOW_RISK_PATH_MARKERS)
        or name.endswith("_report.json")
        or name.endswith("_readback.md")
        or name.endswith("_report.md")
        or name.endswith("_result.json")
        or name.endswith("_summary.md")
    )


def _asks_for_action_advancement(text: str) -> bool:
    lowered = (text or "").lower()
    return any(term in lowered for term in ("推进", "行动", "赚钱", "变现", "商业化", "落地", "go-to-market", "gtm", "monetize"))


def _only_recommends_next_step(answer: str) -> bool:
    lowered = (answer or "").lower()
    next_step_hits = sum(1 for term in ("下一步", "建议", "应该", "correct path", "生成一份", "准备一份") if term in lowered)
    action_packet_hits = sum(1 for term in ("target_buyers", "目标买方", "交付物", "backlog", "validation questions", "验证问题") if term in lowered)
    return next_step_hits >= 2 and action_packet_hits == 0


def _issue_specific_answer_without_owner_topic(owner: str, answer: str) -> bool:
    owner_lower = (owner or "").lower()
    answer_lower = (answer or "").lower()
    if _strategy_candidate_context(owner_lower, answer_lower):
        return False
    for marker in ISSUE_SPECIFIC_MARKERS:
        marker_lower = marker.lower()
        if marker_lower in answer_lower and marker_lower not in owner_lower:
            return True
    return False


def _strategy_candidate_context(owner_lower: str, answer_lower: str) -> bool:
    """Allow route/entity names only when they are clearly runtime-derived strategy candidates."""

    owner_strategy = any(
        term in owner_lower
        for term in ("strategy", "战略", "赚钱", "市场", "first cash", "全球", "变现", "路线", "路径")
    )
    answer_candidate = any(
        term in answer_lower
        for term in ("当前候选排序", "候选路线", "selected route", "strategy runtime", "策略运行结果")
    )
    boundary_present = any(term in answer_lower for term in ("不是客户验证", "没有外部发送", "边界"))
    return owner_strategy and answer_candidate and boundary_present


def _process_ratio(answer: str) -> float:
    words = re.findall(r"[A-Za-z0-9_+\-]+|[\u4e00-\u9fff]{2,}", answer or "")
    if not words:
        return 0.0
    process_terms = (
        "runtime",
        "governance",
        "cieu",
        "Y-star-gov",
        "provider",
        "decision",
        "收据",
        "流程",
        "治理",
        "链路",
        "事件",
    )
    hits = sum(1 for word in words if any(term.lower() in word.lower() for term in process_terms))
    return hits / max(1, len(words))


__all__ = [
    "GENERIC_INTELLIGENCE_REQUIREMENTS",
    "MILESTONE_ID",
    "build_class_level_correct_path",
    "build_owner_answer_revision_guidance",
    "scan_ecosystem_for_hardcoded_intelligence",
    "validate_owner_answer_generalization",
]
