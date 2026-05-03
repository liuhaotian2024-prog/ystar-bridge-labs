from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONSOLE_MD = ROOT / "operations" / "external_validation" / "e14_owner_decision_console.md"
CONSOLE_JSON = ROOT / "operations" / "external_validation" / "e14_owner_decision_console.json"
EXPLAINER = ROOT / "reports" / "integration" / "e14_owner_decision_explainer.md"
DELIVERY_REQUEST = (
    ROOT
    / "operations"
    / "repository_delivery"
    / "delivery_requests"
    / "a1_b1_cross_repo_audit_owner_console_delivery.json"
)


def console() -> dict:
    return json.loads(CONSOLE_JSON.read_text(encoding="utf-8"))


def test_console_explains_approval_clearly() -> None:
    text = CONSOLE_MD.read_text(encoding="utf-8")
    assert "你现在要批准的不是" in text
    assert "owner personally sends" in text
    assert "Aiden/Codex does not send" in text


def test_console_includes_selected_targets() -> None:
    data = console()
    assert len(data["selected_targets"]) == 3
    assert "cand_alicelabs_alicelabs" in text_blob(data)
    assert "cand_botsquash_botsquash" in text_blob(data)
    assert "cand_wotai_wotai" in text_blob(data)


def test_console_includes_exact_approval_boundary() -> None:
    data = console()
    approval_text = data["copyable_approval_text"]
    assert "owner-operated manual validation" in approval_text
    assert "does not authorize Aiden or any agent to send messages" in approval_text
    assert data["risk_boundary"]["aiden_or_codex_sending_authorized"] is False


def test_console_includes_not_approved_list() -> None:
    data = console()
    blocked = set(data["what_is_not_approved"])
    assert "Aiden autonomous sending" in blocked
    assert "payment collection" in blocked
    assert "core brain/CIEU/memory writeback" in blocked


def test_console_includes_feedback_event_instructions() -> None:
    data = console()
    instructions = data["feedback_recording_instructions"]
    for key in [
        "strong_positive",
        "weak_positive",
        "negative",
        "no_response_after_valid_action",
        "invalid_feedback",
        "paid_signal_candidate",
    ]:
        assert key in instructions
        assert instructions[key]


def test_console_blocks_e15_without_action_ledger_and_feedback() -> None:
    data = console()
    assert data["e15_entry_allowed"] is False
    rules = "\n".join(data["e15_entry_rules"])
    assert "valid action ledger exists" in rules
    assert "valid owner-entered feedback event exists" in rules


def test_console_does_not_authorize_aiden_sending() -> None:
    data = console()
    assert all(choice["aiden_sends"] is False for choice in data["owner_choices"])
    assert "no customer contact by Aiden/Codex" in CONSOLE_MD.read_text(encoding="utf-8")


def test_console_generates_copyable_approval_text() -> None:
    assert "```text" in CONSOLE_MD.read_text(encoding="utf-8")
    assert "Valid action ledger entries and feedback events are required before E15." in console()[
        "copyable_approval_text"
    ]


def test_repository_delivery_uses_host_bridge() -> None:
    request = json.loads(DELIVERY_REQUEST.read_text(encoding="utf-8"))
    assert request["milestone_id"] == "A1_B1_cross_repo_audit_owner_console"
    assert request["remote_confirmation_required"] is True
    assert "scripts/host_delivery_runner.py" in request["safety_boundary"]


def test_b1_says_owner_operated_is_transitional() -> None:
    data = console()
    assert data["architecture_note"]["owner_operated_is_transitional"] is True
    text = CONSOLE_MD.read_text(encoding="utf-8")
    assert "B1 是过渡层" in text


def test_b1_references_long_term_y_gov_gov_mcp_direction() -> None:
    data = console()
    direction = data["architecture_note"]["long_term_direction"]
    assert "Y*gov governance decision" in direction
    assert "gov-mcp execute/deny" in direction
    assert "constitutional_boundary_setter_not_operator" == data["architecture_note"]["owner_role"]


def test_explainer_exists_and_keeps_full_mission_open() -> None:
    text = EXPLAINER.read_text(encoding="utf-8")
    assert "B1 decision_console_rt1: 0" in text
    assert "B1 full_mission_rt1: 1" in text


def text_blob(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False)
