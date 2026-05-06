from office.mission_command.e51_runtime_archaeology import build_runtime_archaeology


def test_e51_runtime_archaeology_finds_cross_repo_runtime_assets():
    data = build_runtime_archaeology()
    paths = {item['path'] for item in data['resources']}
    assert 'office/mission_command/e50c_ceo_brain_centerline_smoke.py' in paths
    assert 'ystar/governance/runtime_linkage.py' in paths
    assert 'gov_mcp/runtime_linkage_tools.py' in paths
    assert data['k9audit_read_only'] is True
    assert data['p0_written_not_read'] == []
