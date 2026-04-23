#!/usr/bin/env python3
"""
W10 — Stop Hook: Post-reply prose scan
Purpose: Scan CEO assistant reply after Claude finishes (Stop event), detect
  defer_language / choice_question / drift keywords, emit CIEU event.
  Warn-level only (does NOT block, reply already sent). Fail-open.

Wiring: .claude/settings.json `hooks.Stop` entry invokes this.
"""
import json
import os
import re
import sqlite3
import sys
import time
import uuid
from pathlib import Path

REPO_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
CIEU_DB = REPO_ROOT / ".ystar_cieu.db"

# ── Y-star-gov Adapter Imports (Board 2026-04-16: wire orphan injectors) ─────
sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")
try:
    from ystar.adapters.hooks.stop_hook import (
        inject_warnings_to_session,
        inject_czl_corrections,
        auto_validate_subagent_receipt,
        inject_coordinator_audit_warning,
        scan_action_promises,
    )
    _YSTAR_ADAPTERS_AVAILABLE = True
except ImportError as e:
    _YSTAR_ADAPTERS_AVAILABLE = False
    print(f"[W10] Y-star-gov adapters unavailable: {e}", file=sys.stderr)

# ── Coordinator audit helper import (Board 2026-04-16: 5-tuple enforcement) ─────
sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")
try:
    from ystar.governance.coordinator_audit import check_reply_5tuple_compliance
    _COORD_AUDIT_AVAILABLE = True
except ImportError as e:
    _COORD_AUDIT_AVAILABLE = False
    print(f"[W10] coordinator_audit unavailable: {e}", file=sys.stderr)

# ── Reply taxonomy whitelist import (Maya CZL-123: whitelist-first enforcement) ─────
try:
    from ystar.governance.reply_taxonomy import audit_reply
    _REPLY_TAXONOMY_AVAILABLE = True
except ImportError as e:
    _REPLY_TAXONOMY_AVAILABLE = False
    print(f"[W10] reply_taxonomy unavailable: {e}", file=sys.stderr)

# ── Action Model v2 reply registration (Maya CZL-129: register every reply into CIEU) ─────
sys.path.insert(0, str(REPO_ROOT / "scripts"))
try:
    from action_model_validator import register_reply
    _ACTION_MODEL_VALIDATOR_AVAILABLE = True
except ImportError as e:
    _ACTION_MODEL_VALIDATOR_AVAILABLE = False
    print(f"[W10] action_model_validator unavailable: {e}", file=sys.stderr)

# ═══ WHITELIST DESIGN (Board 2026-04-15 night) ═══
# CEO 只有两种合法状态。不在白名单 = deny。
# 比黑名单（N 个 defer 词永远追不完）根本性优越。
#
# State A: Board 工作状态（Board 在线 → 执行 Board 指令）
# State B: 自主工作学习状态（Board 离线 → Article 11 / 系统测试 / 学习 / 长期设计）
# 没有第三种状态。"idle" / "等指令" / "报告完等下步" 不存在。

# ACTION-ONLY whitelist (Board 2026-04-15 night root fix — topic keywords 被剥离)
# 原设计 bug: "Rt+1/归零/Campaign" 是 topic keywords 不是 action，reply 提到 topic
# 就被当 "在工作"，实际零 action = idle 伪装进白名单后门。
WORK_SIGNALS = [
    # ONLY tool call evidence (CEO 真在做事)
    "commit", "push", "Bash", "Edit", "Write", "Agent", "grep", "Read",
    "pytest", "python3", "git ", "dispatch",
    # ONLY active verb (CEO 说下一步具体动作)
    "立刻", "正在",
    # sub-agent EXPLICIT spawn reference (含 agent_id 前缀才算)
    "派 Ethan", "派 Maya", "派 Leo", "派 Ryan", "派 Samantha", "派 Sofia", "派 Marco", "派 Zara",
    "sub-agent 派",
]

# ═══ STATE MACHINE WHITELIST (Board 2026-04-15 night 真根治) ═══
# 黑名单永远列不完。CEO 只有 3 个合法 state，其他全 deny:
#
# STATE_BOARD_DIRECTIVE: 正在执行 Board 明确指令的任务
# STATE_AUTONOMOUS_WORK: 既有 active campaign 未 Rt+1=0，继续推进
# STATE_BOARD_STOP:      Board 明确指令停止 (唯一合法停止)
#
# Reply 必须含 ≥1 of these state-evidence patterns (whitelist):

