from __future__ import annotations

from pathlib import Path

from office.mission_command.e15d_controlled_outbound_domain import (
    build_e15d_controlled_outbound_domain,
    load_e15a_console,
    validate_e15d_controlled_outbound_domain,
)


ROOT = Path(__file__).resolve().parents[2]


def test_e15d_domain_makes_validation_messaging_governed_not_hard_blocked() -> None:
    domain = build_e15d_controlled_outbound_domain(load_e15a_console(ROOT))
    assert validate_e15d_controlled_outbound_domain(domain) == []
    assert domain["draft_only_available"] is True
    assert domain["send_gated_available_after_authorization"] is True
    assert domain["real_send_allowed_now"] is False


def test_e15d_domain_preserves_owner_hard_gates() -> None:
    domain = build_e15d_controlled_outbound_domain(load_e15a_console(ROOT))
    assert "payment" in domain["hard_gates"]
    assert "contract" in domain["hard_gates"]
    assert "core_brain_cieu_memory_canonical_writeback" in domain["hard_gates"]
    assert len(domain["source_action_ids"]) == 3
