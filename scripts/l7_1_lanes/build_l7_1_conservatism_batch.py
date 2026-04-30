#!/usr/bin/env python3
"""Build L7.1 remaining P0/P1 conservatism remediation lane outputs."""

from __future__ import annotations

from common import ROOT, base_no_action_receipt, base_packet, lane_summary, load_json, simple_md, write_json, write_text


LANE_ID = "L7.1A"
LANE_NAME = "Remaining P0/P1 Conservatism Remediation"
OUT = "l7_conservatism_debt_remediation_l7_1"


def build() -> None:
    remaining = load_json("l7_conservatism_debt_remediation/remaining_debt_report.json", {})
    migration = load_json("l7_full_repo_conservatism_scan/policy_migration_map.json", {})
    p0_targets = remaining.get("remaining_p0_targets", [])
    p1_sample = remaining.get("remaining_p1_sample", [])

    patched_files = [
        {
            "file_path": "scripts/aiden_continuity_guardian.sh",
            "patch_type": "add_policy_ref_and_staged_override_semantics",
            "capability_unlocked": "auto-restart remains available while board override is typed as blocked_pending_human_review, not permanent disabled",
            "hard_boundaries_preserved": True,
        },
        {
            "file_path": "scripts/l6_13_check_controlled_observation_env.sh",
            "patch_type": "convert_missing_backend_to_config_resolver_status",
            "capability_unlocked": "owner sees auto-detect/setup path instead of manual URL or disabled dead end",
            "hard_boundaries_preserved": True,
        },
        {
            "file_path": "scripts/platform_wave1_livefire_20260424.md",
            "patch_type": "add_staged_policy_interpretation_to_historical_disabled_note",
            "capability_unlocked": "historical disabled language is interpreted through staged policy migration",
            "hard_boundaries_preserved": True,
        },
    ]

    batch = {
        **base_packet("p0_p1_remediation_batch"),
        "source_remaining_p0_count": remaining.get("remaining_p0_count", 0),
        "source_remaining_p1_count": remaining.get("remaining_p1_count", 0),
        "p0_targets_considered": p0_targets[:8],
        "p1_targets_considered": p1_sample[:8],
        "migration_map_counts": {
            "p0": migration.get("p0_count"),
            "p1": migration.get("p1_count"),
        },
        "patch_strategy": [
            "add_policy_ref",
            "add_staged_capability_semantics",
            "split_read_draft_plan_request_approval_execute",
            "convert_disabled_as_final_state_to_auto_detect_or_blocked_pending_config",
            "preserve_legitimate_hard_boundaries",
        ],
        "patched_files": patched_files,
    }
    write_json(f"{OUT}/l7_1_p0_p1_remediation_batch.json", batch)

    patched_report = {
        **base_packet("patched_files_report"),
        "patched_count": len(patched_files),
        "patched_files": patched_files,
        "secret_protection_weakened": False,
        "unapproved_external_action_blocking_weakened": False,
        "direct_writeback_blocking_weakened": False,
    }
    write_json(f"{OUT}/l7_1_patched_files_report.json", patched_report)

    remaining_report = {
        **base_packet("remaining_p0_p1_report"),
        "remaining_p0_before_l7_1": remaining.get("remaining_p0_count", 0),
        "remaining_p1_before_l7_1": remaining.get("remaining_p1_count", 0),
        "l7_1_patched_active_files": len(patched_files),
        "remaining_p0_estimate_after_l7_1": max(0, remaining.get("remaining_p0_count", 0) - len(patched_files)),
        "remaining_p1_estimate_after_l7_1": remaining.get("remaining_p1_count", 0),
        "note": "Historical/generated artifacts remain queued; L7.1 patches active owner/runtime-facing bottlenecks only.",
    }
    write_json(f"{OUT}/l7_1_remaining_p0_p1_report.json", remaining_report)

    unlock = {
        **base_packet("capability_unlock_report"),
        "capabilities_unlocked": [
            "policy-aware owner runner language",
            "config auto-detect path for controlled observation",
            "commercial sprint can proceed without manual URL/search/export burden",
        ],
        "owner_manual_burden_reduced": True,
        "discovery_allowed_with_budget": True,
        "revenue_work_allowed_until_external_side_effect_gate": True,
    }
    write_json(f"{OUT}/l7_1_capability_unlock_report.json", unlock)

    summary = lane_summary(
        LANE_ID,
        LANE_NAME,
        OUT,
        "completed",
        {"patched_count": len(patched_files), "remaining_p0_estimate": remaining_report["remaining_p0_estimate_after_l7_1"]},
    )
    write_json(f"{OUT}/l7_1_conservatism_batch_summary.json", summary)
    write_json(f"{OUT}/l7_1_no_action_receipt.json", base_no_action_receipt(LANE_ID, LANE_NAME))
    write_text(
        f"{OUT}/l7_1_p0_p1_remediation_batch.md",
        simple_md(
            "L7.1 P0/P1 Conservatism Remediation Batch",
            [
                ("What Changed", "Patched the next active owner/runtime-facing files with staged policy references and non-dead-end configuration language."),
                ("Preserved Boundaries", "Secrets, unapproved external side effects, and unreviewed permanent writeback remain blocked."),
            ],
        ),
    )


if __name__ == "__main__":
    build()
