#!/usr/bin/env python3
"""Build L6.7 integrated approval record and pilot readiness sandbox artifacts.

This builder is static and local. It creates sandbox approval records and pilot
run readiness artifacts only. It does not grant real approval, create durable
real approval records, observe the external world, or execute network, browser,
search, scraping, API, MCP, live, publication, outreach, payment, revenue,
writeback, canonical update, or direct Y-star work.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "v0"
MILESTONE_ID = "L6.7"
MILESTONE_NAME = "Integrated Approval Record & Pilot Run Readiness Sandbox v0"
NEXT_MILESTONE = "L6.8 User-Mediated Manual Evidence Import Pilot v0"
PLACEHOLDER_LOCATOR_MARKER = (
    "PLACEHOLDER LOCATOR ONLY - NOT FETCHED - NOT OPENED - NOT VERIFIED CURRENT FACT "
    "- NOT AUTHORIZED FOR REAL OBSERVATION - NOT AUTHORIZED FOR PUBLICATION "
    "- NOT AUTHORIZED FOR OUTREACH - NOT AUTHORIZED FOR PAYMENT "
    "- NOT AUTHORIZED FOR REVENUE EXECUTION - NOT AUTHORIZED FOR CANONICAL UPDATE"
)

INPUT_REFS = {
    "l6_0_hypotheses": "open_value_hypothesis_generator/generated_value_hypotheses.json",
    "l6_1_artifact_cases": "selected_mvp_artifact_cases/selected_case_index.json",
    "l6_2_boundary": "l6_governed_external_observation_boundary/l6_2_summary.json",
    "l6_3_sandbox": "l6_controlled_external_observation_sandbox/l6_3_summary.json",
    "l6_4_preflight": "l6_real_read_only_external_observation_preflight/l6_4_summary.json",
    "l6_5_pilot_design": "l6_controlled_real_read_only_observation_pilot_design/l6_5_summary.json",
    "l6_6_approval_packet": "l6_controlled_observation_pilot_approval_packet/l6_6_summary.json",
    "l6_6_selected_candidates": "pilot_approval_candidate_selector/selected_approval_candidates.json",
    "l6_6_approval_packet_index": "pilot_approval_packet_assembler/approval_packet_index.json",
    "l6_6_authority_model": "pilot_approval_authority_model/approval_authority_model.json",
    "l6_6_operator_authorization": "pilot_operator_authorization_prerequisites/operator_authorization_contract.json",
    "l6_6_runtime_attestation": "pilot_runtime_isolation_attestation/runtime_isolation_attestation_template.json",
    "l6_6_evidence_capture_authorization": "pilot_evidence_capture_authorization/evidence_capture_authorization_template.json",
    "l6_6_decision_sandbox": "pilot_approval_decision_sandbox/approval_packet_decision_matrix.json",
    "l6_6_readiness": "l6_pilot_approval_readiness/l6_6_readiness_assessment.json",
    "l6_5_operator_runbook": "pilot_operator_runbook/operator_step_sequence.json",
    "l6_5_evidence_template": "pilot_evidence_packet_templates/pilot_evidence_packet_template.json",
    "l6_5_abort_policy": "pilot_abort_quarantine_decision_policy/pilot_abort_condition_registry.json",
    "l6_5_post_review": "pilot_post_observation_review_workflow/post_observation_review_contract.json",
}

SAFETY_FLAGS = {
    "live_execution_enabled": False,
    "behavior_execution_enabled": False,
    "external_action_enabled": False,
    "external_observation_execution_enabled": False,
    "network_enabled": False,
    "api_enabled": False,
    "scraping_enabled": False,
    "browser_fetch_enabled": False,
    "search_enabled": False,
    "scheduler_enabled": False,
    "daemon_enabled": False,
    "mcp_server_execution_enabled": False,
    "mcp_tool_execution_enabled": False,
    "cieu_persistence_enabled": False,
    "cieu_db_write_enabled": False,
    "durable_approval_persistence_enabled": False,
    "real_approval_record_write_enabled": False,
    "durable_real_approval_record_creation_enabled": False,
    "real_approval_grant_enabled": False,
    "brain_writeback_enabled": False,
    "memory_ingestion_enabled": False,
    "strategy_mutation_enabled": False,
    "candidate_auto_approval_enabled": False,
    "real_candidate_approval_enabled": False,
    "real_canonical_policy_mutation_enabled": False,
    "real_canonical_update_application_enabled": False,
    "real_release_execution_enabled": False,
    "real_y_star_direct_mutation_enabled": False,
    "y_star_gov_modification_enabled": False,
    "gov_mcp_modification_enabled": False,
    "semantic_truth_scoring_enabled": False,
    "raw_runtime_artifact_reading_enabled": False,
    "revenue_opportunity_discovery_enabled": False,
    "revenue_execution_enabled": False,
    "external_market_scan_enabled": False,
    "public_content_publication_enabled": False,
    "publication_enabled": False,
    "outreach_enabled": False,
    "payment_enabled": False,
}

L6_7_FLAGS = {
    "l6_7_integrated_sandbox_only": True,
    "l6_7_approval_record_sandbox_only": True,
    "l6_7_pilot_run_readiness_only": True,
    "l6_7_sandbox_approval_record_created": True,
    "l6_7_manual_evidence_import_future_candidate_allowed": True,
    "l6_7_real_approval_granted": False,
    "l6_7_durable_real_approval_record_created": False,
    "l6_7_real_observation_execution_enabled": False,
    "l6_7_network_enabled": False,
    "l6_7_search_enabled": False,
    "l6_7_publication_enabled": False,
    "l6_7_outreach_enabled": False,
    "l6_7_payment_enabled": False,
    "l6_7_revenue_execution_enabled": False,
    "l6_7_mcp_execution_enabled": False,
    "l6_7_cieu_db_write_enabled": False,
    "l6_7_canonical_update_enabled": False,
    "l6_7_brain_writeback_enabled": False,
    "l6_7_memory_ingestion_enabled": False,
    "l6_7_direct_y_star_mutation_enabled": False,
}

BLOCKED_AUTHORIZATIONS = {
    "durable_real_approval_record_created": False,
    "real_approval_granted": False,
    "real_external_observation_authorized": False,
    "real_pilot_execution_authorized": False,
    "network_authorized": False,
    "api_authorized": False,
    "scraping_authorized": False,
    "browser_fetch_authorized": False,
    "search_authorized": False,
    "publication_authorized": False,
    "outreach_authorized": False,
    "payment_authorized": False,
    "revenue_execution_authorized": False,
    "mcp_execution_authorized": False,
    "live_behavior_authorized": False,
    "cieu_db_write_authorized": False,
    "canonical_update_authorized": False,
    "direct_y_star_mutation_authorized": False,
    "brain_writeback_authorized": False,
    "memory_ingestion_authorized": False,
}

NO_ACTION_CONSTRAINTS = [
    "real approval",
    "durable real approval persistence",
    "real observation execution",
    "network access",
    "API calls",
    "scraping",
    "browser fetch",
    "search",
    "publication",
    "outreach",
    "payment",
    "revenue execution",
    "customer contact",
    "form submission",
    "posting/commenting/messaging",
    "MCP execution",
    "live behavior",
    "CIEU DB write",
    "canonical strategy mutation",
    "canonical update",
    "brain/memory writeback",
    "direct Y-star mutation",
]

LIFECYCLE_STATES = [
    "draft_packet",
    "ready_for_review",
    "blocked_pending_human_approval",
    "sandbox_approved_for_readiness_only",
    "expired",
    "revoked",
    "invalid",
]

NO_ACTION_RECEIPTS = {
    "no_real_approval_granted_receipt.json": "real_approval_granted",
    "no_durable_real_approval_record_receipt.json": "durable_real_approval_record",
    "no_real_observation_execution_receipt.json": "real_observation_execution",
    "no_network_execution_receipt.json": "network_execution",
    "no_api_receipt.json": "api",
    "no_scraping_receipt.json": "scraping",
    "no_browser_fetch_receipt.json": "browser_fetch",
    "no_search_receipt.json": "search",
    "no_publication_receipt.json": "publication",
    "no_outreach_receipt.json": "outreach",
    "no_payment_receipt.json": "payment",
    "no_revenue_execution_receipt.json": "revenue_execution",
    "no_mcp_execution_receipt.json": "mcp_execution",
    "no_live_behavior_receipt.json": "live_behavior",
    "no_cieu_db_write_receipt.json": "cieu_db_write",
    "no_canonical_mutation_receipt.json": "canonical_mutation",
    "no_brain_memory_writeback_receipt.json": "brain_memory_writeback",
    "no_direct_y_star_mutation_receipt.json": "direct_y_star_mutation",
}


class BuildError(Exception):
    """Raised when generated artifacts cannot be built safely."""


def read_json(relative_path: str) -> Any:
    path = ROOT / relative_path
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise BuildError(f"Refusing to read outside repo: {relative_path}") from exc
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(relative_path: str, payload: Any, generated: list[str]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)
        f.write("\n")
    generated.append(relative_path)


def write_text(relative_path: str, text: str, generated: list[str]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)
    generated.append(relative_path)


def with_common(payload: dict[str, Any]) -> dict[str, Any]:
    return {**payload, "safety_flags": SAFETY_FLAGS, "l6_7_flags": L6_7_FLAGS}


def existing_input_map() -> tuple[dict[str, str], list[str]]:
    refs: dict[str, str] = {}
    gaps: list[str] = []
    for key, rel in INPUT_REFS.items():
        if (ROOT / rel).exists():
            refs[key] = rel
        else:
            gaps.append(rel)
    return refs, gaps


def approval_packets() -> list[dict[str, Any]]:
    index = read_json(INPUT_REFS["l6_6_approval_packet_index"]) or {}
    packets: list[dict[str, Any]] = []
    for entry in index.get("packets", [])[:3]:
        packet = read_json(entry.get("path", "")) or {}
        if packet:
            packets.append(packet)
    if packets:
        return packets
    return [
        {
            "approval_packet_id": "l6_6_approval_packet_placeholder",
            "linked_l6_5_pilot_candidate_id": "l6_5_pilot_candidate_placeholder",
            "linked_l6_4_candidate_id": "l6_4_candidate_placeholder",
            "linked_l6_3_packet_id": "l6_3_packet_placeholder",
            "linked_l6_1_artifact_case_id": "case_placeholder",
            "linked_l6_0_hypothesis_id": "hypothesis_placeholder",
            "source_locator_placeholder": f"{PLACEHOLDER_LOCATOR_MARKER} :: l6-7-placeholder",
            "observation_question": "Which user-mediated evidence would clarify this pilot case?",
            "source_type": "user_supplied_public_locator",
            "expected_evidence_type": "manual_evidence_import_packet",
        }
    ]


def build_sandbox_record(index: int, packet: dict[str, Any]) -> dict[str, Any]:
    return with_common(
        {
            "sandbox_record_id": f"l6_7_sandbox_approval_record_{index:03d}",
            "linked_l6_6_approval_packet_id": packet["approval_packet_id"],
            "linked_l6_5_pilot_candidate_id": packet["linked_l6_5_pilot_candidate_id"],
            "scope": {
                "mode": "sandbox_readiness_use_only",
                "candidate_specific": True,
                "source_locator_specific": True,
                "observation_question_specific": True,
                "evidence_capture_plan_specific": True,
            },
            "source_locator_placeholder": packet["source_locator_placeholder"],
            "observation_question": packet["observation_question"],
            "approval_status": "sandbox_approved_for_readiness_only",
            "real_approval_granted": False,
            "durable_real_approval_record": False,
            "real_observation_authorized": False,
            "sandbox_readiness_use_only": True,
            "expiration_policy": {
                "expires_before_real_use": True,
                "real_use_requires_future_record": True,
            },
            "revocation_policy": {
                "revocable_in_sandbox": True,
                "revocation_blocks_readiness_packaging": True,
            },
            "invalidation_conditions": [
                "scope mismatch",
                "source locator no longer matches packet",
                "operator/runtime prerequisite missing",
                "future approval missing",
                "durable real approval record missing",
                "any external action required",
            ],
            "no_action_constraints": NO_ACTION_CONSTRAINTS,
        }
    )


def build_run_package(index: int, record: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any]:
    return with_common(
        {
            "pilot_run_package_id": f"l6_7_pilot_run_package_{index:03d}",
            "linked_sandbox_approval_record": record["sandbox_record_id"],
            "linked_approval_packet": packet["approval_packet_id"],
            "linked_operator_runbook": INPUT_REFS["l6_5_operator_runbook"],
            "linked_runtime_isolation_readiness": "pilot_runtime_isolation_readiness/runtime_isolation_readiness_packet.json",
            "linked_evidence_capture_template": "pilot_evidence_capture_readiness/evidence_capture_packet_template_final.json",
            "linked_abort_quarantine_policy": INPUT_REFS["l6_5_abort_policy"],
            "linked_post_observation_review_workflow": "pilot_post_observation_review_readiness/post_observation_review_packet_template.json",
            "source_locator_placeholder": packet["source_locator_placeholder"],
            "observation_question": packet["observation_question"],
            "run_mode": "future_manual_read_only_pilot_candidate",
            "real_run_authorized": False,
            "network_authorized": False,
            "execution_authorized": False,
            "future_human_approval_required": True,
        }
    )


def receipt(action_type: str) -> dict[str, Any]:
    payload = {
        "action_type": action_type,
        "authorized_in_l6_7": False,
        "executed_in_l6_7": False,
        "blocker_reference": (
            "l6_integrated_approval_record_and_pilot_readiness_sandbox/"
            "l6_7_milestone_contract.json"
        ),
        "future_boundary_required": NEXT_MILESTONE,
        "safety_flags": SAFETY_FLAGS,
        "l6_7_flags": L6_7_FLAGS,
    }
    if action_type in {"durable_real_approval_record", "real_approval_granted"}:
        payload["persisted_in_l6_7"] = False
    return payload


def generate() -> list[str]:
    generated: list[str] = []
    refs, missing_refs = existing_input_map()
    packets = approval_packets()
    records = [build_sandbox_record(i, packet) for i, packet in enumerate(packets, start=1)]
    run_packages = [
        build_run_package(i, record, packet)
        for i, (record, packet) in enumerate(zip(records, packets), start=1)
    ]

    contract = with_common(
        {
            "schema_version": SCHEMA_VERSION,
            "milestone_id": MILESTONE_ID,
            "milestone_name": MILESTONE_NAME,
            "input_milestones": ["L6.0", "L6.1", "L6.2", "L6.3", "L6.4", "L6.5", "L6.6"],
            "mode": "integrated_sandbox_only",
            "approval_record_sandbox_only": True,
            "pilot_run_readiness_only": True,
            "sandbox_approval_record_created": True,
            "manual_evidence_import_future_candidate_allowed": True,
            "requires_future_explicit_human_approval_before_real_observation": True,
            "requires_future_durable_approval_record_before_real_observation": True,
            "requires_future_runtime_isolation_confirmation_before_real_observation": True,
            "requires_future_post_observation_review_before_any_artifact_update": True,
            **BLOCKED_AUTHORIZATIONS,
        }
    )
    write_json(
        "l6_integrated_approval_record_and_pilot_readiness_sandbox/l6_7_milestone_contract.json",
        contract,
        generated,
    )
    write_json(
        "l6_integrated_approval_record_and_pilot_readiness_sandbox/l6_7_integrated_scope.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "scope_status": "integrated_sandbox_only_real_approval_and_execution_blocked",
                "in_scope": [
                    "sandbox approval record lifecycle",
                    "pilot run package assembly",
                    "operator readiness package",
                    "runtime isolation readiness package",
                    "evidence capture readiness package",
                    "post-observation review readiness package",
                    "manual evidence import readiness package",
                    "integrated dry-run decision gate",
                    "strategic residual fixture",
                ],
                "out_of_scope": NO_ACTION_CONSTRAINTS,
            }
        ),
        generated,
    )
    write_json(
        "l6_integrated_approval_record_and_pilot_readiness_sandbox/l6_7_safety_flags.json",
        {"schema_version": SCHEMA_VERSION, "safety_flags": SAFETY_FLAGS, "l6_7_flags": L6_7_FLAGS},
        generated,
    )
    write_text(
        "l6_integrated_approval_record_and_pilot_readiness_sandbox/README.md",
        "# L6.7 Integrated Approval Record & Pilot Run Readiness Sandbox\n\n"
        "This pack creates sandbox approval records and future pilot run readiness "
        "artifacts only. It does not grant real approval, create a durable real "
        "approval record, execute observation, access the network, search, browse, "
        "scrape, publish, contact, pay, execute MCP, write CIEU DB, mutate "
        "canonical strategy, write brain/memory, or directly mutate Y-star.\n",
        generated,
    )
    write_text(
        "l6_integrated_approval_record_and_pilot_readiness_sandbox/l6_7_non_execution_boundary.md",
        "# L6.7 Non-Execution Boundary\n\n"
        f"{PLACEHOLDER_LOCATOR_MARKER}\n\n"
        "L6.7 may create sandbox records and readiness packages only. Sandbox "
        "approval records do not authorize real observation or durable approval "
        "persistence. Network, search, browser fetch, scraping, publication, "
        "outreach, payment, revenue, MCP, live behavior, CIEU DB write, canonical "
        "mutation, writeback, and direct Y-star mutation remain blocked.\n",
        generated,
    )

    summary = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "milestone_name": MILESTONE_NAME,
        "l6_7_integrated_approval_record_and_pilot_readiness_sandbox_defined": True,
        "integrated_sandbox_only": True,
        "approval_record_sandbox_only": True,
        "pilot_run_readiness_only": True,
        "sandbox_approval_record_created": True,
        "sandbox_approval_record_count": len(records),
        "pilot_run_package_count": len(run_packages),
        "operator_readiness_package_created": True,
        "runtime_isolation_readiness_created": True,
        "evidence_capture_readiness_created": True,
        "post_observation_review_readiness_created": True,
        "manual_evidence_import_readiness_created": True,
        "integrated_decision_gate_created": True,
        "no_action_receipts_created": True,
        "strategic_residual_loop_created": True,
        "manual_evidence_import_future_candidate_allowed": True,
        "ready_for_l6_8_user_mediated_manual_evidence_import_pilot": True,
        "ready_for_actual_network_observation_now": False,
        "ready_for_real_approval_now": False,
        "ready_for_durable_real_approval_persistence_now": False,
        "ready_for_publication": False,
        "ready_for_outreach": False,
        "ready_for_payment": False,
        "ready_for_revenue_execution": False,
        "ready_for_mcp_execution": False,
        "ready_for_canonical_update": False,
        "ready_for_brain_memory_writeback": False,
        "next_recommended_milestone": NEXT_MILESTONE,
        "input_refs": refs,
        "missing_optional_refs": missing_refs,
        "safety_flags": SAFETY_FLAGS,
        "l6_7_flags": L6_7_FLAGS,
        **BLOCKED_AUTHORIZATIONS,
        "warning": (
            "L6.7 is integrated-sandbox-only. Sandbox approval records are for "
            "readiness only and do not grant real approval, create durable real "
            "approval records, authorize real observation, or enable network, "
            "search, scraping, browser fetch, publication, outreach, payment, "
            "revenue, MCP, live behavior, CIEU DB writes, canonical mutation, "
            "writeback, or direct Y-star mutation."
        ),
    }
    write_json(
        "l6_integrated_approval_record_and_pilot_readiness_sandbox/l6_7_summary.json",
        summary,
        generated,
    )
    write_text(
        "l6_integrated_approval_record_and_pilot_readiness_sandbox/l6_7_summary.md",
        "# L6.7 Summary\n\n"
        "- Integrated sandbox only: true\n"
        "- Sandbox approval records created: true\n"
        "- Durable real approval record created: false\n"
        "- Real approval granted: false\n"
        f"- Sandbox approval records: {len(records)}\n"
        f"- Pilot run packages: {len(run_packages)}\n"
        f"- Next milestone: {NEXT_MILESTONE}\n",
        generated,
    )

    write_json(
        "sandbox_approval_record_lifecycle/sandbox_approval_record_schema.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "required_fields": [
                    "sandbox_record_id",
                    "linked_l6_6_approval_packet_id",
                    "linked_l6_5_pilot_candidate_id",
                    "scope",
                    "source_locator_placeholder",
                    "observation_question",
                    "approval_status",
                    "real_approval_granted",
                    "durable_real_approval_record",
                    "real_observation_authorized",
                    "sandbox_readiness_use_only",
                    "expiration_policy",
                    "revocation_policy",
                    "invalidation_conditions",
                    "no_action_constraints",
                ],
                "allowed_states": LIFECYCLE_STATES,
            }
        ),
        generated,
    )
    record_index = {
        "schema_version": SCHEMA_VERSION,
        "record_count": len(records),
        "records": [
            {
                "sandbox_record_id": record["sandbox_record_id"],
                "path": f"sandbox_approval_record_lifecycle/sandbox_approval_record_{i:03d}.json",
                "real_approval_granted": False,
                "durable_real_approval_record": False,
                "real_observation_authorized": False,
            }
            for i, record in enumerate(records, start=1)
        ],
        "safety_flags": SAFETY_FLAGS,
        "l6_7_flags": L6_7_FLAGS,
    }
    write_json("sandbox_approval_record_lifecycle/sandbox_approval_record_index.json", record_index, generated)
    for i, record in enumerate(records, start=1):
        write_json(f"sandbox_approval_record_lifecycle/sandbox_approval_record_{i:03d}.json", record, generated)
    write_json(
        "sandbox_approval_record_lifecycle/sandbox_approval_lifecycle_state_machine.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "states": LIFECYCLE_STATES,
                "transitions": [
                    {"from": "draft_packet", "to": "ready_for_review"},
                    {"from": "ready_for_review", "to": "blocked_pending_human_approval"},
                    {"from": "blocked_pending_human_approval", "to": "sandbox_approved_for_readiness_only"},
                    {"from": "sandbox_approved_for_readiness_only", "to": "expired"},
                    {"from": "sandbox_approved_for_readiness_only", "to": "revoked"},
                    {"from": "ready_for_review", "to": "invalid"},
                ],
                "sandbox_approved_for_readiness_only_authorizes_real_observation": False,
            }
        ),
        generated,
    )
    write_json(
        "sandbox_approval_record_lifecycle/sandbox_approval_lifecycle_replay.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "replays": [
                    {
                        "sandbox_record_id": record["sandbox_record_id"],
                        "state_path": [
                            "draft_packet",
                            "ready_for_review",
                            "blocked_pending_human_approval",
                            "sandbox_approved_for_readiness_only",
                        ],
                        "real_observation_authorized_after_replay": False,
                    }
                    for record in records
                ],
            }
        ),
        generated,
    )
    write_json(
        "sandbox_approval_record_lifecycle/sandbox_approval_record_validation_matrix.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "rows": [
                    {
                        "sandbox_record_id": record["sandbox_record_id"],
                        "required_fields_present": True,
                        "sandbox_readiness_use_only": True,
                        "real_approval_granted": False,
                        "durable_real_approval_record": False,
                        "real_observation_authorized": False,
                    }
                    for record in records
                ],
            }
        ),
        generated,
    )
    write_text(
        "sandbox_approval_record_lifecycle/sandbox_approval_record_lifecycle_report.md",
        "# Sandbox Approval Record Lifecycle\n\n"
        "Sandbox approval records are created for readiness replay only. The "
        "sandbox_approved_for_readiness_only state does not authorize real observation.\n",
        generated,
    )

    write_json(
        "pilot_run_package_assembler/pilot_run_package_schema.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "required_fields": [
                    "linked_sandbox_approval_record",
                    "linked_approval_packet",
                    "linked_operator_runbook",
                    "linked_runtime_isolation_readiness",
                    "linked_evidence_capture_template",
                    "linked_abort_quarantine_policy",
                    "linked_post_observation_review_workflow",
                    "source_locator_placeholder",
                    "observation_question",
                    "run_mode",
                    "real_run_authorized",
                    "network_authorized",
                    "execution_authorized",
                    "future_human_approval_required",
                ],
            }
        ),
        generated,
    )
    package_index = {
        "schema_version": SCHEMA_VERSION,
        "package_count": len(run_packages),
        "packages": [
            {
                "pilot_run_package_id": package["pilot_run_package_id"],
                "path": f"pilot_run_package_assembler/pilot_run_package_{i:03d}.json",
                "real_run_authorized": False,
                "execution_authorized": False,
            }
            for i, package in enumerate(run_packages, start=1)
        ],
        "safety_flags": SAFETY_FLAGS,
        "l6_7_flags": L6_7_FLAGS,
    }
    write_json("pilot_run_package_assembler/pilot_run_package_index.json", package_index, generated)
    for i, package in enumerate(run_packages, start=1):
        write_json(f"pilot_run_package_assembler/pilot_run_package_{i:03d}.json", package, generated)
    write_json(
        "pilot_run_package_assembler/pilot_run_package_validation_matrix.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "rows": [
                    {
                        "pilot_run_package_id": package["pilot_run_package_id"],
                        "approval_record_link_present": True,
                        "approval_packet_link_present": True,
                        "operator_readiness_link_present": True,
                        "runtime_isolation_readiness_link_present": True,
                        "evidence_capture_readiness_link_present": True,
                        "post_review_readiness_link_present": True,
                        "real_run_authorized": False,
                        "execution_authorized": False,
                    }
                    for package in run_packages
                ],
            }
        ),
        generated,
    )
    write_text(
        "pilot_run_package_assembler/pilot_run_package_report.md",
        "# Pilot Run Package Assembler\n\n"
        "Pilot run packages assemble future manual read-only pilot inputs without "
        "authorizing execution or network access.\n",
        generated,
    )

    operator_constraints = [
        "no login",
        "no account creation",
        "no contact",
        "no payment",
        "no form submission",
        "no posting/commenting/messaging",
        "no publication",
        "no outreach",
        "no revenue action",
        "no MCP execution",
        "no artifact mutation",
        "no canonical strategy mutation",
        "no brain/memory writeback",
        "no direct Y-star mutation",
    ]
    write_json(
        "pilot_operator_readiness_package/operator_readiness_schema.json",
        with_common({"schema_version": SCHEMA_VERSION, "operator_constraints": operator_constraints}),
        generated,
    )
    write_json(
        "pilot_operator_readiness_package/operator_readiness_checklist.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "readiness_package_created": True,
                "operator_authorized_now": False,
                "future_human_approval_required": True,
                "checklist": [
                    {"constraint": item, "confirmed_for_future_readiness": True}
                    for item in operator_constraints
                ],
            }
        ),
        generated,
    )
    write_json(
        "pilot_operator_readiness_package/operator_non_action_oath_replay.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "oath_replayed_for_sandbox": True,
                "operator_authorized_now": False,
                "non_action_constraints": operator_constraints,
            }
        ),
        generated,
    )
    write_json(
        "pilot_operator_readiness_package/operator_abort_drill.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "abort_drill_mode": "readiness_only",
                "abort_if": [
                    "login appears",
                    "payment appears",
                    "contact requested",
                    "form submission requested",
                    "posting/commenting/messaging requested",
                    "MCP/tool execution requested",
                    "operator uncertainty",
                ],
                "real_run_executed": False,
            }
        ),
        generated,
    )
    write_text(
        "pilot_operator_readiness_package/operator_readiness_report.md",
        "# Operator Readiness Package\n\n"
        "Operator readiness is consolidated for future review only. The operator is "
        "not authorized now.\n",
        generated,
    )

    write_json(
        "pilot_runtime_isolation_readiness/runtime_isolation_readiness_schema.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "readiness_only": True,
                "real_runtime_isolation_activated": False,
                "network_accessed": False,
                "browser_launched": False,
                "external_tool_executed": False,
            }
        ),
        generated,
    )
    write_json(
        "pilot_runtime_isolation_readiness/runtime_isolation_readiness_packet.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "readiness_packet_created": True,
                "real_runtime_isolation_activated": False,
                "network_accessed": False,
                "browser_launched": False,
                "external_tool_executed": False,
                "readiness_only": True,
            }
        ),
        generated,
    )
    write_json(
        "pilot_runtime_isolation_readiness/permitted_future_runtime_profile.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "future_profile_only": True,
                "manual_operator_control": True,
                "read_only_source_viewing": True,
                "evidence_capture_only": True,
                "no_login": True,
                "no_payment": True,
                "no_form_submission": True,
                "activated_in_l6_7": False,
            }
        ),
        generated,
    )
    write_json(
        "pilot_runtime_isolation_readiness/prohibited_runtime_profile.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "prohibited": [
                    "autonomous browsing",
                    "network automation",
                    "scraping loop",
                    "login automation",
                    "account creation",
                    "checkout/payment",
                    "posting/commenting/messaging",
                    "MCP execution",
                    "persistent external mutation",
                ],
            }
        ),
        generated,
    )
    write_json(
        "pilot_runtime_isolation_readiness/runtime_isolation_failure_modes.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "failure_modes": [
                    "runtime isolation not confirmed",
                    "network profile unclear",
                    "browser/tool profile unclear",
                    "manual control absent",
                    "abort controls absent",
                ],
            }
        ),
        generated,
    )
    write_text(
        "pilot_runtime_isolation_readiness/runtime_isolation_readiness_report.md",
        "# Runtime Isolation Readiness\n\n"
        "No real runtime isolation was activated, no network was accessed, no "
        "browser was launched, and no external tool was executed.\n",
        generated,
    )

    evidence_template = with_common(
        {
            "schema_version": SCHEMA_VERSION,
            "template_only": True,
            "real_evidence_captured": False,
            "source_locator": "",
            "source_title": "",
            "source_publisher_or_owner": "",
            "observed_timestamp": "",
            "source_date_or_date_missing": "",
            "freshness_class": "",
            "captured_bounded_claims": [],
            "unsupported_claims": [],
            "missing_context": [],
            "conflict_marker": "",
            "citation_trace": [],
            "claim_boundary": "",
            "review_status": "not_reviewed",
            "external_action_taken": False,
            "publication_taken": False,
            "outreach_taken": False,
            "payment_taken": False,
            "revenue_action_taken": False,
            "mcp_execution_taken": False,
            "canonical_update_taken": False,
            "brain_memory_writeback_taken": False,
            "direct_y_star_mutation_taken": False,
        }
    )
    write_json(
        "pilot_evidence_capture_readiness/evidence_capture_readiness_schema.json",
        with_common({"schema_version": SCHEMA_VERSION, "template_fields": list(evidence_template.keys())}),
        generated,
    )
    write_json(
        "pilot_evidence_capture_readiness/evidence_capture_packet_template_final.json",
        evidence_template,
        generated,
    )
    write_json(
        "pilot_evidence_capture_readiness/citation_capture_template_final.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "template_only": True,
                "citation_trace_required": True,
                "source_locator_required": True,
                "source_title_required": True,
                "real_citation_captured": False,
            }
        ),
        generated,
    )
    write_json(
        "pilot_evidence_capture_readiness/claim_boundary_capture_template_final.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "template_only": True,
                "claim_boundary_required": True,
                "unsupported_claim_marker_required": True,
                "missing_context_required": True,
                "real_claim_captured": False,
            }
        ),
        generated,
    )
    write_json(
        "pilot_evidence_capture_readiness/evidence_capture_quality_gate.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "quality_gate_mode": "structural_no_semantic_truth_scoring",
                "checks": [
                    "source locator present or marked missing",
                    "source title present or marked missing",
                    "source date present or date_missing marker present",
                    "claim boundary present",
                    "unsupported claims listed",
                    "missing context listed",
                    "no external action taken",
                    "review status present",
                ],
            }
        ),
        generated,
    )
    write_text(
        "pilot_evidence_capture_readiness/evidence_capture_readiness_report.md",
        "# Evidence Capture Readiness\n\n"
        "Evidence packet templates are readiness-only and do not claim real evidence "
        "capture.\n",
        generated,
    )

    allowed_review_decisions = [
        "accept_evidence_for_internal_review",
        "quarantine_evidence",
        "reject_evidence",
        "require_additional_source",
        "require_claim_boundary_revision",
        "generate_review_only_artifact_refinement_candidate",
        "block_externalization",
    ]
    write_json(
        "pilot_post_observation_review_readiness/post_observation_review_readiness_schema.json",
        with_common({"schema_version": SCHEMA_VERSION, "allowed_review_decisions": allowed_review_decisions}),
        generated,
    )
    write_json(
        "pilot_post_observation_review_readiness/post_observation_review_packet_template.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "template_only": True,
                "review_required": True,
                "allowed_review_decisions": allowed_review_decisions,
                "publication_authorized": False,
                "outreach_authorized": False,
                "payment_authorized": False,
                "revenue_execution_authorized": False,
                "mcp_execution_authorized": False,
                "canonical_update_authorized": False,
                "brain_memory_writeback_authorized": False,
                "direct_y_star_mutation_authorized": False,
            }
        ),
        generated,
    )
    write_json(
        "pilot_post_observation_review_readiness/evidence_review_decision_matrix.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "decisions": [
                    {"decision": decision, "direct_externalization_authorized": False}
                    for decision in allowed_review_decisions
                ],
            }
        ),
        generated,
    )
    write_json(
        "pilot_post_observation_review_readiness/artifact_refinement_candidate_gate.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "review_only_refinement_candidate_allowed": True,
                "review_required": True,
                "direct_artifact_update_authorized": False,
                "canonical_update_authorized": False,
                "brain_memory_writeback_authorized": False,
                "direct_y_star_mutation_authorized": False,
            }
        ),
        generated,
    )
    write_text(
        "pilot_post_observation_review_readiness/post_observation_review_readiness_report.md",
        "# Post-Observation Review Readiness\n\n"
        "Post-observation review is prepared for future internal review only. No "
        "review decision can authorize externalization or canonical mutation.\n",
        generated,
    )

    manual_import_modes = [
        "user pasted public text",
        "user uploaded public screenshot",
        "user uploaded public document",
        "user supplied public URL as locator only",
        "user supplied source summary",
    ]
    manual_contract = with_common(
        {
            "schema_version": SCHEMA_VERSION,
            "future_manual_evidence_import_candidate_allowed": True,
            "fetch_urls_authorized": False,
            "network_authorized": False,
            "source_supplied_by_user_required": True,
            "source_content_supplied_by_user_required": True,
            "review_required": True,
            "automatic_artifact_update_authorized": False,
            "allowed_future_manual_import_modes": manual_import_modes,
        }
    )
    write_json(
        "manual_evidence_import_readiness/manual_evidence_import_readiness_contract.json",
        manual_contract,
        generated,
    )
    write_json(
        "manual_evidence_import_readiness/manual_evidence_import_packet_template.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "template_only": True,
                "source_supplied_by_user": False,
                "source_content_supplied_by_user": False,
                "source_locator_optional": True,
                "freshness_declared_or_unknown": "",
                "claim_boundary_required": True,
                "missing_context_required": True,
                "unsupported_claim_marker_required": True,
                "external_action_authorized": False,
                "automatic_artifact_update_authorized": False,
                "review_required": True,
                "url_fetch_authorized": False,
            }
        ),
        generated,
    )
    write_json(
        "manual_evidence_import_readiness/user_supplied_evidence_boundary.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "source_supplied_by_user": True,
                "source_content_supplied_by_user": True,
                "source_locator_may_be_locator_only": True,
                "agent_url_fetch_authorized": False,
                "external_action_authorized": False,
            }
        ),
        generated,
    )
    write_json(
        "manual_evidence_import_readiness/manual_evidence_import_validation_matrix.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "validation_mode": "structural_manual_import_readiness_only",
                "checks": [
                    "source supplied by user",
                    "source content supplied by user",
                    "freshness declared or unknown",
                    "claim boundary required",
                    "missing context required",
                    "unsupported claim marker required",
                    "no external action authorized",
                    "no automatic artifact update",
                    "review required",
                    "URL not fetched",
                ],
            }
        ),
        generated,
    )
    write_text(
        "manual_evidence_import_readiness/manual_evidence_import_readiness_report.md",
        "# Manual Evidence Import Readiness\n\n"
        "L6.7 prepares a future user-mediated manual evidence import pilot. It does "
        "not fetch URLs or accept real external evidence in this milestone.\n",
        generated,
    )

    decisions = [
        with_common(
            {
                "candidate_id": package["pilot_run_package_id"],
                "linked_sandbox_approval_record": package["linked_sandbox_approval_record"],
                "sandbox_readiness_decision": "ready_for_manual_evidence_import_pilot",
                "real_observation_execution_decision": "blocked_pending_future_explicit_human_approval",
                "real_network_authorized": False,
                "execution_authorized": False,
                "durable_real_approval_record_created": False,
                "review_required": True,
                "future_milestone_required": True,
                "future_milestone": NEXT_MILESTONE,
            }
        )
        for package in run_packages
    ]
    write_json(
        "pilot_integrated_decision_gate/integrated_decision_gate_contract.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "decision_gate_mode": "integrated_readiness_only_real_execution_blocked",
                "manual_evidence_import_pilot_candidate_allowed": True,
                "real_execution_can_be_authorized_in_l6_7": False,
            }
        ),
        generated,
    )
    write_json(
        "pilot_integrated_decision_gate/integrated_candidate_decision_matrix.json",
        {"schema_version": SCHEMA_VERSION, "decision_count": len(decisions), "decisions": decisions},
        generated,
    )
    write_json(
        "pilot_integrated_decision_gate/blocked_real_execution_decisions.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "blocked_count": len(decisions),
                "decisions": [
                    {
                        "candidate_id": decision["candidate_id"],
                        "real_observation_execution_decision": decision["real_observation_execution_decision"],
                        "real_network_authorized": False,
                        "execution_authorized": False,
                        "durable_real_approval_record_created": False,
                    }
                    for decision in decisions
                ],
            }
        ),
        generated,
    )
    write_json(
        "pilot_integrated_decision_gate/future_entry_conditions.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "future_entry_conditions": [
                    "future explicit human approval",
                    "future durable approval record",
                    "future user-supplied evidence content",
                    "manual evidence import review gate",
                    "post-import claim boundary review",
                    "no automatic artifact update",
                ],
            }
        ),
        generated,
    )
    write_text(
        "pilot_integrated_decision_gate/integrated_decision_gate_report.md",
        "# Integrated Decision Gate\n\n"
        "The integrated gate marks candidates ready for a future manual evidence "
        "import pilot while blocking real observation execution.\n",
        generated,
    )

    for file_name, action_type in NO_ACTION_RECEIPTS.items():
        write_json(f"pilot_integrated_no_action_receipts/{file_name}", receipt(action_type), generated)
    write_text(
        "pilot_integrated_no_action_receipts/integrated_no_action_receipt_report.md",
        "# Integrated No-Action Receipts\n\n"
        "No real approval, durable approval record, real observation, network, "
        "publication, outreach, payment, revenue, MCP, live behavior, CIEU DB "
        "write, canonical mutation, writeback, or direct Y-star mutation occurred.\n",
        generated,
    )

    write_json(
        "l6_integrated_pilot_readiness_strategic_residual_loop/l6_7_cieu_like_fixture.json",
        with_common(
            {
                "X_t": {
                    "l6_0_hypotheses": INPUT_REFS["l6_0_hypotheses"],
                    "l6_1_mvp_artifact_sandbox": INPUT_REFS["l6_1_artifact_cases"],
                    "l6_2_external_observation_boundary": INPUT_REFS["l6_2_boundary"],
                    "l6_3_controlled_observation_sandbox": INPUT_REFS["l6_3_sandbox"],
                    "l6_4_real_read_only_preflight": INPUT_REFS["l6_4_preflight"],
                    "l6_5_pilot_design": INPUT_REFS["l6_5_pilot_design"],
                    "l6_6_approval_packet": INPUT_REFS["l6_6_approval_packet"],
                },
                "U_t": (
                    "Assemble sandbox approval records, pilot run packages, readiness "
                    "packages, manual evidence import readiness, and integrated decisions "
                    "without granting approval or executing observation."
                ),
                "Y_star_t": (
                    "Assemble sandbox approval records, pilot run packages, operator "
                    "readiness, runtime isolation readiness, evidence capture readiness, "
                    "post-observation review readiness, and manual evidence import "
                    "readiness while preserving no-real-approval/no-durable-approval/"
                    "no-network/no-search/no-publication/no-outreach/no-payment/no-"
                    "revenue/no-MCP/no-live/no-CIEU-DB-write/no-canonical-mutation/"
                    "no-brain-memory-writeback/no-direct-Y-star mutation constraints."
                ),
                "Y_t_plus_1": {
                    "sandbox_approval_records_created": len(records),
                    "pilot_run_packages_created": len(run_packages),
                    "operator_readiness_created": True,
                    "runtime_isolation_readiness_created": True,
                    "evidence_capture_readiness_created": True,
                    "post_observation_review_readiness_created": True,
                    "manual_evidence_import_readiness_created": True,
                    "real_approval_granted": False,
                    "durable_real_approval_record_created": False,
                    "real_observation_authorized": False,
                },
                "R_t_plus_1": [
                    "real approval still not granted",
                    "durable real approval record not created",
                    "pilot execution still blocked",
                    "manual evidence import not yet exercised with user-supplied evidence",
                    "source locators remain placeholders",
                    "runtime isolation not activated",
                    "evidence capture templates untested on real user-provided evidence",
                    "post-observation review remains readiness-only",
                    "publication/outreach/payment/revenue remain blocked",
                ],
                "event_mode": "l6_7_integrated_approval_record_and_pilot_readiness_sandbox_fixture",
                "persistence_enabled": False,
                "db_write_performed": False,
                "real_approval_granted": False,
                "durable_real_approval_record_created": False,
                "real_observation_execution_enabled": False,
            }
        ),
        generated,
    )
    write_json(
        "l6_integrated_pilot_readiness_strategic_residual_loop/l6_7_strategic_residual_delta.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "residual_classes": {
                    "real_approval_gap": "real approval still not granted",
                    "durable_record_gap": "durable real approval record not created",
                    "pilot_execution_gap": "pilot execution still blocked",
                    "manual_import_gap": "manual evidence import not yet exercised",
                    "source_locator_gap": "source locators remain placeholders",
                    "runtime_isolation_gap": "runtime isolation not activated",
                    "evidence_capture_gap": "templates untested on real user-provided evidence",
                    "post_review_gap": "post-observation review readiness not exercised",
                    "externalization_gap": "publication/outreach/payment/revenue remain blocked",
                },
            }
        ),
        generated,
    )
    write_json(
        "l6_integrated_pilot_readiness_strategic_residual_loop/l6_7_meta_learning_update_candidate.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "learning_targets": [
                    "sandbox_approval_record_lifecycle_policy",
                    "pilot_run_package_policy",
                    "manual_evidence_import_readiness_policy",
                    "post_observation_review_readiness_policy",
                    "integrated_decision_gate_policy",
                ],
                "eligible_for_review_queue": True,
                "eligible_for_direct_brain_writeback": False,
                "eligible_for_direct_memory_ingestion": False,
                "eligible_for_candidate_auto_approval": False,
                "eligible_for_direct_strategy_mutation": False,
                "approved": False,
                "applied": False,
            }
        ),
        generated,
    )
    write_text(
        "l6_integrated_pilot_readiness_strategic_residual_loop/l6_7_residual_report.md",
        "# L6.7 Strategic Residual\n\n"
        "Integrated sandbox readiness is complete enough for future manual evidence "
        "import planning, but real approval, durable approval persistence, and pilot "
        "execution remain blocked.\n",
        generated,
    )

    readiness = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "l6_7_integrated_approval_record_and_pilot_readiness_sandbox_complete": True,
        "sandbox_approval_record_lifecycle_generated": True,
        "pilot_run_packages_generated": True,
        "operator_readiness_package_generated": True,
        "runtime_isolation_readiness_generated": True,
        "evidence_capture_readiness_generated": True,
        "post_observation_review_readiness_generated": True,
        "manual_evidence_import_readiness_generated": True,
        "integrated_decision_gate_generated": True,
        "no_action_receipts_generated": True,
        "strategic_residual_loop_generated": True,
        "ready_for_l6_8_user_mediated_manual_evidence_import_pilot": True,
        "ready_for_actual_network_observation_now": False,
        "ready_for_real_approval_now": False,
        "ready_for_durable_real_approval_persistence_now": False,
        "ready_for_publication": False,
        "ready_for_outreach": False,
        "ready_for_payment": False,
        "ready_for_revenue_execution": False,
        "ready_for_mcp_execution": False,
        "ready_for_canonical_update": False,
        "ready_for_brain_memory_writeback": False,
        "next_recommended_milestone": NEXT_MILESTONE,
        "blocked_capabilities": NO_ACTION_CONSTRAINTS,
        "safety_flags": SAFETY_FLAGS,
        "l6_7_flags": L6_7_FLAGS,
    }
    write_json("l6_integrated_pilot_readiness_report/l6_7_readiness_assessment.json", readiness, generated)
    write_json(
        "l6_integrated_pilot_readiness_report/l6_7_next_milestone_recommendation.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "recommended_next_milestone": NEXT_MILESTONE,
                "do_not_implement_in_l6_7": True,
                "ready_for_future_user_mediated_manual_evidence_import_pilot": True,
                "ready_for_real_network_observation_now": False,
                "ready_for_real_approval_now": False,
            }
        ),
        generated,
    )
    write_json(
        "l6_integrated_pilot_readiness_report/l6_7_blockers.json",
        with_common(
            {
                "schema_version": SCHEMA_VERSION,
                "blockers": [
                    "future explicit human approval missing",
                    "future durable real approval record missing",
                    "future user-supplied evidence content missing",
                    "manual evidence import review not executed",
                    "runtime isolation not activated",
                    "real network observation still blocked",
                ],
            }
        ),
        generated,
    )
    write_text(
        "l6_integrated_pilot_readiness_report/l6_7_readiness_report.md",
        "# L6.7 Readiness\n\n"
        "- L6.7 integrated approval record and pilot readiness sandbox complete: true\n"
        f"- Ready for {NEXT_MILESTONE}: true\n"
        "- Ready for actual network observation now: false\n"
        "- Ready for real approval now: false\n"
        "- Ready for durable real approval persistence now: false\n"
        "- Ready for publication/outreach/payment/revenue execution: false\n"
        "- Ready for MCP/canonical/writeback/direct Y-star mutation: false\n",
        generated,
    )

    return generated


def main() -> None:
    generated = generate()
    print(
        "Built L6.7 integrated approval record and pilot readiness sandbox artifacts: "
        f"{len(generated)} files"
    )


if __name__ == "__main__":
    main()
