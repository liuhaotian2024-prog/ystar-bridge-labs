from office.mission_command.e52_capability_binding_gate import build_e52_capability_binding_payload, run_e52_capability_binding_gate


def test_e52_capability_binding_gate_passes_valid_and_denies_behavior_bypass():
    assert run_e52_capability_binding_gate()['passed'] is True
    broken = build_e52_capability_binding_payload()
    for record in broken['capability_bindings']:
        if record['functional_class'] == 'behavior_control_capability':
            record['actual_binding'] = ['Y_star_gov_boundary']
            record['binding_status'] = 'wrong_centerline'
            break
    assert run_e52_capability_binding_gate(broken)['passed'] is False
