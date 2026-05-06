from office.mission_command.e50b_counterfactual_asset_inventory import build_counterfactual_asset_inventory


def test_existing_counterfactual_assets_detected():
    data = build_counterfactual_asset_inventory()
    paths = {asset['path'] for asset in data['assets']}
    assert 'agents/CEO.md' in paths
    assert '.claude/agents/ceo.md' in paths
    assert 'knowledge/ceo/wisdom/meta/autonomous_loop_algorithm.md' in paths
    assert 'office/mission_command/counterfactual_router.py' in paths
    assert data['asset_count'] >= 8


def test_gov005_and_counterfactual_symbols_recognized():
    data = build_counterfactual_asset_inventory()
    assert any(asset['contains_xt_y_star_u_rt'] for asset in data['assets'])
    assert any('GOV-005' in asset['evidence_excerpt_or_symbol'] or asset['contains_counterfactual_delta'] for asset in data['assets'])
