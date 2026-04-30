import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SUMMARY_DIR = ROOT / "l7_parallel_commercial_autonomy_sprint"
SECRET_HELPER = ROOT / "policy" / "secret_scanner_policy.py"


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_secret_helper():
    spec = importlib.util.spec_from_file_location("secret_scanner_policy", SECRET_HELPER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_l7_1_summary_and_lane_directories_exist() -> None:
    assert (SUMMARY_DIR / "l7_1_summary.json").is_file()
    summary = load_json("l7_parallel_commercial_autonomy_sprint/l7_1_summary.json")
    assert summary["lanes_executed"] == 6
    for path in [
        "l7_conservatism_debt_remediation_l7_1",
        "l7_revenue_opportunity_radar_l7_1",
        "l7_first_offer_hypothesis_builder",
        "l7_human_approval_workflow_v1",
        "l7_review_gated_memory_dry_run_v1",
        "l7_owner_runtime_cockpit_v2",
    ]:
        assert (ROOT / path).is_dir()


def test_conservatism_batch_and_revenue_scan_outputs_exist() -> None:
    batch = load_json("l7_conservatism_debt_remediation_l7_1/l7_1_p0_p1_remediation_batch.json")
    patched = load_json("l7_conservatism_debt_remediation_l7_1/l7_1_patched_files_report.json")
    scan = load_json("l7_revenue_opportunity_radar_l7_1/real_read_only_revenue_scan_report.json")
    assert batch["patched_files"]
    assert patched["patched_count"] >= 1
    assert scan["run_classification"] in {
        "real_revenue_scan_executed",
        "real_revenue_scan_blocked_by_config",
        "fixture_revenue_scan_executed",
        "partial_real_scan_no_action",
    }
    assert scan["manual_url_request_occurred"] is False


def test_opportunity_packets_and_offer_hypotheses_exist() -> None:
    packets = sorted((ROOT / "l7_revenue_opportunity_radar_l7_1/opportunity_packets").glob("*.json"))
    assert len(packets) >= 1
    packet = json.loads(packets[0].read_text(encoding="utf-8"))
    assert packet["read_only_revenue_work_allowed"] is True
    assert packet["actual_execution_blocked_until_approval"] is True

    offers = load_json("l7_first_offer_hypothesis_builder/offer_hypotheses.json")
    assert len(offers["offer_hypotheses"]) >= 1
    for offer in offers["offer_hypotheses"]:
        assert offer["human_approval_required_before_external_action"] is True
        assert "send outreach" in offer["forbidden_actions"]


def test_approval_workflow_defaults_blocked_until_human_approved() -> None:
    workflow = load_json("l7_human_approval_workflow_v1/approved_action_execution_preflight.json")
    defaults = workflow["all_execution_defaults"]
    assert defaults
    assert all(item["default_state"] == "blocked_until_human_approved" for item in defaults)
    assert all(item["execution_allowed_now"] is False for item in defaults)


def test_memory_dry_run_candidates_are_blocked_and_dry_run_only() -> None:
    receipts = load_json("l7_review_gated_memory_dry_run_v1/writeback_dry_run_receipts.json")
    assert len(receipts["dry_run_receipts"]) >= 1
    for receipt in receipts["dry_run_receipts"]:
        assert receipt["dry_run_only"] is True
        assert receipt["actual_writeback_occurred"] is False
        assert receipt["default_decision"] == "blocked_until_approved"


def test_owner_cockpit_v2_money_path() -> None:
    cockpit = load_json("l7_owner_runtime_cockpit_v2/owner_cockpit_v2.json")
    assert cockpit["what_do_i_own_now"]
    assert "first revenue" in cockpit["shortest_path_toward_first_revenue"]
    assert "bash scripts/run_l7_1_parallel_sprint.sh --mode local-parallel" == cockpit["next_recommended_command"]
    assert cockpit["external_side_effects_occurred"] is False
    assert cockpit["core_writeback_occurred"] is False


def test_orchestrator_script_exists_and_has_required_modes() -> None:
    script = (ROOT / "scripts/run_l7_1_parallel_sprint.sh").read_text(encoding="utf-8")
    assert "--mode scaffold" in script
    assert "local-parallel" in script
    assert "status" in script
    assert "manual URLs: not required" in script
    assert "secrets printed: no" in script


def test_no_ask_user_url_no_side_effects_no_core_writeback() -> None:
    receipts = [
        load_json("l7_parallel_commercial_autonomy_sprint/l7_1_no_action_receipt.json"),
        load_json("l7_revenue_opportunity_radar_l7_1/revenue_no_action_receipt.json"),
        load_json("l7_review_gated_memory_dry_run_v1/writeback_no_action_receipt.json"),
        load_json("l7_owner_runtime_cockpit_v2/owner_no_action_receipt.json"),
    ]
    for receipt in receipts:
        assert receipt["ask_user_for_url_occurred"] is False
        assert receipt["external_side_effects_occurred"] is False
        assert receipt["core_writeback_occurred"] is False
        assert receipt["secret_values_serialized"] is False


def test_policy_refs_and_hard_boundaries_preserved() -> None:
    manifest = load_json("l7_parallel_commercial_autonomy_sprint/l7_1_commercial_autonomy_manifest.json")
    assert manifest["policy_ref"] == "policy/action_capability_registry.json"
    blocked = " ".join(manifest["blocked_until_human_approval"]).lower()
    for term in ["outreach", "publication", "payment", "account", "writeback"]:
        assert term in blocked


def test_no_secret_serialization_in_l7_1_outputs() -> None:
    secret_helper = load_secret_helper()
    scoped_text = "\n".join(
        path.read_text(encoding="utf-8")
        for root in [
            "l7_parallel_commercial_autonomy_sprint",
            "l7_conservatism_debt_remediation_l7_1",
            "l7_revenue_opportunity_radar_l7_1",
            "l7_first_offer_hypothesis_builder",
            "l7_human_approval_workflow_v1",
            "l7_review_gated_memory_dry_run_v1",
            "l7_owner_runtime_cockpit_v2",
        ]
        for path in (ROOT / root).rglob("*")
        if path.is_file() and path.suffix in {".json", ".md"}
    )
    decisions = secret_helper.scan_text_for_secret_policy(scoped_text, file_path="tests/l7_parallel_commercial_autonomy_sprint/test_l7_parallel_commercial_autonomy_sprint.py")
    assert all(decision["safe_for_commit"] for decision in decisions)


def test_no_external_repo_modification_flags() -> None:
    summary = load_json("l7_parallel_commercial_autonomy_sprint/l7_1_summary.json")
    assert summary["y_star_gov_modified"] is False
    assert summary["gov_mcp_modified"] is False
    assert summary["db_log_wal_shm_active_agent_marker_content_read"] is False
