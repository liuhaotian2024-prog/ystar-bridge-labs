from __future__ import annotations

import importlib.util
from functools import lru_cache
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "l7_full_repo_conservatism_scan"
POLICY = ROOT / "policy"
SECRET_HELPER = ROOT / "policy" / "secret_scanner_policy.py"


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_secret_helper():
    spec = importlib.util.spec_from_file_location("secret_scanner_policy", SECRET_HELPER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def line_findings() -> list[dict]:
    payload = load_json("l7_full_repo_conservatism_scan/line_level_findings.json")
    return payload["findings"]


def test_scanner_script_exists_and_uses_git_ls_files() -> None:
    script = ROOT / "scripts/full_repo_conservatism_scan.py"
    text = script.read_text(encoding="utf-8")

    assert script.is_file()
    assert "git" in text
    assert "ls-files" in text
    assert "git_ls_files" in text
    assert "ROOT.rglob" not in text


def test_scanner_excludes_runtime_binary_secret_patterns() -> None:
    script = (ROOT / "scripts/full_repo_conservatism_scan.py").read_text(encoding="utf-8")
    assert '".db"' in script
    assert '".db-wal"' in script
    assert '".db-shm"' in script
    assert '".log"' in script
    assert "__pycache__" in script
    assert "active_agent" in script
    assert "controlled_observation" + ".env" in script

    bad_suffixes = (".db", ".db-wal", ".db-shm", ".sqlite", ".sqlite3", ".log", ".pyc")
    for finding in line_findings()[:]:
        assert not finding["file_path"].endswith(bad_suffixes)
        assert "active_agent" not in finding["file_path"]
        assert "controlled_observation" + ".env" not in finding["file_path"]


def test_required_scan_outputs_exist() -> None:
    required = [
        "full_repo_conservatism_scan_report.json",
        "full_repo_conservatism_scan_report.md",
        "line_level_findings.json",
        "file_level_summary.json",
        "directory_level_summary.json",
        "hardcoded_forbidden_action_inventory.json",
        "blocked_state_inventory.json",
        "no_action_readiness_inventory.json",
        "owner_manual_burden_inventory.json",
        "discovery_suppression_inventory.json",
        "external_action_policy_inventory.json",
        "core_writeback_policy_inventory.json",
        "runtime_visibility_policy_inventory.json",
        "legitimate_hard_boundary_inventory.json",
        "harmful_overconservatism_inventory.json",
        "policy_registry_coverage_report.json",
        "policy_migration_map.json",
        "p0_p1_remediation_plan.md",
        "l7_0q2_summary.json",
        "l7_0q2_summary.md",
        "l7_0q2_no_action_receipt.json",
        "scorecard.json",
        "scorecard.md",
    ]
    for name in required:
        assert (OUT / name).is_file()


def test_line_level_findings_have_required_schema() -> None:
    findings = line_findings()
    assert findings
    required_keys = {
        "finding_id",
        "file_path",
        "line_number",
        "matched_pattern",
        "matched_excerpt_short",
        "directory_group",
        "artifact_epoch",
        "current_behavior",
        "classification",
        "severity",
        "legitimate_hard_boundary",
        "harmful_overconservatism",
        "capability_harmed",
        "commercial_impact",
        "recommended_fix",
        "migration_target_policy",
        "safe_to_patch_now",
        "patch_strategy",
    }
    assert required_keys.issubset(findings[0])
    assert {finding["severity"] for finding in findings}.issubset({"P0", "P1", "P2", "P3"})


def test_scorecard_covers_full_tracked_repo() -> None:
    scorecard = load_json("l7_full_repo_conservatism_scan/scorecard.json")
    summary = load_json("l7_full_repo_conservatism_scan/l7_0q2_summary.json")

    assert scorecard["total_tracked_files"] > 1000
    assert scorecard["total_text_files_scanned"] > 1000
    assert scorecard["total_findings"] > 0
    assert "top_20_files_by_conservatism_density" in scorecard
    assert "top_20_directories_by_conservatism_density" in scorecard
    assert scorecard["total_tracked_files"] == summary["total_tracked_files_scanned"]
    assert scorecard["total_text_files_scanned"] == summary["total_text_files_scanned"]


def test_inventories_and_migration_map_exist_and_are_nonempty() -> None:
    inventories = [
        "hardcoded_forbidden_action_inventory.json",
        "owner_manual_burden_inventory.json",
        "disabled_as_final_state_inventory.json",
        "no_action_readiness_inventory.json",
        "legitimate_hard_boundary_inventory.json",
        "harmful_overconservatism_inventory.json",
    ]
    for inventory in inventories:
        payload = load_json(f"l7_full_repo_conservatism_scan/{inventory}")
        assert payload["count"] > 0

    migration = load_json("l7_full_repo_conservatism_scan/policy_migration_map.json")
    assert migration["total_files_needing_policy_ref_migration"] > 0
    assert set(migration["migration_groups"]) == {"P0", "P1", "P2", "P3"}


def test_policy_registry_files_exist_and_meet_requirements() -> None:
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

    coverage = load_json("l7_full_repo_conservatism_scan/policy_registry_coverage_report.json")
    assert coverage["required_policy_files_present"] is True


def test_discovery_revenue_writeback_runtime_owner_policies_are_staged() -> None:
    discovery = load_json("policy/discovery_policy.json")
    revenue = load_json("policy/revenue_action_policy.json")
    writeback = load_json("policy/writeback_policy.json")
    runtime = load_json("policy/runtime_access_policy.json")
    owner = load_json("policy/owner_burden_reduction_policy.json")

    assert "controlled_search" in discovery["allowed_with_budget"]
    assert "public_page_read" in discovery["allowed_with_budget"]
    assert "evidence_extraction" in discovery["allowed_with_budget"]
    assert "market_research" in revenue["explicitly_allowed"]
    assert "outreach_draft" in revenue["explicitly_allowed"]
    assert "sending_outreach" in revenue["requires_human_approval"]
    assert "payment_purchase" in revenue["requires_human_approval"]
    assert "memory_writeback_candidate_generation" in writeback["explicitly_allowed"]
    assert "writeback_dry_run_receipts" in writeback["explicitly_allowed"]
    assert "actual_memory_writeback" in writeback["blocked_by_default_until_future_approval_gate"]
    assert "safe_runtime_metadata" in runtime["allowed"]
    assert "raw_DB_content" in runtime["restricted_review_required"]
    assert "secret_files" in runtime["hard_forbidden_by_default"]
    assert "asking_user_to_provide_URL" in owner["owner_burden_anti_patterns"]
    assert "asking_user_to_manually_export_many_env_vars" in owner["owner_burden_anti_patterns"]
    assert "asking_user_to_open_multiple_Codex_windows" in owner["owner_burden_anti_patterns"]
    assert "asking_user_to_manually_create_worktrees" in owner["owner_burden_anti_patterns"]
    assert "asking_user_to_manually_merge_branches" in owner["owner_burden_anti_patterns"]


def test_no_secret_values_or_external_repo_modification() -> None:
    scoped_text = "\n".join(
        path.read_text(encoding="utf-8")
        for root in [OUT, POLICY]
        for path in root.glob("*")
        if path.is_file() and path.suffix in {".json", ".md"}
    )
    secret_helper = load_secret_helper()
    decisions = secret_helper.scan_text_for_secret_policy(
        scoped_text,
        file_path="tests/l7_full_repo_conservatism_scan/test_l7_full_repo_conservatism_scan.py",
    )
    assert all(decision["safe_for_commit"] for decision in decisions)
    placeholder = secret_helper.classify_secret_pattern(
        "TAVILY_API_KEY_PLACEHOLDER",
        file_path="tests/l7_full_repo_conservatism_scan/test_l7_full_repo_conservatism_scan.py",
    )
    assert placeholder["safe_for_commit"] is True

    receipt = load_json("l7_full_repo_conservatism_scan/l7_0q2_no_action_receipt.json")
    assert receipt["y_star_gov_modified"] is False
    assert receipt["gov_mcp_modified"] is False
    assert receipt["external_side_effects_occurred"] is False
    assert receipt["core_writeback_occurred"] is False
    assert receipt["ask_user_for_url_occurred"] is False
    assert receipt["db_files_read"] is False
    assert receipt["wal_files_read"] is False
    assert receipt["shm_files_read"] is False
    assert receipt["log_files_read"] is False
    assert receipt["active_agent_marker_content_read"] is False
