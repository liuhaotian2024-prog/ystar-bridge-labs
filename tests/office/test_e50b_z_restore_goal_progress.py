from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_e50b_required_artifacts_exist_after_delivery():
    required = [
        'operations/external_validation/e50b_base_state_manifest.json',
        'operations/external_validation/e50b_counterfactual_asset_inventory.json',
        'operations/external_validation/e50b_counterfactual_disconnection_diagnosis.json',
        'operations/external_validation/e50b_counterfactual_runtime_adapter_smoke.json',
        'operations/external_validation/e50b_counterfactual_money_route_matrix.json',
        'operations/external_validation/e50b_ceo_commercial_decision_packet.json',
        'operations/external_validation/e50b_czl_closure.json',
        'operations/external_validation/e50b_cieu_residual_summary.json',
    ]
    for rel in required:
        assert (ROOT / rel).exists(), rel
