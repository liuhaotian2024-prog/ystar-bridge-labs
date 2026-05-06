import json
from pathlib import Path

from office.mission_command.e63_opportunity_discovery_core import write_all_e63_artifacts


def test_e63_artifacts_regenerate_in_current_environment():
    root = Path(__file__).resolve().parents[2]
    gate = write_all_e63_artifacts(root)
    assert gate["gate_passed"] is True
    assert gate["final_status"] in {
        "e63_public_read_opportunity_discovery_completed",
        "e63_public_read_blocked_but_revenue_opportunity_plan_created",
        "e63_opportunity_discovery_partial_with_blocker",
    }
    assert json.loads((root / "operations/external_validation/e63_completion_gate_result.json").read_text())["gate_passed"] is True
