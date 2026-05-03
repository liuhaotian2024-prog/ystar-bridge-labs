from __future__ import annotations

from pathlib import Path

from office.mission_command.c3_owner_handoff_execution_batch import (
    build_c3_owner_handoff_batch,
    render_c3_owner_handoff_batch,
    validate_c3_owner_handoff_batch,
)
from office.mission_command.c3_validation_batch_selector import build_c3_validation_batch


ROOT = Path(__file__).resolve().parents[2]


def test_c3_owner_handoff_batch_contains_primary_and_fallback_items() -> None:
    packet = build_c3_owner_handoff_batch(build_c3_validation_batch(ROOT))
    assert validate_c3_owner_handoff_batch(packet) == []
    assert len(packet["handoff_items"]) == 5


def test_c3_owner_handoff_batch_has_copy_paste_and_bound_ids() -> None:
    item = build_c3_owner_handoff_batch(build_c3_validation_batch(ROOT))["handoff_items"][0]
    assert "I am Aiden" in item["copy_paste_block"]
    assert item["ledger_id_to_mark_as_sent"].startswith("ledger_")
    assert item["feedback_event_id_to_use_after_reply"].startswith("feedback_")


def test_c3_owner_handoff_render_not_authorized_list() -> None:
    rendered = render_c3_owner_handoff_batch(build_c3_owner_handoff_batch(build_c3_validation_batch(ROOT)))
    assert "Aiden/Codex sending" in rendered
    assert "payment" in rendered
    assert "login" in rendered
