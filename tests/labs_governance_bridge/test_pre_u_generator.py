from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "labs_governance_bridge/pre_u_generator/generated"
REQUIRED_AGENTS = {"Aiden-CEO", "Ethan-CTO", "Samantha-Secretary"}
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


def test_pre_u_packet_generation_and_dry_run_flow() -> None:
    packet_build = run_command(["python3", "labs_governance_bridge/pre_u_generator/tools/build_pre_u_packets.py"])
    assert packet_build.returncode == 0, packet_build.stdout + packet_build.stderr

    packet_files = [
        GENERATED / "aiden_pre_u_packet.json",
        GENERATED / "ethan_pre_u_packet.json",
        GENERATED / "samantha_pre_u_packet.json",
    ]
    packets = [load_json(path) for path in packet_files]
    assert {packet["agent_id"] for packet in packets} == REQUIRED_AGENTS

    required_packet_fields = [
        "packet_id",
        "task_id",
        "agent_id",
        "role",
        "declared_Y_star",
        "Xt",
        "m_functor",
        "candidate_U",
        "selected_U",
        "predicted_Yt_plus_1",
        "predicted_Rt_plus_1",
        "why_min_residual",
        "risk_tier",
        "governance_expectations",
        "cieu_link_policy",
        "evidence_hint_refs",
        "packet_status",
        "action_executed",
        "brain_writeback_allowed",
        "memory_ingestion_allowed",
        "cieu_write_allowed",
    ]
    for packet in packets:
        for field in required_packet_fields:
            assert field in packet
        assert packet["packet_status"] == "generated_dry_run_only"
        assert packet["action_executed"] is False
        assert packet["brain_writeback_allowed"] is False
        assert packet["memory_ingestion_allowed"] is False
        assert packet["cieu_write_allowed"] is False
        assert_no_forbidden_strings(packet)

    envelope_build = run_command(["python3", "labs_governance_bridge/pre_u_generator/tools/build_hook_envelopes_from_packets.py"])
    assert envelope_build.returncode == 0, envelope_build.stdout + envelope_build.stderr

    envelope_files = [
        GENERATED / "aiden_hook_envelope.json",
        GENERATED / "ethan_hook_envelope.json",
        GENERATED / "samantha_hook_envelope.json",
    ]
    required_envelope_fields = [
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
    envelopes = [load_json(path) for path in envelope_files]
    assert {envelope["agent_id"] for envelope in envelopes} == REQUIRED_AGENTS
    for envelope in envelopes:
        for field in required_envelope_fields:
            assert field in envelope
        assert_no_forbidden_strings(envelope)

    dry_run = run_command(["python3", "labs_governance_bridge/pre_u_generator/tools/run_pre_u_governance_dry_run.py"])
    assert dry_run.returncode == 0, dry_run.stdout + dry_run.stderr

    decisions = load_json(GENERATED / "governance_decision_snapshots.json")
    snapshots = decisions["snapshots"]
    assert len(snapshots) == 3
    assert {snapshot["agent_id"] for snapshot in snapshots} == REQUIRED_AGENTS
    for snapshot in snapshots:
        assert snapshot["dry_run_only"] is True
        assert snapshot["non_execution_confirmation"] is True
        assert snapshot["action_executed"] is False
        assert snapshot["cieu_written"] is False
        assert snapshot["brain_writeback_performed"] is False
        assert snapshot["memory_ingestion_performed"] is False
        assert snapshot["ystar_gov_decision"] in {"allow", "warn", "require_revision", "deny", "escalate"}
        assert_no_forbidden_strings(snapshot)


def test_pre_u_generator_tools_do_not_claim_runtime_mutation() -> None:
    for rel in [
        "labs_governance_bridge/pre_u_generator/tools/build_pre_u_packets.py",
        "labs_governance_bridge/pre_u_generator/tools/build_hook_envelopes_from_packets.py",
        "labs_governance_bridge/pre_u_generator/tools/run_pre_u_governance_dry_run.py",
    ]:
        source = (ROOT / rel).read_text(encoding="utf-8")
        assert "shell=True" not in source
        assert "sqlite3" not in source
        assert "action_executed\": True" not in source
        assert "cieu_written\": True" not in source
        assert "brain_writeback_performed\": True" not in source
        assert "memory_ingestion_performed\": True" not in source
