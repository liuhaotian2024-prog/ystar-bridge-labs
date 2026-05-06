from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
from office.mission_command.e61_ceo_brain_readback_smoke import run_ceo_brain_readback_smoke


def test_e61_ceo_brain_reads_live_public_read_state():
    data = run_ceo_brain_readback_smoke()
    assert data["passes"] is True
    context = load_ceo_brain_context({"task_title": "E61 readback", "task_description": "public read state"})
    assert context["current_live_public_read_final_status"] in {
        "live_public_read_adapter_repaired_and_smoke_passed",
        "live_public_read_code_repaired_but_host_network_unavailable",
        "live_public_read_blocker_diagnosed_no_code_repair_needed",
        "live_public_read_adapter_still_blocked",
    }
    assert context["current_live_public_read_external_action_allowed"] is False
