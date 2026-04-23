#!/usr/bin/env python3
"""
W13+W4 — Sub-agent output scan + E1 receipt-honesty enforce + 8 Module Header check

Layer 7 Gap Fix (W13): Scan sub-agent returned text for defer/choice/backlog-disguise patterns.
E1 Receipt-Honesty Enforce (Wave-4): Parse tool_uses breakdown, cross-check vs metadata,
  emit E1_RECEIPT_REJECTED (>30% drift) or E1_RECEIPT_DRIFT_WARN (10-30% drift).
8 Module Header Check (Wave-4): Verify receipt contains "## 8 Module Activation" segment
  per aiden_8_module_cognitive_architecture.md. Warn if missing (7-day baseline, then promote).

Wiring: .claude/settings.json hooks.PostToolUse (matcher: Agent tool).
Fail-open (PostToolUse cannot block, but CAN inject system-reminders into next prompt context).
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
import time
import uuid
from pathlib import Path
from typing import Optional

# Y*gov module path fix (Board 2026-04-16 P0: ModuleNotFoundError emergency)
sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")

REPO_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
CIEU_DB = REPO_ROOT / ".ystar_cieu.db"

DRIFT_KEYWORDS = [
    # defer disguise
    "稍后", "以后再", "改天", "queued for", "wait for", "later",
    "next session", "tomorrow morning",
    # backlog disguise
    "入 backlog", "入 Backlog", "入 Campaign", "下次 session",
    "下 session", "defer to", "推到下",
]
CHOICE_PATTERNS = [
    r"请选择.*[12二]",
    r"Option [AB]",
    r"方案[12一二]",
    r"[选]\s*[一二]",
    r"三选一",
    r"A\)\s.*B\)\s.*C\)",
    r"❕.*选项",
]
# Request-board-shell pattern (Board shell marker violation)
SHELL_REQUEST_PATTERNS = [
    r"Board 请跑",
    r"Board 手动跑",
    r"Board 手动写",
    r"Board 执行",
    r"需要 Board.*手动",
    r"Board 请在 terminal",
]

# ── E1 Receipt-Honesty Constants (Wave-4) ──
E1_DRIFT_REJECT_THRESHOLD = 0.30   # >30% drift = E1_RECEIPT_REJECTED
E1_DRIFT_WARN_THRESHOLD = 0.10     # 10-30% drift = E1_RECEIPT_DRIFT_WARN

# ── 8 Module Header Pattern (Wave-4) ──
EIGHT_MODULE_HEADER_PATTERN = re.compile(
    r"##\s*8\s*Module\s*Activation", re.IGNORECASE
)
# Required M1-M8 line markers (at least 6 of 8 must be present to pass)
EIGHT_MODULE_MARKERS = [
    r"M1\s*(反射|reflex)",
    r"M2\s*(记忆|memory)",
    r"M3\s*(资料|data|research)",
    r"M4\s*(路径|path|plan)",
    r"M5\s*(方法论|methodology)",
    r"M6\s*(错误|error|monitor)",
    r"M7\s*(主动|action|active)",
    r"M8\s*(反思|reflect|sleep)",
]


def _scan(text: str) -> list:
    if not text:
        return []
    hits = []
    text_lower = text.lower()
    for kw in DRIFT_KEYWORDS:
        if kw in text or kw.lower() in text_lower:
            hits.append(("SUBAGENT_DEFER_DRIFT", f"keyword={kw}"))
            break
    for pat in CHOICE_PATTERNS:
        if re.search(pat, text):
            hits.append(("SUBAGENT_CHOICE_DRIFT", f"pattern={pat}"))
            break
    for pat in SHELL_REQUEST_PATTERNS:
        if re.search(pat, text):
            hits.append(("SUBAGENT_BOARD_SHELL_REQUEST", f"pattern={pat}"))
            break
    return hits


def _emit_cieu(event_type: str, metadata, decision: str = "warn") -> None:
    """Emit CIEU event via central emit_cieu() helper (m_functor inference enabled)."""
    try:
        if isinstance(metadata, dict):
            metadata_str = json.dumps(metadata, ensure_ascii=False, default=str)[:500]
        else:
            metadata_str = str(metadata)[:500]
        sys.path.insert(0, str(Path(__file__).parent))
        from _cieu_helpers import emit_cieu
        emit_cieu(
            event_type=event_type,
            decision=decision,
            passed=1,
            task_description=metadata_str,
            session_id="subagent_scan",
        )
    except Exception:
        pass


def _pop_agent_stack() -> str:
    """CZL-P1-e: Pop agent stack and restore previous agent identity."""
    try:
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from agent_stack import pop_agent
        restored = pop_agent()
        return restored
    except Exception as e:
        # Fail-open: do not crash the hook on stack errors
        sys.stderr.write(f"[P1-e] Agent stack pop failed: {e}\n")
        return ""


# ════════════════════════════════════════════════════════════════════════════
# Sub-task A: E1 Receipt-Honesty Enforcement (Wave-4)
# ════════════════════════════════════════════════════════════════════════════

def _extract_tool_uses_metadata(result_text: str) -> int | None:
    """
    Extract actual tool_uses count from <task-notification> metadata.
    Claude Code Agent tool returns include:
      <task-notification><metadata><tool_uses>N</tool_uses></metadata>...</task-notification>
    Returns None if no task-notification metadata found.
    """
    match = re.search(
        r'<task-notification>.*?<metadata>.*?<tool_uses>(\d+)</tool_uses>.*?</metadata>',
        result_text, re.DOTALL
    )
    if match:
        return int(match.group(1))
    return None


def _extract_claimed_tool_uses(receipt_text: str) -> dict | None:
    """
    Extract claimed tool_uses from receipt, including breakdown if present.

    Supported formats:
      1. Breakdown: "Bash 5 + Read 3 + Edit 2 + Write 1 = 11"
         or "U = (Bash 5 + Read 3 + Edit 2 + Write 1 = 11)"
      2. Simple: "tool_uses: 11" or "tool calls: 11"
      3. Template: "Bash N + Read M + Edit P + Write Q = TOTAL"

    Returns dict: {
        "total": int,
        "breakdown": {"Bash": int, "Read": int, "Edit": int, "Write": int} or None,
        "breakdown_sum": int or None (sum of breakdown parts),
        "internally_consistent": bool (breakdown_sum == total if both present)
    } or None if no claim found.
    """
    result = {
        "total": None,
        "breakdown": None,
        "breakdown_sum": None,
        "internally_consistent": True,
    }

    # Pattern 1: Breakdown format "Bash N + Read M + Edit P + Write Q = TOTAL"
    breakdown_pattern = re.compile(
        r'(?:Bash|bash)\s+(\d+)\s*\+\s*(?:Read|read)\s+(\d+)\s*\+\s*(?:Edit|edit)\s+(\d+)\s*\+\s*(?:Write|write)\s+(\d+)\s*=\s*(\d+)',
        re.IGNORECASE
    )
    bd_match = breakdown_pattern.search(receipt_text)
    if bd_match:
        breakdown = {
            "Bash": int(bd_match.group(1)),
            "Read": int(bd_match.group(2)),
            "Edit": int(bd_match.group(3)),
            "Write": int(bd_match.group(4)),
        }
        total = int(bd_match.group(5))
        breakdown_sum = sum(breakdown.values())
        result["total"] = total
        result["breakdown"] = breakdown
        result["breakdown_sum"] = breakdown_sum
        result["internally_consistent"] = (breakdown_sum == total)
        return result

    # Pattern 2: Simple "tool_uses: N" / "tool calls: N" / "tool-uses: N"
    simple_patterns = [
        r"tool[_ -]?uses?\s*[:：]\s*(\d+)",
        r"tool[_ -]?calls?\s*[:：]\s*(\d+)",
        r"工具调用\s*[:：]\s*(\d+)",
        r"=\s*(\d+)\s*(?:tool|tu\b)",
    ]
    for pattern in simple_patterns:
        match = re.search(pattern, receipt_text, re.IGNORECASE)
        if match:
            result["total"] = int(match.group(1))
            return result

    return None


def _compute_e1_drift(claimed_total: int, metadata_total: int) -> dict:
    """
    Compute E1 drift between claimed and metadata tool_uses.

    Returns dict: {
        "drift_abs": int,
        "drift_pct": float (0.0-1.0+),
        "direction": "over_claim" | "under_claim" | "match",
        "severity": "ok" | "warn" | "reject",
    }
    """
    drift_abs = abs(claimed_total - metadata_total)

    # Avoid div-by-zero: if metadata is 0 and claim > 0, 100% drift
    if metadata_total == 0:
        drift_pct = 1.0 if claimed_total > 0 else 0.0
    else:
        drift_pct = drift_abs / metadata_total

    if claimed_total > metadata_total:
        direction = "over_claim"
    elif claimed_total < metadata_total:
        direction = "under_claim"
    else:
        direction = "match"

    if drift_pct > E1_DRIFT_REJECT_THRESHOLD:
        severity = "reject"
    elif drift_pct > E1_DRIFT_WARN_THRESHOLD:
        severity = "warn"
    else:
        severity = "ok"

    return {
        "drift_abs": drift_abs,
        "drift_pct": round(drift_pct, 3),
        "direction": direction,
        "severity": severity,
    }


def e1_receipt_honesty_check(result_text: str) -> dict | None:
    """
    Full E1 receipt-honesty enforcement pipeline.

    1. Extract metadata tool_uses from <task-notification>
    2. Extract claimed tool_uses (with breakdown) from receipt prose
    3. Check internal consistency (breakdown sum == total)
    4. Compute drift percentage
    5. Emit appropriate CIEU event + inject system-reminder if needed

    Returns dict with check results, or None if no claims/metadata to check.
    """
    # Step 1: Get metadata tool_uses
    metadata_tool_uses = _extract_tool_uses_metadata(result_text)
    if metadata_tool_uses is None:
        return None  # No task-notification metadata → skip (non-Agent or missing)

    # Step 2: Extract receipt text from <result> block if task-notification present
    result_match = re.search(
        r'<task-notification>.*?<result>(.*?)</result>.*?</task-notification>',
        result_text, re.DOTALL
    )
    receipt_text = result_match.group(1) if result_match else result_text

    # Step 3: Extract claimed tool_uses
    claimed = _extract_claimed_tool_uses(receipt_text)
    if claimed is None or claimed["total"] is None:
        # No tool_uses claim in receipt → emit missing-claim warn
        _emit_cieu("E1_RECEIPT_NO_CLAIM", {
            "metadata_tool_uses": metadata_tool_uses,
            "reason": "Receipt lacks tool_uses claim — cannot verify honesty",
        }, decision="warn")
        return {"status": "no_claim", "metadata_tool_uses": metadata_tool_uses}

    # Step 4: Check internal consistency of breakdown
    if claimed["breakdown"] and not claimed["internally_consistent"]:
        _emit_cieu("E1_RECEIPT_BREAKDOWN_INCONSISTENT", {
            "breakdown": claimed["breakdown"],
            "breakdown_sum": claimed["breakdown_sum"],
            "claimed_total": claimed["total"],
            "diff": abs(claimed["breakdown_sum"] - claimed["total"]),
        }, decision="warn")

    # Step 5: Compute drift vs metadata
    drift = _compute_e1_drift(claimed["total"], metadata_tool_uses)

    # Step 6: Emit CIEU event based on severity
    event_data = {
        "claimed_total": claimed["total"],
        "metadata_total": metadata_tool_uses,
        "drift_abs": drift["drift_abs"],
        "drift_pct": drift["drift_pct"],
        "direction": drift["direction"],
        "breakdown": claimed["breakdown"],
        "internally_consistent": claimed["internally_consistent"],
    }

    if drift["severity"] == "reject":
        # >30% drift → E1_RECEIPT_REJECTED (deny-level)
        _emit_cieu("E1_RECEIPT_REJECTED", event_data, decision="deny")
        # Inject system-reminder for CEO next prompt context
        agent_id_match = re.search(r'##\s*RECEIPT\s*\(([^#\)]+)', receipt_text)
        agent_label = agent_id_match.group(1).strip() if agent_id_match else "unknown"
        print(
            f"<system-reminder>E1_RECEIPT_REJECTED: {agent_label} claimed {claimed['total']} "
            f"tool_uses but metadata shows {metadata_tool_uses} "
            f"(drift={drift['drift_pct']*100:.0f}%, threshold=30%). "
            f"Direction: {drift['direction']}. "
            f"CEO must re-dispatch sub-agent with explicit re-receipt request. "
            f"Per Board 2026-04-22 Wave-4: receipt-honesty is non-negotiable.</system-reminder>",
            file=sys.stdout
        )

    elif drift["severity"] == "warn":
        # 10-30% drift → E1_RECEIPT_DRIFT_WARN
        _emit_cieu("E1_RECEIPT_DRIFT_WARN", event_data, decision="warn")
        agent_id_match = re.search(r'##\s*RECEIPT\s*\(([^#\)]+)', receipt_text)
        agent_label = agent_id_match.group(1).strip() if agent_id_match else "unknown"
        print(
            f"<system-reminder>E1_RECEIPT_DRIFT_WARN: {agent_label} claimed {claimed['total']} "
            f"tool_uses but metadata shows {metadata_tool_uses} "
            f"(drift={drift['drift_pct']*100:.0f}%, warn threshold=10%). "
            f"Not blocking, but CEO should note for trust_score.</system-reminder>",
            file=sys.stdout
        )
    else:
        # <10% drift → E1_RECEIPT_OK (allow, audit trail only)
        _emit_cieu("E1_RECEIPT_OK", event_data, decision="allow")

    return {
        "status": drift["severity"],
        "claimed": claimed,
        "metadata_tool_uses": metadata_tool_uses,
        "drift": drift,
    }


# ════════════════════════════════════════════════════════════════════════════
# Sub-task B: 8 Module Receipt Header Check (Wave-4)
# ════════════════════════════════════════════════════════════════════════════

def check_8_module_header(result_text: str) -> dict:
    """
    Check if sub-agent receipt contains "## 8 Module Activation" segment
    with M1-M8 line markers per aiden_8_module_cognitive_architecture.md.

    Board 2026-04-22 directive: "thinking is behavior" — enforce cognitive
    process visibility in receipt structure.

    Returns dict: {
        "has_header": bool,
        "markers_found": int (0-8),
        "markers_missing": list[str],
        "passed": bool (header present AND >=6 markers),
    }
    """
    # Extract receipt text from <result> block if task-notification present
    result_match = re.search(
        r'<task-notification>.*?<result>(.*?)</result>.*?</task-notification>',
        result_text, re.DOTALL
    )
    receipt_text = result_match.group(1) if result_match else result_text

    has_header = bool(EIGHT_MODULE_HEADER_PATTERN.search(receipt_text))

    markers_found = 0
    markers_missing = []
    for i, marker_pat in enumerate(EIGHT_MODULE_MARKERS, 1):
        if re.search(marker_pat, receipt_text, re.IGNORECASE):
            markers_found += 1
        else:
            markers_missing.append(f"M{i}")

    passed = has_header and markers_found >= 6

    if not passed:
        event_data = {
            "has_header": has_header,
            "markers_found": markers_found,
            "markers_missing": markers_missing,
        }
        _emit_cieu("ENGINEER_RECEIPT_MISSING_8_MODULE_HEADER", event_data, decision="warn")

        if not has_header:
            print(
                "<system-reminder>ENGINEER_RECEIPT_MISSING_8_MODULE_HEADER: "
                "Receipt lacks '## 8 Module Activation' segment. "
                "Per aiden_8_module_cognitive_architecture.md, thinking is behavior — "
                "agent should explicit-show cognitive process (M1-M8) in receipt structure. "
                "Wave-4 baseline period (warn only, 7 days to promote).</system-reminder>",
                file=sys.stdout
            )
        elif markers_found < 6:
            print(
                f"<system-reminder>ENGINEER_RECEIPT_INCOMPLETE_8_MODULE_HEADER: "
                f"Receipt has header but only {markers_found}/8 module markers present "
                f"(missing: {', '.join(markers_missing)}). Need >=6 to pass. "
                f"Per aiden_8_module_cognitive_architecture.md.</system-reminder>",
                file=sys.stdout
            )

    return {
        "has_header": has_header,
        "markers_found": markers_found,
        "markers_missing": markers_missing,
        "passed": passed,
    }


# ════════════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════════════

def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}

    # Only scan Agent tool outputs
    tool_name = payload.get("tool_name", "")
    if tool_name != "Agent":
        print(json.dumps({"action": "allow", "scanned": False, "reason": "not Agent tool"}))
        sys.exit(0)

    # ── CZL-P1-e: Pop agent stack on subagent completion ──
    restored = _pop_agent_stack()
    if restored:
        _emit_cieu("AGENT_STACK_POP", f"restored={restored}")

    # Extract sub-agent text — multiple possible locations
    result_text = ""
    for key in ("tool_result", "result", "output"):
        v = payload.get(key)
        if isinstance(v, str):
            result_text = v
            break
        if isinstance(v, dict):
            result_text = v.get("content", v.get("text", "")) or ""
            break

    # ── W13 original: drift/choice/shell-request scan ──
    hits = _scan(result_text)
    for event_type, meta in hits:
        _emit_cieu(event_type, meta)

    # ── Wave-4 Sub-task A: E1 Receipt-Honesty Check ──
    e1_result = None
    try:
        e1_result = e1_receipt_honesty_check(result_text)
    except Exception as e:
        sys.stderr.write(f"[E1] Receipt honesty check failed (fail-open): {e}\n")

    # ── Wave-4 Sub-task B: 8 Module Header Check ──
    module_result = None
    try:
        module_result = check_8_module_header(result_text)
    except Exception as e:
        sys.stderr.write(f"[8MOD] 8 Module header check failed (fail-open): {e}\n")

    output = {
        "action": "allow",  # PostToolUse always allow (enforcement via system-reminder injection)
        "scanned": True,
        "hits": len(hits),
        "restored_agent": restored,
        "e1_status": e1_result.get("status") if e1_result else "skipped",
        "module_header_passed": module_result.get("passed") if module_result else "skipped",
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
