import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e70_self_evolution_schema_has_required_cieu_fields_and_boundaries():
    data = json.loads((ROOT / "operations/external_validation/e70_cieu_self_evolution_runtime_schema.json").read_text())
    fields = data["fields"]
    for field in [
        "Y_star_capability_target",
        "X_t_current_capability_state",
        "U_t_improvement_action",
        "Y_t_plus_1_measured_improvement",
        "R_t_plus_1_remaining_gap",
    ]:
        assert field in fields
    assert "autonomous_external_installation" in data["prohibited_improvement_modes"]
    assert "owner_gated_skill_installation_plan" in data["allowed_improvement_modes"]
    assert data["old_creed_integrated"] is True
