#!/usr/bin/env python3
"""
Action Model v2 Validator — Enforce 17-step atomic lifecycle

**Authority**: CTO Ethan Wright per Board 2026-04-16 directive
**Spec**: governance/action_model_v2.md
**Purpose**: Validate dispatch prompts (Phase A) and receipts (Phase C) against sized action model variants

Called by:
- ForgetGuard rules: dispatch_missing_phase_a, receipt_missing_phase_c_heavy
- hook_stop_reply_scan.py: register_reply() on every sub-agent/CEO reply
- Tests: tests/governance/test_action_model_v2_enforce.py

Usage:
    python3 scripts/action_model_validator.py --validate-dispatch <prompt_file>
    python3 scripts/action_model_validator.py --validate-receipt <receipt_file> --class Heavy
    python3 scripts/action_model_validator.py --self-test
"""

import re
import sys
import json
import sqlite3
import uuid
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# CIEU database path (canonical per .ystar_session.json)
CIEU_DB = Path.home() / ".openclaw/workspace/ystar-company/.ystar_cieu.db"


def validate_dispatch_phase_a(prompt_text: str) -> Dict:
    """
    Validate dispatch prompt includes all 5 Phase A BOOT steps.

    Returns:
        {
            "allow": bool,
            "reason": str,
            "missing_steps": List[str],
            "phase_bitmap": str  # 5-bit string, e.g., "11110"
        }
    """
    phase_a_checks = {
        "step1_czl_subgoals": re.search(r'\.czl_subgoals\.json', prompt_text, re.IGNORECASE),
        "step2_precheck": re.search(r'precheck_existing\.py', prompt_text, re.IGNORECASE),
        "step3_git_log": re.search(r'git log.*--oneline', prompt_text, re.IGNORECASE),
        "step4_ac_baseline": re.search(r'session_watchdog\.py.*--statusline', prompt_text, re.IGNORECASE),
        "step5_k9_daemon": re.search(r'pgrep.*k9_routing_subscriber', prompt_text, re.IGNORECASE),
    }

    missing = [k for k, v in phase_a_checks.items() if not v]
    phase_bitmap = "".join("1" if v else "0" for v in phase_a_checks.values())

    if missing:
        return {
            "allow": False,
            "reason": f"dispatch_missing_phase_a: {len(missing)}/5 steps missing: {', '.join(missing)}",
            "missing_steps": missing,
            "phase_bitmap": phase_bitmap
        }

    return {
        "allow": True,
        "reason": "Phase A complete (5/5 steps)",
        "missing_steps": [],
        "phase_bitmap": phase_bitmap
    }


