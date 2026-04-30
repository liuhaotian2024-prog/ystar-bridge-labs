import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "l7_labs_office_legacy_integration"


def load_json(relative_path: str):
    return json.loads((OUT / relative_path).read_text(encoding="utf-8"))


def scoped_text_outputs() -> str:
    chunks = []
    for suffix in ("*.json", "*.md", "*.html"):
        for path in OUT.rglob(suffix):
            chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def test_clone_inspection_receipt_exists():
    receipt = load_json("legacy_repo_inspection/ystar_bridge_labs_clone_receipt.json")
    assert receipt["legacy_repo_available"] is True
    assert receipt["legacy_repo_path"].endswith("ystar-bridge-labs")
    assert receipt["legacy_repo_modified_by_scanner"] is False


def test_legacy_team_discovery_report_exists():
    report = load_json("legacy_repo_inspection/legacy_team_discovery_report.json")
    assert report["legacy_agents"]
    assert (OUT / "legacy_repo_inspection/legacy_team_discovery_report.md").exists()


def test_original_team_registry_contains_verified_members():
    registry = load_json("original_team_registry/original_team_registry.json")
    agent_ids = {agent["agent_id"] for agent in registry["agents"]}
    required = {
        "haotian_board_founder",
        "aiden_ceo",
        "ethan_cto",
        "sofia_cmo",
        "marco_cfo",
        "zara_cso",
        "samantha_secretary",
        "leo_engineer",
        "maya_engineer",
        "ryan_engineer",
        "jordan_engineer",
        "jinjin_k9_scout",
    }
    assert required <= agent_ids


def test_no_coo_invented_as_legacy_member():
    registry = load_json("original_team_registry/original_team_registry.json")
    for agent in registry["agents"]:
        joined = f"{agent['agent_id']} {agent['display_name']} {agent['legacy_role']}".lower()
        assert "coo" not in joined
        assert "operator" not in joined
    summary = load_json("l7_4_labs_office_summary.json")
    assert summary["coo_invented_as_legacy_member"] is False


def test_new_l7_capability_slots_are_separate_from_legacy_identities():
    slots = load_json("legacy_to_current_mapping/new_l7_capability_slots_not_legacy_agents.json")
    assert slots["slots"]
    for slot in slots["slots"]:
        assert slot["legacy_identity"] is None
        assert "not_legacy" in slot["status"] or "not_legacy_person" in slot["status"]


def test_legacy_to_current_mapping_exists():
    mapping = load_json("legacy_to_current_mapping/legacy_to_current_runtime_mapping.json")
    assert mapping["mappings"]
    assert all(row["identity_preserved"] for row in mapping["mappings"])


def test_office_home_exists():
    home = load_json("office_home/labs_office_home.json")
    assert "Y*Bridge Labs" in home["identity"]
    assert (OUT / "office_home/labs_office_home.md").exists()
    assert (OUT / "office_home/labs_office_home.html").exists()


def test_agent_rooms_exist_for_each_registry_member():
    registry = load_json("original_team_registry/original_team_registry.json")
    for agent in registry["agents"]:
        assert (OUT / "agent_rooms" / f"{agent['agent_id']}_room.json").exists()
        assert (OUT / "agent_rooms" / f"{agent['agent_id']}_room.md").exists()


def test_interaction_protocol_exists():
    protocol_dir = OUT / "interaction_protocol"
    assert (protocol_dir / "owner_to_agent_message_schema.json").exists()
    assert (protocol_dir / "ceo_delegation_schema.json").exists()
    assert (protocol_dir / "interaction_protocol.md").exists()
    assert "not an invented legacy person" in (protocol_dir / "interaction_protocol.md").read_text(encoding="utf-8")


def test_work_queue_exists():
    queue = load_json("team_work_queue/team_work_queue.json")
    assert queue["work_items"]
    assert (OUT / "team_work_queue/agent_inboxes/aiden_ceo_inbox.json").exists()
    assert (OUT / "team_work_queue/safe_self_work_policy.json").exists()
    assert (OUT / "team_work_queue/approval_required_policy.json").exists()


def test_integration_gap_report_exists_and_names_mistake_class():
    report = load_json("integration_gap_report/integration_gap_report.json")
    assert "new L7 role assumptions" in report["previous_mistake_class"]
    assert "Operator/COO" in report["new_l7_roles_that_do_not_map_to_legacy_identities"]
    assert (OUT / "integration_gap_report/integration_gap_report.md").exists()


def test_runner_exists_and_status_mode_works():
    runner = ROOT / "scripts/run_l7_4_labs_office_legacy_integration.sh"
    assert runner.exists()
    result = subprocess.run(
        ["bash", str(runner), "--mode", "status"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Y*Bridge Labs Office status" in result.stdout


def test_no_ask_user_url_or_external_side_effects():
    summary = load_json("l7_4_labs_office_summary.json")
    receipt = load_json("l7_4_labs_office_no_action_receipt.json")
    assert summary["ask_user_url_occurred"] is False
    assert receipt["ask_user_url_occurred"] is False
    assert summary["external_side_effects_occurred"] is False
    assert receipt["external_side_effects_occurred"] is False
    assert "ask-user-url" not in scoped_text_outputs().lower()


def test_no_core_writeback_or_secret_serialization():
    text = scoped_text_outputs()
    lowered = text.lower()
    summary = load_json("l7_4_labs_office_summary.json")
    assert summary["core_writeback_occurred"] is False
    assert summary["secret_printed_stored_in_repo"] is False
    assert "tvly-" not in lowered
    assert "bearer " not in lowered
    assert "api_key=" not in lowered
    assert "api-key" not in lowered


def test_no_db_wal_shm_log_active_agent_content_read_by_scanner():
    receipt = load_json("legacy_repo_inspection/ystar_bridge_labs_clone_receipt.json")
    no_action = load_json("legacy_repo_inspection/legacy_discovery_no_action_receipt.json")
    summary = load_json("l7_4_labs_office_summary.json")
    assert receipt["db_wal_shm_log_active_agent_content_read"] is False
    assert no_action["db_wal_shm_log_active_agent_content_read"] is False
    assert summary["db_log_wal_shm_active_agent_marker_content_read"] is False


def test_ystar_bridge_labs_and_gov_repos_not_modified_by_builder():
    summary = load_json("l7_4_labs_office_summary.json")
    receipt = load_json("l7_4_labs_office_no_action_receipt.json")
    assert summary["ystar_bridge_labs_modified"] is False
    assert receipt["ystar_bridge_labs_modified"] is False
    assert summary["y_star_gov_modified"] is False
    assert summary["gov_mcp_modified"] is False
