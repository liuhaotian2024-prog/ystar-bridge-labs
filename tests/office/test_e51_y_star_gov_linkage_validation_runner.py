from office.mission_command.e51_y_star_gov_linkage_validation_runner import validate_labs_manifest_through_y_star_gov
from office.mission_command.e51_labs_runtime_linkage_manifest import build_labs_runtime_linkage_manifest


def test_e51_y_star_gov_validation_allows_current_manifest_and_rejects_broken_p0():
    result = validate_labs_manifest_through_y_star_gov()
    assert result['passed'] is True
    assert result['anti_drift_gate']['status'] == 'anti_drift_gate_passed'
    broken = build_labs_runtime_linkage_manifest()
    broken['artifacts'][0]['readers'] = []
    broken['artifacts'][0]['next_runtime_readers'] = []
    broken_result = validate_labs_manifest_through_y_star_gov(broken)
    assert broken_result['passed'] is False
    assert broken_result['anti_drift_gate']['allowed'] is False
