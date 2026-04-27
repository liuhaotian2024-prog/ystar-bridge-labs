from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "cross_repo_alignment" / "tools" / "run_cross_repo_alignment_acceptance.py"
BUILDER = ROOT / "cross_repo_alignment" / "tools" / "build_cross_repo_status_manifest.py"
MANIFEST = ROOT / "cross_repo_alignment" / "generated" / "cross_repo_status_manifest.json"
SUMMARY = ROOT / "cross_repo_alignment" / "generated" / "cross_repo_alignment_summary.json"
REQUIRED_ROLES = {"Aiden-CEO", "Ethan-CTO", "Samantha-Secretary"}
FORBIDDEN_STRINGS = [
    ".db",
    ".db-wal",
    ".db-shm",
    "scripts/.logs",
    "active_agent",
    ".ystar_active_agent",
    "aiden_brain.db",
]


def run_alignment() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", "cross_repo_alignment/tools/run_cross_repo_alignment_acceptance.py"],
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


def test_cross_repo_alignment_acceptance_passes() -> None:
    result = run_alignment()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Cross-repo alignment: ACCEPTED" in result.stdout

    manifest = load_json(MANIFEST)
    summary = load_json(SUMMARY)

    assert manifest["alignment_status"]["accepted"] is True
    assert summary["alignment_accepted"] is True
    assert manifest["ystar_company_head"]
    assert manifest["ystar_gov_head"]
    assert manifest["ystar_gov_endpoint_acceptance"]["accepted"] is True
    assert manifest["labs_runtime_acceptance"]["accepted"] is True
    assert set(manifest["multi_role_pre_u_governance"]["roles_covered"]) == REQUIRED_ROLES
    assert manifest["multi_role_pre_u_governance"]["decision_counts"]
    assert all(manifest["safety_assertions"].values())
    assert manifest["labs_governance_bridge"]["action_executed"] is False
    assert manifest["labs_governance_bridge"]["cieu_written"] is False
    assert manifest["labs_governance_bridge"]["brain_writeback_performed"] is False
    assert manifest["multi_role_pre_u_governance"]["action_executed"] is False
    assert manifest["multi_role_pre_u_governance"]["cieu_written"] is False
    assert manifest["multi_role_pre_u_governance"]["brain_writeback_performed"] is False
    assert_no_forbidden_strings(manifest)
    assert_no_forbidden_strings(summary)


def test_cross_repo_alignment_tools_are_local_and_non_executing() -> None:
    for path in [BUILDER, RUNNER]:
        source = path.read_text(encoding="utf-8")
        assert "shell=True" not in source
        assert "sqlite3" not in source
        assert "scripts/.logs" not in source
        assert "aiden_brain.db" not in source
        assert "\"action_executed\": True" not in source
        assert "\"cieu_written\": True" not in source
        assert "\"brain_writeback_performed\": True" not in source

