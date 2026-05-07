import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e75_future_e76_prompt_is_disabled_without_owner_approval():
    draft = json.loads((ROOT / "operations/external_validation/e75_future_E76_disabled_execution_prompt_draft.json").read_text())

    assert draft["proposed_future_milestone"] == "E76_Owner_Approved_L3_Read_Only_External_Research_Pilot"
    assert draft["draft_status"] == "disabled_pending_explicit_owner_approval"
    assert draft["execution_disabled"] is True
    assert draft["owner_approval_required"] is True
    assert draft["owner_approval_granted"] is False
    assert draft["external_action_allowed_in_E75"] is False
    assert "Only read owner-approved public source categories." in draft["public_read_only_research_instructions"]
    assert "all sources are owner-approved public-read only" in draft["tests_or_checks"]


def test_e75_next_milestone_waits_for_owner_decision_when_pending():
    proposal = json.loads((ROOT / "operations/external_validation/e75_generated_next_milestone_proposal.json").read_text())

    assert proposal["owner_decision_status"] == "pending_owner_decision"
    assert proposal["selected_next_milestone"] == "E76_Await_or_Record_Owner_Decision_for_L3_Read_Only_Research"
    assert proposal["decision_state_routing"]["APPROVE_L3_READ_ONLY_RESEARCH_PILOT"] == "E76_Owner_Approved_L3_Read_Only_External_Research_Pilot"
    assert proposal["next_step_is_decision_not_construction"] is True
    assert proposal["external_action_allowed"] is False
