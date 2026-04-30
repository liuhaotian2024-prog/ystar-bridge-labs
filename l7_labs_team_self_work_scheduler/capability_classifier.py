#!/usr/bin/env python3
"""Policy-shaped classifier for bounded autonomous Labs team self-work."""

from __future__ import annotations

import re
from typing import Any


AUTONOMOUS_INTERNAL_EXAMPLES = [
    "refine offer package",
    "generate internal strategy memo",
    "compare customer segments",
    "improve delivery workflow",
    "produce owner review packet",
    "summarize existing local packets",
    "prepare draft-only outreach artifacts",
    "create dry-run memory/writeback candidates",
    "create completion report",
    "update local UI-visible progress packets",
]

EXTERNAL_ACTION_PATTERNS = {
    "email_send": r"\b(send|sent|sending)\s+(an?\s+)?(email|outreach|message)\b|邮件发送|发邮件",
    "customer_contact": r"\b(contact|call|message|dm|reach out to)\s+(customer|buyer|founder|lead|prospect)\b|联系客户|客户联系",
    "form_submission": r"\b(submit|fill)\s+(form|application)\b|提交表单",
    "grant_rfp_submission": r"\b(submit|apply)\s+(grant|rfp|proposal|bounty)\b|提交.*(grant|rfp)|申请.*grant",
    "publication": r"\b(publish|post|comment|tweet|release publicly)\b|发布|公开发布",
    "payment": r"\b(pay|purchase|checkout|invoice|charge|collect payment)\b|付款|支付|收款",
    "account_creation": r"\b(create|register|open)\s+(account|login)\b|创建账号|注册账号",
    "mcp_live_behavior": r"\b(mcp|live behavior|execute live)\b|实时行为",
}

CORE_WRITEBACK_PATTERNS = {
    "actual_memory_writeback": r"\b(actual\s+)?memory\s+writeback\b|\bwrite\s+memory\b|真实.*记忆写回",
    "actual_brain_writeback": r"\b(actual\s+)?brain\s+writeback\b|\bwrite\s+brain\b|大脑写回",
    "canonical_writeback": r"\bcanonical\s+(strategy\s+)?(writeback|mutation|update)\b|canonical strategy",
    "cieu_db_write": r"\bcieu\s+db\s+write\b|\bwrite\s+to\s+cieu\b",
    "protected_repo_mutation": r"\bmodify\s+(y-star-gov|gov-mcp|ystar-bridge-labs)\b|修改.*(y-star-gov|gov-mcp)",
}

UNSAFE_READ_PATTERNS = {
    "secret_or_env_read": r"\b(read|open|print|dump)\s+(secret|secrets|env|api key|credential|token)\b|读取.*(secret|env|密钥)",
    "raw_db_or_log_read": r"\b(read|open|dump|ingest)\s+(db|database|wal|shm|log|active-agent|marker content)\b|读取.*(db|日志|wal|shm)",
    "access_control_bypass": r"\b(bypass|evade)\s+(access|auth|permission)\b|绕过.*权限",
}

CLARIFICATION_PATTERNS = [
    r"\bunclear\b",
    r"\bclarify\b",
    r"需要澄清",
]

ALLOW_HINTS = [
    "internal",
    "local",
    "draft",
    "draft-only",
    "review-only",
    "dry-run",
    "compare",
    "refine",
    "summarize",
    "owner review",
    "completion report",
    "delivery workflow",
    "offer package",
    "strategy memo",
    "customer segment",
    "progress packet",
    "内部",
    "本地",
    "草稿",
    "只读",
    "干跑",
    "总结",
    "优化",
]


def _text_from_work_item(work_item_or_text: dict[str, Any] | str) -> str:
    if isinstance(work_item_or_text, str):
        return work_item_or_text
    parts = [
        str(work_item_or_text.get("title", "")),
        str(work_item_or_text.get("description", "")),
        " ".join(str(item) for item in work_item_or_text.get("expected_outputs", [])),
    ]
    return "\n".join(parts).strip()


def _matches(patterns: dict[str, str] | list[str], text: str) -> list[str]:
    lowered = text.lower()
    if isinstance(patterns, dict):
        return [code for code, pattern in patterns.items() if re.search(pattern, lowered, re.IGNORECASE)]
    return [pattern for pattern in patterns if re.search(pattern, lowered, re.IGNORECASE)]