import re

STATE_EVIDENCE_PATTERNS = [
    # Pattern 1: commit hash evidence (CEO/sub-agent 真 ship 了)
    re.compile(r'\b[0-9a-f]{7,40}\b'),  # git short/full hash
    # Pattern 2: 显式 dispatch (派 + 任意 agent name OR sub-agent ID)
    re.compile(r'派\s*(Ethan|Maya|Leo|Ryan|Samantha|Sofia|Marco|Zara|sub-agent)'),
    re.compile(r'\b(a[0-9a-f]{16})\b'),  # sub-agent id pattern (today's format)
    # Pattern 3: Board 直接引用 (含"老大"/"Board"+ 任务 quote)
    re.compile(r'(老大|Board)[^\n]{0,80}["「『]'),
    # Pattern 4: tool action evidence (commit/push/edit/agent 真发生)
    re.compile(r'(commit|push|Edit|Write|Bash|Agent|Read|Grep)\s*\(?[^\s]'),
    # Pattern 5: Rt+1 verify action (实际归零证据，非 topic mention)
    re.compile(r'Rt\+1\s*=\s*0\s*[✓✅]'),
    # Pattern 6: Board explicit stop quote
    re.compile(r'Board\s*(明令停|说停|说收工|stop|今晚到这)'),
]

# 任意 1 pattern match = STATE 在白名单 = allow
# 0 pattern match = STATE_UNDEFINED = drift event


def _read_last_assistant_reply(payload: dict) -> str:
    """Try to extract the latest assistant reply from hook payload."""
    # Claude Code Stop hook payload shape is evolving; best-effort extract
    txt = payload.get("assistant_message", "") or payload.get("reply_text", "")
    if txt:
        return txt
    # Fallback: read session transcript if path given
    tp = payload.get("transcript_path")
    if tp and Path(tp).exists():
        try:
            lines = Path(tp).read_text(encoding="utf-8").strip().split("\n")
            for line in reversed(lines[-20:]):
                try:
                    obj = json.loads(line)
                    if obj.get("role") == "assistant":
                        content = obj.get("content", "")
                        if isinstance(content, list):
                            for block in content:
                                if block.get("type") == "text":
                                    return block.get("text", "")
                        return str(content)
                except Exception:
                    continue
        except Exception:
            pass
    return ""


# ═══ IRON RULE 0 — Choice Question Scanner (Board 2026-04-15 Constitutional) ═══
# Standalone scanner used by Stop hook AND importable for unit tests.
# Detects forbidden choice-question patterns in both Chinese and English.
# Returns structured matches with pattern name, matched text, and position.

_IRON_RULE_0_PATTERNS = [
    # Chinese patterns
    ("chinese_choose", re.compile(r"请选择")),
    ("chinese_plan_abc", re.compile(r"方案[一二三四五六七八九十]")),
    ("chinese_pick_one", re.compile(r"三选一")),
    ("chinese_you_decide", re.compile(r"您决定.{0,10}(哪个|A.{0,3}还是.{0,3}B)")),
    # English patterns
    ("english_option_letter", re.compile(r"Option\s+[A-Z]:", re.IGNORECASE)),
    ("english_option_number", re.compile(r"Option\s+\d:", re.IGNORECASE)),
    ("english_n_paths", re.compile(r"We have \d+ paths", re.IGNORECASE)),
    ("english_which_prefer", re.compile(r"Which.{0,20}prefer", re.IGNORECASE)),
]


def scan_for_choice_question(reply_text: str) -> list:
    """Scan reply text for Iron Rule 0 forbidden choice-question patterns.

    Returns a list of dicts: [{"pattern": str, "match": str, "position": int}, ...]
    Empty list = no violations detected.
    """
    if not reply_text:
        return []
    results = []
    for pattern_name, compiled in _IRON_RULE_0_PATTERNS:
        m = compiled.search(reply_text)
        if m:
            results.append({
                "pattern": pattern_name,
                "match": m.group(),
                "position": m.start(),
            })
    return results


