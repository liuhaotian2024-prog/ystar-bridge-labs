import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_candidate_dossiers_include_present_and_missing_evidence():
    data=load("operations/external_validation/e23_candidate_evidence_dossiers.json")
    assert data["dossier_count"] == 2
    by_id={row["action_id"]: row for row in data["dossiers"]}
    assert by_id["c2_action_fallback_006_cand_wotai_wotai"]["evidence_present"]
    assert by_id["c3_excluded_agent_direct_execution_without_activation"]["evidence_missing"]
    assert by_id["c3_excluded_agent_direct_execution_without_activation"]["target_fit"] == "not_grounded"
