import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_cross_repo_impact_matrix_maps_core_repos():
    data = json.loads((ROOT / "operations/external_validation/e19_cross_repo_impact_matrix.json").read_text())
    repos = {(row["source_repo"], row["consumer_repo"]) for row in data["rows"]}
    assert ("gov-mcp", "ystar-bridge-labs") in repos
    assert ("Y-star-gov", "ystar-bridge-labs") in repos
    assert ("ystar-company", "ystar-bridge-labs") in repos
    assert data["external_action_executed"] is False
