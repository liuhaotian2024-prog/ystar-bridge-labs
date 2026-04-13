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
from pathlib import Path
from datetime import datetime

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

    elif cond_type == "content_contains":
        keywords = condition.get("keywords", [])
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

        # Check if any keyword appears in content
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

    # Check tool match
    allowed_tools = trigger.get("tool", [])
    if allowed_tools and payload.get("tool") not in allowed_tools:
        return False

    # Check all conditions (AND logic)
    conditions = trigger.get("conditions", [])
    for condition in conditions:
        if not check_condition(condition, payload, context):
            return False

    return True


def emit_cieu_event(event_type: str, rule_id: str, severity: str):
    """Emit a CIEU drift event (stub — real implementation would use cieu_trace.py)"""
    # For now, just log to stderr
    # Future: integrate with cieu_trace.py or Y*gov MCP gov_remember
    timestamp = datetime.utcnow().isoformat() + "Z"
    print(f"[CIEU_DRIFT] {timestamp} | {event_type} | rule={rule_id} severity={severity}",
          file=sys.stderr)


def emit_warning(rule_id: str, recipe: str):
    """Print warning with recipe to stderr"""
    banner = "=" * 70
    print(f"\n{banner}", file=sys.stderr)
    print(f"[FORGET_GUARD] Rule violated: {rule_id}", file=sys.stderr)
    print(f"{banner}", file=sys.stderr)
    print(recipe, file=sys.stderr)
    print(f"{banner}\n", file=sys.stderr)


def main():
    """Main entry point — read stdin, evaluate rules, emit warnings"""
    try:
        # Read payload from stdin
        payload_raw = sys.stdin.read()
        if not payload_raw.strip():
            sys.exit(0)

        payload_input = json.loads(payload_raw)

        # Normalize payload schema (support both flat and nested formats)
        # Flat: {"tool": "Bash", "command": "..."} (real PreToolUse format)
        # Nested: {"tool_input": {"command": "..."}} (legacy format)
        if "tool_input" in payload_input:
            payload = payload_input["tool_input"]
            payload["tool"] = payload_input.get("tool_name", "unknown")
        else:
            payload = payload_input

        # Build context
        context = {
            "active_agent": get_active_agent(),
            "ceo_mode": get_ceo_mode(),
        }

        # Load rules
        rules_path = Path.cwd() / "governance" / "forget_guard_rules.yaml"
        rules_data = load_rules(rules_path)

        if not rules_data.get("global_enable", False):
            sys.exit(0)

        # Evaluate each rule
        for rule in rules_data.get("rules", []):
            if evaluate_rule(rule, payload, context):
                rule_id = rule.get("id", "unknown")
                recipe = rule.get("recipe", "No recipe provided.")
                cieu_event = rule.get("cieu_event", "UNKNOWN_DRIFT")
                severity = rule.get("severity", "medium")

                # Emit warning and CIEU event
                emit_warning(rule_id, recipe)
                emit_cieu_event(cieu_event, rule_id, severity)

        sys.exit(0)

    except Exception as e:
        # Fail-open: don't block execution on ForgetGuard errors
        print(f"[FORGET_GUARD] Error (fail-open): {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
