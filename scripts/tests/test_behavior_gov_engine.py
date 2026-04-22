"""Test: Behavior Governance Rule Engine — methodology framework.

Covers:
- Engine loads YAML rules + dispatches to handlers
- DeadlineCheck handler blocks on overdue pending obligations
- Tool allowlist + break-glass override path
- Disabled rules skipped
- Unknown rule type silently ignored (future extensibility)
- StatePresenceCheck blocks when field below min
- Fail-open on missing DB/file
"""
import json
import os
import sqlite3
import sys
import time
from pathlib import Path
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from behavior_gov_engine import (
    BehaviorGovEngine, Decision,
    handle_deadline_check, handle_state_presence,
    HANDLERS,
)


# ─── Handlers ────────────────────────────────────────────────────────────────

def _make_oblig_db(db_path: Path, rows: list):
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE obligations (
            obligation_id TEXT PRIMARY KEY,
            actor_id TEXT,
            status TEXT,
            due_at REAL,
            hard_overdue_secs REAL,
            notes TEXT
        )
    """)
    for r in rows:
        conn.execute(
            "INSERT INTO obligations VALUES (?,?,?,?,?,?)",
            (r["obligation_id"], r["actor_id"], r.get("status", "pending"),
             r["due_at"], r.get("hard_overdue_secs", 0), r.get("notes", ""))
        )
    conn.commit()
    conn.close()


def test_deadline_check_blocks_overdue(tmp_path, monkeypatch):
    import behavior_gov_engine as mod
    db = tmp_path / "oblig.db"
    _make_oblig_db(db, [{
        "obligation_id": "o1", "actor_id": "ceo",
        "due_at": time.time() - 3600, "hard_overdue_secs": 60,
    }])
    monkeypatch.setattr(mod, "WORKSPACE", tmp_path)
    rule = {
        "rule_id": "test",
        "type": "DeadlineCheck",
        "severity": "deny",
        "query": {
            "db": "oblig.db",
            "table": "obligations",
            "actor_col": "actor_id",
            "deadline_col": "due_at",
            "grace_col": "hard_overdue_secs",
            "status_col": "status",
            "status_open_value": "pending",
        },
        "message_template": "Deny {agent}: {count} overdue ({oldest_min}m) ids={ids}",
    }
    decision = handle_deadline_check(rule, {"agent_id": "ceo"})
    assert decision is not None
    assert decision.allowed is False
    assert decision.severity == "deny"
    assert "ceo" in decision.message


def test_deadline_check_allows_when_no_overdue(tmp_path, monkeypatch):
    import behavior_gov_engine as mod
    db = tmp_path / "oblig.db"
    _make_oblig_db(db, [{
        "obligation_id": "o1", "actor_id": "ceo",
        "due_at": time.time() + 3600, "hard_overdue_secs": 0,
    }])
    monkeypatch.setattr(mod, "WORKSPACE", tmp_path)
    rule = {
        "rule_id": "test", "type": "DeadlineCheck",
        "severity": "deny",
        "query": {"db": "oblig.db"},
    }
    decision = handle_deadline_check(rule, {"agent_id": "ceo"})
    assert decision is None


def test_deadline_check_fail_open_on_missing_db(tmp_path, monkeypatch):
    import behavior_gov_engine as mod
    monkeypatch.setattr(mod, "WORKSPACE", tmp_path)
    rule = {
        "rule_id": "test", "type": "DeadlineCheck",
        "severity": "deny",
        "query": {"db": "nonexistent.db"},
    }
    decision = handle_deadline_check(rule, {"agent_id": "ceo"})
    assert decision is None  # fail-open


def test_state_presence_blocks_below_min(tmp_path, monkeypatch):
    import behavior_gov_engine as mod
    monkeypatch.setattr(mod, "WORKSPACE", tmp_path)
    state_file = tmp_path / "state.json"
    state_file.write_text(json.dumps({"distinct_tool_types": 1}))
    rule = {
        "rule_id": "t", "type": "StatePresenceCheck", "severity": "warn",
        "query": {
            "state_file": "state.json",
            "field": "distinct_tool_types",
            "min_value": 3,
        },
        "message_template": "only {value} tools",
    }
    d = handle_state_presence(rule, {})
    assert d is not None
    assert d.allowed is False
    assert "only 1 tools" in d.message


# ─── Engine integration ──────────────────────────────────────────────────────

def test_engine_allowlist_tool_always_passes(tmp_path, monkeypatch):
    rules_yaml = tmp_path / "rules.yaml"
    rules_yaml.write_text("""
