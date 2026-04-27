from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "labs_cieu_runtime_boundary" / "tools" / "build_cieu_runtime_boundary.py"
GENERATED = ROOT / "labs_cieu_runtime_boundary" / "generated"


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


def test_cieu_runtime_boundary_manifest_is_defined_but_disabled() -> None:
    run_builder()
    manifest = load_json(GENERATED / "cieu_runtime_boundary_manifest.json")
    summary = load_json(GENERATED / "cieu_runtime_boundary_summary.json")

    for field in [
        "cieu_runtime_boundary_defined",
        "cieu_runtime_event_schema_defined",
        "prediction_delta_fixture_defined",
        "cieu_writer_policy_defined",
        "dry_run_only",
        "requires_manual_enablement",
    ]:
        assert manifest[field] is True
        assert summary[field] is True

    for field in [
        "persistence_enabled",
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

    assert manifest["blocked_reason"] == "cieu_runtime_boundary_defined_but_persistence_disabled"
    assert summary["blocked_reason"] == "cieu_runtime_boundary_defined_but_persistence_disabled"


def test_sample_event_has_required_prediction_and_boundary_fields() -> None:
    run_builder()
    event = load_json(GENERATED / "sample_cieu_runtime_event.json")

    for field in [
        "Xt",
        "U",
        "Y_star",
        "predicted_Y_t1",
        "predicted_R_t1",
        "actual_Y_t1",
        "actual_R_t1",
        "residual_delta",
        "evidence_refs",
        "governance_decision_ref",
        "live_boundary_ref",
        "write_policy",
    ]:
        assert field in event

    assert event["dry_run_only"] is True
    assert event["persistence_enabled"] is False
    assert event["cieu_write_enabled"] is False
    assert event["validation_status"] == "boundary_defined_disabled"


def test_prediction_delta_fixture_forbids_direct_ingestion_and_writeback() -> None:
    run_builder()
    fixture = load_json(GENERATED / "sample_prediction_delta_fixture.json")

    assert fixture["learning_eligibility"] is False
    assert fixture["curation_required"] is True
    assert fixture["direct_brain_writeback_allowed"] is False
    assert fixture["direct_memory_ingestion_allowed"] is False
    assert fixture["raw_artifact_ingestion_allowed"] is False
    assert fixture["writeback_policy"]["cieu_write_allowed"] is False


def test_generated_boundary_outputs_do_not_embed_forbidden_runtime_content() -> None:
    run_builder()
    generated_paths = [
        GENERATED / "cieu_runtime_boundary_manifest.json",
        GENERATED / "cieu_runtime_boundary_summary.json",
        GENERATED / "cieu_runtime_boundary_report.md",
        GENERATED / "sample_cieu_runtime_event.json",
        GENERATED / "sample_prediction_delta_fixture.json",
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
