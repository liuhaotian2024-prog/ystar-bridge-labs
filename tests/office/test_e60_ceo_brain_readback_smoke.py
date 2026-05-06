from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
from office.mission_command.e60_ceo_brain_readback_smoke import run_ceo_brain_readback_smoke


def test_e60_ceo_brain_reads_market_readiness_state():
    data = run_ceo_brain_readback_smoke()
    assert data["passes"] is True
    observed = data["observed_state"]
    assert observed["selected_next_milestone"] == "E61_live_public_read_adapter_repair_or_host_network_refresh"
    assert observed["fixture_only_evidence_treated_as_live_market_freshness"] is False
    context = load_ceo_brain_context({"task_title": "E60 readback smoke", "task_description": "market readiness"})
    assert context["current_market_entry_readiness_level"] == "L3_external_intelligence_structurally_ready"
    assert context["current_market_readiness_external_action_allowed"] is False