def _remove_negative_safety_clauses(text: str) -> str:
    """Do not treat explicit no-go boundary text as an execution request."""
    clauses = re.split(r"(?<=[.!?。；;])|\n", text)
    kept = []
    combined_patterns = {**EXTERNAL_ACTION_PATTERNS, **CORE_WRITEBACK_PATTERNS, **UNSAFE_READ_PATTERNS}
    for clause in clauses:
        lowered = clause.lower()
        is_negative_boundary = any(marker in lowered for marker in ["do not", "don't", "no ", "without ", "禁止", "不要", "不得", "不允许"])
        contains_guarded_action = bool(_matches(combined_patterns, clause))
        if is_negative_boundary and contains_guarded_action:
            continue
        kept.append(clause)
    return " ".join(kept)


def classify_work_item(work_item_or_text: dict[str, Any] | str) -> dict[str, Any]:
    """Classify whether a work item can run as bounded internal self-work."""
    text = _text_from_work_item(work_item_or_text)
    lowered = text.lower()
    action_text = _remove_negative_safety_clauses(text)
    status = work_item_or_text.get("status", "Inbox") if isinstance(work_item_or_text, dict) else "Inbox"
    if status in {"Done", "Blocked", "Waiting for Approval"}:
        return _decision(
            "no_eligible_action",
            ["work_item_already_terminal"],
            "This work item is already terminal and is not eligible for another autonomous cycle.",
            False,
        )
    if not text:
        return _decision(
            "needs_owner_clarification",
            ["empty_work_item"],
            "The task has no owner-visible objective yet, so the scheduler will not invent one.",
            False,
        )
    unsafe = _matches(UNSAFE_READ_PATTERNS, action_text)
    if unsafe:
        return _decision(
            "blocked_unsafe",
            unsafe,
            "The request appears to involve secrets, raw DB/log/marker content, or access-control bypass.",
            False,
            hard_boundary_preserved=True,
        )
    core = _matches(CORE_WRITEBACK_PATTERNS, action_text)
    if core:
        return _decision(
            "approval_required_core_writeback",
            core,
            "Permanent brain/memory/canonical/CIEU DB writeback or protected-repo mutation requires explicit owner approval and remains blocked here.",
            False,
            approval_required=True,
            core_writeback=True,
            hard_boundary_preserved=True,
        )
    external = _matches(EXTERNAL_ACTION_PATTERNS, action_text)
    if external:
        return _decision(
            "approval_required_external_action",
            external,
            "The request implies an external side effect, so the scheduler creates an approval interruption instead of executing it.",
            False,
            approval_required=True,
            external_side_effects=True,
            hard_boundary_preserved=True,
        )
    if _matches(CLARIFICATION_PATTERNS, text):
        return _decision(
            "needs_owner_clarification",
            ["ambiguous_owner_goal"],
            "The request asks for clarification or is too ambiguous for safe autonomous work.",
            False,
        )
    allow_hits = [hint for hint in ALLOW_HINTS if hint in lowered]
    if allow_hits or any(example in lowered for example in AUTONOMOUS_INTERNAL_EXAMPLES):
        return _decision(
            "autonomous_internal_allowed",
            ["local_internal_work", *allow_hits[:5]],
            "This is bounded internal work: local analysis, draft-only output, packet updates, or completion reporting.",
            True,
        )
    return _decision(
        "needs_owner_clarification",
        ["no_clear_safe_internal_action"],
        "The scheduler could not identify a concrete safe internal action from the task.",
        False,
    )


def _decision(
    classification: str,
    reason_codes: list[str],
    explanation: str,
    autonomous_allowed: bool,
    approval_required: bool = False,
    external_side_effects: bool = False,
    core_writeback: bool = False,
    hard_boundary_preserved: bool = False,
) -> dict[str, Any]:
    return {
        "classification": classification,
        "decision": "allowed" if autonomous_allowed else "blocked_pending_human_review" if approval_required else "blocked_by_policy",
        "reason_codes": reason_codes,
        "owner_visible_explanation": explanation,
        "autonomous_allowed": autonomous_allowed,
        "approval_required": approval_required,
        "external_side_effects": external_side_effects,
        "core_writeback": core_writeback,
        "hard_boundary_preserved": hard_boundary_preserved,
        "policy_ref": "l7_labs_team_self_work_scheduler/capability_classifier.py",
    }
