import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_ecosystem_alignment_gate_checks_four_repos_and_routes_gov_mcp_gap():
    data = json.loads((ROOT / "operations/external_validation/e20_ecosystem_alignment_gate.json").read_text())
    repos = {repo["repo"] for repo in data["repos_checked"]}
    assert repos == {"ystar-bridge-labs", "gov-mcp", "Y-star-gov", "ystar-company"}
    assert data["closure_status"] == "ecosystem_aligned_with_documented_followups"
    decisions = {item["repo"]: item["decision"] for item in data["repo_modification_decisions"]}
    assert decisions["gov-mcp"] == "future_gov_mcp_update_required"
    assert data["external_action_executed"] is False
