#!/usr/bin/env python3
"""
ForgetGuard — Institutional Memory Enforcement Engine
AMENDMENT-020, 2026-04-13

Reads hook payload from stdin, evaluates forget_guard_rules.yaml,
emits CIEU drift events + actionable recipes to stderr.

Design: warn-not-deny, fail-open, async fire from hook_client_labs.sh
"""

import sys
import json
import re
import os
import sqlite3
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent))
from _cieu_helpers import _get_current_agent, emit_cieu

try:
    import yaml
except ImportError:
    # Fail-open if yaml not available
    sys.exit(0)


def load_rules(rules_path: Path) -> dict:
    """Load and parse forget_guard_rules.yaml"""
    try:
        if not rules_path.exists():
            return {"global_enable": False, "rules": []}

        with open(rules_path, 'r', encoding='utf-8') as f:
            rules_data = yaml.safe_load(f)

        return rules_data or {"global_enable": False, "rules": []}
    except Exception:
        # Fail-open on parse errors
        return {"global_enable": False, "rules": []}


def get_active_agent() -> str:
    """Read current active agent from .ystar_active_agent"""
    try:
        agent_file = Path.cwd() / ".ystar_active_agent"
        if agent_file.exists():
            return agent_file.read_text().strip()
    except Exception:
        pass
    return "unknown"


def get_ceo_mode() -> str:
    """Read CEO mode from .ystar_session.json"""
    try:
        session_file = Path.cwd() / ".ystar_session.json"
        if session_file.exists():
            with open(session_file, 'r') as f:
                session_data = json.load(f)
                return session_data.get("ceo_mode", {}).get("status", "normal")
    except Exception:
        pass
    return "normal"


def check_condition(condition: dict, payload: dict, context: dict) -> bool:
    """Evaluate a single trigger condition"""
    cond_type = condition.get("type")

    if cond_type == "path_match":
        pattern = condition.get("pattern", "")
        contexts = condition.get("context", [])
        if isinstance(contexts, str):
            contexts = [contexts]

        # Check command (for Bash tool) or file_path (for Edit/Write)
        for ctx in contexts:
            if ctx == "command" and "command" in payload:
                if re.search(pattern, payload["command"]):
                    return True
            elif ctx == "file_path" and "file_path" in payload:
                file_path = payload["file_path"]

                # Convert absolute path to relative path from ystar-company/
                if "ystar-company/" in file_path:
                    file_path = file_path.split("ystar-company/")[1]
                elif "Y-star-gov/" in file_path:
                    file_path = file_path.split("Y-star-gov/")[1]

                if re.search(pattern, file_path):
                    return True
        return False

    elif cond_type == "file_path_not_matches":
        pattern = condition.get("pattern", "")
        if "file_path" not in payload:
            return False

        file_path = payload["file_path"]

        # Convert absolute path to relative path
        if "ystar-company/" in file_path:
            file_path = file_path.split("ystar-company/")[1]
        elif "Y-star-gov/" in file_path:
            file_path = file_path.split("Y-star-gov/")[1]

        # Return True if pattern does NOT match (inverse of path_match)
        return not re.search(pattern, file_path)

    elif cond_type == "content_contains":
        keywords = condition.get("keywords", [])
        require_companion = condition.get("require_companion", [])
        content = ""

        # Extract content from various payload fields
        if "content" in payload:
            content = payload["content"]
        elif "new_string" in payload:
            content = payload["new_string"]
        elif "command" in payload:
            content = payload["command"]

        if not content:
            return False

        # W10.1: Multi-keyword AND logic
        # If require_companion is set, BOTH a keyword AND a companion must be present
        if require_companion:
            has_keyword = any(keyword in content for keyword in keywords)
            has_companion = any(companion in content for companion in require_companion)
            return has_keyword and has_companion
        else:
            # Original OR logic: any keyword triggers
            for keyword in keywords:
                if keyword in content:
                    return True
            return False

    elif cond_type == "content_missing":
        pattern = condition.get("pattern", "")
        content = ""

        if "content" in payload:
            content = payload["content"]
        elif "new_string" in payload:
            content = payload["new_string"]
        elif "command" in payload:
            content = payload["command"]

        if not content:
            return True  # Empty content = missing pattern

        # Return True if pattern NOT found
        return not re.search(pattern, content)

    elif cond_type == "active_agent_equals":
        value = condition.get("value", "")
        return context.get("active_agent") == value

    elif cond_type == "ceo_mode_not_equals":
        value = condition.get("value", "")
        return context.get("ceo_mode") != value

    elif cond_type == "addressee_context":
        value = condition.get("value", "")
        # Heuristic: check if content mentions Board/board/老大/Haotian
        content = ""
        if "content" in payload:
            content = payload["content"]
        elif "new_string" in payload:
            content = payload["new_string"]

        if value == "board":
            return any(term in content.lower() for term in ["board", "老大", "haotian", "董事会"])
        return False

    return False


