from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ENVELOPE = ROOT / "labs_governance_bridge/generated/sample_hook_envelope.json"
SNAPSHOT = ROOT / "labs_governance_bridge/generated/governance_decision_snapshot.json"
FORBIDDEN_STRINGS = [
    ".db",
    ".db-wal",
    ".db-shm",
    "scripts/.logs",
    "active_agent",
    ".ystar_active_agent",
    "aiden_brain.db",
]


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def assert_no_forbidden_strings(payload: dict) -> None:
    rendered = json.dumps(payload, sort_keys=True).lower()
    for forbidden in FORBIDDEN_STRINGS:
        assert forbidden.lower() not in rendered


def test_labs_gov_bridge_builds_envelope_and_decision_snapshot() -> None:
    build = run_command(["python3", "labs_governance_bridge/tools/build_labs_hook_envelope.py"])
    assert build.returncode == 0, build.stdout + build.stderr
    assert ENVELOPE.exists()

    envelope = load_json(ENVELOPE)
    required_hook_fields = [
        "hook_event_id",
        "agent_id",
        "packet_id",
        "risk_tier",
        "declared_Y_star",
        "Xt",
        "m_functor",
        "candidate_U",
        "selected_U_id",
        "why_min_residual",
        "governance_expectations",
        "cieu_link_policy",
    ]
    for field in required_hook_fields:
        assert field in envelope
    assert envelope["agent_id"] == "Aiden-CEO"
    assert envelope["selected_U_id"] == "u1"
    assert_no_forbidden_strings(envelope)

    before = copy.deepcopy(envelope)
    bridge = run_command(["python3", "labs_governance_bridge/tools/run_labs_gov_dry_run.py"])
    assert bridge.returncode == 0, bridge.stdout + bridge.stderr
    assert load_json(ENVELOPE) == before
    assert SNAPSHOT.exists()

    snapshot = load_json(SNAPSHOT)
    assert snapshot["dry_run_only"] is True
    assert snapshot["non_execution_confirmation"] is True
    assert snapshot["action_executed"] is False
    assert snapshot["cieu_written"] is False
    assert snapshot["brain_writeback_performed"] is False
    assert snapshot["memory_ingestion_performed"] is False
    assert isinstance(snapshot["ystar_gov_exit_code"], int)
    assert snapshot["ystar_gov_decision"] in {"allow", "warn", "require_revision", "deny", "escalate"}
    assert snapshot["decision_envelope"]["dry_run_only"] is True
    assert snapshot["decision_envelope"]["non_execution_confirmation"] is True
    assert_no_forbidden_strings(snapshot)


def test_bridge_tools_do_not_claim_runtime_mutation() -> None:
    for rel in [
        "labs_governance_bridge/tools/build_labs_hook_envelope.py",
        "labs_governance_bridge/tools/run_labs_gov_dry_run.py",
    ]:
        source = (ROOT / rel).read_text(encoding="utf-8")
        assert "shell=True" not in source
        assert "sqlite3" not in source
        assert "action_executed\": True" not in source
        assert "cieu_written\": True" not in source
        assert "brain_writeback_performed\": True" not in source
        assert "memory_ingestion_performed\": True" not in source
