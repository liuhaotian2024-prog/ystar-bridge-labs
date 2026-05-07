import json
from pathlib import Path

from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
from office.mission_command.e78_readback import run_e78_readback_smoke


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e78_cieu_residual_has_five_tuple_and_l3_execution():
    residual = _load("operations/external_validation/e78_cieu_residual_for_l3_research_pilot.json")

    for key in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert key in residual
    assert residual["X_t"]["owner_approval_block_present"] is True
    assert residual["U_t"]["executed_action"] == "owner-approved L3 read-only external research pilot"
    assert residual["Y_t_plus_1"]["L3_executed"] is True
    assert "no paid signal" in residual["R_t_plus_1"]["residual_gaps"]


def test_e78_ceo_readback_and_adapter_report_l3_result():
    smoke = run_e78_readback_smoke(ROOT)
    readback = _load("operations/external_validation/e78_ceo_readback.json")
    context = load_ceo_brain_context({"task_title": "E78 readback", "task_description": "owner-approved L3"})

    assert smoke["passes"] is True
    assert readback["did_execute_L3"] is True
    assert readback["owner_approval_explicit"] is True
    assert readback["L4_owner_decision_packet_preparation_justified"] is True
    assert readback["L4_execution_ready"] is False
    assert context["current_e78_l3_executed"] is True
    assert context["current_e78_public_read_source_count"] >= 20
    assert context["current_e78_L5_ready"] is False

