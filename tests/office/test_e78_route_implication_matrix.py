import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_route_implication_matrix_compares_required_positions():
    matrix = json.loads((ROOT / "operations/external_validation/e78_l3_route_implication_matrix.json").read_text())
    positions = {row["route_position"] for row in matrix["positions"]}

    assert positions == {
        "founder_operator_diagnostic",
        "agent_team_governance_blueprint",
        "AI_operations_control_room_setup",
        "audit_readiness_package",
        "consulting_productized_service",
        "technical_implementation_package",
    }
    assert matrix["top_ranked_positions"][0] == "agent_team_governance_blueprint"
    assert "prepare L4 owner-decision packet" in matrix["matrix_decision"]

