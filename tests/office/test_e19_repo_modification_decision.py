import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_repo_modification_decision_is_bridge_labs_only_now():
    data = json.loads((ROOT / "operations/external_validation/e19_repo_modification_decision_packet.json").read_text())
    decisions = {item["repo"]: item["decision"] for item in data["decisions"]}
    assert decisions["ystar-bridge-labs"] == "bridge_labs_update_only"
    assert decisions["gov-mcp"] == "future_gov_mcp_update_required"
    assert decisions["Y-star-gov"] == "no_change_needed"
    assert decisions["ystar-company"] == "future_ystar_company_migration_required"
    assert data["cross_repo_mutation_performed"] is False
