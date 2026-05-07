import json
from pathlib import Path

from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
from office.mission_command.e79_readback import run_e79_readback_smoke


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e79_cieu_residual_has_five_tuple_and_no_external_action():
    residual = _load("operations/external_validation/e79_cieu_residual_for_ceo_judgment_upgrade_and_l4_packet.json")

    for key in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert key in residual
    assert residual["X_t"]["CEO_judgment_quality_suspect"] is True
    assert residual["U_t"]["external_action_executed"] is False
    assert residual["Y_t_plus_1"]["quality_gate_passed"] is True
    assert "no paid signal" in residual["R_t_plus_1"]["residual_gaps"]


def test_e79_ceo_readback_and_adapter_report_strategy_upgrade():
    smoke = run_e79_readback_smoke(ROOT)
    readback = _load("operations/external_validation/e79_ceo_readback.json")
    context = load_ceo_brain_context({"task_title": "E79 readback", "task_description": "strategic judgment"})

    assert smoke["passes"] is True
    assert readback["E79_status"] == "ceo_strategic_judgment_upgraded_and_l4_packet_prepared"
    assert readback["quality_gate_passed"] is True
    assert readback["L4_execution_authorized"] is False
    assert context["current_e79_quality_gate_passed"] is True
    assert "do not first buy governance" in context["current_e79_selected_strategic_thesis"]
    assert context["current_e79_L4_execution_authorized"] is False