def inject_iron_rule_0_warning(reply_text: str, scan_results: list) -> str:
    """Given scan results from scan_for_choice_question, return a warning string.

    Returns empty string if no violations.
    """
    if not scan_results:
        return ""
    violations = "; ".join(
        f"[{r['pattern']}] \"{r['match']}\" @pos={r['position']}"
        for r in scan_results
    )
    return (
        f"<system-reminder>IRON RULE 0 VIOLATION: Choice question detected in reply. "
        f"Violations: {violations}. "
        f"CEO must pick the best option and execute, never ask Board to choose. "
        f"See CLAUDE.md Iron Rule 0.</system-reminder>"
    )


def _scan(text: str) -> dict:
    """STATE MACHINE WHITELIST (Board 2026-04-15 night 真根治).
    CEO 只有 3 合法 state. Reply 必须含 ≥1 STATE_EVIDENCE_PATTERN.
    任何不在白名单的 state = STATE_UNDEFINED drift.
    根本性优于黑名单（永远列不完）。"""
    if not text:
        return {"triggered": False, "rules": []}
    rules_triggered = []

    # WHITELIST: 任意 1 pattern match = legal state
    matched_patterns = []
    for pattern in STATE_EVIDENCE_PATTERNS:
        if pattern.search(text):
            matched_patterns.append(pattern.pattern[:60])

    if not matched_patterns:
        rules_triggered.append({
            "rule": "state_undefined_drift",
            "detail": "CEO reply 不在合法 state 白名单 (BOARD_DIRECTIVE/AUTONOMOUS_WORK/BOARD_STOP). 缺 ≥1 of: commit hash / dispatch (派 <agent>) / Board quote / tool action / Rt+1=0✓ / Board explicit stop. 此 reply 等价 IDLE/UNDEFINED."
        })

    # Legacy choice pattern check (still useful as explicit violation)
    CHOICE_PATTERNS = [
        r"请选择.*[方案]?\s*[12二]",
        r"Option [AB]",
        r"\b1[\)）]\s*.*2[\)）]",
        r"方案[12一二]",
    ]
    for pat in CHOICE_PATTERNS:
        if re.search(pat, text):
            rules_triggered.append({"rule": "choice_question_in_reply", "pattern": pat})
            break
    return {"triggered": bool(rules_triggered), "rules": rules_triggered}


def _emit_cieu(event_type: str, metadata: dict) -> None:
    try:
        from _cieu_helpers import emit_cieu as _central_emit
        _central_emit(
            event_type=event_type,
            decision="warn",
            passed=1,
            task_description=json.dumps(metadata, ensure_ascii=False)[:500],
            session_id="reply_scan",
        )
    except Exception:
        pass  # fail-open


def inject_reply_taxonomy_whitelist_audit(reply_text: str, agent_id: str) -> None:
    """
    6th injector (NEW — Maya CZL-123): Reply taxonomy whitelist validator.

    Checks if reply starts with one of 5 template tags (DISPATCH/RECEIPT/NOTIFICATION/QUERY/ACK).
    Validates template structure constraints per governance/reply_taxonomy_whitelist_v1.md.

    FAIL-OPEN: If validator unavailable, skip check (governance is advisory, not hard-blocking).
    BIDIRECTIONAL: After whitelist check, ALSO run existing 5-tuple blacklist check (defense-in-depth).
    """
    if not _REPLY_TAXONOMY_AVAILABLE:
        # Fail-open: skip whitelist check if module unavailable
        return

    # Call whitelist validator
    violation = audit_reply(reply_text, agent_id)

    if violation:
        # Emit CIEU event
        _emit_cieu(
            event_type="REPLY_TEMPLATE_VIOLATION",
            metadata=violation
        )

        # Inject system reminder for next turn
        warning = (
            f"<system-reminder>⚠️ REPLY_TEMPLATE_VIOLATION: {violation['correction_hint']} "
            f"Errors: {', '.join(violation['errors'])}. "
            f"See governance/reply_taxonomy_whitelist_v1.md for template specs.</system-reminder>"
        )
        print(warning, file=sys.stdout)


