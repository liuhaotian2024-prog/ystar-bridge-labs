from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_e50c_required_artifacts_exist_after_delivery():
    required = [
        'operations/external_validation/e50c_base_state_manifest.json',
        'operations/external_validation/e50c_ceo_brain_centerline_diagnosis.json',
        'operations/external_validation/e50c_ceo_brain_loader_update.json',
        'operations/external_validation/e50c_ceo_brain_centerline_smoke_result.json',
        'operations/external_validation/e50c_e51_readiness_gate.json',
        'operations/external_validation/e50c_czl_closure.json',
        'operations/external_validation/e50c_cieu_residual_summary.json',
    ]
    for rel in required:
        assert (ROOT / rel).exists(), rel
