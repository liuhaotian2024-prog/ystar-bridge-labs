from pathlib import Path

from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
from office.mission_command.e76_e77_readback import run_e76_e77_readback_smoke


ROOT = Path(__file__).resolve().parents[2]


def test_e76_e77_readback_smoke_passes():
    result = run_e76_e77_readback_smoke(ROOT)

    assert result["passes"] is True
    assert result["external_action_allowed"] is False


def test_ceo_brain_adapter_reads_e76_e77_state():
    context = load_ceo_brain_context({"task_title": "E76/E77 readback", "task_description": "lineage and decision gate"})

    assert context["current_e76_e77_owner_decision_status"] == "pending_owner_decision"
    assert context["current_e76_e77_phase_b_authorized"] is False
    assert context["current_e76_e77_l3_executed"] is False
    assert context["current_e76_e77_prior_public_read_lineage_count"] >= 6
    assert context["current_e76_e77_L4_ready"] is False
    assert context["current_e76_e77_L5_ready"] is False