def auto_compare_tool_uses_claim(receipt_text: str, metadata_tool_uses: int, agent_id: str = "unknown") -> None:
    """
    7th injector (NEW — Maya CZL-152 P0): Auto tool_uses claim vs metadata comparison.

    Context: CEO currently manually catches sub-agent over-claims (9/14 agents today).
    This must be automated.

    Extracts tool_uses claim from receipt text ("tool_uses: N" or "N tool_uses" pattern),
    compares with task-notification metadata <tool_uses>N</tool_uses>,
    emits CIEU TOOL_USES_CLAIM_MISMATCH if |claim - actual| > 2 (tolerance threshold).

    Args:
        receipt_text: Sub-agent receipt text (from <result> block)
        metadata_tool_uses: Actual tool_uses count from <metadata> tag
        agent_id: Agent ID for CIEU event attribution

    Emits:
        CIEU event TOOL_USES_CLAIM_MISMATCH if delta > 2
        Warning injection to session if mismatch detected
    """
    # Extract claimed tool_uses from receipt text
    claim_match = re.search(r'tool_uses.*?(\d+)', receipt_text, re.IGNORECASE)
    if not claim_match:
        # No claim in receipt — acceptable for conversational acks
        return

    claimed = int(claim_match.group(1))
    actual = metadata_tool_uses
    delta = abs(claimed - actual)

    # Tolerance: ±2 tool_uses acceptable (small counting variations)
    if delta <= 2:
        return

    # MISMATCH DETECTED — emit CIEU + inject warning
    _emit_cieu(
        event_type="TOOL_USES_CLAIM_MISMATCH",
        metadata={
            "agent_id": agent_id,
            "claimed": claimed,
            "actual": actual,
            "delta": delta,
            "severity": "high" if delta > 5 else "medium",
            "receipt_excerpt": receipt_text[:200]
        }
    )

    # Inject warning to session
    warning = (
        f"<system-reminder>⚠️ TOOL_USES_CLAIM_MISMATCH: {agent_id} claimed {claimed} tool_uses "
        f"but metadata shows {actual} (delta={delta}, threshold=2). "
        f"Over-claiming erodes trust_score. Honest receipt required per CZL framework. "
        f"See feedback_subagent_receipt_empirical_verify.md.</system-reminder>"
    )
    print(warning, file=sys.stdout)