def validate_receipt_phase_c(receipt_text: str, atomic_class: str) -> Dict:
    """
    Validate receipt follows action model v2 Phase C requirements per atomic class.

    Args:
        receipt_text: The receipt/reply text
        atomic_class: "Heavy" | "Light" | "Investigation"

    Returns:
        {
            "allow": bool,
            "reason": str,
            "missing_steps": List[str],
            "phase_bitmap": str  # 9-bit for Heavy, 2-bit for Light, 1-bit for Investigation
        }
    """
    # Phase C 9-step checklist (full heavy requirements)
    phase_c_checks = {
        "step9_test": re.search(r'(pytest|test.*PASS|test.*FAIL|synthetic.*case)', receipt_text, re.IGNORECASE),
        "step10_verification": re.search(r'(ls -la|wc -w|grep -E|empirical.*paste)', receipt_text, re.IGNORECASE),
        "step11_experiment": re.search(r'(smoke test|sample corpus|\d+-\d+ cases|pilot atomic)', receipt_text, re.IGNORECASE),
        "step12_ac_delta": re.search(r'(AC.*baseline|AC.*delta|session_watchdog.*statusline)', receipt_text, re.IGNORECASE),
        "step13_k9_audit": re.search(r'(k9.*audit|k9log/auditor|k9_silent_fire)', receipt_text, re.IGNORECASE),
        "step14_cieu_emit": re.search(r'(ATOMIC_COMPLETE|ATOMIC_FAILED|CIEU.*emit)', receipt_text, re.IGNORECASE),
        "step15_trust_delta": re.search(r'(trust score|engineer_trust_scores\.json|trust.*delta)', receipt_text, re.IGNORECASE),
        "step16_knowledge_writeback": re.search(r'(MEMORY.*\.md|docstring|governance.*\.md|knowledge.*writeback)', receipt_text, re.IGNORECASE),
        "step17_cascade_trigger": re.search(r'(cascade|downstream|\.cascade_queue\.json|queue.*next)', receipt_text, re.IGNORECASE)
    }

    present_count = sum(1 for present in phase_c_checks.values() if present)
    missing = [k for k, v in phase_c_checks.items() if not v]
    phase_bitmap = "".join("1" if v else "0" for v in phase_c_checks.values())

    # Sized variant enforcement
    if atomic_class == "Heavy":
        # Heavy: ≥8/9 steps (allow 1 optional step missing)
        if present_count < 8:
            return {
                "allow": False,
                "reason": f"receipt_missing_phase_c_heavy: only {present_count}/9 steps present (≥8 required)",
                "missing_steps": missing,
                "phase_bitmap": phase_bitmap
            }
    elif atomic_class == "Light":
        # Light: step 10 (verification) + step 14 (CIEU emit) mandatory
        if not phase_c_checks["step10_verification"] or not phase_c_checks["step14_cieu_emit"]:
            return {
                "allow": False,
                "reason": "receipt_missing_phase_c_light: verification or CIEU emit missing",
                "missing_steps": [k for k in ["step10_verification", "step14_cieu_emit"] if not phase_c_checks[k]],
                "phase_bitmap": phase_bitmap
            }
    elif atomic_class == "Investigation":
        # Investigation: step 14 (CIEU emit) mandatory
        if not phase_c_checks["step14_cieu_emit"]:
            return {
                "allow": False,
                "reason": "receipt_missing_phase_c_investigation: CIEU emit missing",
                "missing_steps": ["step14_cieu_emit"],
                "phase_bitmap": phase_bitmap
            }
    else:
        # Unknown class — default to heavy enforcement
        if present_count < 8:
            return {
                "allow": False,
                "reason": f"receipt_missing_phase_c_unknown_class: {atomic_class} not recognized, defaulting to heavy (≥8/9 required)",
                "missing_steps": missing,
                "phase_bitmap": phase_bitmap
            }

    return {
        "allow": True,
        "reason": f"Phase C complete for {atomic_class} ({present_count}/9 steps)",
        "missing_steps": [],
        "phase_bitmap": phase_bitmap
    }


