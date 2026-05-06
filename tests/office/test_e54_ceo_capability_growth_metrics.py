from office.mission_command.e54_ceo_capability_growth_metrics import build_capability_growth_metrics

def test_growth_metrics_have_self_catch_and_board_plan():
    data=build_capability_growth_metrics()
    assert data['estimate_class'] == 'artifact_supported_estimate'
    assert 'self_catch_rate' in data
    assert data['future_metric_plan']['structured_board_correction_event_required'] is True
