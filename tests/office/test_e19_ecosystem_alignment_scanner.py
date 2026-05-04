import json
from pathlib import Path

from office.mission_command.e19_ecosystem_alignment_scanner import build_ecosystem_alignment_scan

ROOT = Path(__file__).resolve().parents[2]


def test_ecosystem_alignment_scan_checks_four_repos():
    data = json.loads((ROOT / "operations/external_validation/e19_ecosystem_alignment_scan.json").read_text())
    names = {repo["repo_name"] for repo in data["repos"]}
    assert names == {"ystar-bridge-labs", "gov-mcp", "Y-star-gov", "ystar-company"}
    assert data["repos_checked_count"] == 4
    assert data["read_only_scan"] is True
    assert data["external_action_executed"] is False


def test_scanner_handles_missing_repo_without_claiming_success(tmp_path):
    scan = build_ecosystem_alignment_scan({"missing": str(tmp_path / "nope")})
    assert scan["repos"][0]["exists"] is False
    assert scan["repos_available_count"] == 0
