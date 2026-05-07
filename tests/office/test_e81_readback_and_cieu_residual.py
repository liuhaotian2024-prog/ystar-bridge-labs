import json
from pathlib import Path

from office.mission_command.e46b_ceo_brain_adapter import load_ceo_brain_context
from office.mission_command.e81_readback import run_e81_readback_smoke


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e81_readback_reports_enforcement_mode_and_bypass_policy():
    readback = _load("operations/external_validation/e81_ceo_cognitive_os_readback.json")
    smoke = run_e81_readback_smoke(ROOT)

    assert smoke["passes"] is True
    assert readback["current_enforcement_mode"] == "bridge_labs_pre_sync_validator"
    assert readback["YstarGov_sync_status"] == "YstarGov_pending_owner_approved_patch"
    assert readback["bypass_allowed"] is False
    assert readback["bypass_result"] == "DENY"


def test_e81_ceo_adapter_reads_cognitive_os_state():
    context = load_ceo_brain_context({"task_title": "E81 readback", "task_description": "cognitive OS"})

    assert context["current_e81_cognitive_OS_contract_installed"] is True
    assert context["current_e81_future_CEO_work_requires_pre_action_packet"] is True
    assert context["current_e81_future_CEO_work_requires_post_action_residual"] is True
    assert context["current_e81_bypass_allowed"] is False
    assert context["current_e81_enforcement_mode"] == "bridge_labs_pre_sync_validator"


def test_e81_cieu_residual_records_y_star_gov_sync_gap_without_external_action():
    residual = _load("operations/external_validation/e81_cieu_residual_for_cognitive_os_runtime_binding.json")

    for key in ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"]:
        assert key in residual
    assert residual["U_t"]["external_action_executed"] is False
    assert residual["U_t"]["YstarGov_mutated"] is False
    assert "Y-star-gov canonical sync still requires later owner-approved patch" in residual["R_t_plus_1"]["residual_gaps"]