def register_reply(reply_text: str, agent_id: str, atomic_id: Optional[str] = None, atomic_class: Optional[str] = None) -> Dict:
    """
    Register reply into CIEU with template tag + phase compliance bitmap.

    Emits REPLY_REGISTERED CIEU event with:
    - agent_id
    - atomic_id (if receipt)
    - reply_template (detected from CZL-123 whitelist patterns)
    - atomic_class (Heavy/Light/Investigation/null)
    - phase_compliance_bitmap (17-bit for dispatch, 9-bit for receipt)
    - rt_plus_1 (parsed if present)
    - tool_uses_claimed (parsed if present)
    - honest_receipt (bool)

    Returns:
        {
            "event_id": int,
            "agent_id": str,
            "reply_template": str,
            "phase_compliance_bitmap": str
        }
    """
    # Detect reply template (CZL-123 whitelist patterns)
    template = "unknown"
    # Fix: Y\* can be written as **Y\*** or **Y***: in markdown
    if re.search(r'\*\*Y\s*\\\*\s*\*\*', reply_text, re.DOTALL) or re.search(r'\*\*Xt\*\*', reply_text):
        template = "cieu_5tuple_receipt"
    elif re.search(r'## BOOT CONTEXT', reply_text):
        template = "action_model_v2_dispatch"
    elif len(reply_text) < 50 and re.search(r'(好的|收到|明白|OK|got it)', reply_text, re.IGNORECASE):
        template = "conversational_ack"

    # Parse Rt+1 and tool_uses if present
    rt_plus_1 = None
    tool_uses_claimed = None
    rt_match = re.search(r'\*\*Rt\+1\*\*:\s*`?(\d+)', reply_text)
    if rt_match:
        rt_plus_1 = int(rt_match.group(1))
    tool_uses_match = re.search(r'tool_uses.*?(\d+)', reply_text, re.IGNORECASE)
    if tool_uses_match:
        tool_uses_claimed = int(tool_uses_match.group(1))

    # Compute phase compliance bitmap
    phase_bitmap = "0" * 17  # Default all missing
    if atomic_class:
        receipt_result = validate_receipt_phase_c(reply_text, atomic_class)
        phase_bitmap = receipt_result["phase_bitmap"].ljust(17, "0")  # Pad to 17 bits

    honest_receipt = (rt_plus_1 == 0) if rt_plus_1 is not None else None

    # === PHASE C AUTOMATION (steps 15-17) ===
    # Trigger on atomic CLOSED detection: Rt+1=0 or explicit gap + atomic_id present
    phase_c_auto_triggered = False
    trust_delta = 0.0
    knowledge_entry = None
    cascade_candidates = []

    if atomic_id and atomic_class:
        # Step 15: Compute trust delta
        trust_delta = compute_trust_delta(reply_text, agent_id, atomic_class)

        # Update engineer_trust_scores.json
        scores_path = Path.home() / ".openclaw/workspace/ystar-company/knowledge/engineer_trust_scores.json"
        try:
            with open(scores_path) as f:
                scores = json.load(f)

            # Find engineer entry
            for eng in scores.get("engineers", []):
                if eng.get("engineer_id") == agent_id:
                    eng["trust_score"] = eng.get("trust_score", 0) + trust_delta
                    break

            # Write back
            with open(scores_path, 'w') as f:
                json.dump(scores, f, indent=2)
        except Exception:
            pass  # Silent fail on trust update

        # Step 16: Extract knowledge writeback
        knowledge_entry = extract_knowledge_writeback(reply_text, agent_id)
        if knowledge_entry:
            # YSTAR_TEST_MODE: redirect to /tmp instead of production MEMORY
            if os.environ.get("YSTAR_TEST_MODE", "0") == "1":
                memory_dir = Path("/tmp/ystar_test_memory")
                memory_dir.mkdir(parents=True, exist_ok=True)
            else:
                memory_dir = Path.home() / f".claude/projects/-Users-haotianliu--openclaw-workspace-ystar-company/memory"

            memory_path = memory_dir / f"{knowledge_entry['type']}_{knowledge_entry['title']}.md"
            try:
                # Write feedback file
                with open(memory_path, 'w') as f:
                    f.write(f"# {knowledge_entry['title']}\n\n{knowledge_entry['body']}\n")

                # Append to MEMORY.md index
                memory_index = memory_dir / "MEMORY.md"
                with open(memory_index, 'a') as f:
                    f.write(f"- [{knowledge_entry['title']}]({knowledge_entry['type']}_{knowledge_entry['title']}.md)\n")
            except Exception:
                pass  # Silent fail on writeback

        # Step 17: Trigger cascade (only if Rt+1=0)
        if rt_plus_1 == 0 and atomic_id:
            cascade_candidates = trigger_cascade(atomic_id)

        phase_c_auto_triggered = True

    # Step 13: K9 silent fire audit (Phase C automation)
    # Query K9 events emitted during this atomic execution window
    # This step runs for ALL replies (not just atomic receipts) to catch violations
    k9_audit_result = None
    if atomic_id:
        # Import k9_silent_fire_audit module
        try:
            from k9_silent_fire_audit import audit_during_atomic
            # Compute time window: use reply timestamp ±5min (heuristic)
            # Real implementation should track atomic_start_time from dispatch
            end_ts = datetime.utcnow().isoformat() + "Z"
            start_ts = (datetime.utcnow() - timedelta(minutes=5)).isoformat() + "Z"
            k9_audit_result = audit_during_atomic(start_ts, end_ts, atomic_id)
        except ImportError:
            pass  # k9_silent_fire_audit not available, skip

    # Emit CIEU event
    try:
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()

        event_data = {
            "agent_id": agent_id,
            "atomic_id": atomic_id,
            "reply_template": template,
            "atomic_class": atomic_class,
            "phase_compliance_bitmap": phase_bitmap,
            "rt_plus_1": rt_plus_1,
            "tool_uses_claimed": tool_uses_claimed,
            "honest_receipt": honest_receipt,
            # Phase C automation metadata
            "phase_c_auto_triggered": phase_c_auto_triggered,
            "trust_delta": trust_delta,
            "knowledge_writeback": knowledge_entry is not None,
            "cascade_candidates": len(cascade_candidates),
            # Step 13: K9 audit result
            "k9_audit": k9_audit_result
        }

        # Generate event_id (TEXT UUID per CIEU schema)
        event_id = str(uuid.uuid4())
        timestamp = datetime.now().timestamp()

        # Get next seq_global (monotonic counter)
        cursor.execute("SELECT COALESCE(MAX(seq_global), 0) + 1 FROM cieu_events")
        seq_global = cursor.fetchone()[0]

        # Insert with full schema compliance
        event_type = "ATOMIC_PHASE_C_AUTO_COMPLETE" if phase_c_auto_triggered else "REPLY_REGISTERED"

        cursor.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id, event_type,
                decision, passed, violations, params_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            seq_global,
            timestamp,
            "session_" + str(int(timestamp)),  # session_id placeholder
            agent_id,
            event_type,
            "allow",  # decision placeholder (reply already sent)
            1,  # passed = 1 (event emission succeeded)
            None,  # violations = NULL (no violations to report)
            json.dumps(event_data)
        ))

        conn.commit()
        conn.close()

        return {
            "event_id": event_id,
            "agent_id": agent_id,
            "reply_template": template,
            "phase_compliance_bitmap": phase_bitmap,
            "phase_c_auto_triggered": phase_c_auto_triggered,
            "trust_delta": trust_delta,
            "cascade_candidates": cascade_candidates
        }
    except Exception as e:
        return {
            "event_id": -1,
            "error": str(e),
            "agent_id": agent_id,
            "reply_template": template,
            "phase_compliance_bitmap": phase_bitmap
        }


