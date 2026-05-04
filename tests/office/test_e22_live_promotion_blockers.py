import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_live_promotion_blockers_keep_all_actions_blocked_for_live():
    data = load("operations/external_validation/e22_live_promotion_blockers.json")
    assert data["live_ready_count"] == 0
    assert data["live_blocked_count"] == 7
    assert all(row["live_execution_allowed_now"] is False for row in data["rows"])
    assert any("final_evidence_sufficiency" in row["blockers"] for row in data["rows"])
