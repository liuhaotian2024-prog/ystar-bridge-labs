from __future__ import annotations

from pathlib import Path

from office.mission_command.c3_action_ledger_state import build_c3_action_ledger_state_fixture
from office.mission_command.c3_czl_closure import build_c3_czl_closure, validate_c3_czl_closure
from office.mission_command.c3_decision_replay import replay_c3_decisions
from office.mission_command.c3_dry_run_execution_receipts import build_c3_dry_run_receipts
from office.mission_command.c3_e15_next_action_packet import build_c3_e15_next_action_packet
from office.mission_command.c3_feedback_intake_runtime import build_c3_feedback_signal_fixture
from office.mission_command.c3_narrow_constitutional_envelope import build_c3_narrow_envelope
from office.mission_command.c3_owner_handoff_execution_batch import build_c3_owner_handoff_batch
from office.mission_command.c3_validation_batch_selector import build_c3_validation_batch


ROOT = Path(__file__).resolve().parents[2]
BASE_HEAD = "73d0f9513b2481ba0693ee355736094a05b30563"


def closure_payload() -> dict:
    envelope = build_c3_narrow_envelope(ROOT).to_dict()
    batch = build_c3_validation_batch(ROOT)
    replay = replay_c3_decisions(batch, envelope)
    receipts = build_c3_dry_run_receipts(batch, replay)
    ledger = build_c3_action_ledger_state_fixture(batch, receipts)
    handoff = build_c3_owner_handoff_batch(batch)
    e15 = build_c3_e15_next_action_packet(
        batch=batch,
        replay_report=replay,
        handoff_batch=handoff,
        feedback_fixture=build_c3_feedback_signal_fixture(),
    )
    return build_c3_czl_closure(
        base_head=BASE_HEAD,
        envelope=envelope,
        batch=batch,
        replay_report=replay,
        dry_run_receipts=receipts,
        ledger_fixture=ledger,
        e15_packet=e15,
    ).to_dict()


def test_c3_czl_closure_reaches_zero_residual_without_external_action() -> None:
    closure = closure_payload()
    assert validate_c3_czl_closure(closure) == []
    assert closure["r_t1"] == 0
    assert closure["y_t1"]["first_governed_validation_batch_owner_handoff_ready"] is True
    assert closure["y_t1"]["external_action_executed"] is False


def test_c3_czl_closure_records_strict_no_side_effect_receipt() -> None:
    closure = closure_payload()
    assert closure["x_t"]["c2_remote_confirmed_base"] == BASE_HEAD
    assert "E15_next_action_decision_packet" in closure["u"]
    assert all(value is False for value in closure["no_external_side_effects"].values())