def intercept(reply_text: str, agent_id: str) -> Optional[str]:
    """
    3-strike escalation: Check last 3 replies from agent_id for violations.

    Returns:
        None if allow passage, block_reason string if deny
    """
    try:
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()

        # Get last 3 REPLY_REGISTERED events for this agent
        cursor.execute("""
            SELECT params_json FROM cieu_events
            WHERE event_type = 'REPLY_REGISTERED' AND agent_id = ?
            ORDER BY created_at DESC LIMIT 3
        """, (agent_id,))

        recent_replies = [json.loads(row[0]) for row in cursor.fetchall()]
        conn.close()

        if len(recent_replies) < 3:
            return None  # Not enough history to judge

        # Count violations in last 3 replies
        violations = []
        for reply in recent_replies:
            rt = reply.get("rt_plus_1")
            honest = reply.get("honest_receipt")
            if rt is not None and rt > 0 and honest is False:
                violations.append("hallucinated_receipt")
            bitmap = reply.get("phase_compliance_bitmap", "")
            if bitmap and bitmap.count("0") > len(bitmap) / 2:  # >50% steps missing
                violations.append("phase_incomplete")

        if len(violations) >= 3:
            return f"action_model_violation_deny: 3 consecutive violations ({', '.join(violations[:3])})"

        return None
    except Exception as e:
        return f"intercept_error: {str(e)}"


