#!/usr/bin/env python3
"""Read-only CLI for generated team console snapshots."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

SNAPSHOT = "console_read_model/generated/team_console_snapshot.json"
CARDS = "console_read_model/generated/agent_cards_compiled.json"
READINESS = "console_read_model/generated/readiness_summary.json"
MANIFEST = "console_read_model/generated/generation_manifest.json"
QUARANTINE = "console_read_model/generated/quarantine_summary.json"
MINING = "console_read_model/generated/safe_mining_summary.json"
REVIEW_QUEUE = "console_read_model/generated/review_queue_summary.json"
DISPOSITION = "console_read_model/generated/artifact_disposition_summary.json"
EVIDENCE_REVIEW = "console_read_model/generated/evidence_review_summary.json"
GOVERNANCE_BRIDGE = "console_read_model/generated/governance_bridge_summary.json"
PRE_U_GOVERNANCE = "console_read_model/generated/pre_u_governance_summary.json"
LABS_ACCEPTANCE = "console_read_model/generated/labs_acceptance_summary.json"
CROSS_REPO_ALIGNMENT = "console_read_model/generated/cross_repo_alignment_summary.json"
LIVE_READINESS = "console_read_model/generated/live_readiness_summary.json"
LIVE_BOUNDARY = "console_read_model/generated/live_boundary_summary.json"
CIEU_BOUNDARY = "console_read_model/generated/cieu_boundary_summary.json"
AUTONOMY_INVENTORY = "console_read_model/generated/autonomy_inventory_summary.json"
REQUIRED_AGENTS = ["Aiden-CEO", "Ethan-CTO", "Samantha-Secretary"]
UNSAFE_MARKERS = [
    ".db",
    ".db-wal",
    ".db-shm",
    "scripts/.logs",
    "__pycache__",
    "active-agent",
    ".pid",
    "daemon",
    "reports/ceo/brain_dream_diffs",
    "reports/escalation",
    "reports/drift_hourly",
]


def usage() -> str:
    return (
        "Usage: python3 console_read_model/cli/team_console.py "
        "{summary|agents|agent <agent_id>|readiness|capabilities|governance|quarantine|mining-candidates|review-queue|artifact-disposition|evidence-review|governance-bridge|pre-u-governance|labs-acceptance|cross-repo-alignment|live-readiness|live-boundary|cieu-boundary|autonomy-inventory|gaps|sources|warnings|validate-local}"
    )


def ensure_safe_path(relative_path: str) -> Path:
    lowered = relative_path.lower()
    for marker in UNSAFE_MARKERS:
        m = marker.lower()
        if m in {".db", ".db-wal", ".db-shm"}:
            if lowered.endswith(m):
                raise ValueError(f"Refusing unsafe source: {relative_path}")
        elif m in lowered:
            raise ValueError(f"Refusing unsafe source: {relative_path}")
    path = ROOT / relative_path
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"Refusing path outside repo: {relative_path}") from exc
    return path


def load_json(relative_path: str) -> Any:
    path = ensure_safe_path(relative_path)
    if not path.exists():
        raise FileNotFoundError(f"Required snapshot missing: {relative_path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_all() -> dict[str, Any]:
    return {
        "snapshot": load_json(SNAPSHOT),
        "cards": load_json(CARDS),
        "readiness": load_json(READINESS),
        "manifest": load_json(MANIFEST),
        "quarantine": load_json(QUARANTINE),
        "mining": load_json(MINING),
        "review_queue": load_json(REVIEW_QUEUE),
        "disposition": load_json(DISPOSITION),
        "evidence_review": load_json(EVIDENCE_REVIEW),
        "governance_bridge": load_json(GOVERNANCE_BRIDGE),
        "pre_u_governance": load_json(PRE_U_GOVERNANCE),
        "labs_acceptance": load_json(LABS_ACCEPTANCE),
        "cross_repo_alignment": load_json(CROSS_REPO_ALIGNMENT),
        "live_readiness": load_json(LIVE_READINESS),
        "live_boundary": load_json(LIVE_BOUNDARY),
        "cieu_boundary": load_json(CIEU_BOUNDARY),
        "autonomy_inventory": load_json(AUTONOMY_INVENTORY),
    }


def bullet_list(items: list[Any]) -> None:
    for item in items:
        print(f"- {item}")


def cmd_summary(data: dict[str, Any]) -> None:
    snapshot = data["snapshot"]
    readiness = data["readiness"]
    print("# Team Brain Console Snapshot")
    print()
    print(f"model_status: {snapshot.get('schema_name')} / {snapshot.get('schema_version')}")
    print()
    print("Agents included:")
    for agent in snapshot.get("agents", []):
        print(f"- {agent['agent_id']} ({agent.get('readiness_level')})")
    print()
    print("Ready now:")
    bullet_list(readiness.get("ready_now", []))
    print()
    print("Governance:")
    print(snapshot.get("governance_summary", {}).get("principle", "not recorded"))
    print()
    print("Warnings:")
    warnings = snapshot.get("warnings", [])
    bullet_list(warnings or ["none"])


def cmd_agents(data: dict[str, Any]) -> None:
    print("# Agents")
    for agent in data["snapshot"].get("agents", []):
        print()
        print(f"## {agent['agent_id']}")
        print(f"- role: {agent.get('role_type')}")
        print(f"- readiness: {agent.get('readiness_level')} / {agent.get('card_status')}")
        print(f"- focus: {agent.get('focus')}")


def card_by_id(data: dict[str, Any], agent_id: str) -> dict[str, Any] | None:
    for card in data["cards"].get("cards", []):
        if card.get("card_id") == agent_id:
            return card
    return None


def cmd_agent(data: dict[str, Any], agent_id: str) -> int:
    card = card_by_id(data, agent_id)
    if not card:
        print(f"Unknown agent: {agent_id}")
        return 1
    print(f"# {agent_id}")
    print(f"display_name: {card.get('display_name')}")
    print(f"role: {card.get('role')}")
    print(f"status: {card.get('status')}")
    print()
    print("primary_focus:")
    bullet_list(card.get("primary_focus", []))
    print()
    print("capabilities:")
    bullet_list(card.get("capabilities", []))
    print()
    print("limitations:")
    bullet_list(card.get("limitations", []))
    print()
    print("next_actions:")
    bullet_list(card.get("next_actions", []))
    print()
    print("warnings:")
    bullet_list(card.get("warnings", []) or ["none"])
    return 0


def cmd_readiness(data: dict[str, Any]) -> None:
    readiness = data["readiness"]
    print("# Readiness")
    for key in ["ready_now", "not_ready", "recommended_next_steps", "blockers", "safety_boundaries"]:
        print()
        print(f"## {key}")
        bullet_list(readiness.get(key, []))


def cmd_capabilities(data: dict[str, Any]) -> None:
    matrix = data["snapshot"].get("capabilities", {})
    print("# Capabilities")
    print()
    print("Agents:")
    bullet_list(matrix.get("agents", []))
    print()
    print("Matrix:")
    for capability, values in matrix.get("matrix", {}).items():
        rendered = ", ".join(f"{agent}={status}" for agent, status in values.items())
        print(f"- {capability}: {rendered}")


def cmd_governance(data: dict[str, Any]) -> None:
    print("# Governance")
    print("- labs thinks")
    print("- Y-star-gov judges")
    print("- hook enforces")
    print("- CIEU records/teaches")
    print("- brain learns")
    print("- console reads curated snapshots only")
    print()
    summary = data["snapshot"].get("governance_summary", {})
    for key, value in summary.items():
        print(f"- {key}: {value}")


def cmd_quarantine(data: dict[str, Any]) -> None:
    quarantine = data["quarantine"]
    print("# Runtime Artifact Quarantine Summary")
    print()
    print(f"framework_status: {quarantine.get('framework_status')}")
    print(f"current_mining_level: {quarantine.get('current_mining_level')}")
    print(f"artifacts_classified: {quarantine.get('artifacts_classified')}")
    print(f"unsafe_artifacts_count: {quarantine.get('unsafe_artifacts_count')}")
    print()
    print("classes_seen:")
    for class_name, count in sorted(quarantine.get("classes_seen", {}).items()):
        print(f"- {class_name}: {count}")
    print()
    print("forbidden_direct_reads:")
    bullet_list(quarantine.get("forbidden_direct_reads", []))
    print()
    print("future_adapter_candidates:")
    bullet_list(quarantine.get("future_adapter_candidates", []))
    print()
    print(f"generated_manifest_ref: {quarantine.get('generated_manifest_ref')}")
    print(f"warning: {quarantine.get('safety_warning')}")


def cmd_mining_candidates(data: dict[str, Any]) -> None:
    mining = data["mining"]
    print("# Runtime Artifact Safe Mining Candidates")
    print()
    print(f"candidate_count: {mining.get('candidate_count')}")
    print(f"safety_level: {mining.get('safety_level')}")
    print(f"ingestion_status: {mining.get('ingestion_status')}")
    print(f"generated_candidate_index: {mining.get('generated_candidate_index')}")
    print()
    print("classes_seen:")
    for class_name, count in sorted(mining.get("classes_seen", {}).items()):
        print(f"- {class_name}: {count}")
    print()
    print(f"allowed_next_step: {mining.get('allowed_next_step')}")
    print(f"forbidden_next_step: {mining.get('forbidden_next_step')}")
    print(f"warning: {mining.get('warning')}")


def cmd_review_queue(data: dict[str, Any]) -> None:
    queue = data["review_queue"]
    print("# Runtime Artifact Candidate Review Queue")
    print()
    print(f"review_count: {queue.get('review_count')}")
    print(f"generated_queue_path: {queue.get('generated_queue_path')}")
    print(f"ingestion_status: {queue.get('default_ingestion_status')}")
    print()
    print("statuses:")
    for status, count in sorted(queue.get("statuses", {}).items()):
        print(f"- {status}: {count}")
    print()
    print("intended_use_summary:")
    for use, count in sorted(queue.get("intended_use_summary", {}).items()):
        print(f"- {use}: {count}")
    print()
    print(f"warning: {queue.get('warning')}")


def cmd_artifact_disposition(data: dict[str, Any]) -> None:
    disposition = data["disposition"]
    print("# Runtime Artifact Backlog Disposition")
    print()
    print(f"total_artifacts: {disposition.get('total_artifacts')}")
    print(f"artifacts_with_disposition: {disposition.get('artifacts_with_disposition')}")
    print(f"safe_mined_to_review_queue: {disposition.get('safe_mined_to_review_queue')}")
    print(f"forbidden_direct_read_count: {disposition.get('forbidden_direct_read_count')}")
    print("evidence_scoring_status:")
    for status, count in sorted(disposition.get("evidence_scoring_status", {}).items()):
        print(f"- {status}: {count}")
    print()
    print("dispositions:")
    for name, count in sorted(disposition.get("dispositions", {}).items()):
        print(f"- {name}: {count}")
    print()
    print("deferred_adapter_counts:")
    for name, count in sorted(disposition.get("deferred_adapter_counts", {}).items()):
        print(f"- {name}: {count}")
    print()
    print(f"generated_disposition_index: {disposition.get('generated_disposition_index')}")
    print(f"warning: {disposition.get('warning')}")


def cmd_evidence_review(data: dict[str, Any]) -> None:
    evidence = data["evidence_review"]
    print("# Runtime Artifact Evidence Review")
    print()
    print(f"candidates_scored: {evidence.get('candidates_scored')}")
    print(f"decision_stubs_created: {evidence.get('decision_stubs_created')}")
    print(f"routes_created: {evidence.get('routes_created')}")
    print(f"automatic_approvals: {evidence.get('automatic_approvals')}")
    print("semantic_truth_status:")
    for status, count in sorted(evidence.get("semantic_truth_status", {}).items()):
        print(f"- {status}: {count}")
    print()
    print("reuse_readiness:")
    for readiness, count in sorted(evidence.get("reuse_readiness", {}).items()):
        print(f"- {readiness}: {count}")
    print()
    print("route_counts:")
    for route, count in sorted(evidence.get("route_counts", {}).items()):
        print(f"- {route}: {count}")
    print()
    print(f"warning: {evidence.get('warning')}")


def cmd_governance_bridge(data: dict[str, Any]) -> None:
    bridge = data["governance_bridge"]
    print("# Labs-Gov Alignment Bridge")
    print()
    print(f"latest_bridge_run_id: {bridge.get('latest_bridge_run_id')}")
    print(f"source_task_id: {bridge.get('source_task_id')}")
    print(f"agent_id: {bridge.get('agent_id')}")
    print(f"ystar_gov_decision: {bridge.get('ystar_gov_decision')}")
    print(f"ystar_gov_exit_code: {bridge.get('ystar_gov_exit_code')}")
    print(f"allow_execution: {bridge.get('allow_execution')}")
    print(f"require_revision: {bridge.get('require_revision')}")
    print(f"deny: {bridge.get('deny')}")
    print(f"escalate: {bridge.get('escalate')}")
    print(f"dry_run_only: {bridge.get('dry_run_only')}")
    print(f"non_execution_confirmation: {bridge.get('non_execution_confirmation')}")
    print(f"action_executed: {bridge.get('action_executed')}")
    print(f"cieu_written: {bridge.get('cieu_written')}")
    print(f"brain_writeback_performed: {bridge.get('brain_writeback_performed')}")
    print(f"memory_ingestion_performed: {bridge.get('memory_ingestion_performed')}")
    print(f"generated_decision_snapshot: {bridge.get('generated_decision_snapshot')}")
    print(f"warning: {bridge.get('warning')}")


def cmd_pre_u_governance(data: dict[str, Any]) -> None:
    pre_u = data["pre_u_governance"]
    print("# Labs Pre-U Governance Dry Run")
    print()
    print(f"packets_generated: {pre_u.get('packets_generated')}")
    print("roles_covered:")
    bullet_list(pre_u.get("roles_covered", []))
    print()
    print("decision_counts:")
    for decision, count in sorted(pre_u.get("decision_counts", {}).items()):
        print(f"- {decision}: {count}")
    print()
    print("decisions_by_role:")
    for agent_id, decision in sorted(pre_u.get("decisions_by_role", {}).items()):
        print(f"- {agent_id}: {decision.get('decision')} (exit {decision.get('exit_code')})")
    print()
    print(f"dry_run_only: {pre_u.get('dry_run_only')}")
    print(f"action_executed: {pre_u.get('action_executed')}")
    print(f"cieu_written: {pre_u.get('cieu_written')}")
    print(f"brain_writeback_performed: {pre_u.get('brain_writeback_performed')}")
    print(f"memory_ingestion_performed: {pre_u.get('memory_ingestion_performed')}")
    print(f"generated_decision_snapshots: {pre_u.get('generated_decision_snapshots')}")
    print(f"warning: {pre_u.get('warning')}")


def cmd_labs_acceptance(data: dict[str, Any]) -> None:
    acceptance = data["labs_acceptance"]
    print("# Labs Runtime Governance Acceptance")
    print()
    print(f"accepted: {acceptance.get('accepted')}")
    print(f"checks_passed: {acceptance.get('checks_passed')}")
    print(f"checks_total: {acceptance.get('checks_total')}")
    print("roles_covered:")
    bullet_list(acceptance.get("roles_covered", []))
    print()
    print("decision_counts:")
    for decision, count in sorted(acceptance.get("decision_counts", {}).items()):
        print(f"- {decision}: {count}")
    print()
    print(f"action_executed: {acceptance.get('action_executed')}")
    print(f"cieu_written: {acceptance.get('cieu_written')}")
    print(f"brain_writeback_performed: {acceptance.get('brain_writeback_performed')}")
    print(f"memory_ingestion_performed: {acceptance.get('memory_ingestion_performed')}")
    print(f"raw_runtime_artifacts_ingested: {acceptance.get('raw_runtime_artifacts_ingested')}")
    print(f"generated_acceptance_report: {acceptance.get('generated_acceptance_report')}")
    print(f"warning: {acceptance.get('warning')}")


def cmd_cross_repo_alignment(data: dict[str, Any]) -> None:
    alignment = data["cross_repo_alignment"]
    print("# Cross-Repo Governance Alignment")
    print()
    print(f"alignment accepted: {alignment.get('alignment_accepted')}")
    print(f"ystar-company HEAD: {alignment.get('ystar_company_head_summary')}")
    print(f"Y-star-gov HEAD: {alignment.get('ystar_gov_head_summary')}")
    print(f"Y-star-gov endpoint acceptance: {alignment.get('ystar_gov_endpoint_accepted')}")
    print(f"labs runtime acceptance: {alignment.get('labs_runtime_accepted')}")
    print("roles_covered:")
    bullet_list(alignment.get("roles_covered", []))
    print()
    print("decision_counts:")
    for decision, count in sorted(alignment.get("decision_counts", {}).items()):
        print(f"- {decision}: {count}")
    print()
    print("safety_assertions:")
    for name, value in sorted(alignment.get("safety_assertions", {}).items()):
        print(f"- {name}: {value}")
    print(f"generated_manifest: {alignment.get('generated_manifest')}")
    print(f"warning: {alignment.get('warning')}")


def cmd_live_readiness(data: dict[str, Any]) -> None:
    readiness = data["live_readiness"]
    print("# Labs Live Readiness")
    print()
    print(f"dry_run_governance_ready: {readiness.get('dry_run_governance_ready')}")
    print(f"minimal_live_loop_ready: {readiness.get('minimal_live_loop_ready')}")
    print(f"minimal_live_loop_status: {readiness.get('minimal_live_loop_status')}")
    print(f"recommended_next_phase: {readiness.get('recommended_next_phase')}")
    print(f"live_action_execution_allowed: {readiness.get('live_action_execution_allowed')}")
    print(f"live_cieu_write_allowed: {readiness.get('live_cieu_write_allowed')}")
    print(f"live_brain_writeback_allowed: {readiness.get('live_brain_writeback_allowed')}")
    print(f"live_memory_ingestion_allowed: {readiness.get('live_memory_ingestion_allowed')}")
    print(f"candidate_auto_approval_allowed: {readiness.get('candidate_auto_approval_allowed')}")
    print(f"raw_artifact_ingestion_allowed: {readiness.get('raw_artifact_ingestion_allowed')}")
    print(f"transition_backlog_items: {readiness.get('transition_backlog_items')}")
    print()
    print("blockers:")
    bullet_list(readiness.get("blockers", []))
    print()
    print(f"generated_report: {readiness.get('generated_report')}")
    print(f"generated_transition_backlog: {readiness.get('generated_transition_backlog')}")
    print(f"warning: {readiness.get('warning')}")


def cmd_live_boundary(data: dict[str, Any]) -> None:
    boundary = data["live_boundary"]
    print("# Labs Live Boundary")
    print()
    print(f"live boundary defined: {boundary.get('live_boundary_defined')}")
    print(f"operator approval gate defined: {boundary.get('operator_approval_gate_defined')}")
    print(f"action sandbox contract defined: {boundary.get('action_sandbox_contract_defined')}")
    print(f"rollback policy defined: {boundary.get('rollback_policy_defined')}")
    print(f"CIEU writer boundary defined: {boundary.get('cieu_writer_boundary_defined')}")
    print(f"live execution enabled: {boundary.get('live_action_execution_enabled')}")
    print(f"CIEU write enabled: {boundary.get('cieu_write_enabled')}")
    print(f"brain writeback enabled: {boundary.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {boundary.get('memory_ingestion_enabled')}")
    print(f"candidate auto approval enabled: {boundary.get('candidate_auto_approval_enabled')}")
    print(f"raw artifact ingestion enabled: {boundary.get('raw_artifact_ingestion_enabled')}")
    print(f"minimal live loop ready: {boundary.get('minimal_live_loop_ready')}")
    print(f"required manual enablement: {boundary.get('requires_manual_enablement')}")
    print(f"blocked reason: {boundary.get('blocked_reason')}")
    print()
    print("checklist_status_counts:")
    for status, count in sorted(boundary.get("checklist_status_counts", {}).items()):
        print(f"- {status}: {count}")
    print(f"generated_manifest: {boundary.get('generated_manifest')}")
    print(f"generated_checklist: {boundary.get('generated_checklist')}")
    print(f"warning: {boundary.get('warning')}")


def cmd_cieu_boundary(data: dict[str, Any]) -> None:
    boundary = data["cieu_boundary"]
    print("# Labs CIEU Runtime Boundary")
    print()
    print(f"CIEU runtime boundary defined: {boundary.get('cieu_runtime_boundary_defined')}")
    print(f"CIEU runtime event schema defined: {boundary.get('cieu_runtime_event_schema_defined')}")
    print(f"prediction delta fixture defined: {boundary.get('prediction_delta_fixture_defined')}")
    print(f"CIEU writer policy defined: {boundary.get('cieu_writer_policy_defined')}")
    print(f"dry run only: {boundary.get('dry_run_only')}")
    print(f"persistence enabled: {boundary.get('persistence_enabled')}")
    print(f"live action execution enabled: {boundary.get('live_action_execution_enabled')}")
    print(f"CIEU write enabled: {boundary.get('cieu_write_enabled')}")
    print(f"brain writeback enabled: {boundary.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {boundary.get('memory_ingestion_enabled')}")
    print(f"candidate auto approval enabled: {boundary.get('candidate_auto_approval_enabled')}")
    print(f"raw artifact ingestion enabled: {boundary.get('raw_artifact_ingestion_enabled')}")
    print(f"minimal live loop ready: {boundary.get('minimal_live_loop_ready')}")
    print(f"required manual enablement: {boundary.get('requires_manual_enablement')}")
    print(f"blocked reason: {boundary.get('blocked_reason')}")
    print(f"generated_manifest: {boundary.get('generated_manifest')}")
    print(f"generated_sample_event: {boundary.get('generated_sample_event')}")
    print(f"generated_prediction_delta_fixture: {boundary.get('generated_prediction_delta_fixture')}")
    print(f"warning: {boundary.get('warning')}")


def cmd_autonomy_inventory(data: dict[str, Any]) -> None:
    inventory = data["autonomy_inventory"]
    print("# Company Autonomy Inventory")
    print()
    print(f"repo archaeology completed: {inventory.get('repo_archaeology_completed')}")
    print(f"observation map defined: {inventory.get('observation_capability_map_defined')}")
    print(f"resource sensing map defined: {inventory.get('resource_sensing_map_defined')}")
    print(f"action map defined: {inventory.get('action_capability_map_defined')}")
    print(f"governed tool candidates defined: {inventory.get('governed_tool_registry_candidates_defined')}")
    print(f"agent role capability matrix defined: {inventory.get('agent_role_capability_matrix_defined')}")
    print(f"commercial agent company goal aligned: {inventory.get('commercial_agent_company_goal_aligned')}")
    print(f"governance-only runtime: {inventory.get('governance_only_runtime')}")
    print(f"live actions enabled: {inventory.get('live_actions_enabled')}")
    print(f"external actions enabled: {inventory.get('external_actions_enabled')}")
    print(f"brain writeback enabled: {inventory.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {inventory.get('memory_ingestion_enabled')}")
    print(f"CIEU persistence enabled: {inventory.get('cieu_persistence_enabled')}")
    print(f"git push enabled: {inventory.get('git_push_enabled')}")
    print(f"daemon control enabled: {inventory.get('daemon_control_enabled')}")
    print(f"email or external communication enabled: {inventory.get('email_or_external_communication_enabled')}")
    print(f"next required milestone: {inventory.get('next_required_milestone')}")
    print(f"generated_summary: {inventory.get('generated_summary')}")
    print(f"generated_report: {inventory.get('generated_report')}")
    print(f"warning: {inventory.get('warning')}")


def cmd_gaps(data: dict[str, Any]) -> None:
    print("# Gaps")
    bullet_list(data["snapshot"].get("open_gaps", []))
    for item in data["readiness"].get("blockers", []):
        print(f"- blocker: {item}")


def cmd_sources(data: dict[str, Any]) -> None:
    manifest = data["manifest"]
    print("# Sources")
    print()
    print("Source files:")
    bullet_list(manifest.get("source_files", []))
    print()
    print("Unsafe sources not read:")
    bullet_list(manifest.get("unsafe_sources_not_read", []))
    quarantine = data.get("quarantine", {})
    if quarantine:
        print()
        print("Quarantine manifest:")
        print(f"- {quarantine.get('generated_manifest_ref')}")
    mining = data.get("mining", {})
    if mining:
        print()
        print("Safe mining candidate index:")
        print(f"- {mining.get('generated_candidate_index')}")
    review_queue = data.get("review_queue", {})
    if review_queue:
        print()
        print("Candidate review queue:")
        print(f"- {review_queue.get('generated_queue_path')}")
    disposition = data.get("disposition", {})
    if disposition:
        print()
        print("Artifact disposition index:")
        print(f"- {disposition.get('generated_disposition_index')}")
    evidence = data.get("evidence_review", {})
    if evidence:
        print()
        print("Evidence review indexes:")
        print(f"- {evidence.get('generated_evidence_scores')}")
        print(f"- {evidence.get('generated_hint_routing')}")
    bridge = data.get("governance_bridge", {})
    if bridge:
        print()
        print("Labs-Gov bridge decision snapshot:")
        print(f"- {bridge.get('generated_decision_snapshot')}")
    pre_u = data.get("pre_u_governance", {})
    if pre_u:
        print()
        print("Pre-U governance decision snapshots:")
        print(f"- {pre_u.get('generated_decision_snapshots')}")
    acceptance = data.get("labs_acceptance", {})
    if acceptance:
        print()
        print("Labs runtime acceptance report:")
        print(f"- {acceptance.get('generated_acceptance_report')}")
    alignment = data.get("cross_repo_alignment", {})
    if alignment:
        print()
        print("Cross-repo alignment manifest:")
        print(f"- {alignment.get('generated_manifest')}")
    live_readiness = data.get("live_readiness", {})
    if live_readiness:
        print()
        print("Live readiness report:")
        print(f"- {live_readiness.get('generated_report')}")
        print(f"- {live_readiness.get('generated_transition_backlog')}")
    live_boundary = data.get("live_boundary", {})
    if live_boundary:
        print()
        print("Live boundary manifest:")
        print(f"- {live_boundary.get('generated_manifest')}")
        print(f"- {live_boundary.get('generated_checklist')}")
    cieu_boundary = data.get("cieu_boundary", {})
    if cieu_boundary:
        print()
        print("CIEU runtime boundary manifest and fixtures:")
        print(f"- {cieu_boundary.get('generated_manifest')}")
        print(f"- {cieu_boundary.get('generated_sample_event')}")
        print(f"- {cieu_boundary.get('generated_prediction_delta_fixture')}")
    autonomy_inventory = data.get("autonomy_inventory", {})
    if autonomy_inventory:
        print()
        print("Company autonomy inventory:")
        print(f"- {autonomy_inventory.get('generated_summary')}")
        print(f"- {autonomy_inventory.get('generated_report')}")


def cmd_warnings(data: dict[str, Any]) -> None:
    print("# Warnings")
    bullet_list(data["snapshot"].get("warnings", []) or ["none"])


def source_has_unsafe_marker(source: str) -> str | None:
    lowered = source.lower()
    for marker in UNSAFE_MARKERS:
        m = marker.lower()
        if m in {".db", ".db-wal", ".db-shm"}:
            if lowered.endswith(m):
                return marker
        elif m in lowered:
            return marker
    return None


def cmd_validate_local() -> int:
    failures: list[str] = []
    inspected: list[str] = []
    loaded: dict[str, Any] = {}
    for rel in [
        SNAPSHOT,
        CARDS,
        READINESS,
        MANIFEST,
        QUARANTINE,
        MINING,
        REVIEW_QUEUE,
        DISPOSITION,
        EVIDENCE_REVIEW,
        GOVERNANCE_BRIDGE,
        PRE_U_GOVERNANCE,
        LABS_ACCEPTANCE,
        CROSS_REPO_ALIGNMENT,
        LIVE_READINESS,
        LIVE_BOUNDARY,
        CIEU_BOUNDARY,
        AUTONOMY_INVENTORY,
    ]:
        try:
            loaded[rel] = load_json(rel)
            inspected.append(rel)
        except Exception as exc:
            failures.append(str(exc))

    snapshot = loaded.get(SNAPSHOT)
    if snapshot:
        agents = {agent.get("agent_id") for agent in snapshot.get("agents", [])}
        for agent_id in REQUIRED_AGENTS:
            if agent_id not in agents:
                failures.append(f"required agent missing from snapshot: {agent_id}")
        if "quarantine_summary" not in snapshot:
            failures.append("quarantine_summary missing from team console snapshot")
        if "safe_mining_summary" not in snapshot:
            failures.append("safe_mining_summary missing from team console snapshot")
        if "review_queue_summary" not in snapshot:
            failures.append("review_queue_summary missing from team console snapshot")
        if "artifact_disposition_summary" not in snapshot:
            failures.append("artifact_disposition_summary missing from team console snapshot")
        if "evidence_review_summary" not in snapshot:
            failures.append("evidence_review_summary missing from team console snapshot")
        if "governance_bridge_summary" not in snapshot:
            failures.append("governance_bridge_summary missing from team console snapshot")
        if "pre_u_governance_summary" not in snapshot:
            failures.append("pre_u_governance_summary missing from team console snapshot")
        if "labs_acceptance_summary" not in snapshot:
            failures.append("labs_acceptance_summary missing from team console snapshot")
        if "cross_repo_alignment_summary" not in snapshot:
            failures.append("cross_repo_alignment_summary missing from team console snapshot")
        if "live_readiness_summary" not in snapshot:
            failures.append("live_readiness_summary missing from team console snapshot")
        if "live_boundary_summary" not in snapshot:
            failures.append("live_boundary_summary missing from team console snapshot")
        if "cieu_boundary_summary" not in snapshot:
            failures.append("cieu_boundary_summary missing from team console snapshot")
        if "autonomy_inventory_summary" not in snapshot:
            failures.append("autonomy_inventory_summary missing from team console snapshot")

    manifest = loaded.get(MANIFEST)
    if manifest:
        for source in manifest.get("source_files", []):
            marker = source_has_unsafe_marker(str(source))
            if marker:
                failures.append(f"unsafe source in manifest: {source} ({marker})")

    quarantine = loaded.get(QUARANTINE)
    if quarantine:
        required_fields = [
            "framework_status",
            "current_mining_level",
            "artifacts_classified",
            "unsafe_artifacts_count",
            "classes_seen",
            "generated_manifest_ref",
            "forbidden_direct_reads",
            "future_adapter_candidates",
            "safety_warning",
        ]
        for field in required_fields:
            if field not in quarantine:
                failures.append(f"quarantine summary missing field: {field}")

    mining = loaded.get(MINING)
    if mining:
        required_fields = [
            "candidate_count",
            "classes_seen",
            "generated_candidate_index",
            "safety_level",
            "ingestion_status",
            "allowed_next_step",
            "forbidden_next_step",
            "warning",
        ]
        for field in required_fields:
            if field not in mining:
                failures.append(f"safe mining summary missing field: {field}")
        if mining.get("ingestion_status") != "candidate_only":
            failures.append("safe mining summary must remain candidate_only")
        if mining.get("forbidden_next_step") != "direct_brain_writeback":
            failures.append("safe mining summary must forbid direct brain writeback")

    review_queue = loaded.get(REVIEW_QUEUE)
    if review_queue:
        required_fields = [
            "review_count",
            "statuses",
            "intended_use_summary",
            "generated_queue_path",
            "default_review_status",
            "default_ingestion_status",
            "forbidden_actions",
            "warning",
        ]
        for field in required_fields:
            if field not in review_queue:
                failures.append(f"review queue summary missing field: {field}")
        if review_queue.get("default_review_status") != "pending_review":
            failures.append("review queue summary must remain pending_review")
        if review_queue.get("default_ingestion_status") != "not_ingested":
            failures.append("review queue summary must remain not_ingested")
        forbidden = set(review_queue.get("forbidden_actions", []))
        for action in ["direct_brain_writeback", "direct_memory_ingestion", "direct_cieu_write"]:
            if action not in forbidden:
                failures.append(f"review queue summary missing forbidden action: {action}")

    disposition = loaded.get(DISPOSITION)
    if disposition:
        required_fields = [
            "total_artifacts",
            "artifacts_with_disposition",
            "dispositions",
            "safe_mined_to_review_queue",
            "deferred_adapter_counts",
            "forbidden_direct_read_count",
            "evidence_scoring_status",
            "generated_disposition_index",
            "warning",
        ]
        for field in required_fields:
            if field not in disposition:
                failures.append(f"artifact disposition summary missing field: {field}")
        if disposition.get("total_artifacts") != disposition.get("artifacts_with_disposition"):
            failures.append("artifact disposition summary must cover every manifest artifact")
        evidence = set(disposition.get("evidence_scoring_status", {}))
        if evidence and evidence != {"not_started"}:
            failures.append("artifact disposition evidence scoring must remain not_started")

    evidence_review = loaded.get(EVIDENCE_REVIEW)
    if evidence_review:
        required_fields = [
            "candidates_scored",
            "decision_stubs_created",
            "routes_created",
            "reuse_readiness",
            "route_counts",
            "semantic_truth_status",
            "automatic_approvals",
            "brain_writeback_allowed",
            "memory_ingestion_allowed",
            "cieu_write_allowed",
            "warning",
        ]
        for field in required_fields:
            if field not in evidence_review:
                failures.append(f"evidence review summary missing field: {field}")
        if evidence_review.get("automatic_approvals") != 0:
            failures.append("evidence review must not create automatic approvals")
        for field in ["brain_writeback_allowed", "memory_ingestion_allowed", "cieu_write_allowed"]:
            if evidence_review.get(field) != 0:
                failures.append(f"evidence review must not allow {field}")
        semantic = set(evidence_review.get("semantic_truth_status", {}))
        if semantic and semantic != {"not_evaluated"}:
            failures.append("evidence review semantic truth status must remain not_evaluated")

    governance_bridge = loaded.get(GOVERNANCE_BRIDGE)
    if governance_bridge:
        required_fields = [
            "latest_bridge_run_id",
            "source_task_id",
            "agent_id",
            "ystar_gov_cli_path",
            "ystar_gov_exit_code",
            "ystar_gov_decision",
            "allow_execution",
            "require_revision",
            "deny",
            "escalate",
            "dry_run_only",
            "non_execution_confirmation",
            "action_executed",
            "cieu_written",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "generated_decision_snapshot",
            "warning",
        ]
        for field in required_fields:
            if field not in governance_bridge:
                failures.append(f"governance bridge summary missing field: {field}")
        if governance_bridge.get("dry_run_only") is not True:
            failures.append("governance bridge must remain dry_run_only")
        if governance_bridge.get("non_execution_confirmation") is not True:
            failures.append("governance bridge must confirm non-execution")
        for field in [
            "action_executed",
            "cieu_written",
            "brain_writeback_performed",
            "memory_ingestion_performed",
        ]:
            if governance_bridge.get(field) is not False:
                failures.append(f"governance bridge must keep {field}=false")

    pre_u_governance = loaded.get(PRE_U_GOVERNANCE)
    if pre_u_governance:
        required_fields = [
            "packets_generated",
            "roles_covered",
            "decision_counts",
            "decisions_by_role",
            "dry_run_only",
            "action_executed",
            "cieu_written",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "generated_decision_snapshots",
            "warning",
        ]
        for field in required_fields:
            if field not in pre_u_governance:
                failures.append(f"Pre-U governance summary missing field: {field}")
        if set(pre_u_governance.get("roles_covered", [])) != set(REQUIRED_AGENTS):
            failures.append("Pre-U governance summary must cover required agents")
        if pre_u_governance.get("packets_generated") != len(REQUIRED_AGENTS):
            failures.append("Pre-U governance summary must include three generated packets")
        if pre_u_governance.get("dry_run_only") is not True:
            failures.append("Pre-U governance summary must remain dry_run_only")
        for field in [
            "action_executed",
            "cieu_written",
            "brain_writeback_performed",
            "memory_ingestion_performed",
        ]:
            if pre_u_governance.get(field) is not False:
                failures.append(f"Pre-U governance summary must keep {field}=false")

    labs_acceptance = loaded.get(LABS_ACCEPTANCE)
    if labs_acceptance:
        required_fields = [
            "accepted",
            "checks_passed",
            "checks_total",
            "roles_covered",
            "decision_counts",
            "action_executed",
            "cieu_written",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "raw_runtime_artifacts_ingested",
            "generated_acceptance_report",
            "warning",
        ]
        for field in required_fields:
            if field not in labs_acceptance:
                failures.append(f"labs acceptance summary missing field: {field}")
        if set(labs_acceptance.get("roles_covered", [])) and set(labs_acceptance.get("roles_covered", [])) != set(REQUIRED_AGENTS):
            failures.append("labs acceptance summary must cover required agents when roles are present")
        for field in [
            "action_executed",
            "cieu_written",
            "brain_writeback_performed",
            "memory_ingestion_performed",
            "raw_runtime_artifacts_ingested",
        ]:
            if labs_acceptance.get(field) is not False:
                failures.append(f"labs acceptance summary must keep {field}=false")

    cross_repo_alignment = loaded.get(CROSS_REPO_ALIGNMENT)
    if cross_repo_alignment:
        required_fields = [
            "alignment_accepted",
            "ystar_company_head",
            "ystar_company_head_summary",
            "ystar_gov_head",
            "ystar_gov_head_summary",
            "ystar_gov_endpoint_accepted",
            "labs_runtime_accepted",
            "roles_covered",
            "decision_counts",
            "safety_assertions",
            "generated_manifest",
            "warning",
        ]
        for field in required_fields:
            if field not in cross_repo_alignment:
                failures.append(f"cross-repo alignment summary missing field: {field}")
        roles = set(cross_repo_alignment.get("roles_covered", []))
        if roles and roles != set(REQUIRED_AGENTS):
            failures.append("cross-repo alignment summary must cover required agents when roles are present")
        for name, value in cross_repo_alignment.get("safety_assertions", {}).items():
            if value is not True:
                failures.append(f"cross-repo alignment safety assertion must be true: {name}")

    live_readiness = loaded.get(LIVE_READINESS)
    if live_readiness:
        required_fields = [
            "dry_run_governance_ready",
            "minimal_live_loop_ready",
            "minimal_live_loop_status",
            "recommended_next_phase",
            "live_action_execution_allowed",
            "live_cieu_write_allowed",
            "live_brain_writeback_allowed",
            "live_memory_ingestion_allowed",
            "candidate_auto_approval_allowed",
            "raw_artifact_ingestion_allowed",
            "blockers",
            "transition_backlog_items",
            "generated_report",
            "generated_transition_backlog",
            "warning",
        ]
        for field in required_fields:
            if field not in live_readiness:
                failures.append(f"live readiness summary missing field: {field}")
        if live_readiness.get("minimal_live_loop_ready") is not False:
            failures.append("live readiness summary must keep minimal_live_loop_ready=false")
        if live_readiness.get("minimal_live_loop_status") != "blocked_until_required_gates_exist":
            failures.append("live readiness summary must keep minimal live loop blocked")
        for field in [
            "live_action_execution_allowed",
            "live_cieu_write_allowed",
            "live_brain_writeback_allowed",
            "live_memory_ingestion_allowed",
            "candidate_auto_approval_allowed",
            "raw_artifact_ingestion_allowed",
        ]:
            if live_readiness.get(field) is not False:
                failures.append(f"live readiness summary must keep {field}=false")

    live_boundary = loaded.get(LIVE_BOUNDARY)
    if live_boundary:
        required_fields = [
            "live_boundary_defined",
            "operator_approval_gate_defined",
            "action_sandbox_contract_defined",
            "rollback_policy_defined",
            "cieu_writer_boundary_defined",
            "live_action_execution_enabled",
            "cieu_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "raw_artifact_ingestion_enabled",
            "requires_manual_enablement",
            "minimal_live_loop_ready",
            "blocked_reason",
            "checklist_status_counts",
            "ready_or_enabled_checklist_items",
            "generated_manifest",
            "generated_checklist",
            "warning",
        ]
        for field in required_fields:
            if field not in live_boundary:
                failures.append(f"live boundary summary missing field: {field}")
        for field in [
            "live_boundary_defined",
            "operator_approval_gate_defined",
            "action_sandbox_contract_defined",
            "rollback_policy_defined",
            "cieu_writer_boundary_defined",
            "requires_manual_enablement",
        ]:
            if live_boundary.get(field) is not True:
                failures.append(f"live boundary summary must keep {field}=true")
        for field in [
            "live_action_execution_enabled",
            "cieu_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "raw_artifact_ingestion_enabled",
            "minimal_live_loop_ready",
        ]:
            if live_boundary.get(field) is not False:
                failures.append(f"live boundary summary must keep {field}=false")
        if live_boundary.get("blocked_reason") != "required_live_gates_defined_but_disabled":
            failures.append("live boundary summary blocked reason must remain disabled")
        if live_boundary.get("ready_or_enabled_checklist_items") != 0:
            failures.append("live boundary checklist must not contain ready/enabled items")

    cieu_boundary = loaded.get(CIEU_BOUNDARY)
    if cieu_boundary:
        required_fields = [
            "cieu_runtime_boundary_defined",
            "cieu_runtime_event_schema_defined",
            "prediction_delta_fixture_defined",
            "cieu_writer_policy_defined",
            "dry_run_only",
            "persistence_enabled",
            "live_action_execution_enabled",
            "cieu_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "raw_artifact_ingestion_enabled",
            "requires_manual_enablement",
            "minimal_live_loop_ready",
            "blocked_reason",
            "generated_manifest",
            "generated_sample_event",
            "generated_prediction_delta_fixture",
            "warning",
        ]
        for field in required_fields:
            if field not in cieu_boundary:
                failures.append(f"CIEU boundary summary missing field: {field}")
        for field in [
            "cieu_runtime_boundary_defined",
            "cieu_runtime_event_schema_defined",
            "prediction_delta_fixture_defined",
            "cieu_writer_policy_defined",
            "dry_run_only",
            "requires_manual_enablement",
        ]:
            if cieu_boundary.get(field) is not True:
                failures.append(f"CIEU boundary summary must keep {field}=true")
        for field in [
            "persistence_enabled",
            "live_action_execution_enabled",
            "cieu_write_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "raw_artifact_ingestion_enabled",
            "minimal_live_loop_ready",
        ]:
            if cieu_boundary.get(field) is not False:
                failures.append(f"CIEU boundary summary must keep {field}=false")
        if cieu_boundary.get("blocked_reason") != "cieu_runtime_boundary_defined_but_persistence_disabled":
            failures.append("CIEU boundary summary blocked reason must remain persistence disabled")

    autonomy_inventory = loaded.get(AUTONOMY_INVENTORY)
    if autonomy_inventory:
        required_fields = [
            "company_autonomy_inventory_defined",
            "repo_archaeology_completed",
            "observation_capability_map_defined",
            "resource_sensing_map_defined",
            "action_capability_map_defined",
            "governed_tool_registry_candidates_defined",
            "agent_role_capability_matrix_defined",
            "commercial_agent_company_goal_aligned",
            "governance_only_runtime",
            "live_actions_enabled",
            "external_actions_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "cieu_persistence_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "email_or_external_communication_enabled",
            "requires_manual_enablement",
            "next_required_milestone",
            "generated_summary",
            "generated_report",
            "warning",
        ]
        for field in required_fields:
            if field not in autonomy_inventory:
                failures.append(f"autonomy inventory summary missing field: {field}")
        for field in [
            "company_autonomy_inventory_defined",
            "repo_archaeology_completed",
            "observation_capability_map_defined",
            "resource_sensing_map_defined",
            "action_capability_map_defined",
            "governed_tool_registry_candidates_defined",
            "agent_role_capability_matrix_defined",
            "commercial_agent_company_goal_aligned",
            "requires_manual_enablement",
        ]:
            if autonomy_inventory.get(field) is not True:
                failures.append(f"autonomy inventory summary must keep {field}=true")
        for field in [
            "governance_only_runtime",
            "live_actions_enabled",
            "external_actions_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "cieu_persistence_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "email_or_external_communication_enabled",
        ]:
            if autonomy_inventory.get(field) is not False:
                failures.append(f"autonomy inventory summary must keep {field}=false")
        if autonomy_inventory.get("next_required_milestone") != "L4.2 Company Autonomous Work Cycle Simulator v0":
            failures.append("autonomy inventory summary must point to L4.2 simulator milestone")

    print(f"Team Console CLI validate-local: {'PASS' if not failures else 'FAIL'}")
    print(f"Generated JSON files inspected: {len(inspected)}")
    print(f"Required agents: {', '.join(REQUIRED_AGENTS)}")
    if failures:
        print()
        print("Failures:")
        bullet_list(failures)
        return 1
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(usage())
        return 1

    command = argv[1]
    if command == "validate-local":
        return cmd_validate_local()

    try:
        data = load_all()
    except Exception as exc:
        print(f"Failed to load generated snapshots: {exc}")
        return 1

    if command == "summary":
        cmd_summary(data)
    elif command == "agents":
        cmd_agents(data)
    elif command == "agent":
        if len(argv) != 3:
            print("Usage: agent <agent_id>")
            return 1
        return cmd_agent(data, argv[2])
    elif command == "readiness":
        cmd_readiness(data)
    elif command == "capabilities":
        cmd_capabilities(data)
    elif command == "governance":
        cmd_governance(data)
    elif command == "quarantine":
        cmd_quarantine(data)
    elif command == "mining-candidates":
        cmd_mining_candidates(data)
    elif command == "review-queue":
        cmd_review_queue(data)
    elif command == "artifact-disposition":
        cmd_artifact_disposition(data)
    elif command == "evidence-review":
        cmd_evidence_review(data)
    elif command == "governance-bridge":
        cmd_governance_bridge(data)
    elif command == "pre-u-governance":
        cmd_pre_u_governance(data)
    elif command == "labs-acceptance":
        cmd_labs_acceptance(data)
    elif command == "cross-repo-alignment":
        cmd_cross_repo_alignment(data)
    elif command == "live-readiness":
        cmd_live_readiness(data)
    elif command == "live-boundary":
        cmd_live_boundary(data)
    elif command == "cieu-boundary":
        cmd_cieu_boundary(data)
    elif command == "autonomy-inventory":
        cmd_autonomy_inventory(data)
    elif command == "gaps":
        cmd_gaps(data)
    elif command == "sources":
        cmd_sources(data)
    elif command == "warnings":
        cmd_warnings(data)
    else:
        print(f"Invalid command: {command}")
        print(usage())
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
