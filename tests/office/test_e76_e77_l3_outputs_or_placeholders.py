import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_disabled_future_execution_packet_exists_and_inherits_e75_scope():
    future = _load("operations/external_validation/e76_e77_future_L3_execution_prompt_if_owner_approves.json")

    assert future["draft_status"] == "disabled_unless_explicit_owner_approval_is_recorded"
    assert future["required_owner_decision_status"] == "APPROVE_L3_READ_ONLY_RESEARCH_PILOT"
    assert future["disabled_in_E76_E77"] is True
    assert future["external_action_allowed_now"] is False
    assert len(future["inherited_allowlist"]) >= 4
    assert future["receipt_schema"]


def test_placeholder_records_no_source_collection():
    placeholder = _load("operations/external_validation/e76_e77_disabled_l3_execution_placeholder.json")

    assert placeholder["placeholder_only"] is True
    assert placeholder["phase_b_execution_authorized"] is False
    assert placeholder["evidence_synthesis_generated"] is False

