from office.mission_command.e54_ceo_brain_state_schema import build_l5_contract, build_ceo_brain_state, validate_l5_contract
from office.mission_command.e54_ceo_next_action_reasoner import build_next_action_reasoning_packet
from office.mission_command.e54_ceo_capability_growth_metrics import build_capability_growth_metrics

def test_l5_contract_validates_brain_state():
    reason=build_next_action_reasoning_packet(); metrics=build_capability_growth_metrics(); state=build_ceo_brain_state(reason, metrics); result=validate_l5_contract(state, build_l5_contract())
    assert result['valid'] is True
    assert state['external_action_allowed'] is False
