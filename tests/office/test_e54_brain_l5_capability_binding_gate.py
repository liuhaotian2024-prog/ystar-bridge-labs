from office.mission_command.e54_brain_l5_capability_binding_gate import run_brain_l5_capability_binding_gate, build_e54_capability_binding_payload

def test_capability_binding_denies_cognitive_outside_brain():
    assert run_brain_l5_capability_binding_gate()['passed'] is True
    p=build_e54_capability_binding_payload()
    p['capability_bindings'][0]['actual_binding']=[]; p['capability_bindings'][0]['binding_status']='wrong_centerline'
    assert run_brain_l5_capability_binding_gate(p)['passed'] is False