def inject_coordinator_reply_5tuple_audit(reply_text: str) -> None:
    """
    5th injector: Coordinator reply 5-tuple compliance enforcement.

    Board 2026-04-16 hypocrisy catch: CEO dispatches use 5-tuple but replies to Board
    are pure prose tables/散文. Violates CZL dogfood principle.

    Extracts reply body from Stop hook stdin, calls coordinator_audit helper,
    emits CIEU event + injects warning to LLM stdin on violation.

    FAIL-CLOSED (Ryan CZL-112 fix): If helper unavailable, emit COORDINATOR_AUDIT_UNAVAILABLE
    event + try basic regex fallback (detect 5-tuple labels in prose). Don't silently skip.
    """
    # FAIL-CLOSED PATH (Ryan CZL-112): emit unavailable event + try fallback regex
    if not _COORD_AUDIT_AVAILABLE:
        _emit_cieu(
            event_type="COORDINATOR_AUDIT_UNAVAILABLE",
            metadata={
                "import_failure": True,
                "fallback_mode": "basic_regex_labels"
            }
        )
        # Fallback: detect explicit 5-tuple labels (English + Chinese prose allowed)
        # Pattern: "**Y\***" / "**Xt**" / "**U**" / "**Yt+1**" / "**Rt+1**" (markdown bold)
        # Chinese prose with English labels acceptable: "**Y\***：内容..." passes
        required_labels = [r"\*\*Y\\\*\*\*", r"\*\*Xt\*\*", r"\*\*U\*\*", r"\*\*Yt\+1\*\*", r"\*\*Rt\+1\*\*"]
        missing_labels = []
        for label in required_labels:
            if not re.search(label, reply_text):
                missing_labels.append(label.replace(r"\*\*", "**").replace(r"\\", "\\"))

        if missing_labels and len(reply_text) > 200:
            _emit_cieu(
                event_type="COORDINATOR_REPLY_MISSING_5TUPLE",
                metadata={
                    "violation": True,
                    "missing_sections": missing_labels,
                    "char_count": len(reply_text),
                    "fallback_mode": True
                }
            )
            missing_str = ", ".join(missing_labels)
            warning = (
                f"<system-reminder>⚠️ CZL: reply {len(reply_text)} chars "
                f"missing 5-tuple labels [{missing_str}]. Dogfood CZL framework — "
                f"all coordinator replies >200 chars MUST include **Y\\***, **Xt**, **U**, "
                f"**Yt+1**, **Rt+1** section labels (Chinese prose OK, labels English). "
                f"Pure prose violates Board 2026-04-14 directive. [FALLBACK MODE: helper unavailable]</system-reminder>"
            )
            print(warning, file=sys.stdout)
        return  # exit after fallback attempt

    # NORMAL PATH: helper available, use full audit logic
    try:
        violation = check_reply_5tuple_compliance(reply_text)
        if violation:
            # Emit CIEU event
            _emit_cieu(
                event_type="COORDINATOR_REPLY_MISSING_5TUPLE",
                metadata={
                    "violation": True,
                    "missing_sections": violation["missing_sections"],
                    "char_count": violation["char_count"],
                }
            )

            # Inject warning to LLM session (stdout will be captured by hook runtime)
            missing = ", ".join(violation["missing_sections"])
            warning = (
                f"<system-reminder>⚠️ CZL: reply {violation['char_count']} chars "
                f"missing 5-tuple sections [{missing}]. Dogfood CZL framework — "
                f"all coordinator replies >200 chars MUST include **Y\\***, **Xt**, **U**, "
                f"**Yt+1**, **Rt+1** section labels. Pure prose violates Board 2026-04-14 "
                f"directive.</system-reminder>"
            )
            print(warning, file=sys.stdout)
    except Exception as e:
        # fail-open — do not block reply on audit failure
        print(f"[W10] 5-tuple audit exception: {e}", file=sys.stderr)


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}
    reply = _read_last_assistant_reply(payload)
    scan = _scan(reply)
    if scan["triggered"]:
        for r in scan["rules"]:
            _emit_cieu("DEFER_IN_REPLY_DRIFT" if r["rule"] == "defer_in_reply" else "CHOICE_IN_REPLY_DRIFT", r)

    # ── Y-star-gov Injector Calls (Board 2026-04-16: wire orphan code) ───────
    # ── NEW INJECTOR #7 (Maya CZL-129): Action Model v2 reply registration FIRST ───────
    # Register EVERY reply into CIEU with template tag + phase compliance bitmap
    # Per action_model_v2.md §6 — must happen BEFORE whitelist/blacklist checks
    agent_id = payload.get("agent_id", "ceo")  # default to ceo if not in payload
    if _ACTION_MODEL_VALIDATOR_AVAILABLE:
        try:
            # Detect atomic_id and atomic_class from reply if present
            atomic_id_match = re.search(r'(CZL-\d+|#\d+)', reply)
            atomic_id = atomic_id_match.group(1) if atomic_id_match else None
            atomic_class_match = re.search(r'atomic.*?class.*?(Heavy|Light|Investigation)', reply, re.IGNORECASE)
            atomic_class = atomic_class_match.group(1).capitalize() if atomic_class_match else None

            reg_result = register_reply(reply, agent_id, atomic_id, atomic_class)
            if reg_result.get("event_id", -1) > 0:
                # Successfully registered — emit debug log
                print(f"[W10] REPLY_REGISTERED event_id={reg_result['event_id']} agent={agent_id} template={reg_result['reply_template']}", file=sys.stderr)
        except Exception as e:
            print(f"[W10] register_reply failed: {e}", file=sys.stderr)

    # ── NEW INJECTOR #6 (Maya CZL-123): Reply taxonomy whitelist SECOND ───────
    # Whitelist-first architecture: check template tags BEFORE blacklist semantics
    inject_reply_taxonomy_whitelist_audit(reply, agent_id)

    if _YSTAR_ADAPTERS_AVAILABLE:
        # 1. K9-RT warnings injection
        try:
            k9_warnings = inject_warnings_to_session()
            if k9_warnings:
                print(k9_warnings, file=sys.stdout)
        except Exception as e:
            print(f"[W10] K9-RT inject failed: {e}", file=sys.stderr)

        # 2. CZL Gate 2 corrections (receipt validation) — CEO main-thread reply
        try:
            czl_correction = inject_czl_corrections(receipt_text=reply)
            if czl_correction:
                print(czl_correction, file=sys.stdout)
        except Exception as e:
            print(f"[W10] CZL inject failed: {e}", file=sys.stderr)

        # 3. Auto-validate sub-agent receipt (E2) — CEO main-thread reply
        try:
            validation = auto_validate_subagent_receipt(receipt_text=reply)
            if not validation.get("is_valid"):
                print(f"[W10] Receipt validation failed: Rt={validation.get('actual_rt')}", file=sys.stderr)
        except Exception as e:
            print(f"[W10] Receipt auto-validate failed: {e}", file=sys.stderr)

        # 4. TASK-NOTIFICATION extraction (Board 2026-04-16 Gate 2 fix)
        # Sub-agent receipts come through task-notification blocks, not CEO main-thread.
        # Extract each <result>...</result> + <metadata>, validate separately.
        try:
            # NEW (Maya CZL-152): Extract full task-notification with metadata
            notification_full_pattern = re.compile(
                r'<task-notification>.*?<metadata>.*?<tool_uses>(\d+)</tool_uses>.*?</metadata>.*?<result>(.*?)</result>.*?</task-notification>',
                re.DOTALL
            )
            notification_matches = notification_full_pattern.finditer(reply)

            for match in notification_matches:
                metadata_tool_uses = int(match.group(1))
                receipt_text = match.group(2)

                # Extract agent_id from receipt if present (format: "## RECEIPT (AgentName #CZL-N)")
                agent_id_match = re.search(r'##\s*RECEIPT\s*\(([^#\)]+)', receipt_text)
                receipt_agent_id = agent_id_match.group(1).strip() if agent_id_match else "unknown"

                # NEW INJECTOR #7 (Maya CZL-152): Auto tool_uses claim comparison
                try:
                    auto_compare_tool_uses_claim(receipt_text, metadata_tool_uses, receipt_agent_id)
                except Exception as e:
                    print(f"[W10] Tool_uses claim comparison failed: {e}", file=sys.stderr)

                # Per-receipt CZL correction
                try:
                    czl_receipt_correction = inject_czl_corrections(receipt_text=receipt_text)
                    if czl_receipt_correction:
                        print(czl_receipt_correction, file=sys.stdout)
                except Exception as e:
                    print(f"[W10] Task-notification CZL inject failed: {e}", file=sys.stderr)

                # Per-receipt auto-validation
                try:
                    receipt_validation = auto_validate_subagent_receipt(
                        receipt_text=receipt_text,
                        declared_artifacts=None,
                        metadata_tool_uses=metadata_tool_uses,
                    )
                    if not receipt_validation.get("is_valid"):
                        print(f"[W10] Task-notification receipt validation failed: Rt={receipt_validation.get('actual_rt')}", file=sys.stderr)
                except Exception as e:
                    print(f"[W10] Task-notification receipt auto-validate failed: {e}", file=sys.stderr)
        except Exception as e:
            print(f"[W10] Task-notification extraction failed: {e}", file=sys.stderr)

        # 5. Coordinator audit warning (meta-gate)
        try:
            coord_warning = inject_coordinator_audit_warning(reply_text=reply)
            if coord_warning:
                print(coord_warning, file=sys.stdout)
        except Exception as e:
            print(f"[W10] Coordinator audit inject failed: {e}", file=sys.stderr)

        # 6. Coordinator reply 5-tuple compliance (Board 2026-04-16 hypocrisy fix)
        try:
            inject_coordinator_reply_5tuple_audit(reply_text=reply)
        except Exception as e:
            print(f"[W10] Coordinator reply 5-tuple audit failed: {e}", file=sys.stderr)

        # 7. ARCH-11c: Action promise vs tool_use scan (Leo core + Ryan wiring)
        try:
            _res = scan_action_promises(reply, len(payload.get("tool_uses", [])), agent_id)
            if _res.get("warning"):
                print(_res["warning"], file=sys.stdout)
        except Exception as e:
            print(f"[W10] ARCH-11c scan_action_promises failed: {e}", file=sys.stderr)

    # Stop hook: never block, always exit 0
    print(json.dumps({"action": "allow", "scanned": scan["triggered"]}))
    sys.exit(0)


if __name__ == "__main__":
    main()