version: 1
defaults:
  enforced_agents: [ceo]
  tool_allowlist: [Read, Grep, Glob]
rules: []
""")
    ceo_mode = tmp_path / "no_bg.json"
    agent_file = tmp_path / "agent"
    agent_file.write_text("ceo\n")
    engine = BehaviorGovEngine(rules_path=rules_yaml,
                               ceo_mode_path=ceo_mode,
                               active_agent_path=agent_file)
    d = engine.evaluate({"tool_name": "Read"})
    assert d.allowed is True
    assert d.rule_id == "allowlist_tool"


def test_engine_break_glass_overrides(tmp_path, monkeypatch):
    rules_yaml = tmp_path / "rules.yaml"
    rules_yaml.write_text("""
version: 1
defaults:
  enforced_agents: [ceo]
  tool_allowlist: [Read]
  break_glass_override: true
rules: []
""")
    ceo_mode = tmp_path / "bg.json"
    ceo_mode.write_text(json.dumps({
        "mode": "BREAK_GLASS",
        "hard_cap_expires_at": time.time() + 600,
    }))
    agent_file = tmp_path / "agent"
    agent_file.write_text("ceo\n")
    engine = BehaviorGovEngine(rules_path=rules_yaml,
                               ceo_mode_path=ceo_mode,
                               active_agent_path=agent_file)
    d = engine.evaluate({"tool_name": "Write"})
    assert d.allowed is True
    assert d.rule_id == "break_glass_active"


def test_engine_unknown_agent_not_enforced(tmp_path):
    rules_yaml = tmp_path / "rules.yaml"
    rules_yaml.write_text("""
version: 1
defaults:
  enforced_agents: [ceo]
  tool_allowlist: []
rules:
  - rule_id: r
    type: DeadlineCheck
    severity: deny
    query: {db: foo.db}
""")
    ceo_mode = tmp_path / "no_bg.json"
    agent_file = tmp_path / "agent"
    agent_file.write_text("path_a_agent\n")
    engine = BehaviorGovEngine(rules_path=rules_yaml,
                               ceo_mode_path=ceo_mode,
                               active_agent_path=agent_file)
    d = engine.evaluate({"tool_name": "Write"})
    assert d.allowed is True
    assert d.rule_id == "unknown_agent"


def test_engine_disabled_rules_skipped(tmp_path):
    rules_yaml = tmp_path / "rules.yaml"
    rules_yaml.write_text("""
version: 1
defaults:
  enforced_agents: []
  tool_allowlist: []
rules:
  - rule_id: disabled
    type: DeadlineCheck
    severity: deny
    enabled: false
    query: {db: foo.db}
""")
    ceo_mode = tmp_path / "no_bg.json"
    agent_file = tmp_path / "agent"
    agent_file.write_text("ceo\n")
    engine = BehaviorGovEngine(rules_path=rules_yaml,
                               ceo_mode_path=ceo_mode,
                               active_agent_path=agent_file)
    d = engine.evaluate({"tool_name": "Write"})
    assert d.allowed is True


def test_engine_unknown_rule_type_ignored(tmp_path):
    rules_yaml = tmp_path / "rules.yaml"
    rules_yaml.write_text("""
version: 1
defaults:
  enforced_agents: []
  tool_allowlist: []
rules:
  - rule_id: weird
    type: UnknownType
    severity: deny
""")
    ceo_mode = tmp_path / "no_bg.json"
    agent_file = tmp_path / "agent"
    agent_file.write_text("ceo\n")
    engine = BehaviorGovEngine(rules_path=rules_yaml,
                               ceo_mode_path=ceo_mode,
                               active_agent_path=agent_file)
    d = engine.evaluate({"tool_name": "Write"})
    assert d.allowed is True


def test_handlers_registry_has_4_types():
    """Ensure 4 rule types are registered for extensibility."""
    assert "DeadlineCheck" in HANDLERS
    assert "FrequencyCheck" in HANDLERS
    assert "StatePresenceCheck" in HANDLERS
    assert "ToolCountCheck" in HANDLERS
