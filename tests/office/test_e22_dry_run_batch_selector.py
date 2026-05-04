import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())

from office.mission_command.e22_dry_run_batch_selector import select_dry_run_actions


def test_dry_run_selector_selects_only_e21_dry_run_available_actions():
    data = load("operations/external_validation/e22_dry_run_batch_selection.json")
    assert data["selected_count"] == 5
    assert data["excluded_count"] == 2
    assert all(row["dry_run_available"] for row in data["selected_dry_run_actions"])
    assert all("evidence_required" in row["reasons"] for row in data["excluded_actions_with_reasons"])
    assert data["external_action_executed"] is False