def evaluate_rule(rule: dict, payload: dict, context: dict) -> bool:
    """Evaluate if a rule's trigger conditions are met"""
    if not rule.get("enabled", True):
        return False

    trigger = rule.get("trigger", {})

    # Check agent_filter (if specified, rule only applies to those agents)
    agent_filter = trigger.get("agent_filter", [])
    if agent_filter:
        current_agent = context.get("active_agent", "unknown")
        if current_agent not in agent_filter:
            return False

    # Check tool match (normalize: Claude Code sends "tool_name", yaml says "tool")
    allowed_tools = trigger.get("tool", [])
    actual_tool = payload.get("tool_name") or payload.get("tool") or ""
    if allowed_tools and actual_tool not in allowed_tools:
        return False

    # Check conditions (logic: OR or AND)
    conditions = trigger.get("conditions", [])
    if not conditions:
        return True

    # Get logic mode (default to OR for backward compatibility)
    logic_mode = trigger.get("logic", "OR").upper()

    if logic_mode == "AND":
        # AND logic: ALL conditions must match
        for condition in conditions:
            if not check_condition(condition, payload, context):
                return False  # One fail → rule doesn't match
        return True  # All passed → rule matches
    else:
        # OR logic (default): ANY condition match triggers the rule
        for condition in conditions:
            if check_condition(condition, payload, context):
                return True
        return False


def emit_cieu_event(event_type: str, rule_id: str, severity: str, payload: dict):
    """Emit a CIEU drift event to .ystar_cieu.db"""
    try:
        db_path = Path.cwd() / ".ystar_cieu.db"
        if not db_path.exists():
            print(f"[FORGET_GUARD_EMIT] ERROR: CIEU DB not found at {db_path}", file=sys.stderr)
            return

        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()

        # Get session_id and agent_id from session file
        session_file = Path.cwd() / ".ystar_session.json"
        session_id = "unknown"
        agent_id = "forget_guard"
        if session_file.exists():
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    session_id = session_data.get("session_id", "unknown")
            except Exception:
                pass

        # Get next seq_global
        c.execute("SELECT MAX(seq_global) FROM cieu_events")
        max_seq = c.fetchone()[0]
        seq_global = (max_seq or 0) + 1

        # Generate event_id
        event_id = f"fg_{int(datetime.utcnow().timestamp() * 1000)}_{seq_global}"
        created_at = datetime.utcnow().timestamp()

        # Build drift_details
        drift_details = json.dumps({
            "rule_id": rule_id,
            "severity": severity,
            "tool": payload.get("tool", "unknown"),
            "file_path": payload.get("file_path"),
            "command": payload.get("command"),
        })

        # Insert event using emit_cieu helper
        emit_cieu(
            event_type=event_type,
            decision="warn",
            passed=0,
            task_description=f"Rule {rule_id} violated (severity: {severity})",
            session_id=session_id,
            drift_detected=1,
            drift_details=drift_details,
            drift_category="institutional_memory",
            file_path=payload.get("file_path"),
            command=payload.get("command"),
            evidence_grade="drift"
        )

        conn.commit()
        conn.close()

        print(f"[FORGET_GUARD_EMIT] {event_type} | rule={rule_id} severity={severity}", file=sys.stderr)

    except Exception as e:
        # Fail-open: don't crash on CIEU errors
        print(f"[FORGET_GUARD_EMIT] ERROR: {e}", file=sys.stderr)


