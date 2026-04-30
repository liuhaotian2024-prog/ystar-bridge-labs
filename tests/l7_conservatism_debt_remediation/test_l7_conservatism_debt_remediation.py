import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "l7_conservatism_debt_remediation"
POLICY_HELPER = ROOT / "policy" / "policy_decision.py"
SECRET_HELPER = ROOT / "policy" / "secret_scanner_policy.py"


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_policy_helper():
    spec = importlib.util.spec_from_file_location("policy_decision", POLICY_HELPER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def load_secret_helper():
    spec = importlib.util.spec_from_file_location("secret_scanner_policy", SECRET_HELPER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_remediation_reports_exist_and_parse() -> None:
    expected = [
        "l7_0r_remediation_plan.json",
        "p0_remediation_queue.json",
        "p1_remediation_queue.json",
        "patched_files_report.json",
        "preserved_hard_boundaries_report.json",
        "remaining_debt_report.json",
        "capability_unlocked_report.json",
        "owner_burden_reduction_report.json",
        "l7_0r_no_action_receipt.json",
        "l7_0r_summary.json",
    ]
    for name in expected:
        payload = json.loads((OUT / name).read_text(encoding="utf-8"))
        assert payload["schema_version"] == "v0"
    assert (OUT / "l7_0r_remediation_plan.md").exists()
    assert (OUT / "l7_0r_summary.md").exists()


def test_policy_decision_helper_allows_discovery_and_drafts() -> None:
    helper = load_policy_helper()
    discovery = helper.decide_action_capability(
        "controlled_search",
        "search",
        "not_required",
        budget_state={"remaining": 2},
    )
    assert discovery["decision"] == "allowed_with_budget"
    assert discovery["policy_ref"] == "policy/discovery_policy.json"

    draft = helper.decide_action_capability("outreach_email_draft", "draft", "not_required")
    assert draft["decision"] == "allowed_draft_only"
    assert draft["requires_human_approval"] is False


def test_policy_decision_helper_blocks_unapproved_execution() -> None:
    helper = load_policy_helper()
    blocked = helper.decide_action_capability(
        "customer_outreach_send",
        "execute_after_approval",
        "human_review_required",
    )
    assert blocked["decision"] == "blocked_pending_human_review"
    assert blocked["requires_human_approval"] is True

    approved = helper.decide_action_capability(
        "customer_outreach_send",
        "execute_after_approval",
        "approved_by_human",
    )
    assert approved["decision"] == "allowed_after_human_approval"


def test_policy_decision_helper_gates_writeback() -> None:
    helper = load_policy_helper()
    candidate = helper.decide_action_capability(
        "memory_writeback_candidate",
        "writeback_candidate",
        "not_required",
    )
    assert candidate["decision"] == "allowed_draft_only"

    blocked = helper.decide_action_capability(
        "actual_memory_writeback",
        "actual_writeback_after_approval",
        "human_review_required",
    )
    assert blocked["decision"] == "blocked_pending_human_review"


def test_p0_and_p1_queues_and_patched_reports() -> None:
    p0 = load_json("l7_conservatism_debt_remediation/p0_remediation_queue.json")
    p1 = load_json("l7_conservatism_debt_remediation/p1_remediation_queue.json")
    patched = load_json("l7_conservatism_debt_remediation/patched_files_report.json")
    assert p0["considered_items"]
    assert p0["patched_files"]
    assert p1["considered_items"]
    assert p1["patched_files"]
    assert patched["patched_findings"]
    for item in patched["patched_findings"]:
        assert item["policy_ref_added"] is True
        assert item["staged_decision_added"] is True
        assert item["safety_boundary_preserved"] is True


def test_capability_and_owner_burden_reports() -> None:
    capability = load_json("l7_conservatism_debt_remediation/capability_unlocked_report.json")
    owner = load_json("l7_conservatism_debt_remediation/owner_burden_reduction_report.json")
    assert any(item["capability"] == "policy_decision_helper" for item in capability["capabilities_unlocked"])
    assert owner["manual_url_request_occurred"] is False
    assert owner["manual_env_export_required"] is False


def test_selected_l7_0p_files_include_staged_policy_refs() -> None:
    revenue_summary = load_json("l7_revenue_opportunity_radar/l7b_revenue_opportunity_radar_summary.json")
    opportunity = load_json("l7_revenue_opportunity_radar/opportunity_packets/opportunity_packet_001.json")
    cockpit = load_json("l7_owner_runtime_cockpit/owner_cockpit.json")

    remediation = revenue_summary["l7_0r_staged_policy_remediation"]
    assert remediation["principle"] == "Do not block revenue work. Block unapproved revenue side effects."
    assert remediation["read_only_discovery_allowed"] is True
    assert remediation["draft_allowed"] is True
    assert remediation["actual_execution_blocked_until_approval"] is True

    assert opportunity["read_only_revenue_work_allowed"] is True
    assert opportunity["draft_and_planning_allowed"] is True
    assert opportunity["actual_execution_blocked_until_approval"] is True
    assert cockpit["l7_0r_staged_policy_remediation"]["policy_decision_helper"] == "policy/policy_decision.py"


def test_active_p0_files_reference_policy_semantics() -> None:
    files = [
        "scripts/aiden_dream.py",
        "scripts/hook_wrapper.py",
        "scripts/session_health_watchdog.py",
        "scripts/governance_boot.sh",
        "scripts/memory_consistency_check.py",
        "scripts/linkedin_auth.py",
    ]
    for rel in files:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "policy" in text.lower()
        assert "blocked_pending" in text or "policy_decision" in text


def test_preserved_hard_boundary_report_and_no_action_receipt() -> None:
    preserved = load_json("l7_conservatism_debt_remediation/preserved_hard_boundaries_report.json")
    receipt = load_json("l7_conservatism_debt_remediation/l7_0r_no_action_receipt.json")
    boundaries = " ".join(preserved["hard_boundaries_preserved"]).lower()
    for term in ["secret", "payment", "outreach", "db/wal/shm", "y-star-gov", "gov-mcp"]:
        assert term in boundaries
    for key, value in receipt.items():
        if key.endswith("_performed") or key in {
            "external_side_effects_occurred",
            "core_writeback_occurred",
            "secret_values_serialized",
            "db_log_wal_shm_active_agent_marker_content_read",
            "ask_user_for_url_occurred",
        }:
            assert value is False


def test_no_secret_values_or_external_repo_modification() -> None:
    scanned_text = ""
    for path in list(OUT.glob("*.json")) + list(OUT.glob("*.md")) + [POLICY_HELPER]:
        scanned_text += path.read_text(encoding="utf-8")
    secret_helper = load_secret_helper()
    decisions = secret_helper.scan_text_for_secret_policy(scanned_text, file_path="tests/l7_conservatism_debt_remediation/test_l7_conservatism_debt_remediation.py")
    assert all(decision["safe_for_commit"] for decision in decisions)
    placeholder = secret_helper.classify_secret_pattern(
        "TAVILY_API_KEY_PLACEHOLDER",
        file_path="tests/l7_conservatism_debt_remediation/test_l7_conservatism_debt_remediation.py",
    )
    assert placeholder["safe_for_commit"] is True
    summary = load_json("l7_conservatism_debt_remediation/l7_0r_summary.json")
    assert summary["y_star_gov_modified"] is False
    assert summary["gov_mcp_modified"] is False
