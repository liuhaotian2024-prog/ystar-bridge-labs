import json
from pathlib import Path
from office.mission_command.e31_existing_real_world_observation_wheel_inventory import build_existing_real_world_observation_wheel_inventory
ROOT = Path(__file__).resolve().parents[2]
def test_existing_wheels_audited_before_observation():
    data = json.loads((ROOT / "operations/external_validation/e31_existing_real_world_observation_wheel_inventory.json").read_text())
    built = build_existing_real_world_observation_wheel_inventory()
    assert data["audit_completed_before_e31_build"] is True
    assert data["audit_did_not_stop_at_gate"] is True
    assert data["repos_scanned_count"] == 4
    assert data["existing_observation_wheels_found"] == 23
    assert data["safe_observation_path_available"] is True
    assert built["existing_observation_wheels_found"] == data["existing_observation_wheels_found"]
