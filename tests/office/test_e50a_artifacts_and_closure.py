import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_e50a_artifacts_close_mcp_client_blocker():
    inspection = load("operations/external_validation/e50a_gov_mcp_tool_registration_inspection.json")
    harness = load("operations/external_validation/e50a_fake_fastmcp_harness_result.json")
    proof = load("operations/external_validation/e50a_local_tool_layer_proof_result.json")
    update = load("operations/external_validation/e50a_mcp_client_blocker_update.json")
    closure = load("operations/external_validation/e50a_czl_closure.json")
    assert inspection["fake_fastmcp_can_capture_registration"] is True
    assert harness["final_status"] == "tool_layer_allow_deny_closed"
    assert proof["final_status"] == "tool_layer_allow_deny_closed"
    assert update["new_status"] == "tool_layer_allow_deny_closed"
    assert update["whether_external_attempt_blocker_remains"] is False
    assert closure["no_external_action"] is True
    assert closure["no_real_client_config_mutation"] is True
