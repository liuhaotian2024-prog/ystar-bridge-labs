import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_e47_artifacts_and_closure():
    gate = json.loads((ROOT / "operations/external_validation/e47_full_capability_coverage_gate.json").read_text())
    selected = json.loads((ROOT / "operations/external_validation/e47_money_route_selected_path.json").read_text())
    owner = json.loads((ROOT / "operations/external_validation/e47_consolidated_owner_decision_packet.json").read_text())
    closure = json.loads((ROOT / "operations/external_validation/e47_czl_closure.json").read_text())
    assert gate["coverage_gate_passed"] is True
    assert selected["route_id"] == "governed_agent_action_proof_packet"
    assert owner["recommended_next_milestone"] == "E48_gov_mcp_server_client_demo_closure"
    for key in ["no_customer_contact", "no_expert_contact", "no_human_identification", "no_scraping", "no_send", "no_publish", "no_login", "no_provider_API_execution", "no_internet_install", "no_payment", "no_secret_use"]:
        assert closure[key] is True
