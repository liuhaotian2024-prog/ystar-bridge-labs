from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "l7_conservatism_debt_audit"
POLICY = ROOT / "policy"


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def action_map() -> dict[str, dict]:
    registry = load_json("policy/action_capability_registry.json")
    return {item["action_type"]: item for item in registry["actions"]}


def all_scoped_text() -> str:
    paths = [
        *AUDIT.glob("*.json"),
        *AUDIT.glob("*.md"),
        *POLICY.glob("*.json"),
        *POLICY.glob("*.md"),
        *ROOT.glob("l7_agent_team_runtime/**/*.json"),
        *ROOT.glob("l7_revenue_opportunity_radar/**/*.json"),
        *ROOT.glob("l7_human_approved_external_action_gate/**/*.json"),
        *ROOT.glob("l7_review_gated_memory_writeback/**/*.json"),
        *ROOT.glob("l7_owner_runtime_cockpit/**/*.json"),
        *ROOT.glob("l7_parallel_commercial_agent_team_orchestrator/**/*.json"),
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_audit_reports_and_inventories_exist() -> None:
    required = [
        "conservatism_debt_report.json",
        "conservatism_debt_report.md",
        "hardcoded_blacklist_inventory.json",
        "capability_bottleneck_inventory.json",
        "manual_owner_burden_inventory.json",
        "no_action_overuse_inventory.json",
        "disabled_as_final_state_inventory.json",
        "legitimate_hard_boundary_inventory.json",
        "policy_refactor_recommendations.json",
        "migration_queue.json",
        "l7_0q_summary.json",
        "l7_0q_summary.md",
        "l7_0q_no_action_receipt.json",
    ]
    for name in required:
        assert (AUDIT / name).is_file()

    report = load_json("l7_conservatism_debt_audit/conservatism_debt_report.json")
    assert report["total_findings"] > 0
    assert report["classification_counts"]["legitimate_hard_boundary"] > 0


def test_policy_registries_exist_and_manifest_lists_them() -> None:
    required = [
        "README.md",
        "action_capability_registry.json",
        "action_risk_tiers.json",
        "approval_state_machine.json",
        "discovery_policy.json",
        "runtime_access_policy.json",
        "writeback_policy.json",
        "revenue_action_policy.json",
        "owner_burden_reduction_policy.json",
        "policy_registry_manifest.json",
    ]
    for name in required:
        assert (POLICY / name).is_file()

    manifest = load_json("policy/policy_registry_manifest.json")
    assert "policy/action_capability_registry.json" in manifest["registry_files"]


def test_action_capability_registry_includes_staged_actions() -> None:
    actions = action_map()
    expected = {
        "query_planning",
        "controlled_search",
        "public_page_read",
        "bounded_crawl",
        "opportunity_discovery",
        "outreach_email_draft",
        "grant_application_draft",
        "customer_outreach_send",
        "grant_application_submit",
        "payment_or_purchase",
        "memory_writeback_candidate",
        "actual_memory_writeback",
    }
    assert expected.issubset(actions)
    assert actions["controlled_search"]["default_decision"] == "allowed_with_budget"
    assert actions["outreach_email_draft"]["default_decision"] == "allowed_draft_only"
    assert actions["customer_outreach_send"]["requires_human_approval"] is True
    assert actions["actual_memory_writeback"]["requires_human_approval"] is True


def test_revenue_policy_allows_work_but_gates_execution() -> None:
    policy = load_json("policy/revenue_action_policy.json")
    allowed = set(policy["explicitly_allowed"])
    gated = set(policy["requires_human_approval"])

    assert "opportunity_discovery" in allowed
    assert "market_research" in allowed
    assert "outreach_draft" in allowed
    assert "revenue_opportunity_packet_generation" in allowed
    assert "sending_outreach" in gated
    assert "submitting_grant_RFP" in gated
    assert "payment_purchase" in gated
    assert policy["principle"] == "Do not block revenue work. Block unapproved revenue side effects."


def test_discovery_runtime_and_writeback_policies_are_staged() -> None:
    discovery = load_json("policy/discovery_policy.json")
    runtime = load_json("policy/runtime_access_policy.json")
    writeback = load_json("policy/writeback_policy.json")

    assert "controlled_search" in discovery["allowed_with_budget"]
    assert "public_page_read" in discovery["allowed_with_budget"]
    assert "evidence_extraction" in discovery["allowed_with_budget"]
    assert "payment" in discovery["requires_approval_or_blocked"]
    assert "safe_runtime_metadata" in runtime["allowed"]
    assert "raw_DB_content" in runtime["restricted_review_required"]
    assert "raw_DB_WAL_SHM_ingestion" in runtime["hard_forbidden_by_default"]
    assert "memory_writeback_candidate_generation" in writeback["explicitly_allowed"]
    assert "writeback_dry_run_receipts" in writeback["explicitly_allowed"]
    assert "actual_memory_writeback" in writeback["blocked_by_default_until_future_approval_gate"]


def test_owner_burden_policy_replaces_manual_work() -> None:
    policy = load_json("policy/owner_burden_reduction_policy.json")
    anti = set(policy["owner_burden_anti_patterns"])
    replacements = set(policy["preferred_replacements"])

    assert "asking_user_to_provide_URL" in anti
    assert "asking_user_to_manually_export_many_env_vars" in anti
    assert "asking_user_to_open_multiple_Codex_windows" in anti
    assert "asking_user_to_manually_create_worktrees" in anti
    assert "asking_user_to_manually_merge_branches" in anti
    assert "one_command_launcher" in replacements
    assert "worktree_orchestration_script" in replacements
    assert "owner_cockpit" in replacements


def test_legitimate_hard_boundaries_are_preserved() -> None:
    inventory = load_json("l7_conservatism_debt_audit/legitimate_hard_boundary_inventory.json")
    receipt = load_json("l7_conservatism_debt_audit/l7_0q_no_action_receipt.json")

    assert inventory["count"] > 0
    assert receipt["secret_values_serialized"] is False
    assert receipt["db_files_read"] is False
    assert receipt["wal_files_read"] is False
    assert receipt["shm_files_read"] is False
    assert receipt["logs_read"] is False
    assert receipt["active_agent_marker_content_read"] is False


def test_l7_0p_artifacts_include_policy_references_after_migration() -> None:
    sample_paths = [
        "l7_agent_team_runtime/agent_role_profiles/ceo.json",
        "l7_revenue_opportunity_radar/opportunity_packets/opportunity_packet_001.json",
        "l7_human_approved_external_action_gate/external_action_types/customer_outreach_email.json",
        "l7_review_gated_memory_writeback/memory_writeback_candidates/l7d_candidate_004.json",
        "l7_owner_runtime_cockpit/owner_cockpit.json",
        "l7_parallel_commercial_agent_team_orchestrator/l7_0p_summary.json",
    ]
    for path in sample_paths:
        migration = load_json(path)["l7_0q_policy_migration"]
        assert migration["policy_ref"] == "policy/action_capability_registry.json"
        assert migration["approval_state_machine_ref"] == "policy/approval_state_machine.json"
        assert "allowed_capability_stage" in migration


def test_no_secret_values_are_serialized() -> None:
    text = all_scoped_text()
    assert "tvly" + "-" not in text
    assert "TAVILY" + "_API_KEY=" not in text
    assert "BRAVE_SEARCH" + "_API_KEY=" not in text
    assert "SERP" + "API_API_KEY=" not in text


def test_audit_script_excludes_runtime_and_secret_surfaces() -> None:
    spec = importlib.util.spec_from_file_location("audit_conservatism_debt", ROOT / "scripts/audit_conservatism_debt.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert ".db" in module.EXCLUDED_SUFFIXES
    assert ".db-wal" in module.EXCLUDED_SUFFIXES
    assert ".db-shm" in module.EXCLUDED_SUFFIXES
    assert ".log" in module.EXCLUDED_SUFFIXES
    assert "scripts/.logs" in module.EXCLUDED_PATH_FRAGMENTS
    assert "active_agent" in module.EXCLUDED_PATH_FRAGMENTS
    assert "controlled_observation" + ".env" in module.EXCLUDED_PATH_FRAGMENTS


def test_no_external_repo_modification_or_side_effects() -> None:
    summary = load_json("l7_conservatism_debt_audit/l7_0q_summary.json")
    receipt = load_json("l7_conservatism_debt_audit/l7_0q_no_action_receipt.json")

    assert summary["y_star_gov_modified"] is False
    assert summary["gov_mcp_modified"] is False
    assert summary["ask_user_for_url_occurred"] is False
    assert summary["external_side_effects_occurred"] is False
    assert summary["core_writeback_occurred"] is False
    assert receipt["y_star_gov_modified"] is False
    assert receipt["gov_mcp_modified"] is False
