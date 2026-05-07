import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_cieu_residual_contains_required_five_tuple():
    residual = _load("operations/external_validation/e76_e77_cieu_residual_for_lineage_decision_and_l3_pilot.json")

    for key in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert key in residual
    assert residual["X_t"]["prior_public_read_lineage_exists"] is True
    assert residual["Y_t_plus_1"]["phase_B_executed"] is False
    assert residual["R_t_plus_1"]["owner_approval_still_pending"] is True


def test_ceo_readback_answers_lineage_decision_execution_and_readiness():
    readback = _load("operations/external_validation/e76_e77_ceo_readback.json")

    assert readback["did_execute_L3"] is False
    assert readback["owner_approval_explicit"] is False
    assert readback["prior_public_read_lineage_exists"] is True
    assert readback["prior_public_read_lineage_count"] >= 6
    assert "Historical public-read" in readback["why_not_first_external_read_only_research"]
    assert readback["L2_ready"] is True
    assert readback["L3_status"] == "pending_owner_decision"
    assert readback["L4_ready"] is False
    assert readback["L5_ready"] is False