def emit_warning(rule_id: str, recipe: str):
    """Print warning with recipe to stderr"""
    banner = "=" * 70
    print(f"\n{banner}", file=sys.stderr)
    print(f"[FORGET_GUARD] Rule violated: {rule_id}", file=sys.stderr)
    print(f"{banner}", file=sys.stderr)
    print(recipe, file=sys.stderr)
    print(f"{banner}\n", file=sys.stderr)


def main():
    """Main entry point — read stdin, evaluate rules, emit warnings + JSON action"""
    try:
        # Read payload from stdin
        payload_raw = sys.stdin.read()
        if not payload_raw.strip():
            # Campaign v3: always output JSON
            print(json.dumps({"action": "allow", "rules_triggered": []}))
            sys.exit(0)

        payload_input = json.loads(payload_raw)

        # Normalize payload schema (support multiple formats)
        # Format 1: PreToolUse flat {"tool": "Bash", "command": "..."}
        # Format 2: Legacy nested {"tool_input": {"command": "..."}, "tool_name": "Bash"}
        # Format 3: Stress test flat (same as Format 1)
        # Format 4: Claude Code PreToolUse {"tool_name": "Bash", "command": "..."}
        if "tool_input" in payload_input:
            # Legacy nested format
            payload = payload_input["tool_input"]
            payload["tool"] = payload_input.get("tool_name", "unknown")
        elif "tool" in payload_input:
            # PreToolUse flat format (most common)
            payload = payload_input
        elif "tool_name" in payload_input:
            # Claude Code PreToolUse format (tool_name at root level)
            payload = payload_input
            payload["tool"] = payload_input["tool_name"]
        else:
            # Unknown format — fail-open
            print(json.dumps({"action": "allow", "rules_triggered": [], "reason": "unknown_format"}))
            sys.exit(0)

        # Build context
        context = {
            "active_agent": get_active_agent(),
            "ceo_mode": get_ceo_mode(),
        }

        # Gap 2: Reload rules on EVERY call (with mtime-based cache invalidation)
        rules_path = Path.cwd() / "governance" / "forget_guard_rules.yaml"
        if not hasattr(main, '_rules_cache'):
            main._rules_cache = {}

        try:
            current_mtime = rules_path.stat().st_mtime_ns if rules_path.exists() else 0
            cached_mtime = main._rules_cache.get('mtime', -1)

            if current_mtime != cached_mtime:
                # Reload rules
                rules_data = load_rules(rules_path)
                main._rules_cache = {'mtime': current_mtime, 'rules': rules_data}
            else:
                rules_data = main._rules_cache['rules']
        except Exception:
            # Fail-open on mtime check failure — reload every time
            rules_data = load_rules(rules_path)

        if not rules_data.get("global_enable", False):
            print(json.dumps({"action": "allow", "rules_triggered": []}))
            sys.exit(0)

        # Evaluate each rule — collect violations
        triggered_rules = []
        deny_action = False

        for rule in rules_data.get("rules", []):
            if evaluate_rule(rule, payload, context):
                rule_id = rule.get("id", "unknown")
                recipe = rule.get("recipe", "No recipe provided.")
                cieu_event = rule.get("cieu_event", "UNKNOWN_DRIFT")
                severity = rule.get("severity", "medium")
                action = rule.get("action", "warn")

                # Emit warning and CIEU event
                emit_warning(rule_id, recipe)
                emit_cieu_event(cieu_event, rule_id, severity, payload)

                triggered_rules.append(rule_id)

                # Campaign v3: action=deny → block execution
                if action == "deny":
                    deny_action = True

        # Output JSON result (Campaign v3 sync protocol)
        result = {
            "action": "deny" if deny_action else "allow",
            "rules_triggered": triggered_rules
        }
        print(json.dumps(result))

        sys.exit(0)

    except Exception as e:
        # Fail-open: don't block execution on ForgetGuard errors
        print(f"[FORGET_GUARD] Error (fail-open): {e}", file=sys.stderr)
        print(json.dumps({"action": "allow", "rules_triggered": [], "error": str(e)}))
        sys.exit(0)


if __name__ == "__main__":
    main()
