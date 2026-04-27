from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "labs_live_readiness" / "tools" / "build_live_readiness_report.py"
REPORT = ROOT / "labs_live_readiness" / "generated" / "live_readiness_report.json"
BACKLOG = ROOT / "labs_live_readiness" / "generated" / "transition_backlog.json"
MANIFEST = ROOT / "labs_live_readiness" / "generated" / "live_readiness_manifest.json"
FORBIDDEN_STRINGS = [
    ".db",
    ".db-wal",
    ".db-shm",
    "scripts/.logs",
    "active_agent",
    ".ystar_active_agent",
    "aiden_brain.db",
]


def run_builder() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", "labs_live_readiness/tools/build_live_readiness_report.py"],
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


def test_live_readiness_report_blocks_live_loop() -> None:
    result = run_builder()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Labs Live Readiness Builder: PASS" in result.stdout

    report = load_json(REPORT)
    backlog = load_json(BACKLOG)
    manifest = load_json(MANIFEST)

    overall = report["overall_status"]
    assert overall["dry_run_governance_ready"] is True
    assert overall["minimal_live_loop_ready"] is False
    assert overall["minimal_live_loop_status"] == "blocked_until_required_gates_exist"
    assert overall["recommended_next_phase"] == "build_live_boundary_harness_not_runtime_execution"

    safety = report["safety_booleans"]
    assert safety["live_action_execution_allowed"] is False
    assert safety["live_cieu_write_allowed"] is False
    assert safety["live_brain_writeback_allowed"] is False
    assert safety["live_memory_ingestion_allowed"] is False
    assert safety["candidate_auto_approval_allowed"] is False
    assert safety["raw_artifact_ingestion_allowed"] is False

    assert report["live_execution_blockers"]
    assert backlog["items"]
    assert all(item["status"] == "not_started" for item in backlog["items"])
    assert any(item["required_before_live"] is True for item in backlog["items"])
    assert manifest["dry_run_governance_ready"] is True
    assert manifest["minimal_live_loop_ready"] is False

    assert_no_forbidden_strings(report)
    assert_no_forbidden_strings(backlog)
    assert_no_forbidden_strings(manifest)


def test_live_readiness_builder_is_local_and_non_executing() -> None:
    source = BUILDER.read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "sqlite3" not in source
    assert "scripts/.logs" not in source
    assert "aiden_brain.db" not in source
    assert "subprocess" not in source
    assert "\"live_action_execution_allowed\": True" not in source
    assert "\"live_cieu_write_allowed\": True" not in source
    assert "\"live_brain_writeback_allowed\": True" not in source
    assert "\"live_memory_ingestion_allowed\": True" not in source
