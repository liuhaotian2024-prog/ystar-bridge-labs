import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_optional_dry_run_iteration_skips_when_no_new_promotions():
    data=load("operations/external_validation/e23_optional_dry_run_iteration.json")
    assert data["newly_promoted_candidate_count"] == 0
    assert data["dry_run_iteration_executed"] is False
    assert data["newly_dry_run_executed_count"] == 0
    assert "avoids duplicate receipts" in data["reason"]
