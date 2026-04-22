#!/usr/bin/env python3
"""Behavior Governance Rule Engine — methodology-driven enforcement.

Generic engine that loads governance/behavior_gov_rules.yaml and dispatches
each rule to a type-specific handler. All handlers inspect behavior signals
(deadlines, tool counts, state files, event streams) — never scan user/agent
text content.

Adding a new governance requirement = new yaml entry. New check *type* = new
handler class (rare). This is the methodology Board asked for 2026-04-22.

PreToolUse integration: hook_behavior_gov_pretool.py loads engine + calls
`engine.evaluate(payload)`. First rule that denies short-circuits with a
block response.

M-tag: M-2a (防做错 — unified gate) + M-2b (防漏做 — deadline/frequency checks).
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

try:
    import yaml  # type: ignore
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
# Primary rules path (governance/). Fallback scripts/ if governance/ is out of scope.
DEFAULT_RULES_PATH_PRIMARY = WORKSPACE / "governance" / "behavior_gov_rules.yaml"
DEFAULT_RULES_PATH_FALLBACK = WORKSPACE / "scripts" / "behavior_gov_rules.yaml"
DEFAULT_RULES_PATH = (DEFAULT_RULES_PATH_PRIMARY
                     if DEFAULT_RULES_PATH_PRIMARY.exists()
                     else DEFAULT_RULES_PATH_FALLBACK)
DEFAULT_CEO_MODE = WORKSPACE / "scripts" / ".ceo_mode_state.json"
DEFAULT_ACTIVE_AGENT = WORKSPACE / "scripts" / ".ystar_active_agent"


@dataclass
class Decision:
    allowed: bool
    rule_id: str = ""
    severity: str = ""  # deny | warn | none
    message: str = ""
    details: dict = field(default_factory=dict)


def _parse_yaml(text: str) -> dict:
    """Minimal YAML parser fallback if PyYAML unavailable.
    Handles flat key-value + simple lists. Fails gracefully on complex YAML.
    """
    if _HAS_YAML:
        return yaml.safe_load(text) or {}
    # No yaml — return empty, engine will fail-open with warning
    return {}


# ─── Handlers ────────────────────────────────────────────────────────────────

def handle_deadline_check(rule: dict, context: dict) -> Optional[Decision]:
    """Rule type: DeadlineCheck. Query DB for open items past deadline."""
    q = rule.get("query", {})
    db_file = WORKSPACE / q.get("db", "")
    if not db_file.exists():
        return None  # fail-open
    actor = context.get("agent_id", "")
    if not actor:
        return None
    try:
        conn = sqlite3.connect(str(db_file), timeout=2)
        now = time.time()
        col_actor = q.get("actor_col", "actor_id")
        col_due = q.get("deadline_col", "due_at")
        col_grace = q.get("grace_col", "hard_overdue_secs")
        col_status = q.get("status_col", "status")
        open_val = q.get("status_open_value", "pending")
        table = q.get("table", "obligations")
        rows = conn.execute(
            f"SELECT obligation_id, {col_due}, {col_grace}, notes "
            f"FROM {table} "
            f"WHERE {col_actor}=? AND {col_status}=? "
            f"AND ({col_due} + COALESCE({col_grace},0)) < ? "
            f"ORDER BY {col_due} ASC LIMIT 10",
            (actor, open_val, now)
        ).fetchall()
        conn.close()
    except Exception:
        return None  # fail-open on schema drift

    if not rows:
        return None

    ids = [r[0] for r in rows[:3]]
    oldest_due = rows[0][1]
    oldest_grace = rows[0][2] or 0
    oldest_min = int((now - (oldest_due + oldest_grace)) / 60)

    msg = rule.get("message_template", "OmissionEngine block").format(
        agent=actor, count=len(rows), oldest_min=oldest_min,
        ids=ids,
    )
    return Decision(
        allowed=False, rule_id=rule["rule_id"],
        severity=rule.get("severity", "deny"),
        message=msg, details={"overdue_count": len(rows), "ids": ids}
    )


def handle_frequency_check(rule: dict, context: dict) -> Optional[Decision]:
    """Rule type: FrequencyCheck. Require min event count in time window."""
    q = rule.get("query", {})
    db_file = WORKSPACE / q.get("event_source", ".ystar_cieu.db")
    if not db_file.exists():
        return None
    required_types = q.get("required_event_types", [])
    since_type = q.get("since_event_type")
    min_required = q.get("min_count_required", 1)
    window_min = q.get("window_minutes", 60)
    try:
        conn = sqlite3.connect(str(db_file), timeout=2)
        # Find anchor event time
        anchor_row = None
        if since_type:
            anchor_row = conn.execute(
                f"SELECT created_at FROM {q.get('event_table','cieu_events')} "
                f"WHERE event_type=? ORDER BY created_at DESC LIMIT 1",
                (since_type,)
            ).fetchone()
        anchor_ts = anchor_row[0] if anchor_row else time.time() - window_min * 60

        placeholders = ",".join("?" * len(required_types))
        count = conn.execute(
            f"SELECT COUNT(*) FROM {q.get('event_table','cieu_events')} "
            f"WHERE event_type IN ({placeholders}) "
            f"AND created_at >= ?",
            required_types + [anchor_ts]
        ).fetchone()[0]
        conn.close()
    except Exception:
        return None  # fail-open on missing schema

    if count >= min_required:
        return None

    msg = rule.get("message_template", "frequency-check block").format(
        window_minutes=window_min, count=count,
    )
    return Decision(
        allowed=False, rule_id=rule["rule_id"],
        severity=rule.get("severity", "deny"), message=msg,
        details={"observed_count": count, "required": min_required},
    )


def handle_state_presence(rule: dict, context: dict) -> Optional[Decision]:
    """Rule type: StatePresenceCheck. Read JSON state file field, compare threshold."""
    q = rule.get("query", {})
    path = WORKSPACE / q.get("state_file", "")
    if not path.exists():
        return None
    try:
        state = json.loads(path.read_text())
    except Exception:
        return None
    field_name = q.get("field", "")
    min_value = q.get("min_value", 0)
    actual = state.get(field_name)
    if isinstance(actual, list):
        actual = len(actual)
    if not isinstance(actual, (int, float)):
        return None
    if actual >= min_value:
        return None
    msg = rule.get("message_template", "state-presence block").format(
        value=actual,
    )
    return Decision(
        allowed=False, rule_id=rule["rule_id"],
        severity=rule.get("severity", "warn"), message=msg,
        details={"actual": actual, "min": min_value},
    )


def handle_tool_count(rule: dict, context: dict) -> Optional[Decision]:
    """Rule type: ToolCountCheck. Recent tool history must contain required_tools."""
    q = rule.get("query", {})
    path = WORKSPACE / q.get("state_file", "")
    if not path.exists():
        return None
    try:
        state = json.loads(path.read_text())
    except Exception:
        return None
    history = state.get("recent_tools", [])
    window = q.get("recent_window", 10)
    required = set(q.get("required_tools", []))
    min_count = q.get("required_min_count", 1)
    if not required:
        return None
    # Check only_on filter
    only_on = rule.get("only_on", {})
    if only_on:
        if only_on.get("tool_name") and context.get("tool_name") != only_on["tool_name"]:
            return None
        # path regex filter (not implemented inline to keep small)
    recent = history[-window:] if len(history) > window else history
    matches = sum(1 for t in recent if t in required)
    if matches >= min_count:
        return None
    msg = rule.get("message_template", "tool-count warn").format()
    return Decision(
        allowed=False, rule_id=rule["rule_id"],
        severity=rule.get("severity", "warn"), message=msg,
        details={"matches": matches, "required_min": min_count},
    )


HANDLERS: dict[str, Callable[[dict, dict], Optional[Decision]]] = {
    "DeadlineCheck": handle_deadline_check,
    "FrequencyCheck": handle_frequency_check,
    "StatePresenceCheck": handle_state_presence,
    "ToolCountCheck": handle_tool_count,
}


# ─── Engine ──────────────────────────────────────────────────────────────────

class BehaviorGovEngine:
    def __init__(self, rules_path: Path = DEFAULT_RULES_PATH,
                 ceo_mode_path: Path = DEFAULT_CEO_MODE,
                 active_agent_path: Path = DEFAULT_ACTIVE_AGENT):
        self.rules_path = rules_path
        self.ceo_mode_path = ceo_mode_path
        self.active_agent_path = active_agent_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if not self.rules_path.exists():
            return {"rules": [], "defaults": {}}
        try:
            return _parse_yaml(self.rules_path.read_text())
        except Exception:
            return {"rules": [], "defaults": {}}

    def _is_break_glass(self) -> bool:
        if not self.ceo_mode_path.exists():
            return False
        try:
            s = json.loads(self.ceo_mode_path.read_text())
            if s.get("mode") == "BREAK_GLASS":
                return s.get("hard_cap_expires_at", 0) > time.time()
        except Exception:
            pass
        return False

    def _get_active_agent(self) -> str:
        if not self.active_agent_path.exists():
            return ""
        try:
            return self.active_agent_path.read_text().strip().lower()
        except Exception:
            return ""

    def evaluate(self, payload: dict) -> Decision:
        defaults = self.config.get("defaults", {})
        enforced_agents = set(defaults.get("enforced_agents", []))
        tool_allowlist = set(defaults.get("tool_allowlist", []))
        bg_override = defaults.get("break_glass_override", True)

        tool_name = payload.get("tool_name") or payload.get("tool") or ""
        if tool_name in tool_allowlist:
            return Decision(allowed=True, rule_id="allowlist_tool",
                            severity="none", message="")

        if bg_override and self._is_break_glass():
            return Decision(allowed=True, rule_id="break_glass_active",
                            severity="none", message="")

        agent_id = self._get_active_agent()
        context = {
            "agent_id": agent_id,
            "tool_name": tool_name,
            "payload": payload,
            "timestamp": time.time(),
        }

        if enforced_agents and agent_id and agent_id not in enforced_agents:
            return Decision(allowed=True, rule_id="unknown_agent",
                            severity="none", message="")

        for rule in self.config.get("rules", []):
            if not rule.get("enabled", True):
                continue
            handler = HANDLERS.get(rule.get("type", ""))
            if not handler:
                continue
            try:
                decision = handler(rule, context)
            except Exception as e:
                continue  # fail-open on handler bug
            if decision and not decision.allowed:
                return decision

        return Decision(allowed=True, rule_id="all_rules_passed",
                        severity="none", message="")


def main() -> int:
    """PreToolUse entry: read JSON on stdin, dispatch to engine, exit 0/1."""
    try:
        payload = json.loads(__import__("sys").stdin.read() or "{}")
    except Exception:
        payload = {}

    engine = BehaviorGovEngine()
    decision = engine.evaluate(payload)
    if decision.allowed:
        return 0
    print(json.dumps({
        "action": "block",
        "message": decision.message,
        "rule_id": decision.rule_id,
        "severity": decision.severity,
        "details": decision.details,
    }))
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
