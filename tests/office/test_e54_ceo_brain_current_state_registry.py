from office.mission_command.e54_ceo_brain_current_state_registry import build_current_state_registry, resolve_current_state

def test_registry_ignores_reference_only_and_keeps_e53_pending():
    reg=build_current_state_registry(); res=resolve_current_state()
    assert any(s['source_type']=='reference_only' for s in reg['sources'])
    assert 'old_e49_route_decision' in res['stale_sources_ignored']
    assert res['owner_approval_status'] == 'pending_owner_decision'
    assert res['external_action_allowed'] is False
    assert res['non_sent_template_status'] == 'not_sent'
    assert res['pending_owner_decision_treated_as_approval'] is False
