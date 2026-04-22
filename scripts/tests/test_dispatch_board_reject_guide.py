"""
Test: dispatch_board "门卫 + 导游" reject-with-guide format.

Milestone 9c 2026-04-21: Board catch — "治理不是简单拒, 是拒的同时给正确行为指导".
Board 2026-04-20 "governance = 门卫 + 导游" thesis. Every enforcement deny MUST
return violated_rule + fix_command + template + example + docs_url.

M-tag: M-2a structural enforcement, with guide embedded (not just deny).
"""
import os
import sys
import io
import contextlib
import types
import pytest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dispatch_board
import czl_bus


def _args(**kw):
    defaults = dict(
        atomic_id="CZL-TEST-GUIDE",
        scope="tests/only",
        description="too short",
        urgency="P1",
        estimated_tool_uses=5,
    )
    defaults.update(kw)
    return types.SimpleNamespace(**defaults)


def _capture_stderr(fn, *args, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        rc = fn(*args, **kw)
    return rc, buf.getvalue()


def test_reject_uses_existing_REDIRECT_prefix(tmp_path, monkeypatch):
    """Board catch: MUST use existing Y*gov '[Y*] REDIRECT:' prefix from
    hook.py line 1357, not invent new '═══ ENFORCEMENT ═══' banner."""
    monkeypatch.setattr(dispatch_board, "BOARD_PATH", tmp_path / "board.json")
    monkeypatch.setattr(dispatch_board, "LOCK_PATH", tmp_path / "board.lock")
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", tmp_path / "bus.jsonl")

    rc, err = _capture_stderr(dispatch_board.post_task, _args())
    assert rc == 2
    assert "[Y*] REDIRECT:" in err
    assert "czl_minimum_goal_content" in err


def test_reject_includes_m_tag(tmp_path, monkeypatch):
    monkeypatch.setattr(dispatch_board, "BOARD_PATH", tmp_path / "board.json")
    monkeypatch.setattr(dispatch_board, "LOCK_PATH", tmp_path / "board.lock")
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", tmp_path / "bus.jsonl")

    rc, err = _capture_stderr(dispatch_board.post_task, _args())
    assert "VIOLATED_M_TAG:" in err
    assert "M-2a" in err


def test_reject_uses_existing_WRONG_ACTION_CORRECT_STEPS_schema(tmp_path, monkeypatch):
    """boundary_enforcer.py uses `wrong_action` + `correct_steps[]` pattern.
    dispatch_board reject MUST align to same schema, not self-invent."""
    monkeypatch.setattr(dispatch_board, "BOARD_PATH", tmp_path / "board.json")
    monkeypatch.setattr(dispatch_board, "LOCK_PATH", tmp_path / "board.lock")
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", tmp_path / "bus.jsonl")

    rc, err = _capture_stderr(dispatch_board.post_task, _args())
    assert "WRONG_ACTION:" in err
    assert "CORRECT_STEPS:" in err
    # Steps must be numbered (boundary_enforcer precedent)
    assert "1." in err and "2." in err and "3." in err


def test_reject_includes_FIX_COMMAND_existing_hookpy_key(tmp_path, monkeypatch):
    """hook.py line 1358 uses `FIX_COMMAND:` (uppercase). Align."""
    monkeypatch.setattr(dispatch_board, "BOARD_PATH", tmp_path / "board.json")
    monkeypatch.setattr(dispatch_board, "LOCK_PATH", tmp_path / "board.lock")
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", tmp_path / "bus.jsonl")

    rc, err = _capture_stderr(dispatch_board.post_task, _args())
    assert "FIX_COMMAND:" in err


def test_reject_includes_5tuple_template(tmp_path, monkeypatch):
    monkeypatch.setattr(dispatch_board, "BOARD_PATH", tmp_path / "board.json")
    monkeypatch.setattr(dispatch_board, "LOCK_PATH", tmp_path / "board.lock")
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", tmp_path / "bus.jsonl")

    rc, err = _capture_stderr(dispatch_board.post_task, _args())
    assert "y_star" in err
    assert "x_t" in err
    assert "u (actions)" in err
    assert "y_t_plus_1" in err
    assert "rt_value" in err


def test_reject_includes_fix_example(tmp_path, monkeypatch):
    monkeypatch.setattr(dispatch_board, "BOARD_PATH", tmp_path / "board.json")
    monkeypatch.setattr(dispatch_board, "LOCK_PATH", tmp_path / "board.lock")
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", tmp_path / "bus.jsonl")

    rc, err = _capture_stderr(dispatch_board.post_task, _args(atomic_id="CZL-MY-NEW"))
    assert "FIX_EXAMPLE:" in err
    assert "CZL-MY-NEW" in err  # echo caller's atomic_id
    assert "--description" in err


def test_reject_includes_SKILL_REF_existing_boundary_enforcer_key(tmp_path, monkeypatch):
    """boundary_enforcer uses `skill_ref` pointing to governance docs. Align."""
    monkeypatch.setattr(dispatch_board, "BOARD_PATH", tmp_path / "board.json")
    monkeypatch.setattr(dispatch_board, "LOCK_PATH", tmp_path / "board.lock")
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", tmp_path / "bus.jsonl")

    rc, err = _capture_stderr(dispatch_board.post_task, _args())
    assert "SKILL_REF:" in err
    assert "czl_unified_communication_protocol" in err


def test_reject_for_generic_filler_also_has_guide(tmp_path, monkeypatch):
    """Not just short — generic 'TBD' should also trigger full guide."""
    monkeypatch.setattr(dispatch_board, "BOARD_PATH", tmp_path / "board.json")
    monkeypatch.setattr(dispatch_board, "LOCK_PATH", tmp_path / "board.lock")
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", tmp_path / "bus.jsonl")

    rc, err = _capture_stderr(dispatch_board.post_task,
                               _args(description="TBD"))
    assert rc == 2
    assert "FIX_COMMAND:" in err  # align to hook.py uppercase convention
    assert "y_star" in err  # full 5-tuple template still shown


def test_accept_path_does_not_print_guide(tmp_path, monkeypatch):
    """Happy-path (valid description) should NOT print reject-with-guide."""
    monkeypatch.setattr(dispatch_board, "BOARD_PATH", tmp_path / "board.json")
    monkeypatch.setattr(dispatch_board, "LOCK_PATH", tmp_path / "board.lock")
    monkeypatch.setattr(czl_bus, "DEFAULT_BUS", tmp_path / "bus.jsonl")
    monkeypatch.setattr(dispatch_board, "emit_cieu", lambda *a, **kw: None)

    valid = "Properly long and concrete goal statement above 20 chars"
    rc, err = _capture_stderr(dispatch_board.post_task,
                               _args(description=valid))
    assert rc != 2
    assert "ENFORCEMENT REJECT" not in err
