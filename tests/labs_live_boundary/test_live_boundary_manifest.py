from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "labs_live_boundary" / "tools" / "build_live_boundary_manifest.py"
GENERATED = ROOT / "labs_live_boundary" / "generated"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def run_builder() -> None:
    result = subprocess.run(
        ["python3", str(BUILDER.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_live_boundary_manifest_is_defined_but_disabled() -> None:
    run_builder()
    manifest = load_json(GENERATED / "live_boundary_manifest.json")
    summary = load_json(GENERATED / "live_boundary_summary.json")

    for field in [
        "live_boundary_defined",
        "operator_approval_gate_defined",
        "action_sandbox_contract_defined",
        "rollback_policy_defined",
        "cieu_writer_boundary_defined",
    ]:
        assert manifest[field] is True
        assert summary[field] is True

    for field in [
        "live_action_execution_enabled",
        "cieu_write_enabled",
        "brain_writeback_enabled",
        "memory_ingestion_enabled",
        "candidate_auto_approval_enabled",
        "raw_artifact_ingestion_enabled",
        "minimal_live_loop_ready",
    ]:
        assert manifest[field] is False
        assert summary[field] is False

    assert manifest["requires_manual_enablement"] is True
    assert summary["requires_manual_enablement"] is True
    assert manifest["blocked_reason"] == "required_live_gates_defined_but_disabled"
    assert summary["blocked_reason"] == "required_live_gates_defined_but_disabled"


def test_live_transition_checklist_has_only_disabled_or_not_started_statuses() -> None:
    run_builder()
    checklist = load_json(GENERATED / "live_transition_checklist.json")
    statuses = {item["status"] for item in checklist["items"]}

    assert statuses <= {"not_started", "defined_disabled"}
    assert checklist["summary"]["ready_or_enabled_items"] == 0
    forbidden_statuses = {"ready", "enabled", "completed", "accepted", "approved", "live"}
    assert not statuses & forbidden_statuses


def test_generated_boundary_outputs_do_not_embed_forbidden_runtime_content() -> None:
    run_builder()
    generated_paths = [
        GENERATED / "live_boundary_manifest.json",
        GENERATED / "live_boundary_summary.json",
        GENERATED / "live_boundary_report.md",
        GENERATED / "live_transition_checklist.json",
    ]
    forbidden = [
        ".db",
        ".db-wal",
        ".db-shm",
        "scripts/.logs",
        "active_agent",
        ".ystar_active_agent",
        "aiden_brain.db",
        "BOARD_PENDING.md",
        "memory/WORLD_STATE.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in generated_paths)

    for marker in forbidden:
        assert marker not in combined


def test_builder_is_local_only_and_does_not_open_raw_artifact_classes() -> None:
    source = BUILDER.read_text(encoding="utf-8")

    assert "shell=True" not in source
    assert "subprocess" not in source
    assert "sqlite3" not in source
    for marker in [
        ".db-wal",
        ".db-shm",
        "scripts/.logs",
        "active_agent",
        ".ystar_active_agent",
        "aiden_brain.db",
        "BOARD_PENDING.md",
        "memory/WORLD_STATE.md",
    ]:
        assert marker not in source