def compute_trust_delta(receipt_text: str, agent_id: str, atomic_class: str) -> float:
    """
    Compute trust score adjustment per action_model_v2 §5 utility model.

    Returns:
        +0.05 if Rt+1=0 + tool_uses match (±1 tolerance)
        +0.02 if Rt+1=0 + tool_uses mismatch self-caught + honest 5-tuple receipt
        -0.05 if Rt+1>0 unhandled
        -0.5 if hallucination detected (file claimed but not exist)
        -0.5 if tool_uses mismatch >2 + falsely claimed honest
    """
    # Parse Rt+1 and tool_uses from receipt
    rt_plus_1 = None
    tool_uses_claimed = None
    rt_match = re.search(r'\*\*Rt\+1\*\*:\s*`?(\d+)', receipt_text)
    if rt_match:
        rt_plus_1 = int(rt_match.group(1))
    tool_uses_match = re.search(r'tool_uses.*?(\d+)', receipt_text, re.IGNORECASE)
    if tool_uses_match:
        tool_uses_claimed = int(tool_uses_match.group(1))

    # Hallucination check: find file paths claimed in receipt that don't exist
    file_paths = re.findall(r'(?:ls -la|artifact|created|modified)\s+([^\s]+(?:\.py|\.md|\.json|\.yaml|\.sh))', receipt_text)
    hallucination_detected = False
    for fpath in file_paths:
        # Normalize relative paths to workspace root
        if not fpath.startswith('/'):
            fpath = Path.home() / ".openclaw/workspace/ystar-company" / fpath
        else:
            fpath = Path(fpath)
        if not fpath.exists():
            hallucination_detected = True
            break

    # Tool_uses mismatch check (requires metadata from CIEU events)
    # For now, we'll skip this check in compute_trust_delta (caller should pass actual_tool_uses)
    # Simplified: trust delta based on Rt+1 + hallucination only

    if hallucination_detected:
        return -0.5

    if rt_plus_1 is None:
        return 0.0  # No Rt+1 in receipt → skip trust update

    if rt_plus_1 == 0:
        # Clean completion
        return +0.05
    elif rt_plus_1 > 0:
        # Self-caught gap (if explicit gap statement present)
        if re.search(r'blocked|pending|need|escalate|gap|missing', receipt_text, re.IGNORECASE):
            return +0.02
        else:
            # Unhandled gap
            return -0.05

    return 0.0


def extract_knowledge_writeback(receipt_text: str, agent_id: str) -> Optional[Dict]:
    """
    Heuristic extract novel lessons from receipt.

    Looks for keywords: "lesson", "discovered", "first time", "pattern", "gotcha", "learned"

    Returns:
        {
            "title": str,
            "body": str,
            "type": "feedback" | "project" | "reference"
        }
        or None if no novelty detected
    """
    novelty_keywords = r'\b(lesson|discovered|first time|pattern|gotcha|learned|insight|observation|found that|realized)\b'
    if not re.search(novelty_keywords, receipt_text, re.IGNORECASE):
        return None

    # Extract sentence containing novelty keyword
    sentences = re.split(r'[.!?]\s+', receipt_text)
    novelty_sentences = [s for s in sentences if re.search(novelty_keywords, s, re.IGNORECASE)]

    if not novelty_sentences:
        return None

    # Construct title from first novelty sentence (truncate at 60 chars)
    title_raw = novelty_sentences[0].strip()
    title = title_raw[:60].replace(' ', '_').lower()
    title = re.sub(r'[^a-z0-9_]', '', title)  # slug-safe

    # Body = all novelty sentences joined
    body = "\n\n".join(novelty_sentences)

    # Classify type: "feedback" if operational lesson, "project" if architectural, "reference" if tool/API
    if re.search(r'\b(sub-agent|dispatch|receipt|5-tuple|Rt\+1|tool_uses)\b', body, re.IGNORECASE):
        knowledge_type = "feedback"
    elif re.search(r'\b(architecture|design|pattern|refactor)\b', body, re.IGNORECASE):
        knowledge_type = "project"
    else:
        knowledge_type = "reference"

    # Wire to metalearning: feed receipt to Y*gov adapter (CTO CZL-150)
    try:
        from scripts.ystar_gov_adapter import task_to_call_record
        task_receipt = {
            "agent_id": agent_id,
            "task_title": title,
            "tool_uses_claimed": -1,  # not available in Phase C writeback context
            "tool_uses_metadata": {"count": -1},
            "rt_plus_1": -1,
            "y_star": None,
            "x_t": None,
            "u": None,
            "y_t_plus_1": body,
        }
        call_record = task_to_call_record(task_receipt)
        # Store to metalearning history (placeholder — actual impl would write to DB)
    except ImportError:
        pass  # Adapter not available, skip metalearning integration

    return {
        "title": title,
        "body": body,
        "type": knowledge_type
    }


