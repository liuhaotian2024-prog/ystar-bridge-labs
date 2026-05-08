from __future__ import annotations

import json

from office.mission_command.e96_ceo_controlled_capability_control_plane import (
    build_controlled_capability_catalog,
    decide_autonomy_for_action,
    l5_truth_table_after_e96,
    run_e96_controlled_capability_strategy_session,
    write_e96_reports,
)


def test_controlled_capability_catalog_names_active_runtime_and_truth_boundaries():
    catalog = build_controlled_capability_catalog()

    capability_ids = {item["capability_id"] for item in catalog["controlled_capabilities"]}
    assert "owner_facing_aiden_governed_gateway" in capability_ids
    assert "brain_grounding_and_provenance" in capability_ids
    assert "ceo_market_strategy_benchmark" in capability_ids
    assert "gov_mcp_dry_run_boundary" in capability_ids
    assert catalog["truth_boundaries"]["L5-D"] == "absent_or_not_executed"
    assert catalog["truth_boundaries"]["no_live_external_execution"] is True


def test_quarantine_catalog_finds_legacy_external_bypass_surfaces():
    catalog = build_controlled_capability_catalog()
    quarantined_paths = {item["path"] for item in catalog["quarantined_entrypoints"]}

    assert "worker.js" in quarantined_paths
    assert "scripts/meeting_room/server.py" in quarantined_paths
    assert "scripts/linkedin_auth.py" in quarantined_paths
    assert "scripts/publish_x.py" in quarantined_paths
    assert "scripts/publish_telegram.py" in quarantined_paths
    assert all(item["external_action_allowed"] is False for item in catalog["quarantined_entrypoints"])


def test_doctrine_registry_integrity_audit_does_not_overclaim_registry_cleanliness():
    catalog = build_controlled_capability_catalog()
    integrity = catalog["doctrine_registry_integrity"]

    assert integrity["status"] in {
        "clean",
        "needs_registry_hygiene",
        "registry_missing_or_unreadable",
    }
    assert "issue_count" in integrity
    if integrity["issues"]:
        assert any(
            issue["issue"]
            in {
                "callable_path_missing",
                "callable_path_not_found_in_bridge_labs_tree",
                "test_file_cannot_be_canonical_runtime_callable",
            }
            for issue in integrity["issues"]
        )


def test_autonomy_policy_reduces_human_work_but_blocks_hard_risk():
    internal = decide_autonomy_for_action(
        {
            "action_id": "internal_report",
            "action_title": "Build internal governed strategy report and tests",
            "source": "internal_runtime",
        }
    )
    public_read = decide_autonomy_for_action(
        {
            "action_id": "public_read_refresh",
            "action_title": "Run read-only public evidence research without login or outreach",
            "source": "experiment_tier1_research",
        }
    )
    dry_run = decide_autonomy_for_action(
        {
            "action_id": "provider_preflight",
            "action_title": "Run gov-mcp dry-run preflight receipt with no send",
            "source": "obligation_dry_run",
        }
    )
    social_publish = decide_autonomy_for_action(
        {
            "action_id": "social_publish",
            "action_title": "Publish public post on LinkedIn",
            "source": "live_external_action",
        }
    )
    payment = decide_autonomy_for_action(
        {
            "action_id": "payment_link",
            "action_title": "Create payment link and charge customer",
            "source": "revenue_payment_action",
        }
    )

    assert internal["may_execute_without_owner"] is True
    assert public_read["may_execute_without_owner"] is True
    assert dry_run["may_execute_without_owner"] is True
    assert social_publish["autonomy_decision"] == "GOVERNED_PREFLIGHT_ONLY_UNTIL_LIVE_ADAPTER"
    assert social_publish["may_execute_without_owner"] is False
    assert payment["autonomy_decision"] == "DENY_OR_OWNER_DECISION_HARD_RISK"
    assert payment["may_execute_without_owner"] is False


def test_e96_full_session_runs_behavior_center_strategy_cieustore_and_no_external_action(tmp_path):
    result = run_e96_controlled_capability_strategy_session(cieu_db=tmp_path / "e96.db")
    queue = result["autonomous_work_queue"]

    assert result["behavior_center_decision"] == "ALLOW"
    assert result["end_to_end_chain_proven"] is True
    assert result["CIEUStore_summary"]["event_count"] >= 6
    assert result["market_strategy_intelligence_leap"]["selected_first_cash_path"]["route_id"]
    assert queue["human_approval_minimized"] is True
    assert queue["allowed_without_owner_count"] >= 3
    assert queue["hard_risk_owner_or_deny_count"] >= 1
    assert result["L5_truth_table_after_E96"]["L5-D Revenue/Customer/Payment Loop"] == "absent_or_not_executed"
    assert "No L4 feedback was executed." in result["what_was_not_claimed"]


def test_e96_reports_are_written_with_capability_catalog_and_honest_l5_status(tmp_path):
    result = run_e96_controlled_capability_strategy_session(cieu_db=tmp_path / "e96_report.db")
    paths = write_e96_reports(result, repo_root=tmp_path)

    for path in paths.values():
        assert path
    report = json.loads((tmp_path / "office/mission_command/e96_ceo_controlled_capability_control_plane_report.json").read_text())
    status = json.loads(
        (
            tmp_path
            / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e96_ceo_controlled_capability_control_plane.json"
        ).read_text()
    )
    catalog = json.loads(
        (tmp_path / "operations/controlled_capability_catalog/e96_controlled_capability_catalog.json").read_text()
    )

    assert report["end_to_end_chain_proven"] is True
    assert report["quarantined_entrypoint_count"] >= 5
    assert catalog["controlled_capability_count"] >= 8
    assert status["L5_truth_table_after_E96"] == l5_truth_table_after_e96()
    assert status["L5_truth_table_after_E96"]["L5-D Revenue/Customer/Payment Loop"] == "absent_or_not_executed"
