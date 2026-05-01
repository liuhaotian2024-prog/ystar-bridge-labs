from pathlib import Path

from office.mission_command.e2_cycle import build_e2_cycle


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_residual_candidates_are_review_gated():
    cycle = build_e2_cycle(REPO_ROOT)
    assert cycle["residual_candidates"]
    assert all(item["review_required"] and not item["writeback_allowed"] for item in cycle["residual_candidates"])


def test_e2_czl_closure_distinguishes_blocked_vs_complete():
    cycle = build_e2_cycle(REPO_ROOT)
    assert cycle["final_status"] in {"complete", "BLOCKED_BY_MISSING_LIVE_RESEARCH_CONFIG", "residual"}
    if cycle["final_status"] == "BLOCKED_BY_MISSING_LIVE_RESEARCH_CONFIG":
        assert cycle["exact_blocking_owner_config_action"]
        assert cycle["rt1_score"] == 0


def test_no_external_side_effects_or_writeback_or_obligation_registration():
    cycle = build_e2_cycle(REPO_ROOT)
    assert cycle["external_action_executed"] is False
    assert cycle["y_t1"]["no_external_side_effects"] is True
    assert all(not item["writeback_allowed"] for item in cycle["residual_candidates"])


def test_no_cieu_write_no_coo_invented():
    text = str(build_e2_cycle(REPO_ROOT))
    assert "COO" not in text
    assert "CIEU write: true" not in text
