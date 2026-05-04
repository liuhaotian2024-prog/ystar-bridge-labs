import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_evidence_tightening_keeps_blockers_honest():
    data=load("operations/external_validation/e23_evidence_tightening_evaluation.json")
    assert data["evidence_required_before"] == 2
    assert data["promoted_to_dry_run_available"] == 0
    assert data["still_evidence_required"] == 1
    assert data["suppressed_or_rejected"] == 2
    classes={row["action_id"]: row["updated_classification"] for row in data["rows"]}
    assert classes["c2_action_fallback_006_cand_wotai_wotai"] == "suppress_or_do_not_contact"
    assert classes["c3_excluded_agent_direct_execution_without_activation"] == "blocked_missing_source"
    assert data["external_action_executed"] is False