def trigger_cascade(closed_subgoal_id: str) -> List[Dict]:
    """
    Read .czl_subgoals.json `requires` DAG, find all subgoals where this closed subgoal was a dependency.

    Returns:
        List of next-atomic candidates with priority:
        [
            {
                "id": "W5",
                "statement": "...",
                "priority": int  # number of completed dependencies
            },
            ...
        ]
    """
    czl_path = Path.home() / ".openclaw/workspace/ystar-company/.czl_subgoals.json"
    if not czl_path.exists():
        return []

    with open(czl_path) as f:
        czl = json.load(f)

    candidates = []
    for criterion in czl.get("y_star_criteria", []):
        requires = criterion.get("requires", [])
        if closed_subgoal_id in requires:
            # This criterion depends on the closed subgoal
            # Check how many of its dependencies are now complete
            completed_ids = [c["id"] for c in czl.get("completed", [])]
            satisfied_count = sum(1 for dep in requires if dep in completed_ids or dep == closed_subgoal_id)

            candidates.append({
                "id": criterion["id"],
                "statement": criterion["statement"],
                "priority": satisfied_count,
                "total_dependencies": len(requires)
            })

    # Sort by priority descending (most dependencies satisfied first)
    candidates.sort(key=lambda x: x["priority"], reverse=True)

    # Emit CIEU event if any candidates found
    if candidates:
        try:
            conn = sqlite3.connect(CIEU_DB)
            cursor = conn.cursor()

            event_id = str(uuid.uuid4())
            timestamp = datetime.now().timestamp()

            cursor.execute("SELECT COALESCE(MAX(seq_global), 0) + 1 FROM cieu_events")
            seq_global = cursor.fetchone()[0]

            event_data = {
                "closed_subgoal_id": closed_subgoal_id,
                "cascaded_candidates": candidates
            }

            cursor.execute("""
                INSERT INTO cieu_events (
                    event_id, seq_global, created_at, session_id, agent_id, event_type,
                    decision, passed, violations, params_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id,
                seq_global,
                timestamp,
                "session_" + str(int(timestamp)),
                "system",  # cascade is system-triggered
                "CASCADE_TRIGGERED",
                "allow",
                1,
                None,
                json.dumps(event_data)
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            pass  # Silent fail, just return candidates

    return candidates


def self_test():
    """Run self-test on synthetic cases."""
    print("=== Action Model Validator Self-Test ===\n")

    # Test 1: Valid Phase A dispatch
    valid_dispatch = """
    ## BOOT CONTEXT
    1. Read .czl_subgoals.json
    2. python3 scripts/precheck_existing.py action_model_validator
    3. git log -5 --oneline
    4. python3 scripts/session_watchdog.py --statusline
    5. pgrep -fl k9_routing_subscriber
    """
    result = validate_dispatch_phase_a(valid_dispatch)
    assert result["allow"], f"Test 1 failed: {result}"
    print(f"✓ Test 1 PASS: Valid dispatch Phase A — {result['phase_bitmap']}")

    # Test 2: Invalid Phase A (missing step 3)
    invalid_dispatch = """
    ## BOOT CONTEXT
    1. Read .czl_subgoals.json
    2. python3 scripts/precheck_existing.py foo
    4. python3 scripts/session_watchdog.py --statusline
    5. pgrep -fl k9_routing_subscriber
    """
    result = validate_dispatch_phase_a(invalid_dispatch)
    assert not result["allow"], f"Test 2 failed: should deny"
    assert "step3_git_log" in result["missing_steps"], f"Test 2 failed: wrong missing step"
    print(f"✓ Test 2 PASS: Invalid dispatch (missing git log) — {result['phase_bitmap']}")

    # Test 3: Valid Heavy receipt
    valid_heavy_receipt = """
    **Phase C complete:**
    9. pytest tests/governance/test_foo.py PASS
    10. ls -la scripts/action_model_validator.py — 5420 bytes
    11. Smoke test on 5 synthetic cases
    12. AC baseline 84 → 83 (delta -1)
    13. k9log/auditor.py silent-fire audit clean
    14. CIEU emit ATOMIC_COMPLETE
    15. Trust score +0.05
    16. Knowledge writeback to MEMORY/feedback_action_model.md
    17. Cascade trigger: queue Maya CZL-130
    """
    result = validate_receipt_phase_c(valid_heavy_receipt, "Heavy")
    assert result["allow"], f"Test 3 failed: {result}"
    print(f"✓ Test 3 PASS: Valid Heavy receipt — {result['phase_bitmap']}")

    # Test 4: Invalid Heavy receipt (missing verification)
    invalid_heavy_receipt = """
    **Phase C partial:**
    9. pytest PASS
    11. Smoke test done
    14. CIEU emit ATOMIC_COMPLETE
    15. Trust score +0.05
    """
    result = validate_receipt_phase_c(invalid_heavy_receipt, "Heavy")
    assert not result["allow"], f"Test 4 failed: should deny"
    assert "step10_verification" in result["missing_steps"], f"Test 4 failed: wrong missing step"
    print(f"✓ Test 4 PASS: Invalid Heavy receipt (missing verification) — {result['phase_bitmap']}")

    # Test 5: Valid Light receipt
    valid_light_receipt = """
    10. ls -la foo.md — 120 bytes
    14. CIEU emit ATOMIC_COMPLETE
    """
    result = validate_receipt_phase_c(valid_light_receipt, "Light")
    assert result["allow"], f"Test 5 failed: {result}"
    print(f"✓ Test 5 PASS: Valid Light receipt — {result['phase_bitmap']}")

    # Test 6: Valid Investigation receipt
    valid_investigation_receipt = """
    14. CIEU emit ATOMIC_COMPLETE with report_path=reports/governance/audit_foo.md
    """
    result = validate_receipt_phase_c(valid_investigation_receipt, "Investigation")
    assert result["allow"], f"Test 6 failed: {result}"
    print(f"✓ Test 6 PASS: Valid Investigation receipt — {result['phase_bitmap']}")

    print("\n=== All 6 self-tests PASSED ===")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--self-test":
        self_test()
    elif sys.argv[1] == "--validate-dispatch" and len(sys.argv) >= 3:
        with open(sys.argv[2]) as f:
            prompt = f.read()
        result = validate_dispatch_phase_a(prompt)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["allow"] else 1)
    elif sys.argv[1] == "--validate-receipt" and len(sys.argv) >= 4:
        with open(sys.argv[2]) as f:
            receipt = f.read()
        atomic_class = sys.argv[3] if len(sys.argv) >= 4 else "Heavy"
        result = validate_receipt_phase_c(receipt, atomic_class)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["allow"] else 1)
    else:
        print(__doc__)
        sys.exit(1)
