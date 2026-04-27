from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "labs_runtime_acceptance" / "tools" / "run_labs_runtime_acceptance.py"
REPORT = ROOT / "labs_runtime_acceptance" / "generated" / "labs_runtime_acceptance_report.json"
MANIFEST = ROOT / "labs_runtime_acceptance" / "generated" / "labs_runtime_acceptance_manifest.json"
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


def run_acceptance() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", "labs_runtime_acceptance/tools/run_labs_runtime_acceptance.py"],
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


def test_labs_runtime_acceptance_runner_accepts_current_stack() -> None:
    result = run_acceptance()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Labs governance acceptance: ACCEPTED" in result.stdout
    assert "no action execution" in result.stdout

    report = load_json(REPORT)
    manifest = load_json(MANIFEST)

    assert report["accepted"] is True
    assert manifest["accepted"] is True
    assert all(check["status"] == "PASS" for check in report["checks"])
    assert set(report["decision_summary"]["roles_covered"]) == REQUIRED_AGENTS
    assert report["decision_summary"]["decision_counts"]

    safety = report["safety_assertions"]
    assert safety["action_executed"] is False
    assert safety["cieu_written"] is False
    assert safety["brain_writeback_performed"] is False
    assert safety["memory_ingestion_performed"] is False
    assert safety["raw_runtime_artifacts_ingested"] is False

    assert_no_forbidden_strings(report)
    assert_no_forbidden_strings(manifest)


def test_acceptance_runner_is_non_recursive_and_dry_run_only() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "sqlite3" not in source
    assert "scripts/.logs" not in source
    assert "aiden_brain.db" not in source
    assert "labs_runtime_acceptance/tools/run_labs_runtime_acceptance.py" not in source
    assert "\"action_executed\": True" not in source
    assert "\"cieu_written\": True" not in source
    assert "\"brain_writeback_performed\": True" not in source
    assert "\"memory_ingestion_performed\": True" not in source

