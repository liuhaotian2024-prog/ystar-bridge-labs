#!/usr/bin/env python3
"""
Prompt Gate Hook (W7.1 — Campaign v3 Phase 3)
Hook into PostToolUse to check CEO output narrative coherence vs current subgoal.

Warns (not blocks) if drift_score > 0.7, emits CIEU event PROMPT_SUBGOAL_DRIFT.
Fail-open on all exceptions.
"""
import json
import sys
import os
from pathlib import Path

# Y*gov module path fix (Board 2026-04-16 P0: ModuleNotFoundError emergency)
sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")

REPO_ROOT = Path(__file__).parent.parent
LOG = REPO_ROOT / "scripts" / "hook_debug.log"

def log(msg):
    """Append to hook_debug.log."""
    with open(LOG, "a", encoding="utf-8") as f:
        import time
        f.write(f"{time.strftime('%H:%M:%S')} [PROMPT_GATE] {msg}\n")

def main():
    try:
        # Read hook payload (PostToolUse format)
        raw = sys.stdin.buffer.read().decode('utf-8-sig')
        payload = json.loads(raw.lstrip(chr(0xFEFF)))

        # ═══ K9 Event-Driven Audit (Board 2026-04-16) ═══
        try:
            from k9_event_trigger import k9_audit_on_event
            from _cieu_helpers import _get_current_agent

            event_type = payload.get("tool_name", "HOOK_POST_CALL")
            agent_id = _get_current_agent()
            k9_audit_on_event(event_type, agent_id, payload)
        except Exception as k9_exc:
            log(f"K9 event audit failed (fail-open): {k9_exc}")

        # Extract assistant reply (PostToolUse provides tool_result, not assistant message)
        # Workaround: read last assistant reply from session transcript or .logs/
        # For MVP: read from .ystar_last_board_msg as proxy (CEO writes there on each reply)
        last_msg_file = REPO_ROOT / "scripts" / ".ystar_last_board_msg"
        if not last_msg_file.exists():
            # Silent skip — this is expected, .ystar_last_board_msg only written on Board interaction
            sys.stdout.write(json.dumps({"action": "allow"}))
            sys.stdout.flush()
            sys.exit(0)

        try:
            reply_text = last_msg_file.read_text(encoding="utf-8")
        except Exception:
            # File exists but unreadable — skip silently
            sys.stdout.write(json.dumps({"action": "allow"}))
            sys.stdout.flush()
            sys.exit(0)

        # Skip if reply is empty or too short (likely not a real CEO reply)
        if not reply_text or len(reply_text.strip()) < 50:
            sys.stdout.write(json.dumps({"action": "allow"}))
            sys.stdout.flush()
            sys.exit(0)

        # Import Y*gov narrative detector
        from ystar.governance.narrative_coherence_detector import check_ceo_output_vs_subgoal

        # Run check
        result = check_ceo_output_vs_subgoal(
            reply_text=reply_text,
            subgoal_file=str(REPO_ROOT / ".czl_subgoals.json")
        )

        drift_score = result.get("drift_score", 0.0)
        if drift_score > 0.7:
            # Emit CIEU event (warn only, not deny)
            try:
                from ystar.adapters.cieu_writer import write_cieu_event
                import json as json_lib
                write_cieu_event(
                    event_type="PROMPT_SUBGOAL_DRIFT",
                    decision="allow",  # Warn-only design
                    agent_id="ceo",
                    drift_detected=1,
                    drift_details=json_lib.dumps({
                        "drift_score": drift_score,
                        "mismatched_keywords": result.get("mismatched_keywords", []),
                        "reply_preview": reply_text[:200]
                    }),
                    drift_category="narrative_coherence"
                )
                log(f"DRIFT detected: score={drift_score:.2f}, CIEU event emitted")
            except Exception as cieu_exc:
                log(f"CIEU event failed: {cieu_exc}")

        # Always allow (warn-only design)
        sys.stdout.write(json.dumps({"action": "allow"}))
        sys.stdout.flush()

    except Exception as e:
        # Fail-open
        log(f"Exception: {e}")
        sys.stdout.write(json.dumps({"action": "allow"}))
        sys.stdout.flush()

if __name__ == "__main__":
    main()
