import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_guard_stack_replay_passes_all_selected_actions():
    data = load("operations/external_validation/e22_guard_stack_results.json")
    assert data["guard_pass_count"] == 5
    assert data["guard_block_count"] == 0
    for row in data["guard_results"]:
        assert row["resulting_action_status"] == "dry_run_guard_passed"
        assert row["checks"]["owner_approval_check"]["status"] == "not_applicable"
        assert row["external_action_executed"] is False
