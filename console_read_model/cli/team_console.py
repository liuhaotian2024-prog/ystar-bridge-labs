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
AUTONOMOUS_CYCLE = "console_read_model/generated/autonomous_cycle_summary.json"
LEGACY_TRIAGE = "console_read_model/generated/legacy_triage_summary.json"
OBSERVATION_LOOP = "console_read_model/generated/observation_loop_summary.json"
READONLY_TOOL = "console_read_model/generated/readonly_tool_summary.json"
TOOL_BRIDGE = "console_read_model/generated/tool_bridge_summary.json"
WORK_PROPOSAL = "console_read_model/generated/work_proposal_summary.json"
DASHBOARD_REFRESH = "console_read_model/generated/dashboard_refresh_summary.json"
RECURRING_LOOP = "console_read_model/generated/recurring_loop_summary.json"
MANUAL_TICK = "console_read_model/generated/manual_tick_summary.json"
FIELD_FUNCTIONAL = "console_read_model/generated/field_functional_summary.json"
MISSION_PROJECTION = "console_read_model/generated/mission_projection_summary.json"
FIELD_PROJECTION = "console_read_model/generated/field_projection_summary.json"
PROJECTION_CYCLE = "console_read_model/generated/projection_cycle_summary.json"
SHADOW_LEARNING_CYCLE = "console_read_model/generated/shadow_learning_cycle_summary.json"
CROSS_REPO_GOVERNANCE = "console_read_model/generated/cross_repo_governance_summary.json"
GOVERNED_MCP_ADAPTER = "console_read_model/generated/governed_mcp_adapter_summary.json"
CONTROLLED_CANONICAL_LEARNING = (
    "console_read_model/generated/controlled_canonical_learning_summary.json"
)
APPROVED_SANDBOX_UPDATE = "console_read_model/generated/approved_sandbox_update_summary.json"
REAL_APPROVAL_WORKFLOW = "console_read_model/generated/real_approval_workflow_summary.json"
APPROVAL_RECORD_SANDBOX = "console_read_model/generated/approval_record_sandbox_summary.json"
REAL_RELEASE_PREFLIGHT = "console_read_model/generated/real_release_preflight_summary.json"
REAL_RELEASE_SIMULATION = "console_read_model/generated/real_release_simulation_summary.json"
LIVE_BOUNDARY_NO_GO = "console_read_model/generated/live_boundary_no_go_summary.json"
L6_META_DEVELOPMENT = "console_read_model/generated/l6_meta_development_summary.json"
L6_MVP_ARTIFACT_SANDBOX = (
    "console_read_model/generated/l6_mvp_artifact_sandbox_summary.json"
)
L6_EXTERNAL_OBSERVATION_BOUNDARY = (
    "console_read_model/generated/l6_external_observation_boundary_summary.json"
)
L6_CONTROLLED_OBSERVATION_SANDBOX = (
    "console_read_model/generated/l6_controlled_observation_sandbox_summary.json"
)
L6_REAL_OBSERVATION_PREFLIGHT = (
    "console_read_model/generated/l6_real_observation_preflight_summary.json"
)
L6_PILOT_DESIGN = "console_read_model/generated/l6_pilot_design_summary.json"
L6_PILOT_APPROVAL = "console_read_model/generated/l6_pilot_approval_summary.json"
L6_INTEGRATED_PILOT_READINESS = (
    "console_read_model/generated/l6_integrated_pilot_readiness_summary.json"
)
L6_AGENTIC_EVIDENCE = "console_read_model/generated/l6_agentic_evidence_summary.json"
L6_AGENTIC_PILOT_DRY_RUN = (
    "console_read_model/generated/l6_agentic_pilot_dry_run_summary.json"
)
L6_TINY_OBSERVATION_PILOT = (
    "console_read_model/generated/l6_tiny_observation_pilot_summary.json"
)
L6_10R_LOCATOR_RETRY = (
    "console_read_model/generated/l6_10r_locator_retry_summary.json"
)
L6_10T_TOOLMAKING_LOCATOR_RESOLVER = (
    "console_read_model/generated/l6_10t_toolmaking_locator_resolver_summary.json"
)
L6_10U_LOCATOR_RESOLVER_ENABLEMENT = (
    "console_read_model/generated/l6_10u_locator_resolver_enablement_summary.json"
)
L6_10V_SEED_OR_SEARCH_RESOLVER_ENABLEMENT = (
    "console_read_model/generated/l6_10v_seed_or_search_resolver_enablement_summary.json"
)
L6_10W_REVIEWED_SEED_LOCATOR_INJECTION = (
    "console_read_model/generated/l6_10w_reviewed_seed_locator_injection_summary.json"
)
L6_10X_BUDGETED_CONTROLLED_SEARCH_EVIDENCE = (
    "console_read_model/generated/l6_10x_budgeted_controlled_search_evidence_summary.json"
)
L6_11_CONTROLLED_BACKEND_PAGE_READ_ENABLEMENT = (
    "console_read_model/generated/l6_11_controlled_backend_page_read_enablement_summary.json"
)
L6_12_UNIFIED_CONTROLLED_EXTERNAL_OBSERVATION = (
    "console_read_model/generated/l6_12_unified_controlled_external_observation_evidence_loop_summary.json"
)
L6_13_REAL_CONTROLLED_EXTERNAL_OBSERVATION_MISSION = (
    "console_read_model/generated/l6_13_real_controlled_external_observation_mission_sprint_summary.json"
)
L6_14_REAL_EVIDENCE_CONFLICT_RESOLUTION = (
    "console_read_model/generated/l6_14_real_evidence_conflict_resolution_sprint_summary.json"
)
L6_15_HUMAN_REVIEW_DECISION_BOUNDARY = (
    "console_read_model/generated/l6_15_human_review_decision_boundary_sprint_summary.json"
)
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
        "{summary|agents|agent <agent_id>|readiness|capabilities|governance|quarantine|mining-candidates|review-queue|artifact-disposition|evidence-review|governance-bridge|pre-u-governance|labs-acceptance|cross-repo-alignment|live-readiness|live-boundary|cieu-boundary|autonomy-inventory|autonomous-cycle|legacy-triage|observation-loop|readonly-tool|tool-bridge|work-proposal|dashboard-refresh|recurring-loop|manual-tick|field-functional|mission-projection|field-projection|projection-cycle|shadow-learning-cycle|cross-repo-governance|governed-mcp-adapter|controlled-canonical-learning|approved-sandbox-update|real-approval-boundary|approval-record-sandbox|real-release-preflight|release-simulation-sandbox|live-boundary-no-go|meta-development-design|meta-development-mvp-artifact-sandbox|governed-external-observation-boundary|controlled-external-observation-sandbox|real-read-only-observation-preflight|controlled-real-read-only-observation-pilot-design|controlled-observation-pilot-approval-packet|integrated-approval-record-and-pilot-readiness|agentic-evidence-discovery-trust-engine|controlled-agentic-evidence-pilot-approval-dry-run|tiny-real-read-only-agentic-evidence-observation-pilot|controlled-source-locator-resolution-tiny-observation-retry|governed-capability-gap-toolmaking-locator-resolver|controlled-locator-resolver-enable-first-attempt|controlled-seed-locator-or-search-resolver-enablement|reviewed-seed-locator-injection-tiny-retry|budgeted-controlled-external-search-evidence-pilot|controlled-search-backend-page-read-enablement|unified-controlled-external-observation-evidence-loop|real-controlled-external-observation-mission-sprint|real-evidence-conflict-resolution-sprint|human-review-decision-boundary-sprint|gaps|sources|warnings|validate-local}"
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
        "autonomous_cycle": load_json(AUTONOMOUS_CYCLE),
        "legacy_triage": load_json(LEGACY_TRIAGE),
        "observation_loop": load_json(OBSERVATION_LOOP),
        "readonly_tool": load_json(READONLY_TOOL),
        "tool_bridge": load_json(TOOL_BRIDGE),
        "work_proposal": load_json(WORK_PROPOSAL),
        "dashboard_refresh": load_json(DASHBOARD_REFRESH),
        "recurring_loop": load_json(RECURRING_LOOP),
        "manual_tick": load_json(MANUAL_TICK),
        "field_functional": load_json(FIELD_FUNCTIONAL),
        "mission_projection": load_json(MISSION_PROJECTION),
        "field_projection": load_json(FIELD_PROJECTION),
        "projection_cycle": load_json(PROJECTION_CYCLE),
        "shadow_learning_cycle": load_json(SHADOW_LEARNING_CYCLE),
        "cross_repo_governance": load_json(CROSS_REPO_GOVERNANCE),
        "governed_mcp_adapter": load_json(GOVERNED_MCP_ADAPTER),
        "controlled_canonical_learning": load_json(CONTROLLED_CANONICAL_LEARNING),
        "approved_sandbox_update": load_json(APPROVED_SANDBOX_UPDATE),
        "real_approval_workflow": load_json(REAL_APPROVAL_WORKFLOW),
        "approval_record_sandbox": load_json(APPROVAL_RECORD_SANDBOX),
        "real_release_preflight": load_json(REAL_RELEASE_PREFLIGHT),
        "real_release_simulation": load_json(REAL_RELEASE_SIMULATION),
        "live_boundary_no_go": load_json(LIVE_BOUNDARY_NO_GO),
        "l6_meta_development": load_json(L6_META_DEVELOPMENT),
        "l6_mvp_artifact_sandbox": load_json(L6_MVP_ARTIFACT_SANDBOX),
        "l6_external_observation_boundary": load_json(L6_EXTERNAL_OBSERVATION_BOUNDARY),
        "l6_controlled_observation_sandbox": load_json(L6_CONTROLLED_OBSERVATION_SANDBOX),
        "l6_real_observation_preflight": load_json(L6_REAL_OBSERVATION_PREFLIGHT),
        "l6_pilot_design": load_json(L6_PILOT_DESIGN),
        "l6_pilot_approval": load_json(L6_PILOT_APPROVAL),
        "l6_integrated_pilot_readiness": load_json(L6_INTEGRATED_PILOT_READINESS),
        "l6_agentic_evidence": load_json(L6_AGENTIC_EVIDENCE),
        "l6_agentic_pilot_dry_run": load_json(L6_AGENTIC_PILOT_DRY_RUN),
        "l6_tiny_observation_pilot": load_json(L6_TINY_OBSERVATION_PILOT),
        "l6_10r_locator_retry": load_json(L6_10R_LOCATOR_RETRY),
        "l6_10t_toolmaking_locator_resolver": load_json(L6_10T_TOOLMAKING_LOCATOR_RESOLVER),
        "l6_10u_locator_resolver_enablement": load_json(L6_10U_LOCATOR_RESOLVER_ENABLEMENT),
        "l6_10v_seed_or_search_resolver_enablement": load_json(
            L6_10V_SEED_OR_SEARCH_RESOLVER_ENABLEMENT
        ),
        "l6_10w_reviewed_seed_locator_injection": load_json(
            L6_10W_REVIEWED_SEED_LOCATOR_INJECTION
        ),
        "l6_10x_budgeted_controlled_search_evidence": load_json(
            L6_10X_BUDGETED_CONTROLLED_SEARCH_EVIDENCE
        ),
        "l6_11_controlled_backend_page_read_enablement": load_json(
            L6_11_CONTROLLED_BACKEND_PAGE_READ_ENABLEMENT
        ),
        "l6_12_unified_controlled_observation": load_json(
            L6_12_UNIFIED_CONTROLLED_EXTERNAL_OBSERVATION
        ),
        "l6_13_real_controlled_observation_mission": load_json(
            L6_13_REAL_CONTROLLED_EXTERNAL_OBSERVATION_MISSION
        ),
        "l6_14_real_evidence_conflict_resolution": load_json(
            L6_14_REAL_EVIDENCE_CONFLICT_RESOLUTION
        ),
        "l6_15_human_review_decision_boundary": load_json(
            L6_15_HUMAN_REVIEW_DECISION_BOUNDARY
        ),
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


def cmd_autonomous_cycle(data: dict[str, Any]) -> None:
    cycle = data["autonomous_cycle"]
    print("# Company Autonomous Work Cycle")
    print()
    print(f"mission-bounded autonomy defined: {cycle.get('mission_bounded_autonomy_defined')}")
    print(f"founder sets mission, agent team drives: {cycle.get('founder_sets_mission_agent_team_drives')}")
    print(f"step-by-step human prompting required: {cycle.get('step_by_step_human_prompting_required')}")
    print(f"observation snapshot defined: {cycle.get('observation_snapshot_defined')}")
    print(f"autonomous work backlog defined: {cycle.get('autonomous_work_backlog_defined')}")
    print(f"selected work item defined: {cycle.get('selected_work_item_defined')}")
    print(f"role delegation defined: {cycle.get('role_delegation_defined')}")
    print(f"governed tool selection defined: {cycle.get('governed_tool_selection_defined')}")
    print(f"Pre-U packet simulated: {cycle.get('pre_u_packet_simulated')}")
    print(f"governance decision simulated: {cycle.get('governance_decision_simulated')}")
    print(f"action plan simulated: {cycle.get('action_plan_simulated')}")
    print(f"CIEU event simulated: {cycle.get('cieu_event_simulated')}")
    print(f"residual delta simulated: {cycle.get('residual_delta_simulated')}")
    print(f"real action executed: {cycle.get('real_action_executed')}")
    print(f"live action enabled: {cycle.get('live_action_enabled')}")
    print(f"external action executed: {cycle.get('external_action_executed')}")
    print(f"CIEU persistence enabled: {cycle.get('cieu_persistence_enabled')}")
    print(f"brain writeback enabled: {cycle.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {cycle.get('memory_ingestion_enabled')}")
    print(f"next required milestone: {cycle.get('next_required_milestone')}")
    print(f"generated_summary: {cycle.get('generated_summary')}")
    print(f"generated_report: {cycle.get('generated_report')}")
    print(f"warning: {cycle.get('warning')}")


def cmd_legacy_triage(data: dict[str, Any]) -> None:
    triage = data["legacy_triage"]
    print("# Legacy Asset Triage")
    print()
    print(f"assets scored: {triage.get('assets_scored')}")
    print(f"absorption buckets defined: {triage.get('absorption_buckets_defined')}")
    print(f"top absorption candidates defined: {triage.get('top_absorption_candidates_defined')}")
    print(f"governed absorption backlog defined: {triage.get('governed_absorption_backlog_defined')}")
    print(f"blind absorption allowed: {triage.get('blind_absorption_allowed')}")
    print(f"blanket rewrite allowed: {triage.get('blanket_rewrite_allowed')}")
    print(f"live actions enabled: {triage.get('live_actions_enabled')}")
    print("bucket counts:")
    for bucket, count in sorted(triage.get("bucket_counts", {}).items()):
        print(f"- {bucket}: {count}")
    print(f"next required milestone: {triage.get('next_required_milestone')}")
    print(f"generated_summary: {triage.get('generated_summary')}")
    print(f"generated_report: {triage.get('generated_report')}")
    print(f"warning: {triage.get('warning')}")


def cmd_observation_loop(data: dict[str, Any]) -> None:
    loop = data["observation_loop"]
    print("# Governed Observation Loop")
    print()
    print(f"read-only observation loop defined: {loop.get('read_only_observation_loop_defined')}")
    print(f"observation source registry defined: {loop.get('observation_source_registry_defined')}")
    print(f"observation tick generated: {loop.get('observation_tick_generated')}")
    print(f"mission dashboard snapshot defined: {loop.get('mission_dashboard_snapshot_defined')}")
    print(f"company state digest defined: {loop.get('company_state_digest_defined')}")
    print(f"observation-to-work candidates defined: {loop.get('observation_to_work_item_candidates_defined')}")
    print(f"mission-bounded autonomy supported: {loop.get('mission_bounded_autonomy_supported')}")
    print(f"step-by-step human prompting reduced: {loop.get('step_by_step_human_prompting_reduced')}")
    print(f"real action executed: {loop.get('real_action_executed')}")
    print(f"live action enabled: {loop.get('live_action_enabled')}")
    print(f"external action executed: {loop.get('external_action_executed')}")
    print(f"CIEU persistence enabled: {loop.get('cieu_persistence_enabled')}")
    print(f"brain writeback enabled: {loop.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {loop.get('memory_ingestion_enabled')}")
    print(f"next required milestone: {loop.get('next_required_milestone')}")
    print(f"generated_summary: {loop.get('generated_summary')}")
    print(f"generated_report: {loop.get('generated_report')}")
    print(f"warning: {loop.get('warning')}")


def cmd_readonly_tool(data: dict[str, Any]) -> None:
    tool = data["readonly_tool"]
    print("# Governed Read-Only Observation Tool")
    print()
    print(f"tool contract defined: {tool.get('tool_contract_defined')}")
    print(f"allowed source registry defined: {tool.get('allowed_source_registry_defined')}")
    print(f"sample invocation defined: {tool.get('sample_invocation_defined')}")
    print(f"sample result defined: {tool.get('sample_result_defined')}")
    print(f"unsafe invocation rejected: {tool.get('unsafe_invocation_rejected')}")
    print(f"local read-only dry-run callable: {tool.get('local_readonly_dry_run_callable')}")
    print(f"first governed tool wrapper created: {tool.get('first_governed_tool_wrapper_created')}")
    print(f"real action executed: {tool.get('real_action_executed')}")
    print(f"live action enabled: {tool.get('live_action_enabled')}")
    print(f"external action executed: {tool.get('external_action_executed')}")
    print(f"CIEU persistence enabled: {tool.get('cieu_persistence_enabled')}")
    print(f"brain writeback enabled: {tool.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {tool.get('memory_ingestion_enabled')}")
    print(f"next required milestone: {tool.get('next_required_milestone')}")
    print(f"generated_summary: {tool.get('generated_summary')}")
    print(f"generated_contract: {tool.get('generated_contract')}")
    print(f"generated_registry: {tool.get('generated_registry')}")
    print(f"warning: {tool.get('warning')}")


def cmd_tool_bridge(data: dict[str, Any]) -> None:
    bridge = data["tool_bridge"]
    print("# Governed Tool Invocation Bridge")
    print()
    print(f"bridge contract defined: {bridge.get('bridge_contract_defined')}")
    print(f"agent tool request defined: {bridge.get('agent_tool_request_defined')}")
    print(f"Pre-U tool packet defined: {bridge.get('pre_u_tool_packet_defined')}")
    print(f"governance decision defined: {bridge.get('governance_decision_defined')}")
    print(f"bridge authorization defined: {bridge.get('bridge_authorization_defined')}")
    print(f"tool invoked through bridge: {bridge.get('tool_invoked_through_bridge')}")
    print(f"direct tool invocation rejected: {bridge.get('direct_tool_invocation_rejected')}")
    print(f"unsafe bridge request rejected: {bridge.get('unsafe_bridge_request_rejected')}")
    print(f"bridge CIEU event defined: {bridge.get('bridge_cieu_event_defined')}")
    print(f"bridge residual delta defined: {bridge.get('bridge_residual_delta_defined')}")
    print(
        "first governed tool invocation chain created: "
        f"{bridge.get('first_governed_tool_invocation_chain_created')}"
    )
    print(f"real action executed: {bridge.get('real_action_executed')}")
    print(f"live action enabled: {bridge.get('live_action_enabled')}")
    print(f"external action executed: {bridge.get('external_action_executed')}")
    print(f"CIEU persistence enabled: {bridge.get('cieu_persistence_enabled')}")
    print(f"brain writeback enabled: {bridge.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {bridge.get('memory_ingestion_enabled')}")
    print(f"next required milestone: {bridge.get('next_required_milestone')}")
    print(f"generated_summary: {bridge.get('generated_summary')}")
    print(f"generated_pre_u_packet: {bridge.get('generated_pre_u_packet')}")
    print(f"generated_bridged_result: {bridge.get('generated_bridged_result')}")
    print(f"warning: {bridge.get('warning')}")


def cmd_work_proposal(data: dict[str, Any]) -> None:
    proposal = data["work_proposal"]
    print("# Agent Team Work Proposal")
    print()
    print(f"mission context snapshot defined: {proposal.get('mission_context_snapshot_defined')}")
    print(f"agent team observation input defined: {proposal.get('agent_team_observation_input_defined')}")
    print(f"autonomous work proposals defined: {proposal.get('autonomous_work_proposals_defined')}")
    print(f"selected work proposal defined: {proposal.get('selected_work_proposal_defined')}")
    print(f"role review board defined: {proposal.get('role_review_board_defined')}")
    print(f"tool need analysis defined: {proposal.get('tool_need_analysis_defined')}")
    print(f"generated tool request defined: {proposal.get('generated_tool_request_defined')}")
    print(f"work proposal routed to bridge: {proposal.get('work_proposal_routed_to_bridge')}")
    print(f"direct tool invocation used: {proposal.get('direct_tool_invocation_used')}")
    print(f"bridged tool result reference defined: {proposal.get('bridged_tool_result_ref_defined')}")
    print(f"work proposal CIEU event defined: {proposal.get('work_proposal_cieu_event_defined')}")
    print(f"residual delta defined: {proposal.get('work_proposal_residual_delta_defined')}")
    print(f"agent team generated the work: {proposal.get('agent_team_generated_the_work')}")
    print(f"agent team selected governed tool: {proposal.get('agent_team_selected_governed_tool')}")
    print(f"Pre-U bridge required: {proposal.get('pre_u_bridge_required')}")
    print(f"Pre-U bridge satisfied: {proposal.get('pre_u_bridge_satisfied')}")
    print(f"real action executed: {proposal.get('real_action_executed')}")
    print(f"live action enabled: {proposal.get('live_action_enabled')}")
    print(f"external action executed: {proposal.get('external_action_executed')}")
    print(f"CIEU persistence enabled: {proposal.get('cieu_persistence_enabled')}")
    print(f"brain writeback enabled: {proposal.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {proposal.get('memory_ingestion_enabled')}")
    print(f"next required milestone: {proposal.get('next_required_milestone')}")
    print(f"generated_summary: {proposal.get('generated_summary')}")
    print(f"generated_tool_request: {proposal.get('generated_tool_request')}")
    print(f"generated_bridge_trace: {proposal.get('generated_bridge_trace')}")
    print(f"warning: {proposal.get('warning')}")


def cmd_dashboard_refresh(data: dict[str, Any]) -> None:
    refresh = data["dashboard_refresh"]
    print("# Mission Dashboard Refresh Loop")
    print()
    print(f"refresh loop contract defined: {refresh.get('refresh_loop_contract_defined')}")
    print(f"previous dashboard snapshot defined: {refresh.get('previous_dashboard_snapshot_defined')}")
    print(f"current observation input defined: {refresh.get('current_observation_input_defined')}")
    print(f"refreshed mission dashboard defined: {refresh.get('refreshed_mission_dashboard_defined')}")
    print(f"company state delta defined: {refresh.get('company_state_delta_defined')}")
    print(f"refreshed autonomous backlog defined: {refresh.get('refreshed_autonomous_backlog_defined')}")
    print(f"refresh loop trace defined: {refresh.get('refresh_loop_trace_defined')}")
    print(f"refresh CIEU event defined: {refresh.get('refresh_cieu_event_defined')}")
    print(f"refresh residual delta defined: {refresh.get('refresh_residual_delta_defined')}")
    print(f"dashboard refresh loop ran: {refresh.get('dashboard_refresh_loop_ran')}")
    print(f"scheduler used: {refresh.get('scheduler_used')}")
    print(f"daemon used: {refresh.get('daemon_used')}")
    print(f"manual local run only: {refresh.get('manual_local_run_only')}")
    print(f"real action executed: {refresh.get('real_action_executed')}")
    print(f"live action enabled: {refresh.get('live_action_enabled')}")
    print(f"external action executed: {refresh.get('external_action_executed')}")
    print(f"CIEU persistence enabled: {refresh.get('cieu_persistence_enabled')}")
    print(f"brain writeback enabled: {refresh.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {refresh.get('memory_ingestion_enabled')}")
    print(f"next required milestone: {refresh.get('next_required_milestone')}")
    print(f"generated_summary: {refresh.get('generated_summary')}")
    print(f"generated_refreshed_dashboard: {refresh.get('generated_refreshed_dashboard')}")
    print(f"generated_company_state_delta: {refresh.get('generated_company_state_delta')}")
    print(f"warning: {refresh.get('warning')}")


def cmd_recurring_loop(data: dict[str, Any]) -> None:
    loop = data["recurring_loop"]
    print("# Governed Recurring Observation Loop Contract")
    print()
    print(f"recurring observation loop contract defined: {loop.get('recurring_observation_loop_contract_defined')}")
    print(f"recurrence policy defined: {loop.get('recurrence_policy_defined')}")
    print(f"recurrence enabled: {loop.get('recurrence_enabled')}")
    print(f"scheduler enabled: {loop.get('scheduler_enabled')}")
    print(f"daemon enabled: {loop.get('daemon_enabled')}")
    print(f"auto-run enabled: {loop.get('auto_run_enabled')}")
    print(f"manual local simulation only: {loop.get('manual_local_simulation_only')}")
    print(f"allowed observation sources defined: {loop.get('allowed_observation_sources_defined')}")
    print(f"tick governance gate defined: {loop.get('tick_governance_gate_defined')}")
    print(f"simulated observation tick defined: {loop.get('simulated_observation_tick_defined')}")
    print(f"CIEU tick event defined: {loop.get('simulated_tick_cieu_event_defined')}")
    print(f"residual delta defined: {loop.get('simulated_tick_residual_delta_defined')}")
    print(f"stop/abort conditions defined: {loop.get('stop_abort_conditions_defined')}")
    print(f"escalation conditions defined: {loop.get('escalation_conditions_defined')}")
    print(f"manual enablement checklist defined: {loop.get('manual_enablement_checklist_defined')}")
    print(f"real action executed: {loop.get('real_action_executed')}")
    print(f"live action enabled: {loop.get('live_action_enabled')}")
    print(f"external action executed: {loop.get('external_action_executed')}")
    print(f"CIEU persistence enabled: {loop.get('cieu_persistence_enabled')}")
    print(f"brain writeback enabled: {loop.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {loop.get('memory_ingestion_enabled')}")
    print(f"next required milestone: {loop.get('next_required_milestone')}")
    print(f"generated_summary: {loop.get('generated_summary')}")
    print(f"generated_tick: {loop.get('generated_tick')}")
    print(f"warning: {loop.get('warning')}")


def cmd_manual_tick(data: dict[str, Any]) -> None:
    tick = data["manual_tick"]
    print("# Manual Recurring Observation Tick Runner")
    print()
    print(f"manual tick runner contract defined: {tick.get('manual_tick_runner_contract_defined')}")
    print(f"manual tick request defined: {tick.get('manual_tick_request_defined')}")
    print(f"preflight defined: {tick.get('manual_tick_preflight_defined')}")
    print(f"source validation defined: {tick.get('manual_tick_source_validation_defined')}")
    print(f"governance decision defined: {tick.get('manual_tick_governance_decision_defined')}")
    print(f"manual tick result defined: {tick.get('manual_tick_result_defined')}")
    print(f"dashboard delta defined: {tick.get('manual_tick_dashboard_delta_defined')}")
    print(f"work candidates defined: {tick.get('manual_tick_work_candidates_defined')}")
    print(f"CIEU event defined: {tick.get('manual_tick_cieu_event_defined')}")
    print(f"residual delta defined: {tick.get('manual_tick_residual_delta_defined')}")
    print(f"tick run receipt defined: {tick.get('manual_tick_run_receipt_defined')}")
    print(f"tick history index defined: {tick.get('manual_tick_history_index_defined')}")
    print(f"manual trigger required: {tick.get('manual_trigger_required')}")
    print(f"one tick per invocation: {tick.get('one_tick_per_invocation')}")
    print(f"total recorded ticks: {tick.get('total_recorded_ticks')}")
    print(f"recurrence enabled: {tick.get('recurrence_enabled')}")
    print(f"scheduler enabled: {tick.get('scheduler_enabled')}")
    print(f"daemon enabled: {tick.get('daemon_enabled')}")
    print(f"auto-run enabled: {tick.get('auto_run_enabled')}")
    print(f"manual local run only: {tick.get('manual_local_run_only')}")
    print(f"real action executed: {tick.get('real_action_executed')}")
    print(f"live action enabled: {tick.get('live_action_enabled')}")
    print(f"external action executed: {tick.get('external_action_executed')}")
    print(f"CIEU persistence enabled: {tick.get('cieu_persistence_enabled')}")
    print(f"brain writeback enabled: {tick.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {tick.get('memory_ingestion_enabled')}")
    print(f"next required milestone: {tick.get('next_required_milestone')}")
    print(f"generated_summary: {tick.get('generated_summary')}")
    print(f"generated_result: {tick.get('generated_result')}")
    print(f"generated_receipt: {tick.get('generated_receipt')}")
    print(f"warning: {tick.get('warning')}")


def cmd_field_functional(data: dict[str, Any]) -> None:
    field = data["field_functional"]
    print("# Field Functional Archaeology")
    print()
    print(f"field functional archaeology defined: {field.get('field_functional_archaeology_defined')}")
    print(f"repos scanned: {field.get('repos_scanned')}")
    print(f"assets scanned: {field.get('assets_scanned')}")
    print(f"field functional assets found: {field.get('field_functional_assets_found')}")
    print(f"reuse candidates: {field.get('reuse_candidates_count')}")
    print(f"wrap candidates: {field.get('wrap_candidates_count')}")
    print(f"rewrite candidates: {field.get('rewrite_candidates_count')}")
    print(f"concept references: {field.get('concept_reference_count')}")
    print(f"do-not-absorb candidates: {field.get('do_not_absorb_count')}")
    print(f"mission projection merge plan defined: {field.get('mission_projection_merge_plan_defined')}")
    print(f"ready for L5 projection harness: {field.get('ready_for_L5_projection_harness')}")
    print(f"live action enabled: {field.get('live_action_enabled')}")
    print(f"external action enabled: {field.get('external_action_enabled')}")
    print(f"CIEU persistence enabled: {field.get('cieu_persistence_enabled')}")
    print(f"brain writeback enabled: {field.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {field.get('memory_ingestion_enabled')}")
    print(f"next required milestone: {field.get('next_required_milestone')}")
    print(f"generated_summary: {field.get('generated_summary')}")
    print(f"generated_merge_plan: {field.get('generated_merge_plan')}")
    print(f"warning: {field.get('warning')}")


def cmd_mission_projection(data: dict[str, Any]) -> None:
    projection = data["mission_projection"]
    print("# Mission Field Functional Projection Harness")
    print()
    print(
        "L5.1 projection contract defined: "
        f"{projection.get('l5_1_projection_contract_defined')}"
    )
    print(
        "layered projection trace generated: "
        f"{projection.get('layered_projection_trace_generated')}"
    )
    print(
        "Pre-U adapter candidate generated: "
        f"{projection.get('pre_u_adapter_candidate_generated')}"
    )
    print(
        "residual delta fixture generated: "
        f"{projection.get('residual_delta_fixture_generated')}"
    )
    print(f"action layer projection only: {projection.get('action_layer_projection_only')}")
    print(
        "action field execution implemented: "
        f"{projection.get('action_field_execution_implemented')}"
    )
    print(f"live execution enabled: {projection.get('live_execution_enabled')}")
    print(f"external action enabled: {projection.get('external_action_enabled')}")
    print(f"network enabled: {projection.get('network_enabled')}")
    print(f"scheduler enabled: {projection.get('scheduler_enabled')}")
    print(f"daemon enabled: {projection.get('daemon_enabled')}")
    print(f"CIEU persistence enabled: {projection.get('cieu_persistence_enabled')}")
    print(f"brain writeback enabled: {projection.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {projection.get('memory_ingestion_enabled')}")
    print(
        "ready for L5.2 Field Functional Auto-Projection Core: "
        f"{projection.get('ready_for_L5_2_field_functional_auto_projection_core')}"
    )
    print(
        "Deep Xt is not the L5.2 main milestone: "
        f"{projection.get('deep_xt_model_is_not_l5_2_main_milestone')}"
    )
    print(f"next required milestone: {projection.get('next_required_milestone')}")
    print(f"generated_summary: {projection.get('generated_summary')}")
    print(f"generated_trace: {projection.get('generated_trace')}")
    print(f"generated_pre_u_candidate: {projection.get('generated_pre_u_candidate')}")
    print(f"generated_residual_delta: {projection.get('generated_residual_delta')}")
    print(f"warning: {projection.get('warning')}")


def cmd_field_projection(data: dict[str, Any]) -> None:
    projection = data["field_projection"]
    print("# Field Functional Auto-Projection Core")
    print()
    print(
        "L5.2 field functional auto-projection core defined: "
        f"{projection.get('field_functional_auto_projection_core_defined')}"
    )
    print(
        "mission-level Y* input defined: "
        f"{projection.get('mission_level_y_star_input_defined')}"
    )
    print(
        "mission -> company -> milestone -> session -> task -> behavior projection generated: "
        f"{projection.get('mission_to_behavior_projection_generated')}"
    )
    print(
        "behavior-level Y* candidate generated: "
        f"{projection.get('behavior_level_y_star_candidate_generated')}"
    )
    print(
        "Pre-U packet candidate from behavior Y* generated: "
        f"{projection.get('pre_u_packet_candidate_from_behavior_y_star_generated')}"
    )
    print(
        "residual delta loop fixture generated: "
        f"{projection.get('residual_delta_loop_fixture_generated')}"
    )
    print(
        "learning candidate stub generated but not approved: "
        f"{projection.get('learning_candidate_stub_generated_but_not_approved')}"
    )
    print(f"live execution enabled: {projection.get('live_execution_enabled')}")
    print(f"external action enabled: {projection.get('external_action_enabled')}")
    print(f"network enabled: {projection.get('network_enabled')}")
    print(f"scheduler enabled: {projection.get('scheduler_enabled')}")
    print(f"daemon enabled: {projection.get('daemon_enabled')}")
    print(f"CIEU persistence enabled: {projection.get('cieu_persistence_enabled')}")
    print(f"brain writeback enabled: {projection.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {projection.get('memory_ingestion_enabled')}")
    print(f"behavior execution enabled: {projection.get('behavior_execution_enabled')}")
    print(
        "ready for L5.3 projection-checked autonomous cycle: "
        f"{projection.get('ready_for_l5_3_projection_checked_autonomous_cycle')}"
    )
    print(f"next required milestone: {projection.get('next_required_milestone')}")
    print(f"generated_operator_summary: {projection.get('generated_operator_summary')}")
    print(f"generated_projection_summary: {projection.get('generated_projection_summary')}")
    print(f"generated_pre_u_candidate: {projection.get('generated_pre_u_candidate')}")
    print(f"generated_residual_loop_summary: {projection.get('generated_residual_loop_summary')}")
    print(f"warning: {projection.get('warning')}")


def cmd_projection_cycle(data: dict[str, Any]) -> None:
    cycle = data["projection_cycle"]
    print("# Projection-Checked Autonomous Work Cycle")
    print()
    print(
        "L5.3 projection-checked autonomous work cycle defined: "
        f"{cycle.get('projection_checked_autonomous_work_cycle_defined')}"
    )
    print(
        "behavior-level Y* consumed by cycle: "
        f"{cycle.get('behavior_y_star_consumed_by_cycle')}"
    )
    print(
        "work proposal checked against behavior-level Y*: "
        f"{cycle.get('work_proposal_checked_against_behavior_y_star')}"
    )
    print(
        "Pre-U packet candidate generated: "
        f"{cycle.get('pre_u_packet_candidate_generated')}"
    )
    print(
        "dry-run gate decision generated: "
        f"{cycle.get('dry_run_gate_decision_generated')}"
    )
    print(f"dry-run result generated: {cycle.get('dry_run_result_generated')}")
    print(
        "CIEU-like event fixture generated: "
        f"{cycle.get('cieu_like_event_fixture_generated')}"
    )
    print(f"residual delta generated: {cycle.get('residual_delta_generated')}")
    print(
        "learning review candidate generated but not approved: "
        f"{cycle.get('learning_review_candidate_generated_but_not_approved')}"
    )
    print(f"live execution enabled: {cycle.get('live_execution_enabled')}")
    print(f"behavior execution enabled: {cycle.get('behavior_execution_enabled')}")
    print(f"external action enabled: {cycle.get('external_action_enabled')}")
    print(f"network enabled: {cycle.get('network_enabled')}")
    print(f"scheduler enabled: {cycle.get('scheduler_enabled')}")
    print(f"daemon enabled: {cycle.get('daemon_enabled')}")
    print(f"CIEU persistence enabled: {cycle.get('cieu_persistence_enabled')}")
    print(f"brain writeback enabled: {cycle.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {cycle.get('memory_ingestion_enabled')}")
    print(
        "ready for L5.4 review-gated learning loop: "
        f"{cycle.get('ready_for_l5_4_review_gated_learning_loop')}"
    )
    print(f"next required milestone: {cycle.get('next_required_milestone')}")
    print(f"generated_cycle_summary: {cycle.get('generated_cycle_summary')}")
    print(f"generated_work_summary: {cycle.get('generated_work_summary')}")
    print(f"generated_pre_u_summary: {cycle.get('generated_pre_u_summary')}")
    print(f"generated_residual_summary: {cycle.get('generated_residual_summary')}")
    print(f"generated_learning_summary: {cycle.get('generated_learning_summary')}")
    print(f"warning: {cycle.get('warning')}")


def cmd_shadow_learning_cycle(data: dict[str, Any]) -> None:
    cycle = data["shadow_learning_cycle"]
    print("# Integrated Review-Gated Shadow Learning Cycle")
    print()
    print(
        "L5.4 integrated review-gated shadow learning cycle defined: "
        f"{cycle.get('integrated_review_gated_shadow_learning_cycle_defined')}"
    )
    print(f"L5.3 residual consumed: {cycle.get('l5_3_residual_consumed')}")
    print(
        "deterministic review gate decision generated: "
        f"{cycle.get('deterministic_review_gate_decision_generated')}"
    )
    print(f"review gate decision: {cycle.get('review_gate_decision')}")
    print(
        "learning target classification generated: "
        f"{cycle.get('learning_target_classification_generated')}"
    )
    print(
        "projection policy update candidate generated: "
        f"{cycle.get('projection_policy_update_candidate_generated')}"
    )
    print(
        "shadow projection policy patch generated: "
        f"{cycle.get('shadow_projection_policy_patch_generated')}"
    )
    print(
        "shadow behavior-level Y* preview generated: "
        f"{cycle.get('shadow_behavior_y_star_preview_generated')}"
    )
    print(
        "shadow-updated projection-checked cycle generated: "
        f"{cycle.get('shadow_updated_projection_cycle_generated')}"
    )
    print(
        "original-vs-shadow cycle comparison generated: "
        f"{cycle.get('original_vs_shadow_cycle_comparison_generated')}"
    )
    print(
        "integrated CIEU-like fixture generated: "
        f"{cycle.get('integrated_cieu_like_fixture_generated')}"
    )
    print(f"no candidate approved: {cycle.get('candidate_approved') is False}")
    print(f"no candidate applied: {cycle.get('candidate_applied') is False}")
    print(f"canonical policy mutation enabled: {cycle.get('canonical_policy_mutation_enabled')}")
    print(f"brain writeback enabled: {cycle.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {cycle.get('memory_ingestion_enabled')}")
    print(f"live execution enabled: {cycle.get('live_execution_enabled')}")
    print(f"behavior execution enabled: {cycle.get('behavior_execution_enabled')}")
    print(f"external action enabled: {cycle.get('external_action_enabled')}")
    print(f"network enabled: {cycle.get('network_enabled')}")
    print(f"scheduler enabled: {cycle.get('scheduler_enabled')}")
    print(f"daemon enabled: {cycle.get('daemon_enabled')}")
    print(f"CIEU persistence enabled: {cycle.get('cieu_persistence_enabled')}")
    print(
        "previous residual influenced shadow projection: "
        f"{cycle.get('previous_residual_influenced_shadow_projection')}"
    )
    print(f"shadow learning effect class: {cycle.get('shadow_learning_effect_class')}")
    print(
        "ready for controlled canonical learning design: "
        f"{cycle.get('ready_for_controlled_canonical_learning_design')}"
    )
    print(
        "ready for L6 revenue opportunity discovery: "
        f"{cycle.get('ready_for_l6_revenue_opportunity_discovery')}"
    )
    print(f"next required milestone: {cycle.get('next_required_milestone')}")
    print(f"generated_loop_summary: {cycle.get('generated_loop_summary')}")
    print(f"generated_review_summary: {cycle.get('generated_review_summary')}")
    print(f"generated_shadow_patch_summary: {cycle.get('generated_shadow_patch_summary')}")
    print(f"generated_readiness: {cycle.get('generated_readiness')}")
    print(f"warning: {cycle.get('warning')}")


def cmd_cross_repo_governance(data: dict[str, Any]) -> None:
    proof = data["cross_repo_governance"]
    print("# Cross-Repo Governance Contract Proof")
    print()
    print(
        "L5.5 cross-repo governance contract proof defined: "
        f"{proof.get('cross_repo_governance_contract_proof_defined')}"
    )
    print(
        "Y-star-gov surfaces inventoried read-only: "
        f"{proof.get('y_star_gov_surfaces_inventoried_read_only')}"
    )
    print(
        "gov-mcp surfaces inventoried read-only: "
        f"{proof.get('gov_mcp_surfaces_inventoried_read_only')}"
    )
    print(
        "behavior-level Y* mapped to governance contract expectations: "
        f"{proof.get('behavior_y_star_mapped_to_governance_contract')}"
    )
    print(
        "Pre-U candidates mapped to validator expectations: "
        f"{proof.get('pre_u_candidates_mapped_to_validator_expectations')}"
    )
    print(
        "CIEU/residual artifacts mapped to prediction-delta expectations: "
        f"{proof.get('cieu_fixtures_mapped_to_prediction_delta_expectations')}"
    )
    print(f"gov-mcp boundary mapped: {proof.get('gov_mcp_boundary_mapped')}")
    print(f"non-bypass invariants defined: {proof.get('non_bypass_invariants_defined')}")
    print(f"bypass risks identified: {proof.get('bypass_risks_identified')}")
    print(f"no non-ystar-company repo modified: {proof.get('no_non_ystar_company_repo_modified')}")
    print(f"no MCP server/tool executed: {proof.get('no_mcp_server_or_tool_executed')}")
    print(f"live execution enabled: {proof.get('live_execution_enabled')}")
    print(f"behavior execution enabled: {proof.get('behavior_execution_enabled')}")
    print(f"external action enabled: {proof.get('external_action_enabled')}")
    print(f"network enabled: {proof.get('network_enabled')}")
    print(f"scheduler enabled: {proof.get('scheduler_enabled')}")
    print(f"daemon enabled: {proof.get('daemon_enabled')}")
    print(f"CIEU persistence enabled: {proof.get('cieu_persistence_enabled')}")
    print(f"brain writeback enabled: {proof.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {proof.get('memory_ingestion_enabled')}")
    print(f"canonical policy mutation enabled: {proof.get('canonical_policy_mutation_enabled')}")
    print(f"Y-star-gov modification enabled: {proof.get('y_star_gov_modification_enabled')}")
    print(f"gov-mcp modification enabled: {proof.get('gov_mcp_modification_enabled')}")
    print(f"MCP tool execution enabled: {proof.get('mcp_tool_execution_enabled')}")
    print(
        "ready for L5.6 governed MCP dry-run adapter: "
        f"{proof.get('ready_for_l5_6_governed_mcp_dry_run_adapter')}"
    )
    print(
        "ready for L6 revenue opportunity discovery: "
        f"{proof.get('ready_for_l6_revenue_opportunity_discovery')}"
    )
    print(f"next required milestone: {proof.get('next_required_milestone')}")
    print(f"generated_readiness: {proof.get('generated_readiness')}")
    print(f"warning: {proof.get('warning')}")


def cmd_governed_mcp_adapter(data: dict[str, Any]) -> None:
    adapter = data["governed_mcp_adapter"]
    print("# Governed MCP Dry-Run Adapter")
    print()
    print(
        "L5.6 governed MCP dry-run adapter defined: "
        f"{adapter.get('l5_6_governed_mcp_dry_run_adapter_defined')}"
    )
    print(f"behavior-level Y* loaded: {adapter.get('behavior_y_star_loaded')}")
    print(f"MCP request intent generated: {adapter.get('mcp_request_intent_generated')}")
    print(f"MCP Pre-U packet candidate generated: {adapter.get('mcp_pre_u_packet_candidate_generated')}")
    print(
        "dry-run governance decision envelope generated: "
        f"{adapter.get('dry_run_governance_decision_envelope_generated')}"
    )
    print(f"bridge authorization receipt generated: {adapter.get('bridge_authorization_receipt_generated')}")
    print(f"governed MCP call candidate generated: {adapter.get('governed_mcp_call_candidate_generated')}")
    print(f"real MCP execution blocked: {adapter.get('real_mcp_execution_blocked')}")
    print(f"MCP dry-run receipt generated: {adapter.get('mcp_dry_run_receipt_generated')}")
    print(f"MCP CIEU-like event generated: {adapter.get('mcp_cieu_like_event_generated')}")
    print(f"MCP residual delta generated: {adapter.get('mcp_residual_delta_generated')}")
    print(
        "review-only MCP learning candidate generated: "
        f"{adapter.get('review_only_mcp_learning_candidate_generated')}"
    )
    print(f"Y-star-gov unmodified: {adapter.get('y_star_gov_unmodified')}")
    print(f"gov-mcp unmodified: {adapter.get('gov_mcp_unmodified')}")
    print(f"no MCP server/tool executed: {adapter.get('mcp_server_not_started') and adapter.get('mcp_tool_not_executed')}")
    print(f"MCP resource mutated: {not adapter.get('mcp_resource_not_mutated')}")
    print(f"live execution enabled: {adapter.get('live_execution_enabled')}")
    print(f"behavior execution enabled: {adapter.get('behavior_execution_enabled')}")
    print(f"external action enabled: {adapter.get('external_action_enabled')}")
    print(f"network enabled: {adapter.get('network_enabled')}")
    print(f"scheduler enabled: {adapter.get('scheduler_enabled')}")
    print(f"daemon enabled: {adapter.get('daemon_enabled')}")
    print(f"CIEU persistence enabled: {adapter.get('cieu_persistence_enabled')}")
    print(f"brain writeback enabled: {adapter.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {adapter.get('memory_ingestion_enabled')}")
    print(f"canonical policy mutation enabled: {adapter.get('canonical_policy_mutation_enabled')}")
    print(f"MCP server execution enabled: {adapter.get('mcp_server_execution_enabled')}")
    print(f"MCP tool execution enabled: {adapter.get('mcp_tool_execution_enabled')}")
    print(f"MCP resource mutation enabled: {adapter.get('mcp_resource_mutation_enabled')}")
    print(
        "ready for L5.7 controlled canonical learning design: "
        f"{adapter.get('ready_for_l5_7_controlled_canonical_learning_design')}"
    )
    print(
        "ready for L6 revenue opportunity discovery: "
        f"{adapter.get('ready_for_l6_revenue_opportunity_discovery')}"
    )
    print(f"next required milestone: {adapter.get('next_required_milestone')}")
    print(f"generated_readiness: {adapter.get('generated_readiness')}")
    print(f"warning: {adapter.get('warning')}")


def cmd_controlled_canonical_learning(data: dict[str, Any]) -> None:
    learning = data["controlled_canonical_learning"]
    print("# Controlled Canonical Learning Design")
    print()
    print(
        "L5.7 controlled canonical learning design defined: "
        f"{learning.get('l5_7_controlled_canonical_learning_design_defined')}"
    )
    print(
        "Y* non-mutation invariant defined: "
        f"{learning.get('y_star_non_mutation_invariant_defined')}"
    )
    print(
        "canonical learning target registry generated: "
        f"{learning.get('canonical_learning_target_registry_generated')}"
    )
    print(f"promotion evidence bundle generated: {learning.get('promotion_evidence_bundle_generated')}")
    print(f"promotion eligibility gate generated: {learning.get('promotion_eligibility_gate_generated')}")
    print(
        "canonical update package candidate generated: "
        f"{learning.get('canonical_update_package_candidate_generated')}"
    )
    print(f"versioned patch plan generated: {learning.get('versioned_patch_plan_generated')}")
    print(f"rollback/audit plan generated: {learning.get('rollback_audit_plan_generated')}")
    print(
        "post-promotion validation plan generated: "
        f"{learning.get('post_promotion_validation_plan_generated')}"
    )
    print(f"dry-run promotion fixture generated: {learning.get('dry_run_promotion_fixture_generated')}")
    print(f"no candidate approved: {not learning.get('candidate_approved')}")
    print(f"no candidate applied: {not learning.get('candidate_applied')}")
    print(f"no canonical policy mutation: {not learning.get('canonical_policy_mutation_performed')}")
    print(f"no canonical update application: {not learning.get('canonical_update_application_performed')}")
    print(f"no brain writeback: {not learning.get('brain_writeback_performed')}")
    print(f"no memory ingestion: {not learning.get('memory_ingestion_performed')}")
    print(f"no strategy mutation: {not learning.get('strategy_mutation_performed')}")
    print(f"no Y* direct mutation: {not learning.get('y_star_direct_mutation_performed')}")
    print(f"Y-star-gov unmodified: {learning.get('y_star_gov_unmodified')}")
    print(f"gov-mcp unmodified: {learning.get('gov_mcp_unmodified')}")
    print(f"live execution enabled: {learning.get('live_execution_enabled')}")
    print(f"behavior execution enabled: {learning.get('behavior_execution_enabled')}")
    print(f"external action enabled: {learning.get('external_action_enabled')}")
    print(f"network enabled: {learning.get('network_enabled')}")
    print(f"scheduler enabled: {learning.get('scheduler_enabled')}")
    print(f"daemon enabled: {learning.get('daemon_enabled')}")
    print(f"MCP server execution enabled: {learning.get('mcp_server_execution_enabled')}")
    print(f"MCP tool execution enabled: {learning.get('mcp_tool_execution_enabled')}")
    print(f"CIEU persistence enabled: {learning.get('cieu_persistence_enabled')}")
    print(
        "canonical update application enabled: "
        f"{learning.get('canonical_update_application_enabled')}"
    )
    print(f"Y* direct mutation enabled: {learning.get('y_star_direct_mutation_enabled')}")
    print(
        "ready for L5.8 approved canonical update sandbox: "
        f"{learning.get('ready_for_l5_8_approved_canonical_update_sandbox')}"
    )
    print(
        "ready for L6 revenue opportunity discovery: "
        f"{learning.get('ready_for_l6_revenue_opportunity_discovery')}"
    )
    print(f"next required milestone: {learning.get('next_required_milestone')}")
    print(f"generated_readiness: {learning.get('generated_readiness')}")
    print(f"warning: {learning.get('warning')}")


def cmd_approved_sandbox_update(data: dict[str, Any]) -> None:
    sandbox = data["approved_sandbox_update"]
    print("# Approved Canonical Update Sandbox")
    print()
    print(
        "L5.8 approved canonical update sandbox defined: "
        f"{sandbox.get('l5_8_approved_canonical_update_sandbox_defined')}"
    )
    print(f"sandbox approval fixture generated: {sandbox.get('sandbox_approval_fixture_generated')}")
    print(f"sandbox baseline generated: {sandbox.get('sandbox_baseline_generated')}")
    print(f"sandbox patch applied: {sandbox.get('sandbox_patch_applied')}")
    print(f"real canonical state unchanged: {sandbox.get('real_canonical_state_unchanged')}")
    print(
        "Y* non-mutation invariant preserved: "
        f"{sandbox.get('y_star_non_mutation_invariant_preserved')}"
    )
    print(
        "sandbox post-update validation generated: "
        f"{sandbox.get('sandbox_post_update_validation_generated')}"
    )
    print(
        "sandbox behavior-level Y* reprojection generated: "
        f"{sandbox.get('sandbox_behavior_y_star_reprojection_generated')}"
    )
    print(
        "sandbox governed MCP preview generated: "
        f"{sandbox.get('sandbox_governed_mcp_preview_generated')}"
    )
    print(
        "sandbox update CIEU-like fixture generated: "
        f"{sandbox.get('sandbox_update_cieu_like_fixture_generated')}"
    )
    print(
        "sandbox rollback validation generated: "
        f"{sandbox.get('sandbox_rollback_validation_generated')}"
    )
    print(
        "original-vs-sandbox-vs-rollback comparison generated: "
        f"{sandbox.get('original_vs_sandbox_vs_rollback_comparison_generated')}"
    )
    print(f"no real candidate approval: {not sandbox.get('real_candidate_approved')}")
    print(f"no real candidate application: {not sandbox.get('real_candidate_applied')}")
    print(
        "no real canonical policy mutation: "
        f"{not sandbox.get('real_canonical_policy_mutation_performed')}"
    )
    print(
        "no real canonical update application: "
        f"{not sandbox.get('real_canonical_update_application_performed')}"
    )
    print(f"no brain writeback: {not sandbox.get('brain_writeback_performed')}")
    print(f"no memory ingestion: {not sandbox.get('memory_ingestion_performed')}")
    print(f"no direct Y* mutation: {not sandbox.get('direct_y_star_mutation_performed')}")
    print(f"Y-star-gov unmodified: {sandbox.get('y_star_gov_unmodified')}")
    print(f"gov-mcp unmodified: {sandbox.get('gov_mcp_unmodified')}")
    print(f"live execution enabled: {sandbox.get('live_execution_enabled')}")
    print(f"behavior execution enabled: {sandbox.get('behavior_execution_enabled')}")
    print(f"external action enabled: {sandbox.get('external_action_enabled')}")
    print(f"network enabled: {sandbox.get('network_enabled')}")
    print(f"scheduler enabled: {sandbox.get('scheduler_enabled')}")
    print(f"daemon enabled: {sandbox.get('daemon_enabled')}")
    print(f"MCP server execution enabled: {sandbox.get('mcp_server_execution_enabled')}")
    print(f"MCP tool execution enabled: {sandbox.get('mcp_tool_execution_enabled')}")
    print(f"CIEU persistence enabled: {sandbox.get('cieu_persistence_enabled')}")
    print(
        "ready for L5.9 real approval workflow boundary: "
        f"{sandbox.get('ready_for_l5_9_real_approval_workflow_boundary')}"
    )
    print(
        "ready for L6 revenue opportunity discovery: "
        f"{sandbox.get('ready_for_l6_revenue_opportunity_discovery')}"
    )
    print(f"next required milestone: {sandbox.get('next_required_milestone')}")
    print(f"generated_readiness: {sandbox.get('generated_readiness')}")
    print(f"warning: {sandbox.get('warning')}")


def cmd_real_approval_workflow(data: dict[str, Any]) -> None:
    approval = data["real_approval_workflow"]
    print("# Real Approval Workflow Boundary")
    print()
    print(
        "L5.9 real approval workflow boundary defined: "
        f"{approval.get('l5_9_real_approval_workflow_boundary_defined')}"
    )
    print(f"approval authority model generated: {approval.get('approval_authority_model_generated')}")
    print(f"approval evidence dossier generated: {approval.get('approval_evidence_dossier_generated')}")
    print(
        "durable approval record contract generated: "
        f"{approval.get('durable_approval_record_contract_generated')}"
    )
    print(
        "approval decision packet fixture generated: "
        f"{approval.get('approval_decision_packet_fixture_generated')}"
    )
    print(f"validity/revocation policy generated: {approval.get('validity_revocation_policy_generated')}")
    print(
        "pre-application snapshot policy generated: "
        f"{approval.get('pre_application_snapshot_policy_generated')}"
    )
    print(
        "real application boundary gate generated: "
        f"{approval.get('real_application_boundary_gate_generated')}"
    )
    print(
        "post-approval preflight validation plan generated: "
        f"{approval.get('post_approval_preflight_validation_plan_generated')}"
    )
    print(f"manual approval runbook generated: {approval.get('manual_approval_runbook_generated')}")
    print(
        "approval workflow CIEU-like fixture generated: "
        f"{approval.get('approval_workflow_cieu_like_fixture_generated')}"
    )
    print(f"no real approval granted: {not approval.get('real_approval_granted')}")
    print(f"no real application authorized: {not approval.get('real_application_authorized')}")
    print(
        "no durable approval record written: "
        f"{not approval.get('durable_approval_record_written')}"
    )
    print(
        "no canonical policy mutation: "
        f"{not approval.get('real_canonical_policy_mutation_performed')}"
    )
    print(f"no brain writeback: {not approval.get('brain_writeback_performed')}")
    print(f"no memory ingestion: {not approval.get('memory_ingestion_performed')}")
    print(f"no direct Y* mutation: {not approval.get('direct_y_star_mutation_performed')}")
    print(f"Y-star-gov unmodified: {approval.get('y_star_gov_unmodified')}")
    print(f"gov-mcp unmodified: {approval.get('gov_mcp_unmodified')}")
    print(f"live execution enabled: {approval.get('live_execution_enabled')}")
    print(f"external action enabled: {approval.get('external_action_enabled')}")
    print(f"network enabled: {approval.get('network_enabled')}")
    print(f"scheduler enabled: {approval.get('scheduler_enabled')}")
    print(f"daemon enabled: {approval.get('daemon_enabled')}")
    print(f"MCP server execution enabled: {approval.get('mcp_server_execution_enabled')}")
    print(f"MCP tool execution enabled: {approval.get('mcp_tool_execution_enabled')}")
    print(f"CIEU persistence enabled: {approval.get('cieu_persistence_enabled')}")
    print(
        "durable approval persistence enabled: "
        f"{approval.get('durable_approval_persistence_enabled')}"
    )
    print(
        "ready for L5.10 controlled approval record sandbox: "
        f"{approval.get('ready_for_l5_10_controlled_approval_record_sandbox')}"
    )
    print(
        "ready for L6 revenue opportunity discovery: "
        f"{approval.get('ready_for_l6_revenue_opportunity_discovery')}"
    )
    print(f"next required milestone: {approval.get('next_required_milestone')}")
    print(f"generated_readiness: {approval.get('generated_readiness')}")
    print(f"warning: {approval.get('warning')}")


def cmd_approval_record_sandbox(data: dict[str, Any]) -> None:
    record = data["approval_record_sandbox"]
    print("# Controlled Approval Record Sandbox")
    print()
    print(
        "L5.10 controlled approval record sandbox defined: "
        f"{record.get('l5_10_controlled_approval_record_sandbox_defined')}"
    )
    print(
        "sandbox approval record instance generated: "
        f"{record.get('sandbox_approval_record_instance_generated')}"
    )
    print(f"integrity validation generated: {record.get('integrity_validation_generated')}")
    print(
        "validity state machine replay generated: "
        f"{record.get('validity_state_machine_replay_generated')}"
    )
    print(
        "expired/revoked/tampered/wrong-scope/missing-evidence variants generated and blocked: "
        f"{record.get('expired_revoked_tampered_wrong_scope_missing_evidence_blocked')}"
    )
    print(
        "valid sandbox record gate replay generated: "
        f"{record.get('valid_sandbox_record_gate_replay_generated')}"
    )
    print(
        "invalid record gate blocking generated: "
        f"{record.get('invalid_record_gate_blocking_generated')}"
    )
    print(f"audit lineage generated: {record.get('audit_lineage_generated')}")
    print(
        "approval record CIEU-like fixture generated: "
        f"{record.get('approval_record_cieu_like_fixture_generated')}"
    )
    print(f"no real approval granted: {not record.get('real_approval_granted')}")
    print(
        "no durable approval record written: "
        f"{not record.get('durable_approval_record_written')}"
    )
    print(f"no real application authorized: {not record.get('real_application_authorized')}")
    print(
        "no canonical policy mutation: "
        f"{not record.get('canonical_policy_mutation_performed')}"
    )
    print(f"no brain writeback: {not record.get('brain_writeback_performed')}")
    print(f"no memory ingestion: {not record.get('memory_ingestion_performed')}")
    print(f"no direct Y* mutation: {not record.get('direct_y_star_mutation_performed')}")
    print(f"Y-star-gov unmodified: {record.get('y_star_gov_unmodified')}")
    print(f"gov-mcp unmodified: {record.get('gov_mcp_unmodified')}")
    print(f"live execution enabled: {record.get('live_execution_enabled')}")
    print(f"external action enabled: {record.get('external_action_enabled')}")
    print(f"network enabled: {record.get('network_enabled')}")
    print(f"scheduler enabled: {record.get('scheduler_enabled')}")
    print(f"daemon enabled: {record.get('daemon_enabled')}")
    print(f"MCP server execution enabled: {record.get('mcp_server_execution_enabled')}")
    print(f"MCP tool execution enabled: {record.get('mcp_tool_execution_enabled')}")
    print(f"CIEU persistence enabled: {record.get('cieu_persistence_enabled')}")
    print(
        "durable approval persistence enabled: "
        f"{record.get('durable_approval_persistence_enabled')}"
    )
    print(
        "ready for L5.11 controlled real release preflight: "
        f"{record.get('ready_for_l5_11_controlled_real_release_preflight')}"
    )
    print(
        "ready for L6 revenue opportunity discovery: "
        f"{record.get('ready_for_l6_revenue_opportunity_discovery')}"
    )
    print(f"next required milestone: {record.get('next_required_milestone')}")
    print(f"generated_readiness: {record.get('generated_readiness')}")
    print(f"warning: {record.get('warning')}")


def cmd_real_release_preflight(data: dict[str, Any]) -> None:
    release = data["real_release_preflight"]
    print("# Controlled Real Release Preflight")
    print()
    print(
        "L5.11 controlled real release preflight defined: "
        f"{release.get('l5_11_controlled_real_release_preflight_defined')}"
    )
    print(f"release candidate assembled: {release.get('release_candidate_assembled')}")
    print(
        "release scope validation generated: "
        f"{release.get('release_scope_validation_generated')}"
    )
    print(
        "approval record preflight generated: "
        f"{release.get('approval_record_preflight_generated')}"
    )
    print(
        "snapshot/rollback preflight generated: "
        f"{release.get('snapshot_rollback_preflight_generated')}"
    )
    print(
        "Y* non-mutation preflight generated: "
        f"{release.get('y_star_non_mutation_preflight_generated')}"
    )
    print(
        "MCP non-bypass preflight generated: "
        f"{release.get('mcp_non_bypass_preflight_generated')}"
    )
    print(
        "post-release validation matrix generated: "
        f"{release.get('post_release_validation_matrix_generated')}"
    )
    print(
        "release operator handoff packet generated: "
        f"{release.get('release_operator_handoff_packet_generated')}"
    )
    print(
        "release blocker decision generated: "
        f"{release.get('release_blocker_decision_generated')}"
    )
    print(
        "release preflight CIEU-like fixture generated: "
        f"{release.get('release_preflight_cieu_like_fixture_generated')}"
    )
    print(f"no real approval granted: {not release.get('real_approval_granted')}")
    print(f"no real release authorized: {not release.get('real_release_authorized')}")
    print(
        "no durable approval record written: "
        f"{not release.get('durable_approval_record_written')}"
    )
    print(
        "no canonical policy mutation: "
        f"{not release.get('canonical_policy_mutation_performed')}"
    )
    print(f"no brain writeback: {not release.get('brain_writeback_performed')}")
    print(f"no memory ingestion: {not release.get('memory_ingestion_performed')}")
    print(f"no direct Y* mutation: {not release.get('direct_y_star_mutation_performed')}")
    print(f"Y-star-gov unmodified: {release.get('y_star_gov_unmodified')}")
    print(f"gov-mcp unmodified: {release.get('gov_mcp_unmodified')}")
    print(f"live execution enabled: {release.get('live_execution_enabled')}")
    print(f"external action enabled: {release.get('external_action_enabled')}")
    print(f"network enabled: {release.get('network_enabled')}")
    print(f"scheduler enabled: {release.get('scheduler_enabled')}")
    print(f"daemon enabled: {release.get('daemon_enabled')}")
    print(f"MCP server execution enabled: {release.get('mcp_server_execution_enabled')}")
    print(f"MCP tool execution enabled: {release.get('mcp_tool_execution_enabled')}")
    print(f"CIEU persistence enabled: {release.get('cieu_persistence_enabled')}")
    print(
        "durable approval persistence enabled: "
        f"{release.get('durable_approval_persistence_enabled')}"
    )
    print(
        "ready for L5.12 real release simulation sandbox: "
        f"{release.get('ready_for_l5_12_real_release_simulation_sandbox')}"
    )
    print(
        "ready for L6 revenue opportunity discovery: "
        f"{release.get('ready_for_l6_revenue_opportunity_discovery')}"
    )
    print(f"next required milestone: {release.get('next_required_milestone')}")
    print(f"generated_readiness: {release.get('generated_readiness')}")
    print(f"warning: {release.get('warning')}")


def cmd_release_simulation_sandbox(data: dict[str, Any]) -> None:
    release = data["real_release_simulation"]
    print("# Real Release Simulation Sandbox")
    print()
    print(
        "L5.12 real release simulation sandbox defined: "
        f"{release.get('l5_12_real_release_simulation_sandbox_defined')}"
    )
    print(
        "sandbox release authority fixture generated: "
        f"{release.get('sandbox_release_authority_fixture_generated')}"
    )
    print(
        "simulated durable approval record generated: "
        f"{release.get('simulated_durable_approval_record_generated')}"
    )
    print(f"sandbox snapshot generated: {release.get('sandbox_snapshot_generated')}")
    print(
        "simulated release/rollback operators confirmed: "
        f"{release.get('simulated_release_operator_confirmed') and release.get('simulated_rollback_operator_confirmed')}"
    )
    print(
        "sandbox release execution generated: "
        f"{release.get('sandbox_release_execution_generated')}"
    )
    print(
        "real canonical state unchanged: "
        f"{release.get('real_canonical_state_unchanged')}"
    )
    print(
        "sandbox post-release validation generated: "
        f"{release.get('sandbox_post_release_validation_generated')}"
    )
    print(
        "sandbox behavior-level Y* projection generated: "
        f"{release.get('sandbox_post_release_projection_generated')}"
    )
    print(f"sandbox MCP preview generated: {release.get('sandbox_mcp_preview_generated')}")
    print(
        "sandbox rollback drill generated: "
        f"{release.get('sandbox_rollback_drill_generated')}"
    )
    print(
        "release simulation CIEU-like fixture generated: "
        f"{release.get('release_simulation_cieu_like_fixture_generated')}"
    )
    print(f"no real approval granted: {not release.get('real_approval_granted')}")
    print(f"no real release authorized: {not release.get('real_release_authorized')}")
    print(
        "no durable approval record written: "
        f"{not release.get('durable_approval_record_written')}"
    )
    print(
        "no canonical policy mutation: "
        f"{not release.get('canonical_policy_mutation_performed')}"
    )
    print(f"no brain writeback: {not release.get('brain_writeback_performed')}")
    print(f"no memory ingestion: {not release.get('memory_ingestion_performed')}")
    print(f"no direct Y* mutation: {not release.get('direct_y_star_mutation_performed')}")
    print(f"Y-star-gov unmodified: {release.get('y_star_gov_unmodified')}")
    print(f"gov-mcp unmodified: {release.get('gov_mcp_unmodified')}")
    print(f"live execution enabled: {release.get('live_execution_enabled')}")
    print(f"external action enabled: {release.get('external_action_enabled')}")
    print(f"network enabled: {release.get('network_enabled')}")
    print(f"scheduler enabled: {release.get('scheduler_enabled')}")
    print(f"daemon enabled: {release.get('daemon_enabled')}")
    print(f"MCP server execution enabled: {release.get('mcp_server_execution_enabled')}")
    print(f"MCP tool execution enabled: {release.get('mcp_tool_execution_enabled')}")
    print(f"CIEU persistence enabled: {release.get('cieu_persistence_enabled')}")
    print(
        "durable approval persistence enabled: "
        f"{release.get('durable_approval_persistence_enabled')}"
    )
    print(
        "ready for L5.13 live boundary no-go decision framework: "
        f"{release.get('ready_for_l5_13_live_boundary_no_go_decision_framework')}"
    )
    print(
        "ready for L6 revenue opportunity discovery: "
        f"{release.get('ready_for_l6_revenue_opportunity_discovery')}"
    )
    print(f"next required milestone: {release.get('next_required_milestone')}")
    print(f"generated_readiness: {release.get('generated_readiness')}")
    print(f"warning: {release.get('warning')}")


def cmd_live_boundary_no_go(data: dict[str, Any]) -> None:
    boundary = data["live_boundary_no_go"]
    print("# Live Boundary No-Go Framework")
    print()
    print(
        "L5.13 live boundary no-go framework defined: "
        f"{boundary.get('l5_13_live_boundary_no_go_framework_defined')}"
    )
    print(
        "live capability domains classified: "
        f"{boundary.get('live_capability_domains_classified')}"
    )
    print(f"no-go invariants defined: {boundary.get('no_go_invariants_defined')}")
    print(
        "L5.0-L5.12 evidence indexed: "
        f"{boundary.get('l5_0_to_l5_12_evidence_indexed')}"
    )
    print(f"live blockers identified: {boundary.get('live_blockers_identified')}")
    print(
        "L6 design entry gate generated: "
        f"{boundary.get('l6_design_entry_gate_generated')}"
    )
    print(
        "L6 non-execution boundary defined: "
        f"{boundary.get('l6_non_execution_boundary_defined')}"
    )
    print(
        "L6 forbidden hardcoding policy defined: "
        f"{boundary.get('l6_forbidden_hardcoding_policy_defined')}"
    )
    print(
        "system no-go decision packet generated: "
        f"{boundary.get('system_no_go_decision_packet_generated')}"
    )
    print(
        "live boundary CIEU-like fixture generated: "
        f"{boundary.get('live_boundary_cieu_like_fixture_generated')}"
    )
    print(f"live execution: {boundary.get('live_execution_decision')}")
    print(f"real MCP execution: {boundary.get('real_mcp_execution_decision')}")
    print(f"real canonical update: {boundary.get('real_canonical_update_decision')}")
    print(f"brain/memory writeback: {boundary.get('brain_memory_writeback_decision')}")
    print(f"durable persistence: {boundary.get('durable_persistence_decision')}")
    print(f"real release: {boundary.get('real_release_decision')}")
    print(f"L6 design entry: {boundary.get('l6_design_entry_decision')}")
    print(f"L6 revenue execution: {boundary.get('l6_execution_decision')}")
    print(f"live execution enabled: {boundary.get('live_execution_enabled')}")
    print(f"external action enabled: {boundary.get('external_action_enabled')}")
    print(f"network enabled: {boundary.get('network_enabled')}")
    print(f"scheduler enabled: {boundary.get('scheduler_enabled')}")
    print(f"daemon enabled: {boundary.get('daemon_enabled')}")
    print(f"MCP server execution enabled: {boundary.get('mcp_server_execution_enabled')}")
    print(f"MCP tool execution enabled: {boundary.get('mcp_tool_execution_enabled')}")
    print(f"CIEU persistence enabled: {boundary.get('cieu_persistence_enabled')}")
    print(
        "durable approval persistence enabled: "
        f"{boundary.get('durable_approval_persistence_enabled')}"
    )
    print(f"revenue execution enabled: {boundary.get('revenue_execution_enabled')}")
    print(
        "ready for L6 Meta-Development Generative Engine Design v0: "
        f"{boundary.get('ready_for_l6_meta_development_generative_engine_design')}"
    )
    print(
        "ready for L6 revenue opportunity execution: "
        f"{boundary.get('ready_for_l6_revenue_opportunity_execution')}"
    )
    print(f"generated_readiness: {boundary.get('generated_readiness')}")
    print(f"warning: {boundary.get('warning')}")


def cmd_meta_development_design(data: dict[str, Any]) -> None:
    meta = data["l6_meta_development"]
    print("# L6.0 Meta-Development Generative Selection Engine")
    print()
    print(
        "L6.0 meta-development generative selection engine defined: "
        f"{meta.get('l6_0_meta_development_generative_selection_engine_defined')}"
    )
    print(f"self model generated: {meta.get('self_model_generated')}")
    print(f"unique asset field generated: {meta.get('unique_asset_field_generated')}")
    print(f"world-value field generated: {meta.get('world_value_field_generated')}")
    print(
        "conversion operators generated: "
        f"{meta.get('conversion_operator_library_generated')}"
    )
    print(f"value hypotheses generated: {meta.get('value_hypotheses_generated')}")
    print(f"conversion physics defined: {meta.get('conversion_physics_defined')}")
    print(
        "redeemability selection generated: "
        f"{meta.get('redeemability_selection_generated')}"
    )
    print(
        "MVP proof plans generated: "
        f"{meta.get('minimum_viable_proof_plans_generated')}"
    )
    print(
        "governed experiment portfolio generated: "
        f"{meta.get('governed_experiment_portfolio_generated')}"
    )
    print(
        "strategic residual loop generated: "
        f"{meta.get('strategic_residual_loop_generated')}"
    )
    print(f"L6 is design-only: {meta.get('l6_design_only')}")
    print(f"network enabled: {meta.get('network_enabled')}")
    print(f"external action enabled: {meta.get('external_action_enabled')}")
    print(
        "public content publication enabled: "
        f"{meta.get('public_content_publication_enabled')}"
    )
    print(f"payment enabled: {meta.get('payment_enabled')}")
    print(f"revenue execution enabled: {meta.get('revenue_execution_enabled')}")
    print(
        "hardcoded opportunity categories forbidden: "
        f"{meta.get('hardcoded_opportunity_categories_forbidden')}"
    )
    print(f"examples marked non-exhaustive: {meta.get('seed_examples_non_exhaustive')}")
    print(
        "examples not authorized for execution: "
        f"{meta.get('seed_examples_not_authorized_for_execution')}"
    )
    print(
        "ready for L6.1 MVP artifact sandbox: "
        f"{meta.get('ready_for_l6_1_meta_development_mvp_artifact_sandbox')}"
    )
    print(
        "ready for L6 revenue opportunity execution: "
        f"{meta.get('ready_for_l6_revenue_opportunity_execution')}"
    )
    print(f"next required milestone: {meta.get('next_required_milestone')}")
    print(f"generated_readiness: {meta.get('generated_readiness')}")
    print(f"warning: {meta.get('warning')}")


def cmd_meta_development_mvp_artifact_sandbox(data: dict[str, Any]) -> None:
    sandbox = data["l6_mvp_artifact_sandbox"]
    print("# L6.1 Meta-Development MVP Artifact Sandbox")
    print()
    print(
        "L6.1 MVP artifact sandbox defined: "
        f"{sandbox.get('l6_1_mvp_artifact_sandbox_defined')}"
    )
    print(f"selected hypotheses: {sandbox.get('selected_hypotheses_count')}")
    print(f"generated artifact cases: {sandbox.get('generated_case_count')}")
    print(f"internal artifacts generated: {sandbox.get('internal_artifacts_generated')}")
    print(f"artifact generation authorized: {sandbox.get('artifact_generation_authorized')}")
    print(f"review gate generated: {sandbox.get('review_gate_generated')}")
    print(
        "externalization boundary generated: "
        f"{sandbox.get('externalization_boundary_generated')}"
    )
    print(
        "strategic residual loop generated: "
        f"{sandbox.get('strategic_residual_loop_generated')}"
    )
    print(f"network enabled: {sandbox.get('network_enabled')}")
    print(f"external action enabled: {sandbox.get('external_action_enabled')}")
    print(f"publication enabled: {sandbox.get('publication_enabled')}")
    print(f"outreach enabled: {sandbox.get('outreach_enabled')}")
    print(f"payment enabled: {sandbox.get('payment_enabled')}")
    print(f"revenue execution enabled: {sandbox.get('revenue_execution_enabled')}")
    print(f"MCP tool execution enabled: {sandbox.get('mcp_tool_execution_enabled')}")
    print(f"brain writeback enabled: {sandbox.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {sandbox.get('memory_ingestion_enabled')}")
    print(
        "ready for L6.2 external observation boundary design: "
        f"{sandbox.get('ready_for_l6_2_external_observation_boundary_design')}"
    )
    print(f"ready for external execution: {sandbox.get('ready_for_external_execution')}")
    print(f"ready for publication: {sandbox.get('ready_for_publication')}")
    print(f"ready for outreach: {sandbox.get('ready_for_outreach')}")
    print(f"ready for payment: {sandbox.get('ready_for_payment')}")
    print(f"ready for revenue execution: {sandbox.get('ready_for_revenue_execution')}")
    print(f"next recommended milestone: {sandbox.get('next_recommended_milestone')}")
    print(f"generated_case_index: {sandbox.get('generated_case_index')}")
    print(f"generated_readiness: {sandbox.get('generated_readiness')}")
    print(f"warning: {sandbox.get('warning')}")


def cmd_governed_external_observation_boundary(data: dict[str, Any]) -> None:
    boundary = data["l6_external_observation_boundary"]
    print("# L6.2 Governed External Observation Boundary")
    print()
    print(
        "L6.2 external observation boundary defined: "
        f"{boundary.get('l6_2_external_observation_boundary_defined')}"
    )
    print(f"boundary only: {boundary.get('boundary_only')}")
    print(f"sandbox only: {boundary.get('sandbox_only')}")
    print(
        "Pre-Observation packet schema defined: "
        f"{boundary.get('pre_observation_packet_schema_defined')}"
    )
    print(f"source registry defined: {boundary.get('source_registry_defined')}")
    print(f"permission gate defined: {boundary.get('permission_gate_defined')}")
    print(f"manual import sandbox defined: {boundary.get('manual_import_sandbox_defined')}")
    print(
        "observation-to-artifact linker defined: "
        f"{boundary.get('observation_to_artifact_linker_defined')}"
    )
    print(f"claim boundary policy defined: {boundary.get('claim_boundary_policy_defined')}")
    print(f"no-action receipts generated: {boundary.get('no_action_receipts_generated')}")
    print(
        "strategic residual loop generated: "
        f"{boundary.get('strategic_residual_loop_generated')}"
    )
    print(
        "static fixture generation authorized: "
        f"{boundary.get('static_fixture_generation_authorized')}"
    )
    print(
        "manual evidence import contract authorized: "
        f"{boundary.get('manual_evidence_import_contract_authorized')}"
    )
    print(
        "real external observation authorized: "
        f"{boundary.get('real_external_observation_authorized')}"
    )
    print(f"network enabled: {boundary.get('network_enabled')}")
    print(f"API enabled: {boundary.get('api_enabled')}")
    print(f"scraping enabled: {boundary.get('scraping_enabled')}")
    print(f"browser fetch enabled: {boundary.get('browser_fetch_enabled')}")
    print(f"publication enabled: {boundary.get('publication_enabled')}")
    print(f"outreach enabled: {boundary.get('outreach_enabled')}")
    print(f"payment enabled: {boundary.get('payment_enabled')}")
    print(f"revenue execution enabled: {boundary.get('revenue_execution_enabled')}")
    print(f"MCP tool execution enabled: {boundary.get('mcp_tool_execution_enabled')}")
    print(f"live execution enabled: {boundary.get('live_execution_enabled')}")
    print(f"brain writeback enabled: {boundary.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {boundary.get('memory_ingestion_enabled')}")
    print(
        "ready for L6.3 controlled external observation sandbox: "
        f"{boundary.get('ready_for_l6_3_controlled_external_observation_sandbox')}"
    )
    print(
        "ready for real network observation: "
        f"{boundary.get('ready_for_real_network_observation')}"
    )
    print(f"ready for publication: {boundary.get('ready_for_publication')}")
    print(f"ready for outreach: {boundary.get('ready_for_outreach')}")
    print(f"ready for payment: {boundary.get('ready_for_payment')}")
    print(f"ready for revenue execution: {boundary.get('ready_for_revenue_execution')}")
    print(f"next recommended milestone: {boundary.get('next_recommended_milestone')}")
    print(f"generated_packet_schema: {boundary.get('generated_packet_schema')}")
    print(f"generated_readiness: {boundary.get('generated_readiness')}")


def cmd_controlled_external_observation_sandbox(data: dict[str, Any]) -> None:
    sandbox = data["l6_controlled_observation_sandbox"]
    print("# L6.3 Controlled External Observation Sandbox")
    print()
    print(
        "L6.3 controlled observation sandbox defined: "
        f"{sandbox.get('l6_3_controlled_observation_sandbox_defined')}"
    )
    print(f"sandbox only: {sandbox.get('sandbox_only')}")
    print(f"fixture only: {sandbox.get('fixture_only')}")
    print(
        "static fixture observation authorized: "
        f"{sandbox.get('static_fixture_observation_authorized')}"
    )
    print(
        "manual import fixture authorized: "
        f"{sandbox.get('manual_import_fixture_authorized')}"
    )
    print(f"selected observation cases: {sandbox.get('selected_observation_case_count')}")
    print(f"pre-observation packets: {sandbox.get('pre_observation_packet_count')}")
    print(f"static/manual fixtures: {sandbox.get('static_manual_fixture_count')}")
    print(f"permission replay generated: {sandbox.get('permission_replay_generated')}")
    print(f"evidence validation generated: {sandbox.get('evidence_validation_generated')}")
    print(
        "claim/freshness assessment generated: "
        f"{sandbox.get('claim_freshness_assessment_generated')}"
    )
    print(f"refinement candidates generated: {sandbox.get('refinement_candidates_generated')}")
    print(f"review packets generated: {sandbox.get('review_packets_generated')}")
    print(f"no-action receipts generated: {sandbox.get('no_action_receipts_generated')}")
    print(
        "strategic residual loop generated: "
        f"{sandbox.get('strategic_residual_loop_generated')}"
    )
    print(
        "real external observation authorized: "
        f"{sandbox.get('real_external_observation_authorized')}"
    )
    print(f"network enabled: {sandbox.get('network_enabled')}")
    print(f"API enabled: {sandbox.get('api_enabled')}")
    print(f"scraping enabled: {sandbox.get('scraping_enabled')}")
    print(f"browser fetch enabled: {sandbox.get('browser_fetch_enabled')}")
    print(f"publication enabled: {sandbox.get('publication_enabled')}")
    print(f"outreach enabled: {sandbox.get('outreach_enabled')}")
    print(f"payment enabled: {sandbox.get('payment_enabled')}")
    print(f"revenue execution enabled: {sandbox.get('revenue_execution_enabled')}")
    print(f"MCP tool execution enabled: {sandbox.get('mcp_tool_execution_enabled')}")
    print(f"live execution enabled: {sandbox.get('live_execution_enabled')}")
    print(f"brain writeback enabled: {sandbox.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {sandbox.get('memory_ingestion_enabled')}")
    print(
        "ready for L6.4 real read-only external observation preflight: "
        f"{sandbox.get('ready_for_l6_4_real_read_only_external_observation_preflight')}"
    )
    print(
        "ready for real network observation: "
        f"{sandbox.get('ready_for_real_network_observation')}"
    )
    print(f"ready for scraping: {sandbox.get('ready_for_scraping')}")
    print(f"ready for publication: {sandbox.get('ready_for_publication')}")
    print(f"ready for outreach: {sandbox.get('ready_for_outreach')}")
    print(f"ready for payment: {sandbox.get('ready_for_payment')}")
    print(f"ready for revenue execution: {sandbox.get('ready_for_revenue_execution')}")
    print(f"next recommended milestone: {sandbox.get('next_recommended_milestone')}")
    print(f"generated_selected_cases: {sandbox.get('generated_selected_cases')}")
    print(f"generated_packet_index: {sandbox.get('generated_packet_index')}")
    print(f"generated_fixture_index: {sandbox.get('generated_fixture_index')}")
    print(f"generated_readiness: {sandbox.get('generated_readiness')}")
    print(f"warning: {sandbox.get('warning')}")


def cmd_real_read_only_observation_preflight(data: dict[str, Any]) -> None:
    preflight = data["l6_real_observation_preflight"]
    print("# L6.4 Real Read-Only External Observation Preflight")
    print()
    print(
        "L6.4 real read-only observation preflight defined: "
        f"{preflight.get('l6_4_real_read_only_observation_preflight_defined')}"
    )
    print(f"preflight only: {preflight.get('preflight_only')}")
    print(f"sandbox only: {preflight.get('sandbox_only')}")
    print(
        "future real read-only observation candidate allowed: "
        f"{preflight.get('future_real_read_only_observation_candidate_allowed')}"
    )
    print(f"selected real observation candidates: {preflight.get('candidate_count')}")
    print(f"approval packets: {preflight.get('approval_packet_count')}")
    print(f"preflight requirements: {preflight.get('preflight_requirement_count')}")
    print(f"source allowlist defined: {preflight.get('source_allowlist_defined')}")
    print(f"source denylist defined: {preflight.get('source_denylist_defined')}")
    print(f"operator handoff generated: {preflight.get('operator_handoff_plan_generated')}")
    print(
        "network isolation preflight defined: "
        f"{preflight.get('network_isolation_preflight_defined')}"
    )
    print(
        "evidence capture preflight defined: "
        f"{preflight.get('evidence_capture_preflight_defined')}"
    )
    print(
        "abort/rollback/quarantine policy defined: "
        f"{preflight.get('abort_rollback_quarantine_policy_defined')}"
    )
    print(f"no-action guarantees generated: {preflight.get('no_action_guarantees_generated')}")
    print(f"preflight decision gate generated: {preflight.get('preflight_decision_gate_generated')}")
    print(
        "strategic residual loop generated: "
        f"{preflight.get('strategic_residual_loop_generated')}"
    )
    print(
        "real external observation authorized: "
        f"{preflight.get('real_external_observation_authorized')}"
    )
    print(
        "real observation execution authorized: "
        f"{preflight.get('real_observation_execution_authorized')}"
    )
    print(f"network enabled: {preflight.get('network_enabled')}")
    print(f"API enabled: {preflight.get('api_enabled')}")
    print(f"scraping enabled: {preflight.get('scraping_enabled')}")
    print(f"browser fetch enabled: {preflight.get('browser_fetch_enabled')}")
    print(f"publication enabled: {preflight.get('publication_enabled')}")
    print(f"outreach enabled: {preflight.get('outreach_enabled')}")
    print(f"payment enabled: {preflight.get('payment_enabled')}")
    print(f"revenue execution enabled: {preflight.get('revenue_execution_enabled')}")
    print(f"MCP tool execution enabled: {preflight.get('mcp_tool_execution_enabled')}")
    print(f"live execution enabled: {preflight.get('live_execution_enabled')}")
    print(f"CIEU DB write enabled: {preflight.get('cieu_db_write_enabled')}")
    print(f"brain writeback enabled: {preflight.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {preflight.get('memory_ingestion_enabled')}")
    print(
        "ready for L6.5 controlled real read-only observation pilot design: "
        f"{preflight.get('ready_for_l6_5_controlled_real_read_only_observation_pilot_design')}"
    )
    print(
        "ready for actual network observation now: "
        f"{preflight.get('ready_for_actual_network_observation_now')}"
    )
    print(f"ready for scraping: {preflight.get('ready_for_scraping')}")
    print(f"ready for publication: {preflight.get('ready_for_publication')}")
    print(f"ready for outreach: {preflight.get('ready_for_outreach')}")
    print(f"ready for payment: {preflight.get('ready_for_payment')}")
    print(f"ready for revenue execution: {preflight.get('ready_for_revenue_execution')}")
    print(f"next recommended milestone: {preflight.get('next_recommended_milestone')}")
    print(f"generated_selected_candidates: {preflight.get('generated_selected_candidates')}")
    print(f"generated_approval_packets: {preflight.get('generated_approval_packets')}")
    print(f"generated_decision_gate: {preflight.get('generated_decision_gate')}")
    print(f"generated_readiness: {preflight.get('generated_readiness')}")
    print(f"warning: {preflight.get('warning')}")


def cmd_controlled_real_read_only_observation_pilot_design(data: dict[str, Any]) -> None:
    pilot = data["l6_pilot_design"]
    print("# L6.5 Controlled Real Read-Only Observation Pilot Design")
    print()
    print(
        "L6.5 controlled real read-only observation pilot design defined: "
        f"{pilot.get('l6_5_controlled_real_read_only_observation_pilot_design_defined')}"
    )
    print(f"pilot design only: {pilot.get('pilot_design_only')}")
    print(f"preflight only: {pilot.get('preflight_only')}")
    print(
        "future real read-only observation pilot candidate allowed: "
        f"{pilot.get('future_real_read_only_observation_pilot_candidate_allowed')}"
    )
    print(f"selected pilot candidates: {pilot.get('candidate_count')}")
    print(f"approval packet candidates: {pilot.get('approval_packet_count')}")
    print(f"pilot scope defined: {pilot.get('pilot_scope_defined')}")
    print(f"pilot source constraints defined: {pilot.get('pilot_source_constraints_defined')}")
    print(
        "pilot approval packet candidates generated: "
        f"{pilot.get('pilot_approval_packet_candidates_generated')}"
    )
    print(f"operator runbook generated: {pilot.get('pilot_operator_runbook_generated')}")
    print(
        "evidence packet templates generated: "
        f"{pilot.get('pilot_evidence_packet_templates_generated')}"
    )
    print(
        "post-observation review workflow defined: "
        f"{pilot.get('post_observation_review_workflow_defined')}"
    )
    print(f"abort/quarantine policy defined: {pilot.get('abort_quarantine_policy_defined')}")
    print(f"success/failure criteria defined: {pilot.get('success_failure_criteria_defined')}")
    print(f"no-action guarantees generated: {pilot.get('no_action_guarantees_generated')}")
    print(f"pilot design decision gate generated: {pilot.get('pilot_design_decision_gate_generated')}")
    print(
        "real external observation authorized: "
        f"{pilot.get('real_external_observation_authorized')}"
    )
    print(f"real pilot execution authorized: {pilot.get('real_pilot_execution_authorized')}")
    print(f"network enabled: {pilot.get('network_enabled')}")
    print(f"API enabled: {pilot.get('api_enabled')}")
    print(f"scraping enabled: {pilot.get('scraping_enabled')}")
    print(f"browser fetch enabled: {pilot.get('browser_fetch_enabled')}")
    print(f"search enabled: {pilot.get('search_enabled')}")
    print(f"publication enabled: {pilot.get('publication_enabled')}")
    print(f"outreach enabled: {pilot.get('outreach_enabled')}")
    print(f"payment enabled: {pilot.get('payment_enabled')}")
    print(f"revenue execution enabled: {pilot.get('revenue_execution_enabled')}")
    print(f"MCP tool execution enabled: {pilot.get('mcp_tool_execution_enabled')}")
    print(f"live execution enabled: {pilot.get('live_execution_enabled')}")
    print(f"CIEU DB write enabled: {pilot.get('cieu_db_write_enabled')}")
    print(f"brain writeback enabled: {pilot.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {pilot.get('memory_ingestion_enabled')}")
    print(
        "ready for L6.6 controlled real read-only observation pilot approval packet: "
        f"{pilot.get('ready_for_l6_6_controlled_real_read_only_observation_pilot_approval_packet')}"
    )
    print(
        "ready for actual network observation now: "
        f"{pilot.get('ready_for_actual_network_observation_now')}"
    )
    print(f"ready for scraping: {pilot.get('ready_for_scraping')}")
    print(f"ready for publication: {pilot.get('ready_for_publication')}")
    print(f"ready for outreach: {pilot.get('ready_for_outreach')}")
    print(f"ready for payment: {pilot.get('ready_for_payment')}")
    print(f"ready for revenue execution: {pilot.get('ready_for_revenue_execution')}")
    print(f"next recommended milestone: {pilot.get('next_recommended_milestone')}")
    print(f"generated_selected_candidates: {pilot.get('generated_selected_candidates')}")
    print(f"generated_approval_packets: {pilot.get('generated_approval_packets')}")
    print(f"generated_operator_runbook: {pilot.get('generated_operator_runbook')}")
    print(f"generated_evidence_template: {pilot.get('generated_evidence_template')}")
    print(f"generated_decision_gate: {pilot.get('generated_decision_gate')}")
    print(f"generated_readiness: {pilot.get('generated_readiness')}")
    print(f"warning: {pilot.get('warning')}")


def cmd_controlled_observation_pilot_approval_packet(data: dict[str, Any]) -> None:
    approval = data["l6_pilot_approval"]
    print("# L6.6 Controlled Observation Pilot Approval Packet")
    print()
    print(
        "L6.6 controlled observation pilot approval packet defined: "
        f"{approval.get('l6_6_controlled_observation_pilot_approval_packet_defined')}"
    )
    print(f"approval packet only: {approval.get('approval_packet_only')}")
    print(f"approval sandbox only: {approval.get('approval_sandbox_only')}")
    print(
        "future real read-only observation pilot candidate allowed: "
        f"{approval.get('future_real_read_only_observation_pilot_candidate_allowed')}"
    )
    print(f"approval candidates: {approval.get('approval_candidate_count')}")
    print(f"approval packets: {approval.get('approval_packet_count')}")
    print(f"evidence dossiers: {approval.get('evidence_dossier_count')}")
    print(f"risk reviews: {approval.get('risk_review_count')}")
    print(f"approval authority model generated: {approval.get('approval_authority_model_generated')}")
    print(f"approval packet instances generated: {approval.get('approval_packet_instances_generated')}")
    print(f"evidence dossiers generated: {approval.get('evidence_dossiers_generated')}")
    print(f"risk reviews generated: {approval.get('risk_reviews_generated')}")
    print(
        "operator authorization prerequisites generated: "
        f"{approval.get('operator_authorization_prerequisites_generated')}"
    )
    print(
        "runtime isolation attestation templates generated: "
        f"{approval.get('runtime_isolation_attestation_templates_generated')}"
    )
    print(
        "evidence capture authorization templates generated: "
        f"{approval.get('evidence_capture_authorization_templates_generated')}"
    )
    print(f"no-action constraints generated: {approval.get('no_action_constraints_generated')}")
    print(f"approval decision sandbox generated: {approval.get('approval_decision_sandbox_generated')}")
    print(f"non-persistence receipts generated: {approval.get('non_persistence_receipts_generated')}")
    print(f"real approval granted: {approval.get('real_approval_granted')}")
    print(
        "durable real approval record created: "
        f"{approval.get('durable_real_approval_record_created')}"
    )
    print(
        "real external observation authorized: "
        f"{approval.get('real_external_observation_authorized')}"
    )
    print(f"real pilot execution authorized: {approval.get('real_pilot_execution_authorized')}")
    print(f"network enabled: {approval.get('network_enabled')}")
    print(f"API enabled: {approval.get('api_enabled')}")
    print(f"scraping enabled: {approval.get('scraping_enabled')}")
    print(f"browser fetch enabled: {approval.get('browser_fetch_enabled')}")
    print(f"search enabled: {approval.get('search_enabled')}")
    print(f"publication enabled: {approval.get('publication_enabled')}")
    print(f"outreach enabled: {approval.get('outreach_enabled')}")
    print(f"payment enabled: {approval.get('payment_enabled')}")
    print(f"revenue execution enabled: {approval.get('revenue_execution_enabled')}")
    print(f"MCP tool execution enabled: {approval.get('mcp_tool_execution_enabled')}")
    print(f"live execution enabled: {approval.get('live_execution_enabled')}")
    print(f"CIEU DB write enabled: {approval.get('cieu_db_write_enabled')}")
    print(f"brain writeback enabled: {approval.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {approval.get('memory_ingestion_enabled')}")
    print(
        "ready for L6.7 controlled real read-only observation approval record sandbox: "
        f"{approval.get('ready_for_l6_7_controlled_real_read_only_observation_approval_record_sandbox')}"
    )
    print(
        "ready for actual network observation now: "
        f"{approval.get('ready_for_actual_network_observation_now')}"
    )
    print(f"ready for real approval now: {approval.get('ready_for_real_approval_now')}")
    print(
        "ready for durable approval persistence now: "
        f"{approval.get('ready_for_durable_approval_persistence_now')}"
    )
    print(f"ready for publication: {approval.get('ready_for_publication')}")
    print(f"ready for outreach: {approval.get('ready_for_outreach')}")
    print(f"ready for payment: {approval.get('ready_for_payment')}")
    print(f"ready for revenue execution: {approval.get('ready_for_revenue_execution')}")
    print(f"next recommended milestone: {approval.get('next_recommended_milestone')}")
    print(f"generated_selected_candidates: {approval.get('generated_selected_candidates')}")
    print(f"generated_approval_packets: {approval.get('generated_approval_packets')}")
    print(f"generated_evidence_dossiers: {approval.get('generated_evidence_dossiers')}")
    print(f"generated_risk_reviews: {approval.get('generated_risk_reviews')}")
    print(f"generated_decision_sandbox: {approval.get('generated_decision_sandbox')}")
    print(f"generated_non_persistence_receipt: {approval.get('generated_non_persistence_receipt')}")
    print(f"generated_readiness: {approval.get('generated_readiness')}")
    print(f"warning: {approval.get('warning')}")


def cmd_integrated_approval_record_and_pilot_readiness(data: dict[str, Any]) -> None:
    readiness = data["l6_integrated_pilot_readiness"]
    print("# L6.7 Integrated Approval Record And Pilot Readiness Sandbox")
    print()
    print(
        "L6.7 integrated approval record and pilot readiness sandbox defined: "
        f"{readiness.get('l6_7_integrated_approval_record_and_pilot_readiness_sandbox_defined')}"
    )
    print(f"integrated sandbox only: {readiness.get('integrated_sandbox_only')}")
    print(f"approval record sandbox only: {readiness.get('approval_record_sandbox_only')}")
    print(f"pilot run readiness only: {readiness.get('pilot_run_readiness_only')}")
    print(f"sandbox approval record created: {readiness.get('sandbox_approval_record_created')}")
    print(f"sandbox approval records: {readiness.get('sandbox_approval_record_count')}")
    print(f"pilot run packages: {readiness.get('pilot_run_package_count')}")
    print(f"operator readiness package created: {readiness.get('operator_readiness_package_created')}")
    print(f"runtime isolation readiness created: {readiness.get('runtime_isolation_readiness_created')}")
    print(f"evidence capture readiness created: {readiness.get('evidence_capture_readiness_created')}")
    print(
        "post-observation review readiness created: "
        f"{readiness.get('post_observation_review_readiness_created')}"
    )
    print(
        "manual evidence import readiness created: "
        f"{readiness.get('manual_evidence_import_readiness_created')}"
    )
    print(f"integrated decision gate created: {readiness.get('integrated_decision_gate_created')}")
    print(f"no-action receipts created: {readiness.get('no_action_receipts_created')}")
    print(f"real approval granted: {readiness.get('real_approval_granted')}")
    print(
        "durable real approval record created: "
        f"{readiness.get('durable_real_approval_record_created')}"
    )
    print(
        "real external observation authorized: "
        f"{readiness.get('real_external_observation_authorized')}"
    )
    print(f"real pilot execution authorized: {readiness.get('real_pilot_execution_authorized')}")
    print(f"network enabled: {readiness.get('network_enabled')}")
    print(f"API enabled: {readiness.get('api_enabled')}")
    print(f"scraping enabled: {readiness.get('scraping_enabled')}")
    print(f"browser fetch enabled: {readiness.get('browser_fetch_enabled')}")
    print(f"search enabled: {readiness.get('search_enabled')}")
    print(f"publication enabled: {readiness.get('publication_enabled')}")
    print(f"outreach enabled: {readiness.get('outreach_enabled')}")
    print(f"payment enabled: {readiness.get('payment_enabled')}")
    print(f"revenue execution enabled: {readiness.get('revenue_execution_enabled')}")
    print(f"MCP tool execution enabled: {readiness.get('mcp_tool_execution_enabled')}")
    print(f"live execution enabled: {readiness.get('live_execution_enabled')}")
    print(f"CIEU DB write enabled: {readiness.get('cieu_db_write_enabled')}")
    print(f"brain writeback enabled: {readiness.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {readiness.get('memory_ingestion_enabled')}")
    print(
        "ready for L6.8 user-mediated manual evidence import pilot: "
        f"{readiness.get('ready_for_l6_8_user_mediated_manual_evidence_import_pilot')}"
    )
    print(
        "ready for actual network observation now: "
        f"{readiness.get('ready_for_actual_network_observation_now')}"
    )
    print(f"ready for real approval now: {readiness.get('ready_for_real_approval_now')}")
    print(
        "ready for durable real approval persistence now: "
        f"{readiness.get('ready_for_durable_real_approval_persistence_now')}"
    )
    print(f"ready for publication: {readiness.get('ready_for_publication')}")
    print(f"ready for outreach: {readiness.get('ready_for_outreach')}")
    print(f"ready for payment: {readiness.get('ready_for_payment')}")
    print(f"ready for revenue execution: {readiness.get('ready_for_revenue_execution')}")
    print(f"next recommended milestone: {readiness.get('next_recommended_milestone')}")
    print(f"generated_sandbox_records: {readiness.get('generated_sandbox_records')}")
    print(f"generated_pilot_run_packages: {readiness.get('generated_pilot_run_packages')}")
    print(f"generated_operator_readiness: {readiness.get('generated_operator_readiness')}")
    print(f"generated_runtime_readiness: {readiness.get('generated_runtime_readiness')}")
    print(f"generated_evidence_capture: {readiness.get('generated_evidence_capture')}")
    print(
        "generated_manual_import_readiness: "
        f"{readiness.get('generated_manual_import_readiness')}"
    )
    print(f"generated_decision_gate: {readiness.get('generated_decision_gate')}")
    print(f"generated_no_action_receipt: {readiness.get('generated_no_action_receipt')}")
    print(f"generated_readiness: {readiness.get('generated_readiness')}")
    print(f"warning: {readiness.get('warning')}")


def cmd_agentic_evidence_discovery_trust_engine(data: dict[str, Any]) -> None:
    evidence = data["l6_agentic_evidence"]
    print("# L6.8 Agentic Evidence Discovery Trust Engine")
    print()
    print(
        "L6.8 agentic evidence discovery trust engine defined: "
        f"{evidence.get('l6_8_agentic_evidence_discovery_trust_engine_defined')}"
    )
    print(f"mode: {evidence.get('mode')}")
    print(
        "agentic evidence discovery design/sandbox only: "
        f"{evidence.get('agentic_evidence_discovery_design_and_sandbox_only')}"
    )
    print(
        "autonomous evidence need inference authorized: "
        f"{evidence.get('autonomous_evidence_need_inference_authorized')}"
    )
    print(
        "autonomous source hypothesis generation authorized: "
        f"{evidence.get('autonomous_source_hypothesis_generation_authorized')}"
    )
    print(
        "autonomous evidence value judgment authorized: "
        f"{evidence.get('autonomous_evidence_value_judgment_authorized')}"
    )
    print(
        "autonomous trust assessment authorized: "
        f"{evidence.get('autonomous_trust_assessment_authorized')}"
    )
    print(
        "observation work order generation authorized: "
        f"{evidence.get('observation_work_order_generation_authorized')}"
    )
    print(f"evidence needs: {evidence.get('evidence_need_count')}")
    print(f"source hypotheses: {evidence.get('source_hypothesis_count')}")
    print(f"ranked source hypotheses: {evidence.get('ranked_source_hypothesis_count')}")
    print(f"observation work orders: {evidence.get('observation_work_order_count')}")
    print(f"rejected source hypotheses: {evidence.get('rejected_source_hypothesis_count')}")
    print(f"source value model generated: {evidence.get('source_type_value_model_generated')}")
    print(f"structural trust judgment generated: {evidence.get('structural_trust_judgment_generated')}")
    print(f"value of information model generated: {evidence.get('value_of_information_model_generated')}")
    print(
        "conflict/corroboration model generated: "
        f"{evidence.get('conflict_corroboration_model_generated')}"
    )
    print(
        "pre-observation rejection filter generated: "
        f"{evidence.get('pre_observation_rejection_filter_generated')}"
    )
    print(
        "agentic evidence decision gate generated: "
        f"{evidence.get('agentic_evidence_decision_gate_generated')}"
    )
    print(f"no-action receipts generated: {evidence.get('no_action_receipts_generated')}")
    print(f"strategic residual loop generated: {evidence.get('strategic_residual_loop_generated')}")
    print(
        "future controlled read-only observation pilot candidate allowed: "
        f"{evidence.get('future_controlled_read_only_observation_pilot_candidate_allowed')}"
    )
    print(
        "real external observation authorized: "
        f"{evidence.get('real_external_observation_authorized')}"
    )
    print(f"agent external fetch authorized: {evidence.get('agent_external_fetch_authorized')}")
    print(f"network enabled: {evidence.get('network_enabled')}")
    print(f"API enabled: {evidence.get('api_enabled')}")
    print(f"scraping enabled: {evidence.get('scraping_enabled')}")
    print(f"browser fetch enabled: {evidence.get('browser_fetch_enabled')}")
    print(f"search enabled: {evidence.get('search_enabled')}")
    print(f"publication enabled: {evidence.get('publication_enabled')}")
    print(f"outreach enabled: {evidence.get('outreach_enabled')}")
    print(f"payment enabled: {evidence.get('payment_enabled')}")
    print(f"revenue execution enabled: {evidence.get('revenue_execution_enabled')}")
    print(f"MCP tool execution enabled: {evidence.get('mcp_tool_execution_enabled')}")
    print(f"live execution enabled: {evidence.get('live_execution_enabled')}")
    print(f"CIEU DB write enabled: {evidence.get('cieu_db_write_enabled')}")
    print(f"canonical update enabled: {evidence.get('real_canonical_update_application_enabled')}")
    print(f"brain writeback enabled: {evidence.get('brain_writeback_enabled')}")
    print(f"memory ingestion enabled: {evidence.get('memory_ingestion_enabled')}")
    print(
        "ready for L6.9 controlled read-only agentic evidence discovery pilot approval: "
        f"{evidence.get('ready_for_l6_9_controlled_read_only_agentic_evidence_discovery_pilot_approval')}"
    )
    print(
        "ready for actual network observation now: "
        f"{evidence.get('ready_for_actual_network_observation_now')}"
    )
    print(
        "ready for autonomous web search now: "
        f"{evidence.get('ready_for_autonomous_web_search_now')}"
    )
    print(f"ready for scraping: {evidence.get('ready_for_scraping')}")
    print(f"ready for publication: {evidence.get('ready_for_publication')}")
    print(f"ready for outreach: {evidence.get('ready_for_outreach')}")
    print(f"ready for payment: {evidence.get('ready_for_payment')}")
    print(f"ready for revenue execution: {evidence.get('ready_for_revenue_execution')}")
    print(f"next recommended milestone: {evidence.get('next_recommended_milestone')}")
    print(f"generated_evidence_needs: {evidence.get('generated_evidence_needs')}")
    print(f"generated_source_hypotheses: {evidence.get('generated_source_hypotheses')}")
    print(f"generated_source_ranking: {evidence.get('generated_source_ranking')}")
    print(f"generated_work_orders: {evidence.get('generated_work_orders')}")
    print(f"generated_rejection_filter: {evidence.get('generated_rejection_filter')}")
    print(f"generated_decision_gate: {evidence.get('generated_decision_gate')}")
    print(f"generated_readiness: {evidence.get('generated_readiness')}")
    print(f"warning: {evidence.get('warning')}")


def cmd_controlled_agentic_evidence_pilot_approval_dry_run(data: dict[str, Any]) -> None:
    pilot = data["l6_agentic_pilot_dry_run"]
    print("# L6.9 Controlled Agentic Evidence Pilot Approval Dry-Run")
    print()
    print(
        "L6.9 controlled agentic evidence pilot approval dry-run defined: "
        f"{pilot.get('l6_9_controlled_agentic_evidence_pilot_approval_dry_run_defined')}"
    )
    print(f"mode: {pilot.get('mode')}")
    print(f"pilot approval and dry-run only: {pilot.get('pilot_approval_and_dry_run_only')}")
    print(f"sandbox approval record only: {pilot.get('sandbox_approval_record_only')}")
    print(
        "work order selection authorized: "
        f"{pilot.get('agentic_work_order_selection_authorized')}"
    )
    print(
        "approval packet generation authorized: "
        f"{pilot.get('pilot_approval_packet_generation_authorized')}"
    )
    print(
        "sandbox approval record generation authorized: "
        f"{pilot.get('sandbox_approval_record_generation_authorized')}"
    )
    print(
        "dry-run lifecycle simulation authorized: "
        f"{pilot.get('dry_run_lifecycle_simulation_authorized')}"
    )
    print(
        "empty evidence capture simulation authorized: "
        f"{pilot.get('empty_evidence_capture_simulation_authorized')}"
    )
    print(f"selected work orders: {pilot.get('selected_work_order_count')}")
    print(f"eligible work orders: {pilot.get('eligible_work_order_count')}")
    print(f"approval packets: {pilot.get('approval_packet_count')}")
    print(f"sandbox approval records: {pilot.get('sandbox_approval_record_count')}")
    print(f"runtime readiness packets: {pilot.get('runtime_readiness_packet_count')}")
    print(f"dry-run traces: {pilot.get('dry_run_trace_count')}")
    print(f"empty evidence packets: {pilot.get('empty_evidence_packet_count')}")
    print(f"post-run review packets: {pilot.get('post_run_review_packet_count')}")
    print(f"refinement candidates: {pilot.get('refinement_candidate_count')}")
    print(f"real external observation authorized: {pilot.get('real_external_observation_authorized')}")
    print(f"real pilot execution authorized: {pilot.get('real_pilot_execution_authorized')}")
    print(f"real approval granted: {pilot.get('real_approval_granted')}")
    print(
        "durable real approval record created: "
        f"{pilot.get('durable_real_approval_record_created')}"
    )
    print(f"agent external fetch authorized: {pilot.get('agent_external_fetch_authorized')}")
    print(f"network enabled: {pilot.get('network_enabled')}")
    print(f"API enabled: {pilot.get('api_enabled')}")
    print(f"scraping enabled: {pilot.get('scraping_enabled')}")
    print(f"browser fetch enabled: {pilot.get('browser_fetch_enabled')}")
    print(f"search enabled: {pilot.get('search_enabled')}")
    print(f"publication enabled: {pilot.get('publication_enabled')}")
    print(f"outreach enabled: {pilot.get('outreach_enabled')}")
    print(f"payment enabled: {pilot.get('payment_enabled')}")
    print(f"revenue execution enabled: {pilot.get('revenue_execution_enabled')}")
    print(f"MCP tool execution enabled: {pilot.get('mcp_tool_execution_enabled')}")
    print(f"live execution enabled: {pilot.get('live_execution_enabled')}")
    print(f"CIEU DB write enabled: {pilot.get('cieu_db_write_enabled')}")
    print(
        "ready for L6.10 tiny real read-only agentic evidence observation pilot: "
        f"{pilot.get('ready_for_l6_10_tiny_real_read_only_agentic_evidence_observation_pilot')}"
    )
    print(
        "ready for actual network observation now: "
        f"{pilot.get('ready_for_actual_network_observation_now')}"
    )
    print(
        "ready for autonomous web search now: "
        f"{pilot.get('ready_for_autonomous_web_search_now')}"
    )
    print(f"next recommended milestone: {pilot.get('next_recommended_milestone')}")
    print(f"generated_selected_work_orders: {pilot.get('generated_selected_work_orders')}")
    print(f"generated_approval_packets: {pilot.get('generated_approval_packets')}")
    print(f"generated_sandbox_records: {pilot.get('generated_sandbox_records')}")
    print(f"generated_dry_run_traces: {pilot.get('generated_dry_run_traces')}")
    print(f"generated_empty_evidence: {pilot.get('generated_empty_evidence')}")
    print(f"generated_readiness: {pilot.get('generated_readiness')}")
    print(f"warning: {pilot.get('warning')}")


def cmd_tiny_real_read_only_agentic_evidence_observation_pilot(data: dict[str, Any]) -> None:
    pilot = data["l6_tiny_observation_pilot"]
    print("# L6.10 Tiny Real Read-Only Agentic Evidence Observation Pilot")
    print()
    print(
        "L6.10 tiny real read-only observation pilot defined: "
        f"{pilot.get('l6_10_tiny_real_read_only_observation_pilot_defined')}"
    )
    print(f"mode: {pilot.get('mode')}")
    print(f"selected work orders: {pilot.get('selected_work_order_count')}")
    print(f"source locator resolved: {pilot.get('source_locator_resolved')}")
    print(f"observation executed: {pilot.get('observation_executed')}")
    print(f"blocked pilot: {pilot.get('blocked_pilot')}")
    print(f"external requests count: {pilot.get('external_requests_count')}")
    print(f"pages read count: {pilot.get('pages_read_count')}")
    print(f"search queries count: {pilot.get('search_queries_count')}")
    print(f"evidence packet generated: {pilot.get('evidence_packet_generated')}")
    print(
        "post-observation review packet generated: "
        f"{pilot.get('post_observation_review_packet_generated')}"
    )
    print(
        "artifact refinement candidate generated: "
        f"{pilot.get('artifact_refinement_candidate_generated')}"
    )
    print(f"artifact refinement applied: {pilot.get('artifact_refinement_applied')}")
    print(f"real read-only pilot authorized: {pilot.get('real_read_only_observation_pilot_authorized')}")
    print(f"broad web search authorized: {pilot.get('broad_web_search_authorized')}")
    print(f"crawling authorized: {pilot.get('crawling_authorized')}")
    print(f"scraping authorized: {pilot.get('scraping_authorized')}")
    print(f"browser automation authorized: {pilot.get('browser_automation_authorized')}")
    print(f"login authorized: {pilot.get('login_authorized')}")
    print(f"account creation authorized: {pilot.get('account_creation_authorized')}")
    print(f"payment authorized: {pilot.get('payment_authorized')}")
    print(f"form submission authorized: {pilot.get('form_submission_authorized')}")
    print(
        "posting/commenting/messaging authorized: "
        f"{pilot.get('posting_commenting_messaging_authorized')}"
    )
    print(f"publication authorized: {pilot.get('publication_authorized')}")
    print(f"outreach authorized: {pilot.get('outreach_authorized')}")
    print(f"revenue execution authorized: {pilot.get('revenue_execution_authorized')}")
    print(f"MCP execution authorized: {pilot.get('mcp_execution_authorized')}")
    print(f"live behavior authorized: {pilot.get('live_behavior_authorized')}")
    print(f"CIEU DB write authorized: {pilot.get('cieu_db_write_authorized')}")
    print(f"canonical update authorized: {pilot.get('canonical_update_authorized')}")
    print(f"brain writeback authorized: {pilot.get('brain_writeback_authorized')}")
    print(f"memory ingestion authorized: {pilot.get('memory_ingestion_authorized')}")
    print(f"direct Y* mutation authorized: {pilot.get('direct_y_star_mutation_authorized')}")
    print(
        "ready for retry after condition resolved: "
        f"{pilot.get('ready_for_retry_after_condition_resolved')}"
    )
    print(
        "ready for L6.11 controlled multi-source corroboration pilot: "
        f"{pilot.get('ready_for_l6_11_controlled_multi_source_read_only_evidence_corroboration_pilot')}"
    )
    print(f"next recommended milestone: {pilot.get('next_recommended_milestone')}")
    print(f"generated_selected_work_order: {pilot.get('generated_selected_work_order')}")
    print(f"generated_observation_trace: {pilot.get('generated_observation_trace')}")
    print(f"generated_evidence_packet: {pilot.get('generated_evidence_packet')}")
    print(f"generated_readiness: {pilot.get('generated_readiness')}")
    print(f"warning: {pilot.get('warning')}")


def cmd_controlled_source_locator_resolution_tiny_observation_retry(data: dict[str, Any]) -> None:
    retry = data["l6_10r_locator_retry"]
    print("# L6.10R Controlled Source Locator Resolution And Tiny Observation Retry")
    print()
    print(
        "L6.10R controlled locator retry defined: "
        f"{retry.get('l6_10r_controlled_source_locator_resolution_retry_defined')}"
    )
    print(f"mode: {retry.get('mode')}")
    print(f"selected work orders: {retry.get('selected_work_order_count')}")
    print(f"controlled locator discovery authorized: {retry.get('controlled_locator_discovery_authorized')}")
    print(f"locator discovery executed: {retry.get('locator_discovery_executed')}")
    print(f"locator discovery queries count: {retry.get('locator_discovery_queries_count')}")
    print(f"concrete locator resolved: {retry.get('concrete_locator_resolved')}")
    print(f"locator eligible for observation: {retry.get('locator_eligible_for_observation')}")
    print(f"retry observation authorized: {retry.get('retry_observation_authorized')}")
    print(f"tiny read-only observation executed: {retry.get('tiny_read_only_observation_executed')}")
    print(f"external reads total: {retry.get('external_reads_total')}")
    print(f"pages read count: {retry.get('pages_read_count')}")
    print(f"evidence packet generated: {retry.get('evidence_packet_generated')}")
    print(f"live source evidence captured: {retry.get('live_source_evidence_captured')}")
    print(
        "post-observation review packet generated: "
        f"{retry.get('post_observation_review_packet_generated')}"
    )
    print(
        "artifact refinement candidate generated: "
        f"{retry.get('artifact_refinement_candidate_generated')}"
    )
    print(f"artifact refinement applied: {retry.get('artifact_refinement_applied')}")
    print(f"broad web search authorized: {retry.get('broad_web_search_authorized')}")
    print(f"repeated search loop authorized: {retry.get('repeated_search_loop_authorized')}")
    print(f"crawling authorized: {retry.get('crawling_authorized')}")
    print(f"scraping authorized: {retry.get('scraping_authorized')}")
    print(f"browser automation authorized: {retry.get('browser_automation_authorized')}")
    print(f"login authorized: {retry.get('login_authorized')}")
    print(f"account creation authorized: {retry.get('account_creation_authorized')}")
    print(f"contact authorized: {retry.get('contact_authorized')}")
    print(f"payment authorized: {retry.get('payment_authorized')}")
    print(f"form submission authorized: {retry.get('form_submission_authorized')}")
    print(
        "posting/commenting/messaging authorized: "
        f"{retry.get('posting_commenting_messaging_authorized')}"
    )
    print(f"publication authorized: {retry.get('publication_authorized')}")
    print(f"outreach authorized: {retry.get('outreach_authorized')}")
    print(f"revenue execution authorized: {retry.get('revenue_execution_authorized')}")
    print(f"MCP execution authorized: {retry.get('mcp_execution_authorized')}")
    print(f"live behavior authorized: {retry.get('live_behavior_authorized')}")
    print(f"CIEU DB write authorized: {retry.get('cieu_db_write_authorized')}")
    print(f"canonical update authorized: {retry.get('canonical_update_authorized')}")
    print(f"brain writeback authorized: {retry.get('brain_writeback_authorized')}")
    print(f"memory ingestion authorized: {retry.get('memory_ingestion_authorized')}")
    print(f"direct Y* mutation authorized: {retry.get('direct_y_star_mutation_authorized')}")
    print(f"remaining blocker: {retry.get('remaining_blocker')}")
    print(f"next recommended milestone: {retry.get('next_recommended_milestone')}")
    print(f"generated_selected_work_order: {retry.get('generated_selected_work_order')}")
    print(f"generated_locator_resolution: {retry.get('generated_locator_resolution')}")
    print(f"generated_observation_trace: {retry.get('generated_observation_trace')}")
    print(f"generated_evidence_packet: {retry.get('generated_evidence_packet')}")
    print(f"generated_readiness: {retry.get('generated_readiness')}")
    print(f"warning: {retry.get('warning')}")


def cmd_governed_capability_gap_toolmaking_locator_resolver(data: dict[str, Any]) -> None:
    summary = data["l6_10t_toolmaking_locator_resolver"]
    print("# L6.10T Governed Capability Gap Toolmaking Locator Resolver")
    print()
    print(
        "L6.10T governed capability-gap toolmaking defined: "
        f"{summary.get('l6_10t_governed_capability_gap_toolmaking_defined')}"
    )
    print(f"mode: {summary.get('mode')}")
    print(f"OS-neutral design required: {summary.get('os_neutral_design_required')}")
    print(f"mac-only solution allowed: {summary.get('mac_only_solution_allowed')}")
    print(f"primary gap type: {summary.get('primary_gap_type')}")
    print(f"secondary gap type: {summary.get('secondary_gap_type')}")
    print(f"methodology created: {summary.get('governed_toolmaking_methodology_created')}")
    print(f"controlled tool contract model created: {summary.get('controlled_tool_contract_model_created')}")
    print(f"tool authority/use gate created: {summary.get('tool_authority_use_gate_created')}")
    print(f"validation harness created: {summary.get('tool_validation_harness_created')}")
    print(f"capability probe executed: {summary.get('resolver_capability_probe_executed')}")
    print(f"capability probe local-only: {summary.get('capability_probe_local_only')}")
    print(f"probe used network: {summary.get('probe_used_network')}")
    print(f"controlled resolver adapter available: {summary.get('controlled_resolver_adapter_available')}")
    print(f"selected resolver adapter id: {summary.get('selected_resolver_adapter_id')}")
    print(f"resolver mode: {summary.get('resolver_mode')}")
    print(f"capability gap code: {summary.get('capability_gap_code')}")
    print(f"locator discovery executed: {summary.get('locator_discovery_executed')}")
    print(f"locator discovery queries count: {summary.get('locator_discovery_queries_count')}")
    print(f"concrete locator resolved: {summary.get('concrete_locator_resolved')}")
    print(f"tiny read-only observation executed: {summary.get('tiny_read_only_observation_executed')}")
    print(f"external reads total: {summary.get('external_reads_total')}")
    print(f"pages read count: {summary.get('pages_read_count')}")
    print(f"evidence packet generated: {summary.get('evidence_packet_generated')}")
    print(f"live source evidence captured: {summary.get('live_source_evidence_captured')}")
    print(f"generated tools granted live authority: {summary.get('generated_tools_granted_live_authority')}")
    print(f"artifact refinement candidate generated: {summary.get('artifact_refinement_candidate_generated')}")
    print(f"artifact refinement applied: {summary.get('artifact_refinement_applied')}")
    print(f"broad web search authorized: {summary.get('broad_web_search_authorized')}")
    print(f"repeated search loop authorized: {summary.get('repeated_search_loop_authorized')}")
    print(f"crawling authorized: {summary.get('crawling_authorized')}")
    print(f"scraping authorized: {summary.get('scraping_authorized')}")
    print(f"browser automation authorized: {summary.get('browser_automation_authorized')}")
    print(f"login authorized: {summary.get('login_authorized')}")
    print(f"account creation authorized: {summary.get('account_creation_authorized')}")
    print(f"contact authorized: {summary.get('contact_authorized')}")
    print(f"payment authorized: {summary.get('payment_authorized')}")
    print(f"form submission authorized: {summary.get('form_submission_authorized')}")
    print(f"publication authorized: {summary.get('publication_authorized')}")
    print(f"outreach authorized: {summary.get('outreach_authorized')}")
    print(f"revenue execution authorized: {summary.get('revenue_execution_authorized')}")
    print(f"MCP execution authorized: {summary.get('mcp_execution_authorized')}")
    print(f"live behavior authorized: {summary.get('live_behavior_authorized')}")
    print(f"CIEU DB write authorized: {summary.get('cieu_db_write_authorized')}")
    print(f"canonical update authorized: {summary.get('canonical_update_authorized')}")
    print(f"brain writeback authorized: {summary.get('brain_writeback_authorized')}")
    print(f"memory ingestion authorized: {summary.get('memory_ingestion_authorized')}")
    print(f"direct Y* mutation authorized: {summary.get('direct_y_star_mutation_authorized')}")
    print(
        "general governed toolmaking methodology ready for reuse: "
        f"{summary.get('general_governed_toolmaking_methodology_ready_for_reuse')}"
    )
    print(f"remaining blocker: {summary.get('remaining_blocker')}")
    print(f"next recommended milestone: {summary.get('next_recommended_milestone')}")
    print(f"generated_probe_result: {summary.get('generated_probe_result')}")
    print(f"generated_adapter_trace: {summary.get('generated_adapter_trace')}")
    print(f"generated_evidence_packet: {summary.get('generated_evidence_packet')}")
    print(f"generated_readiness: {summary.get('generated_readiness')}")
    print(f"warning: {summary.get('warning')}")


def cmd_controlled_locator_resolver_enable_first_attempt(data: dict[str, Any]) -> None:
    summary = data["l6_10u_locator_resolver_enablement"]
    print("# L6.10U Controlled Locator Resolver Enablement First Attempt")
    print()
    print(
        "L6.10U complete: "
        f"{summary.get('l6_10u_controlled_locator_resolver_enablement_complete')}"
    )
    print(f"mode: {summary.get('mode')}")
    print(f"resolver runtime created: {summary.get('resolver_runtime_created')}")
    print(f"seed registry resolver created: {summary.get('seed_registry_resolver_created')}")
    print(
        "environment gated search resolver created: "
        f"{summary.get('environment_gated_search_resolver_created')}"
    )
    print(f"disabled resolver created: {summary.get('disabled_resolver_created')}")
    print(f"selected work order id: {summary.get('selected_work_order_id')}")
    print(f"source selected work order id: {summary.get('source_selected_work_order_id')}")
    print(f"resolver mode used: {summary.get('resolver_mode_used')}")
    print(f"resolver id: {summary.get('resolver_id')}")
    print(f"seed registry lookup executed: {summary.get('seed_registry_lookup_executed')}")
    print(f"seed registry lookup count: {summary.get('seed_registry_lookup_count')}")
    print(f"controlled search executed: {summary.get('controlled_search_executed')}")
    print(f"search query count: {summary.get('search_query_count')}")
    print(f"external reads count: {summary.get('external_reads_count')}")
    print(f"concrete locator resolved: {summary.get('concrete_locator_resolved')}")
    print(f"resolved locator: {summary.get('resolved_locator')}")
    print(f"facts inferred from resolution: {summary.get('facts_inferred_from_resolution')}")
    print(
        "locator eligible for observation: "
        f"{summary.get('locator_eligible_for_observation')}"
    )
    print(
        "tiny read-only observation executed: "
        f"{summary.get('tiny_read_only_observation_executed')}"
    )
    print(f"evidence packet generated: {summary.get('evidence_packet_generated')}")
    print(f"live source evidence captured: {summary.get('live_source_evidence_captured')}")
    print(f"artifact refinement applied: {summary.get('artifact_refinement_applied')}")
    print(f"broad search authorized: {summary.get('broad_search_authorized')}")
    print(f"repeated search loop authorized: {summary.get('repeated_search_loop_authorized')}")
    print(f"crawling authorized: {summary.get('crawling_authorized')}")
    print(f"scraping authorized: {summary.get('scraping_authorized')}")
    print(f"browser automation authorized: {summary.get('browser_automation_authorized')}")
    print(f"login authorized: {summary.get('login_authorized')}")
    print(f"account creation authorized: {summary.get('account_creation_authorized')}")
    print(f"contact authorized: {summary.get('contact_authorized')}")
    print(f"payment authorized: {summary.get('payment_authorized')}")
    print(f"form submission authorized: {summary.get('form_submission_authorized')}")
    print(f"publication authorized: {summary.get('publication_authorized')}")
    print(f"outreach authorized: {summary.get('outreach_authorized')}")
    print(f"revenue execution authorized: {summary.get('revenue_execution_authorized')}")
    print(f"MCP execution authorized: {summary.get('mcp_execution_authorized')}")
    print(f"live behavior authorized: {summary.get('live_behavior_authorized')}")
    print(f"CIEU DB write authorized: {summary.get('cieu_db_write_authorized')}")
    print(f"canonical update authorized: {summary.get('canonical_update_authorized')}")
    print(f"brain writeback authorized: {summary.get('brain_writeback_authorized')}")
    print(f"memory ingestion authorized: {summary.get('memory_ingestion_authorized')}")
    print(f"direct Y* mutation authorized: {summary.get('direct_y_star_mutation_authorized')}")
    print(f"remaining blocker: {summary.get('remaining_blocker')}")
    print(f"next recommended milestone: {summary.get('next_recommended_milestone')}")
    print(f"generated_resolution_result: {summary.get('generated_resolution_result')}")
    print(f"generated_observation_trace: {summary.get('generated_observation_trace')}")
    print(f"generated_evidence_packet: {summary.get('generated_evidence_packet')}")
    print(f"generated_readiness: {summary.get('generated_readiness')}")
    print(f"warning: {summary.get('warning')}")


def cmd_controlled_seed_locator_or_search_resolver_enablement(data: dict[str, Any]) -> None:
    summary = data["l6_10v_seed_or_search_resolver_enablement"]
    print("# L6.10V Controlled Seed Locator Or Search Resolver Enablement")
    print()
    print(
        "L6.10V complete: "
        f"{summary.get('l6_10v_controlled_seed_locator_or_search_resolver_enablement_complete')}"
    )
    print(f"mode: {summary.get('mode')}")
    print(
        "reviewed seed locator registry created: "
        f"{summary.get('reviewed_seed_locator_registry_created')}"
    )
    print(
        "explicit controlled search resolver created: "
        f"{summary.get('explicit_controlled_search_resolver_created')}"
    )
    print(f"selected work order id: {summary.get('selected_work_order_id')}")
    print(f"source selected work order id: {summary.get('source_selected_work_order_id')}")
    print(f"resolution path used: {summary.get('resolution_path_used')}")
    print(f"seed registry lookup executed: {summary.get('seed_registry_lookup_executed')}")
    print(f"seed registry lookup count: {summary.get('seed_registry_lookup_count')}")
    print(f"reviewed seed locator count: {summary.get('reviewed_seed_locator_count')}")
    print(f"seed locator resolved: {summary.get('seed_locator_resolved')}")
    print(f"controlled search enabled: {summary.get('controlled_search_enabled')}")
    print(f"controlled search executed: {summary.get('controlled_search_executed')}")
    print(f"controlled search query count: {summary.get('controlled_search_query_count')}")
    print(f"external reads count: {summary.get('external_reads_count')}")
    print(f"concrete locator resolved: {summary.get('concrete_locator_resolved')}")
    print(f"resolved locator: {summary.get('resolved_locator')}")
    print(f"facts inferred from resolution: {summary.get('facts_inferred_from_resolution')}")
    print(f"search snippets used as evidence: {summary.get('search_snippets_used_as_evidence')}")
    print(
        "locator eligible for observation: "
        f"{summary.get('locator_eligible_for_observation')}"
    )
    print(
        "tiny read-only observation executed: "
        f"{summary.get('tiny_read_only_observation_executed')}"
    )
    print(f"evidence packet generated: {summary.get('evidence_packet_generated')}")
    print(f"live source evidence captured: {summary.get('live_source_evidence_captured')}")
    print(f"artifact refinement applied: {summary.get('artifact_refinement_applied')}")
    print(f"broad search authorized: {summary.get('broad_search_authorized')}")
    print(f"repeated search loop authorized: {summary.get('repeated_search_loop_authorized')}")
    print(f"crawling authorized: {summary.get('crawling_authorized')}")
    print(f"scraping authorized: {summary.get('scraping_authorized')}")
    print(f"browser automation authorized: {summary.get('browser_automation_authorized')}")
    print(f"login authorized: {summary.get('login_authorized')}")
    print(f"account creation authorized: {summary.get('account_creation_authorized')}")
    print(f"contact authorized: {summary.get('contact_authorized')}")
    print(f"payment authorized: {summary.get('payment_authorized')}")
    print(f"form submission authorized: {summary.get('form_submission_authorized')}")
    print(f"publication authorized: {summary.get('publication_authorized')}")
    print(f"outreach authorized: {summary.get('outreach_authorized')}")
    print(f"revenue execution authorized: {summary.get('revenue_execution_authorized')}")
    print(f"MCP execution authorized: {summary.get('mcp_execution_authorized')}")
    print(f"live behavior authorized: {summary.get('live_behavior_authorized')}")
    print(f"CIEU DB write authorized: {summary.get('cieu_db_write_authorized')}")
    print(f"canonical update authorized: {summary.get('canonical_update_authorized')}")
    print(f"brain writeback authorized: {summary.get('brain_writeback_authorized')}")
    print(f"memory ingestion authorized: {summary.get('memory_ingestion_authorized')}")
    print(f"direct Y* mutation authorized: {summary.get('direct_y_star_mutation_authorized')}")
    print(f"remaining blocker: {summary.get('remaining_blocker')}")
    print(f"next recommended milestone: {summary.get('next_recommended_milestone')}")
    print(f"generated_registry: {summary.get('generated_registry')}")
    print(f"generated_resolution_result: {summary.get('generated_resolution_result')}")
    print(f"generated_observation_trace: {summary.get('generated_observation_trace')}")
    print(f"generated_evidence_packet: {summary.get('generated_evidence_packet')}")
    print(f"generated_readiness: {summary.get('generated_readiness')}")
    print(f"warning: {summary.get('warning')}")


def cmd_reviewed_seed_locator_injection_tiny_retry(data: dict[str, Any]) -> None:
    summary = data["l6_10w_reviewed_seed_locator_injection"]
    print("# L6.10W Reviewed Seed Locator Injection Tiny Retry")
    print()
    print(
        "L6.10W complete: "
        f"{summary.get('l6_10w_reviewed_seed_locator_injection_tiny_retry_complete')}"
    )
    print(f"mode: {summary.get('mode')}")
    print(f"selected work order id: {summary.get('selected_work_order_id')}")
    print(f"reviewed seed locator found: {summary.get('reviewed_seed_locator_found')}")
    print(f"concrete locator: {summary.get('concrete_locator')}")
    print(f"user action required generated: {summary.get('user_action_required_generated')}")
    print(f"requested item: {summary.get('requested_item')}")
    print(f"retry attempted: {summary.get('retry_attempted')}")
    print(
        "tiny read-only observation executed: "
        f"{summary.get('tiny_read_only_observation_executed')}"
    )
    print(f"external reads count: {summary.get('external_reads_count')}")
    print(f"pages read count: {summary.get('pages_read_count')}")
    print(f"evidence packet generated: {summary.get('evidence_packet_generated')}")
    print(f"live source evidence captured: {summary.get('live_source_evidence_captured')}")
    print(f"url invention authorized: {summary.get('url_invention_authorized')}")
    print(f"fake locator authorized: {summary.get('fake_locator_authorized')}")
    print(f"broad search authorized: {summary.get('broad_search_authorized')}")
    print(f"repeated search loop authorized: {summary.get('repeated_search_loop_authorized')}")
    print(f"crawling authorized: {summary.get('crawling_authorized')}")
    print(f"scraping authorized: {summary.get('scraping_authorized')}")
    print(f"browser automation authorized: {summary.get('browser_automation_authorized')}")
    print(f"login authorized: {summary.get('login_authorized')}")
    print(f"account creation authorized: {summary.get('account_creation_authorized')}")
    print(f"contact authorized: {summary.get('contact_authorized')}")
    print(f"payment authorized: {summary.get('payment_authorized')}")
    print(f"form submission authorized: {summary.get('form_submission_authorized')}")
    print(f"publication authorized: {summary.get('publication_authorized')}")
    print(f"outreach authorized: {summary.get('outreach_authorized')}")
    print(f"revenue execution authorized: {summary.get('revenue_execution_authorized')}")
    print(f"MCP execution authorized: {summary.get('mcp_execution_authorized')}")
    print(f"live behavior authorized: {summary.get('live_behavior_authorized')}")
    print(f"CIEU DB write authorized: {summary.get('cieu_db_write_authorized')}")
    print(f"canonical update authorized: {summary.get('canonical_update_authorized')}")
    print(f"brain writeback authorized: {summary.get('brain_writeback_authorized')}")
    print(f"memory ingestion authorized: {summary.get('memory_ingestion_authorized')}")
    print(f"direct Y* mutation authorized: {summary.get('direct_y_star_mutation_authorized')}")
    print(f"remaining blocker: {summary.get('remaining_blocker')}")
    print(f"next recommended milestone: {summary.get('next_recommended_milestone')}")
    print(f"generated user action required: {summary.get('generated_user_action_required')}")
    print(f"generated seed candidate: {summary.get('generated_seed_candidate')}")
    print(f"generated evidence packet: {summary.get('generated_evidence_packet')}")
    print(f"generated readiness: {summary.get('generated_readiness')}")
    print(f"warning: {summary.get('warning')}")


def cmd_budgeted_controlled_external_search_evidence_pilot(data: dict[str, Any]) -> None:
    summary = data["l6_10x_budgeted_controlled_search_evidence"]
    print("# L6.10X Budgeted Controlled External Search Evidence Pilot")
    print()
    print(
        "L6.10X complete: "
        f"{summary.get('l6_10x_budgeted_controlled_external_search_evidence_pilot_complete')}"
    )
    print(f"mode: {summary.get('mode')}")
    print(f"selected work order id: {summary.get('selected_work_order_id')}")
    print(f"query count: {summary.get('query_count')}")
    print(f"query categories: {summary.get('query_categories')}")
    print(f"search backend mode: {summary.get('search_backend_mode')}")
    print(f"backend missing: {summary.get('backend_missing')}")
    print(f"search executed: {summary.get('search_executed')}")
    print(f"search results considered: {summary.get('search_results_considered')}")
    print(f"pages opened: {summary.get('pages_opened')}")
    print(f"domains touched: {summary.get('domains_touched')}")
    print(f"crawl depth used: {summary.get('crawl_depth_used')}")
    print(f"evidence packets generated: {summary.get('evidence_packets_generated')}")
    print(f"conflicts found: {summary.get('conflicts_found')}")
    print(f"page read backend missing: {summary.get('page_read_backend_missing')}")
    print(f"manual URL request avoided: {summary.get('manual_url_request_avoided')}")
    print(f"controlled external search authorized: {summary.get('controlled_external_search_authorized')}")
    print(f"bounded crawl authorized: {summary.get('bounded_crawl_authorized')}")
    print(f"ask user for URL authorized: {summary.get('ask_user_for_url_authorized')}")
    print(f"user manual URL provision required: {summary.get('user_manual_url_provision_required')}")
    print(f"login authorized: {summary.get('login_authorized')}")
    print(f"account creation authorized: {summary.get('account_creation_authorized')}")
    print(f"payment authorized: {summary.get('payment_authorized')}")
    print(f"form submission authorized: {summary.get('form_submission_authorized')}")
    print(f"contact authorized: {summary.get('contact_authorized')}")
    print(f"posting/commenting/messaging authorized: {summary.get('posting_commenting_messaging_authorized')}")
    print(f"publication authorized: {summary.get('publication_authorized')}")
    print(f"outreach authorized: {summary.get('outreach_authorized')}")
    print(f"revenue execution authorized: {summary.get('revenue_execution_authorized')}")
    print(f"MCP execution authorized: {summary.get('mcp_execution_authorized')}")
    print(f"live behavior authorized: {summary.get('live_behavior_authorized')}")
    print(f"CIEU DB write authorized: {summary.get('cieu_db_write_authorized')}")
    print(f"canonical update authorized: {summary.get('canonical_update_authorized')}")
    print(f"brain writeback authorized: {summary.get('brain_writeback_authorized')}")
    print(f"memory ingestion authorized: {summary.get('memory_ingestion_authorized')}")
    print(f"direct Y* mutation authorized: {summary.get('direct_y_star_mutation_authorized')}")
    print(f"remaining blocker: {summary.get('remaining_blocker')}")
    print(f"next step: {summary.get('next_step')}")
    print(f"generated query plan: {summary.get('generated_query_plan')}")
    print(f"generated search trace: {summary.get('generated_search_trace')}")
    print(f"generated evidence index: {summary.get('generated_evidence_index')}")
    print(f"generated readiness: {summary.get('generated_readiness')}")
    print(f"warning: {summary.get('warning')}")


def cmd_controlled_search_backend_page_read_enablement(data: dict[str, Any]) -> None:
    summary = data["l6_11_controlled_backend_page_read_enablement"]
    print("# L6.11 Controlled Search Backend & Public Page-Read Adapter Enablement")
    print()
    print(
        "L6.11 complete: "
        f"{summary.get('l6_11_controlled_search_backend_page_read_enablement_complete')}"
    )
    print(f"mode: {summary.get('mode')}")
    print(f"selected work order id: {summary.get('selected_work_order_id')}")
    print(f"backend mode tested: {summary.get('backend_mode_tested')}")
    print(f"page-read mode tested: {summary.get('page_read_mode_tested')}")
    print(f"default backend mode: {summary.get('default_backend_mode')}")
    print(f"network allowed: {summary.get('network_allowed')}")
    print(
        "real network use requires explicit backend configuration: "
        f"{summary.get('real_network_use_requires_explicit_backend_configuration')}"
    )
    print(
        "manual URL request replaced by backend configuration: "
        f"{summary.get('manual_url_request_replaced_by_backend_configuration')}"
    )
    print(f"queries generated: {summary.get('query_count')}")
    print(f"search results considered: {summary.get('search_results_considered')}")
    print(f"pages opened: {summary.get('pages_opened')}")
    print(f"domains touched: {summary.get('domains_touched')}")
    print(f"crawl depth used: {summary.get('crawl_depth_used')}")
    print(f"evidence packets generated: {summary.get('evidence_packets_generated')}")
    print(f"conflicts found: {summary.get('conflicts_found')}")
    print(
        "fixture full pipeline generated non-empty evidence packet: "
        f"{summary.get('fixture_full_pipeline_generated_non_empty_evidence_packet')}"
    )
    print(f"blockers: {summary.get('blockers')}")
    print(f"disabled blockers: {summary.get('disabled_blockers')}")
    print(f"ask-user-URL occurred: {summary.get('ask_user_for_url_occurred')}")
    print(f"search snippets used as evidence: {summary.get('search_snippets_used_as_evidence')}")
    print(
        "page-read extracted content used as evidence candidate: "
        f"{summary.get('page_read_extracted_content_used_as_evidence_candidate')}"
    )
    print(f"login authorized: {summary.get('login_authorized')}")
    print(f"account creation authorized: {summary.get('account_creation_authorized')}")
    print(f"payment authorized: {summary.get('payment_authorized')}")
    print(f"form submission authorized: {summary.get('form_submission_authorized')}")
    print(f"contact authorized: {summary.get('contact_authorized')}")
    print(f"posting/commenting/messaging authorized: {summary.get('posting_commenting_messaging_authorized')}")
    print(f"publication authorized: {summary.get('publication_authorized')}")
    print(f"outreach authorized: {summary.get('outreach_authorized')}")
    print(f"revenue execution authorized: {summary.get('revenue_execution_authorized')}")
    print(f"MCP execution authorized: {summary.get('mcp_execution_authorized')}")
    print(f"live behavior authorized: {summary.get('live_behavior_authorized')}")
    print(f"CIEU DB write authorized: {summary.get('cieu_db_write_authorized')}")
    print(f"canonical update authorized: {summary.get('canonical_update_authorized')}")
    print(f"brain writeback authorized: {summary.get('brain_writeback_authorized')}")
    print(f"memory ingestion authorized: {summary.get('memory_ingestion_authorized')}")
    print(f"direct Y* mutation authorized: {summary.get('direct_y_star_mutation_authorized')}")
    print(f"safety preflight decision: {summary.get('safety_preflight_decision')}")
    print(f"next step: {summary.get('next_step')}")
    print(f"generated configuration receipt: {summary.get('generated_configuration_receipt')}")
    print(f"generated safety preflight: {summary.get('generated_safety_preflight')}")
    print(f"generated fixture pipeline trace: {summary.get('generated_fixture_pipeline_trace')}")
    print(f"generated evidence index: {summary.get('generated_evidence_index')}")
    print(f"generated readiness: {summary.get('generated_readiness')}")
    print(f"warning: {summary.get('warning')}")


def cmd_unified_controlled_external_observation_evidence_loop(data: dict[str, Any]) -> None:
    summary = data["l6_12_unified_controlled_observation"]
    print("# L6.12 Unified Controlled External Observation Evidence Loop")
    print()
    print(
        "L6.12 complete: "
        f"{summary.get('l6_12_unified_controlled_external_observation_evidence_loop_complete')}"
    )
    print(f"mode: {summary.get('mode')}")
    print(f"run classification: {summary.get('run_classification')}")
    print(f"selected work order id: {summary.get('selected_work_order_id')}")
    print(f"backend mode: {summary.get('backend_mode')}")
    print(f"page-read mode: {summary.get('page_read_mode')}")
    print(f"network allowed: {summary.get('network_allowed')}")
    print(f"safety preflight decision: {summary.get('safety_preflight_decision')}")
    print(f"fixture proof executed: {summary.get('fixture_proof_executed')}")
    print(f"real observation executed: {summary.get('real_observation_executed')}")
    print(f"queries generated: {summary.get('query_count')}")
    print(f"search results considered: {summary.get('search_results_considered')}")
    print(f"pages opened: {summary.get('pages_opened')}")
    print(f"domains touched: {summary.get('domains_touched')}")
    print(f"crawl depth used: {summary.get('crawl_depth_used')}")
    print(f"external reads used: {summary.get('external_reads_used')}")
    print(f"evidence packets generated: {summary.get('evidence_packets_generated')}")
    print(f"conflicts found: {summary.get('conflicts_found')}")
    print(f"unresolved claims: {summary.get('unresolved_claims')}")
    print(
        "query refinement candidates generated: "
        f"{summary.get('query_refinement_candidates_generated')}"
    )
    print(f"capability gaps generated: {summary.get('capability_gaps_generated')}")
    print(f"blockers: {summary.get('blockers')}")
    print(f"ask-user-URL occurred: {summary.get('ask_user_for_url_occurred')}")
    print(f"external side effects occurred: {summary.get('external_side_effects_occurred')}")
    print(f"core writeback occurred: {summary.get('core_writeback_occurred')}")
    print(f"search snippets used as evidence: {summary.get('search_snippets_used_as_evidence')}")
    print(f"page-read content used as evidence: {summary.get('page_read_content_used_as_evidence')}")
    print(f"login authorized: {summary.get('login_authorized')}")
    print(f"payment authorized: {summary.get('payment_authorized')}")
    print(f"form submission authorized: {summary.get('form_submission_authorized')}")
    print(f"posting authorized: {summary.get('posting_authorized')}")
    print(f"publication authorized: {summary.get('publication_authorized')}")
    print(f"outreach authorized: {summary.get('outreach_authorized')}")
    print(f"revenue execution authorized: {summary.get('revenue_execution_authorized')}")
    print(f"MCP execution authorized: {summary.get('mcp_execution_authorized')}")
    print(f"live behavior authorized: {summary.get('live_behavior_authorized')}")
    print(f"CIEU DB write authorized: {summary.get('cieu_db_write_authorized')}")
    print(f"canonical update authorized: {summary.get('canonical_update_authorized')}")
    print(f"brain writeback authorized: {summary.get('brain_writeback_authorized')}")
    print(f"memory ingestion authorized: {summary.get('memory_ingestion_authorized')}")
    print(f"direct Y* mutation authorized: {summary.get('direct_y_star_mutation_authorized')}")
    print(f"next step: {summary.get('next_step')}")
    print(f"generated review packet: {summary.get('generated_review_packet')}")
    print(f"generated capability gap registry: {summary.get('generated_capability_gap_registry')}")
    print(f"generated no-side-effect receipt: {summary.get('generated_no_side_effect_receipt')}")
    print(f"generated readiness: {summary.get('generated_readiness')}")
    print(f"warning: {summary.get('warning')}")


def cmd_real_controlled_external_observation_mission_sprint(data: dict[str, Any]) -> None:
    summary = data["l6_13_real_controlled_observation_mission"]
    print("# L6.13 Real Controlled External Observation Mission Sprint")
    print()
    print(
        "L6.13 complete: "
        f"{summary.get('l6_13_real_controlled_external_observation_mission_sprint_complete')}"
    )
    print(f"mode: {summary.get('mode')}")
    print(f"run classification: {summary.get('run_classification')}")
    print(f"selected work order id: {summary.get('selected_work_order_id')}")
    print(f"backend mode: {summary.get('backend_mode')}")
    print(f"page-read mode: {summary.get('page_read_mode')}")
    print(f"network allowed: {summary.get('network_allowed')}")
    print(f"safety preflight decision: {summary.get('safety_preflight_decision')}")
    print(f"fixture proof executed: {summary.get('fixture_proof_executed')}")
    print(f"real observation executed: {summary.get('real_observation_executed')}")
    print(f"queries generated: {summary.get('query_count')}")
    print(f"search results considered: {summary.get('search_results_considered')}")
    print(f"pages opened: {summary.get('pages_opened')}")
    print(f"domains touched: {summary.get('domains_touched')}")
    print(f"crawl depth used: {summary.get('crawl_depth_used')}")
    print(f"external reads used: {summary.get('external_reads_used')}")
    print(f"real evidence packets generated: {summary.get('real_evidence_packets_generated')}")
    print(f"fixture evidence packets generated: {summary.get('fixture_evidence_packets_generated')}")
    print(f"conflicts found: {summary.get('conflicts_found')}")
    print(f"unresolved claims: {summary.get('unresolved_claims')}")
    print(f"query refinements generated: {summary.get('query_refinements_generated')}")
    print(f"capability gaps resolved: {summary.get('capability_gaps_resolved')}")
    print(f"capability gaps remaining: {summary.get('capability_gaps_remaining')}")
    print(f"activation kit generated: {summary.get('activation_kit_generated')}")
    print(f"blockers: {summary.get('blockers')}")
    print(f"ask-user-URL occurred: {summary.get('ask_user_for_url_occurred')}")
    print(f"external side effects occurred: {summary.get('external_side_effects_occurred')}")
    print(f"core writeback occurred: {summary.get('core_writeback_occurred')}")
    print(f"Y-star-gov modified: {summary.get('y_star_gov_modified')}")
    print(f"gov-mcp modified: {summary.get('gov_mcp_modified')}")
    print(f"search snippets used as evidence: {summary.get('search_snippets_used_as_evidence')}")
    print(f"page-read content used as evidence: {summary.get('page_read_content_used_as_evidence')}")
    print(f"login authorized: {summary.get('login_authorized')}")
    print(f"payment authorized: {summary.get('payment_authorized')}")
    print(f"form submission authorized: {summary.get('form_submission_authorized')}")
    print(f"posting authorized: {summary.get('posting_authorized')}")
    print(f"publication authorized: {summary.get('publication_authorized')}")
    print(f"outreach authorized: {summary.get('outreach_authorized')}")
    print(f"revenue execution authorized: {summary.get('revenue_execution_authorized')}")
    print(f"MCP execution authorized: {summary.get('mcp_execution_authorized')}")
    print(f"live behavior authorized: {summary.get('live_behavior_authorized')}")
    print(f"CIEU DB write authorized: {summary.get('cieu_db_write_authorized')}")
    print(f"canonical update authorized: {summary.get('canonical_update_authorized')}")
    print(f"brain writeback authorized: {summary.get('brain_writeback_authorized')}")
    print(f"memory ingestion authorized: {summary.get('memory_ingestion_authorized')}")
    print(f"direct Y* mutation authorized: {summary.get('direct_y_star_mutation_authorized')}")
    print(f"next step: {summary.get('next_step')}")
    print(f"generated mission report: {summary.get('generated_mission_report')}")
    print(f"generated review packet: {summary.get('generated_review_packet')}")
    print(f"generated capability gap closure: {summary.get('generated_capability_gap_closure')}")
    print(f"generated no-side-effect receipt: {summary.get('generated_no_side_effect_receipt')}")
    print(f"generated readiness: {summary.get('generated_readiness')}")
    print(f"warning: {summary.get('warning')}")


def cmd_real_evidence_conflict_resolution_sprint(data: dict[str, Any]) -> None:
    summary = data["l6_14_real_evidence_conflict_resolution"]
    print("# L6.14 Real Evidence Conflict Resolution Sprint")
    print()
    print(
        "L6.14 complete: "
        f"{summary.get('l6_14_real_evidence_conflict_resolution_sprint_complete')}"
    )
    print(f"mode: {summary.get('mode')}")
    print(f"prior run classification: {summary.get('prior_run_classification')}")
    print(f"post-second-pass classification: {summary.get('post_second_pass_classification')}")
    print(f"selected work order id: {summary.get('selected_work_order_id')}")
    print(f"backend mode: {summary.get('backend_mode')}")
    print(f"page-read mode: {summary.get('page_read_mode')}")
    print(f"network allowed: {summary.get('network_allowed')}")
    print(f"safety preflight decision: {summary.get('safety_preflight_decision')}")
    print(f"second-pass real observation executed: {summary.get('second_pass_real_observation_executed')}")
    print(f"second-pass queries generated: {summary.get('second_pass_queries_generated')}")
    print(f"search results considered: {summary.get('search_results_considered')}")
    print(f"pages opened: {summary.get('pages_opened')}")
    print(f"domains touched: {summary.get('domains_touched')}")
    print(f"crawl depth used: {summary.get('crawl_depth_used')}")
    print(f"external reads used: {summary.get('external_reads_used')}")
    print(f"prior real evidence packets: {summary.get('prior_real_evidence_packets')}")
    print(f"new real evidence packets: {summary.get('new_real_evidence_packets')}")
    print(f"total real evidence packets: {summary.get('total_real_evidence_packets')}")
    print(f"conflicts before: {summary.get('conflicts_before')}")
    print(f"conflicts after: {summary.get('conflicts_after')}")
    print(f"unresolved claims before: {summary.get('unresolved_claims_before')}")
    print(f"unresolved claims after: {summary.get('unresolved_claims_after')}")
    print(f"conflict resolution status: {summary.get('conflict_resolution_status')}")
    print(f"next action recommendation: {summary.get('next_action_recommendation')}")
    print(f"blockers: {summary.get('blockers')}")
    print(f"ask-user-URL occurred: {summary.get('ask_user_for_url_occurred')}")
    print(f"external side effects occurred: {summary.get('external_side_effects_occurred')}")
    print(f"core writeback occurred: {summary.get('core_writeback_occurred')}")
    print(f"Y-star-gov modified: {summary.get('y_star_gov_modified')}")
    print(f"gov-mcp modified: {summary.get('gov_mcp_modified')}")
    print(f"search snippets used as evidence: {summary.get('search_snippets_used_as_evidence')}")
    print(f"page-read content used as evidence: {summary.get('page_read_content_used_as_evidence')}")
    print(f"login authorized: {summary.get('login_authorized')}")
    print(f"payment authorized: {summary.get('payment_authorized')}")
    print(f"form submission authorized: {summary.get('form_submission_authorized')}")
    print(f"posting authorized: {summary.get('posting_authorized')}")
    print(f"publication authorized: {summary.get('publication_authorized')}")
    print(f"outreach authorized: {summary.get('outreach_authorized')}")
    print(f"revenue execution authorized: {summary.get('revenue_execution_authorized')}")
    print(f"MCP execution authorized: {summary.get('mcp_execution_authorized')}")
    print(f"live behavior authorized: {summary.get('live_behavior_authorized')}")
    print(f"CIEU DB write authorized: {summary.get('cieu_db_write_authorized')}")
    print(f"canonical update authorized: {summary.get('canonical_update_authorized')}")
    print(f"brain writeback authorized: {summary.get('brain_writeback_authorized')}")
    print(f"memory ingestion authorized: {summary.get('memory_ingestion_authorized')}")
    print(f"direct Y* mutation authorized: {summary.get('direct_y_star_mutation_authorized')}")
    print(f"generated updated mission report: {summary.get('generated_updated_mission_report')}")
    print(f"generated conflict decision packet: {summary.get('generated_conflict_decision_packet')}")
    print(f"generated next action packet: {summary.get('generated_next_action_packet')}")
    print(f"generated no-side-effect receipt: {summary.get('generated_no_side_effect_receipt')}")
    print(f"generated readiness: {summary.get('generated_readiness')}")
    print(f"warning: {summary.get('warning')}")


def cmd_human_review_decision_boundary_sprint(data: dict[str, Any]) -> None:
    summary = data["l6_15_human_review_decision_boundary"]
    print("# L6.15 Human Review Decision Boundary Sprint")
    print()
    print(
        "L6.15 complete: "
        f"{summary.get('l6_15_human_review_decision_boundary_sprint_complete')}"
    )
    print(f"mode: {summary.get('mode')}")
    print(f"prior classification: {summary.get('prior_classification')}")
    print(f"L6.14 conflict status: {summary.get('l6_14_conflict_status')}")
    print(f"L6.15 review status: {summary.get('l6_15_review_status')}")
    print(f"selected work order id: {summary.get('selected_work_order_id')}")
    print(f"evidence packets considered: {summary.get('evidence_packets_considered')}")
    print(f"usable claims: {summary.get('usable_claims')}")
    print(f"caveated claims: {summary.get('caveated_claims')}")
    print(f"human-review-required claims: {summary.get('human_review_required_claims')}")
    print(f"not-usable claims: {summary.get('not_usable_claims')}")
    print(f"bounded conflicts: {summary.get('bounded_conflicts')}")
    print(f"governed planning candidates: {summary.get('governed_planning_candidates')}")
    print(f"blocked external actions: {summary.get('blocked_external_actions')}")
    print(f"blocked core writebacks: {summary.get('blocked_core_writebacks')}")
    print(f"next recommended safe step: {summary.get('next_recommended_safe_step')}")
    print(f"blockers: {summary.get('blockers')}")
    print(f"ask-user-URL occurred: {summary.get('ask_user_for_url_occurred')}")
    print(f"external side effects occurred: {summary.get('external_side_effects_occurred')}")
    print(f"core writeback occurred: {summary.get('core_writeback_occurred')}")
    print(f"Y-star-gov modified: {summary.get('y_star_gov_modified')}")
    print(f"gov-mcp modified: {summary.get('gov_mcp_modified')}")
    print(f"login authorized: {summary.get('login_authorized')}")
    print(f"payment authorized: {summary.get('payment_authorized')}")
    print(f"form submission authorized: {summary.get('form_submission_authorized')}")
    print(f"posting authorized: {summary.get('posting_authorized')}")
    print(f"publication authorized: {summary.get('publication_authorized')}")
    print(f"outreach authorized: {summary.get('outreach_authorized')}")
    print(
        "grant/RFP/bounty submission authorized: "
        f"{summary.get('grant_rfp_bounty_submission_authorized')}"
    )
    print(f"revenue execution authorized: {summary.get('revenue_execution_authorized')}")
    print(f"MCP execution authorized: {summary.get('mcp_execution_authorized')}")
    print(f"live behavior authorized: {summary.get('live_behavior_authorized')}")
    print(f"CIEU DB write authorized: {summary.get('cieu_db_write_authorized')}")
    print(f"canonical update authorized: {summary.get('canonical_update_authorized')}")
    print(f"brain writeback authorized: {summary.get('brain_writeback_authorized')}")
    print(f"memory ingestion authorized: {summary.get('memory_ingestion_authorized')}")
    print(f"direct Y* mutation authorized: {summary.get('direct_y_star_mutation_authorized')}")
    print(f"generated human review packet: {summary.get('generated_human_review_packet')}")
    print(
        "generated evidence usability assessment: "
        f"{summary.get('generated_evidence_usability_assessment')}"
    )
    print(
        "generated planning eligibility matrix: "
        f"{summary.get('generated_planning_eligibility_matrix')}"
    )
    print(
        "generated governed planning candidates: "
        f"{summary.get('generated_governed_planning_candidates')}"
    )
    print(f"generated decision boundary packet: {summary.get('generated_decision_boundary_packet')}")
    print(f"generated human approval gate: {summary.get('generated_human_approval_gate')}")
    print(f"generated residual risk register: {summary.get('generated_residual_risk_register')}")
    print(f"generated no-side-effect receipt: {summary.get('generated_no_side_effect_receipt')}")
    print(f"generated readiness: {summary.get('generated_readiness')}")
    print(f"warning: {summary.get('warning')}")


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
    autonomous_cycle = data.get("autonomous_cycle", {})
    if autonomous_cycle:
        print()
        print("Company autonomous work cycle:")
        print(f"- {autonomous_cycle.get('generated_summary')}")
        print(f"- {autonomous_cycle.get('generated_report')}")
    legacy_triage = data.get("legacy_triage", {})
    if legacy_triage:
        print()
        print("Legacy asset triage:")
        print(f"- {legacy_triage.get('generated_summary')}")
        print(f"- {legacy_triage.get('generated_report')}")
    observation_loop = data.get("observation_loop", {})
    if observation_loop:
        print()
        print("Governed observation loop:")
        print(f"- {observation_loop.get('generated_summary')}")
        print(f"- {observation_loop.get('generated_report')}")
    readonly_tool = data.get("readonly_tool", {})
    if readonly_tool:
        print()
        print("Governed read-only observation tool:")
        print(f"- {readonly_tool.get('generated_summary')}")
        print(f"- {readonly_tool.get('generated_contract')}")
        print(f"- {readonly_tool.get('generated_registry')}")
    tool_bridge = data.get("tool_bridge", {})
    if tool_bridge:
        print()
        print("Governed tool invocation bridge:")
        print(f"- {tool_bridge.get('generated_summary')}")
        print(f"- {tool_bridge.get('generated_contract')}")
        print(f"- {tool_bridge.get('generated_pre_u_packet')}")
        print(f"- {tool_bridge.get('generated_bridged_result')}")
    work_proposal = data.get("work_proposal", {})
    if work_proposal:
        print()
        print("Agent team work proposal:")
        print(f"- {work_proposal.get('generated_summary')}")
        print(f"- {work_proposal.get('generated_tool_request')}")
        print(f"- {work_proposal.get('generated_bridge_trace')}")
        print(f"- {work_proposal.get('generated_bridged_result_ref')}")
    dashboard_refresh = data.get("dashboard_refresh", {})
    if dashboard_refresh:
        print()
        print("Mission dashboard refresh loop:")
        print(f"- {dashboard_refresh.get('generated_summary')}")
        print(f"- {dashboard_refresh.get('generated_refreshed_dashboard')}")
        print(f"- {dashboard_refresh.get('generated_company_state_delta')}")
    recurring_loop = data.get("recurring_loop", {})
    if recurring_loop:
        print()
        print("Governed recurring observation loop contract:")
        print(f"- {recurring_loop.get('generated_summary')}")
        print(f"- {recurring_loop.get('generated_contract')}")
        print(f"- {recurring_loop.get('generated_tick')}")
    manual_tick = data.get("manual_tick", {})
    if manual_tick:
        print()
        print("Manual recurring observation tick runner:")
        print(f"- {manual_tick.get('generated_summary')}")
        print(f"- {manual_tick.get('generated_contract')}")
        print(f"- {manual_tick.get('generated_result')}")
        print(f"- {manual_tick.get('generated_receipt')}")
    field = data.get("field_functional", {})
    if field:
        print()
        print("Field functional archaeology:")
        print(f"- {field.get('generated_summary')}")
        print(f"- {field.get('generated_inventory')}")
        print(f"- {field.get('generated_merge_plan')}")
    mission_projection = data.get("mission_projection", {})
    if mission_projection:
        print()
        print("Mission field projection harness:")
        print(f"- {mission_projection.get('generated_summary')}")
        print(f"- {mission_projection.get('generated_trace')}")
        print(f"- {mission_projection.get('generated_pre_u_candidate')}")
        print(f"- {mission_projection.get('generated_residual_delta')}")
    field_projection = data.get("field_projection", {})
    if field_projection:
        print()
        print("Field functional auto-projection core:")
        print(f"- {field_projection.get('generated_operator_summary')}")
        print(f"- {field_projection.get('generated_projection_summary')}")
        print(f"- {field_projection.get('generated_behavior_candidate')}")
        print(f"- {field_projection.get('generated_pre_u_candidate')}")
        print(f"- {field_projection.get('generated_residual_loop_summary')}")
        print(f"- {field_projection.get('generated_readiness')}")
    projection_cycle = data.get("projection_cycle", {})
    if projection_cycle:
        print()
        print("Projection-checked autonomous work cycle:")
        print(f"- {projection_cycle.get('generated_cycle_summary')}")
        print(f"- {projection_cycle.get('generated_work_summary')}")
        print(f"- {projection_cycle.get('generated_pre_u_summary')}")
        print(f"- {projection_cycle.get('generated_result_summary')}")
        print(f"- {projection_cycle.get('generated_residual_summary')}")
        print(f"- {projection_cycle.get('generated_learning_summary')}")
        print(f"- {projection_cycle.get('generated_readiness')}")
    shadow_learning_cycle = data.get("shadow_learning_cycle", {})
    if shadow_learning_cycle:
        print()
        print("Integrated review-gated shadow learning cycle:")
        print(f"- {shadow_learning_cycle.get('generated_loop_summary')}")
        print(f"- {shadow_learning_cycle.get('generated_review_summary')}")
        print(f"- {shadow_learning_cycle.get('generated_target_summary')}")
        print(f"- {shadow_learning_cycle.get('generated_update_summary')}")
        print(f"- {shadow_learning_cycle.get('generated_shadow_patch_summary')}")
        print(f"- {shadow_learning_cycle.get('generated_reprojection_summary')}")
        print(f"- {shadow_learning_cycle.get('generated_shadow_cycle_summary')}")
        print(f"- {shadow_learning_cycle.get('generated_integrated_cieu_summary')}")
        print(f"- {shadow_learning_cycle.get('generated_readiness')}")
    cross_repo_governance = data.get("cross_repo_governance", {})
    if cross_repo_governance:
        print()
        print("Cross-repo governance contract proof:")
        print(f"- {cross_repo_governance.get('generated_contract_summary')}")
        print(f"- {cross_repo_governance.get('generated_y_star_gov_surface_summary')}")
        print(f"- {cross_repo_governance.get('generated_alignment_summary')}")
        print(f"- {cross_repo_governance.get('generated_gov_mcp_surface_summary')}")
        print(f"- {cross_repo_governance.get('generated_governed_mcp_interface_summary')}")
        print(f"- {cross_repo_governance.get('generated_non_bypass_summary')}")
        print(f"- {cross_repo_governance.get('generated_readiness')}")
    governed_mcp_adapter = data.get("governed_mcp_adapter", {})
    if governed_mcp_adapter:
        print()
        print("Governed MCP dry-run adapter:")
        print(f"- {governed_mcp_adapter.get('generated_adapter_summary')}")
        print(f"- {governed_mcp_adapter.get('generated_intent_summary')}")
        print(f"- {governed_mcp_adapter.get('generated_pre_u_summary')}")
        print(f"- {governed_mcp_adapter.get('generated_decision_summary')}")
        print(f"- {governed_mcp_adapter.get('generated_bridge_summary')}")
        print(f"- {governed_mcp_adapter.get('generated_call_summary')}")
        print(f"- {governed_mcp_adapter.get('generated_receipt_summary')}")
        print(f"- {governed_mcp_adapter.get('generated_residual_summary')}")
        print(f"- {governed_mcp_adapter.get('generated_readiness')}")
    controlled_canonical_learning = data.get("controlled_canonical_learning", {})
    if controlled_canonical_learning:
        print()
        print("Controlled canonical learning design:")
        print(f"- {controlled_canonical_learning.get('generated_design_summary')}")
        print(f"- {controlled_canonical_learning.get('generated_invariant_summary')}")
        print(f"- {controlled_canonical_learning.get('generated_target_summary')}")
        print(f"- {controlled_canonical_learning.get('generated_evidence_summary')}")
        print(f"- {controlled_canonical_learning.get('generated_gate_summary')}")
        print(f"- {controlled_canonical_learning.get('generated_package_summary')}")
        print(f"- {controlled_canonical_learning.get('generated_patch_summary')}")
        print(f"- {controlled_canonical_learning.get('generated_rollback_summary')}")
        print(f"- {controlled_canonical_learning.get('generated_validation_summary')}")
        print(f"- {controlled_canonical_learning.get('generated_promotion_summary')}")
        print(f"- {controlled_canonical_learning.get('generated_readiness')}")
    approved_sandbox_update = data.get("approved_sandbox_update", {})
    if approved_sandbox_update:
        print()
        print("Approved canonical update sandbox:")
        print(f"- {approved_sandbox_update.get('generated_sandbox_summary')}")
        print(f"- {approved_sandbox_update.get('generated_approval_summary')}")
        print(f"- {approved_sandbox_update.get('generated_baseline_summary')}")
        print(f"- {approved_sandbox_update.get('generated_patch_summary')}")
        print(f"- {approved_sandbox_update.get('generated_validation_summary')}")
        print(f"- {approved_sandbox_update.get('generated_reprojection_summary')}")
        print(f"- {approved_sandbox_update.get('generated_cieu_summary')}")
        print(f"- {approved_sandbox_update.get('generated_rollback_summary')}")
        print(f"- {approved_sandbox_update.get('generated_effect_summary')}")
        print(f"- {approved_sandbox_update.get('generated_readiness')}")
    real_approval_workflow = data.get("real_approval_workflow", {})
    if real_approval_workflow:
        print()
        print("Real approval workflow boundary:")
        print(f"- {real_approval_workflow.get('generated_workflow_summary')}")
        print(f"- {real_approval_workflow.get('generated_authority_summary')}")
        print(f"- {real_approval_workflow.get('generated_evidence_summary')}")
        print(f"- {real_approval_workflow.get('generated_record_summary')}")
        print(f"- {real_approval_workflow.get('generated_decision_summary')}")
        print(f"- {real_approval_workflow.get('generated_validity_summary')}")
        print(f"- {real_approval_workflow.get('generated_snapshot_summary')}")
        print(f"- {real_approval_workflow.get('generated_boundary_summary')}")
        print(f"- {real_approval_workflow.get('generated_preflight_summary')}")
        print(f"- {real_approval_workflow.get('generated_runbook_summary')}")
        print(f"- {real_approval_workflow.get('generated_audit_summary')}")
        print(f"- {real_approval_workflow.get('generated_readiness')}")
    approval_record_sandbox = data.get("approval_record_sandbox", {})
    if approval_record_sandbox:
        print()
        print("Controlled approval record sandbox:")
        print(f"- {approval_record_sandbox.get('generated_sandbox_summary')}")
        print(f"- {approval_record_sandbox.get('generated_record_summary')}")
        print(f"- {approval_record_sandbox.get('generated_integrity_summary')}")
        print(f"- {approval_record_sandbox.get('generated_state_machine_summary')}")
        print(f"- {approval_record_sandbox.get('generated_revocation_summary')}")
        print(f"- {approval_record_sandbox.get('generated_gate_summary')}")
        print(f"- {approval_record_sandbox.get('generated_audit_summary')}")
        print(f"- {approval_record_sandbox.get('generated_cieu_summary')}")
        print(f"- {approval_record_sandbox.get('generated_readiness')}")
    real_release_preflight = data.get("real_release_preflight", {})
    if real_release_preflight:
        print()
        print("Controlled real release preflight:")
        print(f"- {real_release_preflight.get('generated_preflight_summary')}")
        print(f"- {real_release_preflight.get('generated_release_candidate_summary')}")
        print(f"- {real_release_preflight.get('generated_scope_summary')}")
        print(f"- {real_release_preflight.get('generated_approval_record_preflight_summary')}")
        print(f"- {real_release_preflight.get('generated_snapshot_rollback_summary')}")
        print(f"- {real_release_preflight.get('generated_invariant_summary')}")
        print(f"- {real_release_preflight.get('generated_post_release_summary')}")
        print(f"- {real_release_preflight.get('generated_handoff_summary')}")
        print(f"- {real_release_preflight.get('generated_blocker_summary')}")
        print(f"- {real_release_preflight.get('generated_cieu_summary')}")
        print(f"- {real_release_preflight.get('generated_readiness')}")
    real_release_simulation = data.get("real_release_simulation", {})
    if real_release_simulation:
        print()
        print("Real release simulation sandbox:")
        print(f"- {real_release_simulation.get('generated_simulation_summary')}")
        print(f"- {real_release_simulation.get('generated_authority_summary')}")
        print(f"- {real_release_simulation.get('generated_simulated_record_summary')}")
        print(f"- {real_release_simulation.get('generated_snapshot_summary')}")
        print(f"- {real_release_simulation.get('generated_plan_summary')}")
        print(f"- {real_release_simulation.get('generated_result_summary')}")
        print(f"- {real_release_simulation.get('generated_validation_summary')}")
        print(f"- {real_release_simulation.get('generated_projection_mcp_summary')}")
        print(f"- {real_release_simulation.get('generated_rollback_summary')}")
        print(f"- {real_release_simulation.get('generated_comparison_summary')}")
        print(f"- {real_release_simulation.get('generated_cieu_summary')}")
        print(f"- {real_release_simulation.get('generated_readiness')}")
    live_boundary_no_go = data.get("live_boundary_no_go", {})
    if live_boundary_no_go:
        print()
        print("Live boundary no-go framework:")
        print(f"- {live_boundary_no_go.get('generated_framework_summary')}")
        print(f"- {live_boundary_no_go.get('generated_capability_summary')}")
        print(f"- {live_boundary_no_go.get('generated_invariant_summary')}")
        print(f"- {live_boundary_no_go.get('generated_evidence_summary')}")
        print(f"- {live_boundary_no_go.get('generated_blocker_summary')}")
        print(f"- {live_boundary_no_go.get('generated_l6_entry_summary')}")
        print(f"- {live_boundary_no_go.get('generated_decision_summary')}")
        print(f"- {live_boundary_no_go.get('generated_cieu_summary')}")
        print(f"- {live_boundary_no_go.get('generated_readiness')}")


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
        AUTONOMOUS_CYCLE,
        LEGACY_TRIAGE,
        OBSERVATION_LOOP,
        READONLY_TOOL,
        TOOL_BRIDGE,
        WORK_PROPOSAL,
        DASHBOARD_REFRESH,
        RECURRING_LOOP,
        MANUAL_TICK,
        FIELD_FUNCTIONAL,
        MISSION_PROJECTION,
        FIELD_PROJECTION,
        PROJECTION_CYCLE,
        SHADOW_LEARNING_CYCLE,
        CROSS_REPO_GOVERNANCE,
        GOVERNED_MCP_ADAPTER,
        CONTROLLED_CANONICAL_LEARNING,
        APPROVED_SANDBOX_UPDATE,
        REAL_APPROVAL_WORKFLOW,
        APPROVAL_RECORD_SANDBOX,
        REAL_RELEASE_PREFLIGHT,
        REAL_RELEASE_SIMULATION,
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
        if "autonomous_cycle_summary" not in snapshot:
            failures.append("autonomous_cycle_summary missing from team console snapshot")
        if "legacy_triage_summary" not in snapshot:
            failures.append("legacy_triage_summary missing from team console snapshot")
        if "observation_loop_summary" not in snapshot:
            failures.append("observation_loop_summary missing from team console snapshot")
        if "readonly_tool_summary" not in snapshot:
            failures.append("readonly_tool_summary missing from team console snapshot")
        if "tool_bridge_summary" not in snapshot:
            failures.append("tool_bridge_summary missing from team console snapshot")
        if "work_proposal_summary" not in snapshot:
            failures.append("work_proposal_summary missing from team console snapshot")
        if "dashboard_refresh_summary" not in snapshot:
            failures.append("dashboard_refresh_summary missing from team console snapshot")
        if "recurring_loop_summary" not in snapshot:
            failures.append("recurring_loop_summary missing from team console snapshot")
        if "manual_tick_summary" not in snapshot:
            failures.append("manual_tick_summary missing from team console snapshot")
        if "field_functional_summary" not in snapshot:
            failures.append("field_functional_summary missing from team console snapshot")
        if "mission_projection_summary" not in snapshot:
            failures.append("mission_projection_summary missing from team console snapshot")
        if "field_projection_summary" not in snapshot:
            failures.append("field_projection_summary missing from team console snapshot")
        if "projection_cycle_summary" not in snapshot:
            failures.append("projection_cycle_summary missing from team console snapshot")
        if "shadow_learning_cycle_summary" not in snapshot:
            failures.append("shadow_learning_cycle_summary missing from team console snapshot")
        if "cross_repo_governance_summary" not in snapshot:
            failures.append("cross_repo_governance_summary missing from team console snapshot")
        if "governed_mcp_adapter_summary" not in snapshot:
            failures.append("governed_mcp_adapter_summary missing from team console snapshot")
        if "controlled_canonical_learning_summary" not in snapshot:
            failures.append("controlled_canonical_learning_summary missing from team console snapshot")
        if "approved_sandbox_update_summary" not in snapshot:
            failures.append("approved_sandbox_update_summary missing from team console snapshot")
        if "real_approval_workflow_summary" not in snapshot:
            failures.append("real_approval_workflow_summary missing from team console snapshot")
        if "controlled_approval_record_summary" not in snapshot:
            failures.append("controlled_approval_record_summary missing from team console snapshot")
        if "controlled_real_release_preflight_summary" not in snapshot:
            failures.append(
                "controlled_real_release_preflight_summary missing from team console snapshot"
            )
        if "real_release_simulation_summary" not in snapshot:
            failures.append("real_release_simulation_summary missing from team console snapshot")
        if "live_boundary_no_go_summary" not in snapshot:
            failures.append("live_boundary_no_go_summary missing from team console snapshot")

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

    autonomous_cycle = loaded.get(AUTONOMOUS_CYCLE)
    if autonomous_cycle:
        required_fields = [
            "autonomous_work_cycle_defined",
            "mission_bounded_autonomy_defined",
            "founder_sets_mission_agent_team_drives",
            "step_by_step_human_prompting_required",
            "observation_snapshot_defined",
            "autonomous_work_backlog_defined",
            "selected_work_item_defined",
            "role_delegation_defined",
            "governed_tool_selection_defined",
            "pre_u_packet_simulated",
            "governance_decision_simulated",
            "action_plan_simulated",
            "cieu_event_simulated",
            "residual_delta_simulated",
            "next_task_recommendations_defined",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "email_or_external_communication_enabled",
            "requires_manual_enablement_for_live",
            "next_required_milestone",
            "generated_summary",
            "generated_report",
            "warning",
        ]
        for field in required_fields:
            if field not in autonomous_cycle:
                failures.append(f"autonomous cycle summary missing field: {field}")
        for field in [
            "autonomous_work_cycle_defined",
            "mission_bounded_autonomy_defined",
            "founder_sets_mission_agent_team_drives",
            "observation_snapshot_defined",
            "autonomous_work_backlog_defined",
            "selected_work_item_defined",
            "role_delegation_defined",
            "governed_tool_selection_defined",
            "pre_u_packet_simulated",
            "governance_decision_simulated",
            "action_plan_simulated",
            "cieu_event_simulated",
            "residual_delta_simulated",
            "next_task_recommendations_defined",
            "requires_manual_enablement_for_live",
        ]:
            if autonomous_cycle.get(field) is not True:
                failures.append(f"autonomous cycle summary must keep {field}=true")
        for field in [
            "step_by_step_human_prompting_required",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "git_push_enabled",
            "daemon_control_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "email_or_external_communication_enabled",
        ]:
            if autonomous_cycle.get(field) is not False:
                failures.append(f"autonomous cycle summary must keep {field}=false")
        if autonomous_cycle.get("next_required_milestone") != "L4.3 Governed Read-Only Observation Loop v0":
            failures.append("autonomous cycle summary must point to L4.3 observation-loop milestone")

    legacy_triage = loaded.get(LEGACY_TRIAGE)
    if legacy_triage:
        required_fields = [
            "legacy_asset_triage_defined",
            "assets_scored",
            "absorption_buckets_defined",
            "bucket_counts",
            "top_absorption_candidates_defined",
            "governed_absorption_backlog_defined",
            "blind_absorption_allowed",
            "blanket_rewrite_allowed",
            "live_actions_enabled",
            "next_required_milestone",
            "generated_summary",
            "generated_report",
            "warning",
        ]
        for field in required_fields:
            if field not in legacy_triage:
                failures.append(f"legacy triage summary missing field: {field}")
        for field in [
            "legacy_asset_triage_defined",
            "absorption_buckets_defined",
            "top_absorption_candidates_defined",
            "governed_absorption_backlog_defined",
        ]:
            if legacy_triage.get(field) is not True:
                failures.append(f"legacy triage summary must keep {field}=true")
        for field in ["blind_absorption_allowed", "blanket_rewrite_allowed", "live_actions_enabled"]:
            if legacy_triage.get(field) is not False:
                failures.append(f"legacy triage summary must keep {field}=false")
        if not legacy_triage.get("assets_scored", 0) > 0:
            failures.append("legacy triage summary must score assets")
        if legacy_triage.get("next_required_milestone") != "L4.4 First Governed Read-Only Observation Tool Wrapper v0":
            failures.append("legacy triage summary must point to L4.4 wrapper milestone")

    observation_loop = loaded.get(OBSERVATION_LOOP)
    if observation_loop:
        required_fields = [
            "governed_observation_loop_defined",
            "read_only_observation_loop_defined",
            "observation_source_registry_defined",
            "observation_tick_generated",
            "mission_dashboard_snapshot_defined",
            "company_state_digest_defined",
            "observation_to_work_item_candidates_defined",
            "mission_bounded_autonomy_supported",
            "step_by_step_human_prompting_reduced",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "next_required_milestone",
            "generated_summary",
            "generated_report",
            "warning",
        ]
        for field in required_fields:
            if field not in observation_loop:
                failures.append(f"observation loop summary missing field: {field}")
        for field in [
            "governed_observation_loop_defined",
            "read_only_observation_loop_defined",
            "observation_source_registry_defined",
            "observation_tick_generated",
            "mission_dashboard_snapshot_defined",
            "company_state_digest_defined",
            "observation_to_work_item_candidates_defined",
            "mission_bounded_autonomy_supported",
            "step_by_step_human_prompting_reduced",
        ]:
            if observation_loop.get(field) is not True:
                failures.append(f"observation loop summary must keep {field}=true")
        for field in [
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
        ]:
            if observation_loop.get(field) is not False:
                failures.append(f"observation loop summary must keep {field}=false")
        if observation_loop.get("next_required_milestone") != "L4.4 First Governed Read-Only Observation Tool Wrapper v0":
            failures.append("observation loop summary must point to L4.4 wrapper milestone")

    readonly_tool = loaded.get(READONLY_TOOL)
    if readonly_tool:
        required_fields = [
            "governed_readonly_observation_tool_defined",
            "tool_contract_defined",
            "allowed_source_registry_defined",
            "sample_invocation_defined",
            "sample_result_defined",
            "unsafe_invocation_rejected",
            "tool_cieu_event_defined",
            "local_readonly_dry_run_callable",
            "first_governed_tool_wrapper_created",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "next_required_milestone",
            "warning",
        ]
        for field in required_fields:
            if field not in readonly_tool:
                failures.append(f"readonly tool summary missing field: {field}")
        for field in [
            "governed_readonly_observation_tool_defined",
            "tool_contract_defined",
            "allowed_source_registry_defined",
            "sample_invocation_defined",
            "sample_result_defined",
            "unsafe_invocation_rejected",
            "tool_cieu_event_defined",
            "local_readonly_dry_run_callable",
            "first_governed_tool_wrapper_created",
        ]:
            if readonly_tool.get(field) is not True:
                failures.append(f"readonly tool summary must keep {field}=true")
        for field in [
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
        ]:
            if readonly_tool.get(field) is not False:
                failures.append(f"readonly tool summary must keep {field}=false")
        if readonly_tool.get("next_required_milestone") != "L4.5 Governed Tool Invocation Through Pre-U Bridge v0":
            failures.append("readonly tool summary must point to L4.5 Pre-U bridge milestone")

    tool_bridge = loaded.get(TOOL_BRIDGE)
    if tool_bridge:
        required_fields = [
            "governed_tool_invocation_bridge_defined",
            "bridge_contract_defined",
            "agent_tool_request_defined",
            "pre_u_tool_packet_defined",
            "governance_decision_defined",
            "bridge_authorization_defined",
            "tool_invoked_through_bridge",
            "direct_tool_invocation_rejected",
            "unsafe_bridge_request_rejected",
            "bridge_cieu_event_defined",
            "bridge_residual_delta_defined",
            "first_governed_tool_invocation_chain_created",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "next_required_milestone",
            "warning",
        ]
        for field in required_fields:
            if field not in tool_bridge:
                failures.append(f"tool bridge summary missing field: {field}")
        for field in [
            "governed_tool_invocation_bridge_defined",
            "bridge_contract_defined",
            "agent_tool_request_defined",
            "pre_u_tool_packet_defined",
            "governance_decision_defined",
            "bridge_authorization_defined",
            "tool_invoked_through_bridge",
            "direct_tool_invocation_rejected",
            "unsafe_bridge_request_rejected",
            "bridge_cieu_event_defined",
            "bridge_residual_delta_defined",
            "first_governed_tool_invocation_chain_created",
        ]:
            if tool_bridge.get(field) is not True:
                failures.append(f"tool bridge summary must keep {field}=true")
        for field in [
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
        ]:
            if tool_bridge.get(field) is not False:
                failures.append(f"tool bridge summary must keep {field}=false")
        if tool_bridge.get("next_required_milestone") != "L4.6 Agent Team Work Proposal to Governed Tool Invocation v0":
            failures.append("tool bridge summary must point to L4.6 agent proposal bridge milestone")

    work_proposal = loaded.get(WORK_PROPOSAL)
    if work_proposal:
        required_fields = [
            "agent_team_work_proposal_defined",
            "mission_context_snapshot_defined",
            "agent_team_observation_input_defined",
            "autonomous_work_proposals_defined",
            "selected_work_proposal_defined",
            "role_review_board_defined",
            "tool_need_analysis_defined",
            "generated_tool_request_defined",
            "work_proposal_routed_to_bridge",
            "direct_tool_invocation_used",
            "bridged_tool_result_ref_defined",
            "work_proposal_cieu_event_defined",
            "work_proposal_residual_delta_defined",
            "agent_team_generated_the_work",
            "agent_team_selected_governed_tool",
            "pre_u_bridge_required",
            "pre_u_bridge_satisfied",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "next_required_milestone",
            "warning",
        ]
        for field in required_fields:
            if field not in work_proposal:
                failures.append(f"work proposal summary missing field: {field}")
        for field in [
            "agent_team_work_proposal_defined",
            "mission_context_snapshot_defined",
            "agent_team_observation_input_defined",
            "autonomous_work_proposals_defined",
            "selected_work_proposal_defined",
            "role_review_board_defined",
            "tool_need_analysis_defined",
            "generated_tool_request_defined",
            "work_proposal_routed_to_bridge",
            "bridged_tool_result_ref_defined",
            "work_proposal_cieu_event_defined",
            "work_proposal_residual_delta_defined",
            "agent_team_generated_the_work",
            "agent_team_selected_governed_tool",
            "pre_u_bridge_required",
            "pre_u_bridge_satisfied",
        ]:
            if work_proposal.get(field) is not True:
                failures.append(f"work proposal summary must keep {field}=true")
        for field in [
            "direct_tool_invocation_used",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
        ]:
            if work_proposal.get(field) is not False:
                failures.append(f"work proposal summary must keep {field}=false")
        if work_proposal.get("next_required_milestone") != "L4.7 First Mission Dashboard Refresh Loop v0":
            failures.append("work proposal summary must point to L4.7 mission dashboard refresh milestone")

    recurring_loop = loaded.get(RECURRING_LOOP)
    if recurring_loop:
        required_fields = [
            "recurring_observation_loop_contract_defined",
            "recurrence_policy_defined",
            "recurrence_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "auto_run_enabled",
            "manual_local_simulation_only",
            "allowed_observation_sources_defined",
            "tick_governance_gate_defined",
            "simulated_observation_tick_defined",
            "simulated_tick_cieu_event_defined",
            "simulated_tick_residual_delta_defined",
            "stop_abort_conditions_defined",
            "escalation_conditions_defined",
            "manual_enablement_checklist_defined",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "next_required_milestone",
            "warning",
        ]
        for field in required_fields:
            if field not in recurring_loop:
                failures.append(f"recurring loop summary missing field: {field}")
        for field in [
            "recurring_observation_loop_contract_defined",
            "recurrence_policy_defined",
            "manual_local_simulation_only",
            "allowed_observation_sources_defined",
            "tick_governance_gate_defined",
            "simulated_observation_tick_defined",
            "simulated_tick_cieu_event_defined",
            "simulated_tick_residual_delta_defined",
            "stop_abort_conditions_defined",
            "escalation_conditions_defined",
            "manual_enablement_checklist_defined",
        ]:
            if recurring_loop.get(field) is not True:
                failures.append(f"recurring loop summary must keep {field}=true")
        for field in [
            "recurrence_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "auto_run_enabled",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
        ]:
            if recurring_loop.get(field) is not False:
                failures.append(f"recurring loop summary must keep {field}=false")
        if recurring_loop.get("next_required_milestone") != "L4.9 Manual Recurring Observation Tick Runner v0":
            failures.append("recurring loop summary must point to L4.9 manual tick runner milestone")

    manual_tick = loaded.get(MANUAL_TICK)
    if manual_tick:
        required_fields = [
            "manual_recurring_observation_tick_runner_defined",
            "manual_tick_runner_contract_defined",
            "manual_tick_request_defined",
            "manual_tick_preflight_defined",
            "manual_tick_source_validation_defined",
            "manual_tick_governance_decision_defined",
            "manual_tick_result_defined",
            "manual_tick_dashboard_delta_defined",
            "manual_tick_work_candidates_defined",
            "manual_tick_cieu_event_defined",
            "manual_tick_residual_delta_defined",
            "manual_tick_run_receipt_defined",
            "manual_tick_history_index_defined",
            "manual_tick_next_recommendations_defined",
            "manual_trigger_required",
            "one_tick_per_invocation",
            "total_recorded_ticks",
            "recurrence_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "auto_run_enabled",
            "manual_local_run_only",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "next_required_milestone",
            "warning",
        ]
        for field in required_fields:
            if field not in manual_tick:
                failures.append(f"manual tick summary missing field: {field}")
        for field in [
            "manual_recurring_observation_tick_runner_defined",
            "manual_tick_runner_contract_defined",
            "manual_tick_request_defined",
            "manual_tick_preflight_defined",
            "manual_tick_source_validation_defined",
            "manual_tick_governance_decision_defined",
            "manual_tick_result_defined",
            "manual_tick_dashboard_delta_defined",
            "manual_tick_work_candidates_defined",
            "manual_tick_cieu_event_defined",
            "manual_tick_residual_delta_defined",
            "manual_tick_run_receipt_defined",
            "manual_tick_history_index_defined",
            "manual_tick_next_recommendations_defined",
            "manual_trigger_required",
            "one_tick_per_invocation",
            "manual_local_run_only",
        ]:
            if manual_tick.get(field) is not True:
                failures.append(f"manual tick summary must keep {field}=true")
        for field in [
            "recurrence_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "auto_run_enabled",
            "real_action_executed",
            "external_action_executed",
            "live_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
        ]:
            if manual_tick.get(field) is not False:
                failures.append(f"manual tick summary must keep {field}=false")
        if manual_tick.get("total_recorded_ticks") != 1:
            failures.append("manual tick summary must record exactly one tick")
        if manual_tick.get("next_required_milestone") != "L5.0 Review-Gated Learning Candidate Queue v0":
            failures.append("manual tick summary must point to L5.0 review-gated learning milestone")

    field_functional = loaded.get(FIELD_FUNCTIONAL)
    if field_functional:
        required_fields = [
            "field_functional_archaeology_defined",
            "repos_scanned",
            "assets_scanned",
            "field_functional_assets_found",
            "reuse_candidates_count",
            "wrap_candidates_count",
            "rewrite_candidates_count",
            "concept_reference_count",
            "do_not_absorb_count",
            "old_field_functional_work_found",
            "mission_projection_merge_plan_defined",
            "ready_for_L5_projection_harness",
            "live_action_enabled",
            "external_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "next_required_milestone",
            "warning",
        ]
        for field in required_fields:
            if field not in field_functional:
                failures.append(f"field functional summary missing field: {field}")
        for field in [
            "field_functional_archaeology_defined",
            "old_field_functional_work_found",
            "mission_projection_merge_plan_defined",
            "ready_for_L5_projection_harness",
        ]:
            if field_functional.get(field) is not True:
                failures.append(f"field functional summary must keep {field}=true")
        for field in [
            "live_action_enabled",
            "external_action_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
        ]:
            if field_functional.get(field) is not False:
                failures.append(f"field functional summary must keep {field}=false")
        if field_functional.get("field_functional_assets_found", 0) <= 0:
            failures.append("field functional summary must find at least one asset")
        if field_functional.get("next_required_milestone") != (
            "L5.1 Mission Field Functional Projection Harness v0"
        ):
            failures.append("field functional summary must point to L5.1 projection harness milestone")

    mission_projection = loaded.get(MISSION_PROJECTION)
    if mission_projection:
        required_fields = [
            "mission_field_projection_harness_defined",
            "l5_1_projection_contract_defined",
            "layered_projection_trace_generated",
            "pre_u_adapter_candidate_generated",
            "residual_delta_fixture_generated",
            "action_layer_projection_only",
            "action_field_execution_implemented",
            "ready_for_L5_2_field_functional_auto_projection_core",
            "deep_xt_model_is_not_l5_2_main_milestone",
            "live_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "next_required_milestone",
            "warning",
        ]
        for field in required_fields:
            if field not in mission_projection:
                failures.append(f"mission projection summary missing field: {field}")
        for field in [
            "mission_field_projection_harness_defined",
            "l5_1_projection_contract_defined",
            "layered_projection_trace_generated",
            "pre_u_adapter_candidate_generated",
            "residual_delta_fixture_generated",
            "action_layer_projection_only",
            "ready_for_L5_2_field_functional_auto_projection_core",
            "deep_xt_model_is_not_l5_2_main_milestone",
        ]:
            if mission_projection.get(field) is not True:
                failures.append(f"mission projection summary must keep {field}=true")
        for field in [
            "action_field_execution_implemented",
            "live_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
        ]:
            if mission_projection.get(field) is not False:
                failures.append(f"mission projection summary must keep {field}=false")
        if mission_projection.get("next_required_milestone") != (
            "L5.2 Field Functional Auto-Projection Core v0"
        ):
            failures.append("mission projection summary must point to L5.2 auto-projection core milestone")

    field_projection = loaded.get(FIELD_PROJECTION)
    if field_projection:
        required_fields = [
            "field_functional_auto_projection_core_defined",
            "projection_operator_defined",
            "mission_level_y_star_input_defined",
            "mission_to_behavior_projection_generated",
            "projection_layers",
            "behavior_level_y_star_candidate_generated",
            "pre_u_packet_candidate_from_behavior_y_star_generated",
            "residual_delta_loop_fixture_generated",
            "learning_candidate_stub_generated_but_not_approved",
            "live_execution_still_blocked",
            "writeback_still_blocked",
            "external_action_still_blocked",
            "ready_for_l5_3_projection_checked_autonomous_cycle",
            "l6_revenue_opportunity_discovery_enabled",
            "dry_run_only",
            "pre_u_production_ready",
            "live_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "behavior_execution_enabled",
            "next_required_milestone",
            "warning",
        ]
        for field in required_fields:
            if field not in field_projection:
                failures.append(f"field projection summary missing field: {field}")
        for field in [
            "field_functional_auto_projection_core_defined",
            "projection_operator_defined",
            "mission_level_y_star_input_defined",
            "mission_to_behavior_projection_generated",
            "behavior_level_y_star_candidate_generated",
            "pre_u_packet_candidate_from_behavior_y_star_generated",
            "residual_delta_loop_fixture_generated",
            "learning_candidate_stub_generated_but_not_approved",
            "live_execution_still_blocked",
            "writeback_still_blocked",
            "external_action_still_blocked",
            "ready_for_l5_3_projection_checked_autonomous_cycle",
            "dry_run_only",
        ]:
            if field_projection.get(field) is not True:
                failures.append(f"field projection summary must keep {field}=true")
        if field_projection.get("projection_layers") != [
            "mission",
            "company",
            "milestone",
            "session",
            "task",
            "behavior",
        ]:
            failures.append("field projection summary must use mission/company/milestone/session/task/behavior layers")
        for field in [
            "l6_revenue_opportunity_discovery_enabled",
            "pre_u_production_ready",
            "live_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "behavior_execution_enabled",
        ]:
            if field_projection.get(field) is not False:
                failures.append(f"field projection summary must keep {field}=false")
        if field_projection.get("next_required_milestone") != (
            "L5.3 Projection-Checked Autonomous Work Cycle v0"
        ):
            failures.append("field projection summary must point to L5.3 projection-checked cycle milestone")

    projection_cycle = loaded.get(PROJECTION_CYCLE)
    if projection_cycle:
        required_fields = [
            "projection_checked_autonomous_work_cycle_defined",
            "behavior_y_star_consumed_by_cycle",
            "work_proposal_checked_against_behavior_y_star",
            "pre_u_packet_candidate_generated",
            "dry_run_gate_decision_generated",
            "dry_run_result_generated",
            "cieu_like_event_fixture_generated",
            "residual_delta_generated",
            "learning_review_candidate_generated_but_not_approved",
            "ready_for_l5_4_review_gated_learning_loop",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "next_required_milestone",
            "warning",
        ]
        for field in required_fields:
            if field not in projection_cycle:
                failures.append(f"projection cycle summary missing field: {field}")
        for field in [
            "projection_checked_autonomous_work_cycle_defined",
            "behavior_y_star_consumed_by_cycle",
            "work_proposal_checked_against_behavior_y_star",
            "pre_u_packet_candidate_generated",
            "dry_run_gate_decision_generated",
            "dry_run_result_generated",
            "cieu_like_event_fixture_generated",
            "residual_delta_generated",
            "learning_review_candidate_generated_but_not_approved",
            "ready_for_l5_4_review_gated_learning_loop",
            "dry_run_only",
        ]:
            if projection_cycle.get(field) is not True:
                failures.append(f"projection cycle summary must keep {field}=true")
        for field in [
            "pre_u_production_ready",
            "real_execution_performed",
            "db_write_performed",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
        ]:
            if projection_cycle.get(field) is not False:
                failures.append(f"projection cycle summary must keep {field}=false")
        if projection_cycle.get("next_required_milestone") != "L5.4 Review-Gated Learning Loop v0":
            failures.append("projection cycle summary must point to L5.4 review-gated learning loop")

    shadow_learning_cycle = loaded.get(SHADOW_LEARNING_CYCLE)
    if shadow_learning_cycle:
        required_fields = [
            "integrated_review_gated_shadow_learning_cycle_defined",
            "l5_3_residual_consumed",
            "deterministic_review_gate_decision_generated",
            "review_gate_decision",
            "learning_target_classification_generated",
            "projection_policy_update_candidate_generated",
            "shadow_projection_policy_patch_generated",
            "shadow_behavior_y_star_preview_generated",
            "shadow_updated_projection_cycle_generated",
            "shadow_cycle_cieu_fixture_generated",
            "original_vs_shadow_cycle_comparison_generated",
            "integrated_cieu_like_fixture_generated",
            "candidate_approved",
            "candidate_applied",
            "canonical_policy_mutation_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "previous_residual_influenced_shadow_projection",
            "ready_for_controlled_canonical_learning_design",
            "ready_for_l6_revenue_opportunity_discovery",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "cieu_persistence_enabled",
            "candidate_auto_approval_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "shadow_patch_live_application_enabled",
            "shadow_patch_preview_only",
            "shadow_cycle_real_execution_performed",
            "shadow_cycle_db_write_performed",
            "integrated_cieu_db_write_performed",
            "next_required_milestone",
            "warning",
        ]
        for field in required_fields:
            if field not in shadow_learning_cycle:
                failures.append(f"shadow learning cycle summary missing field: {field}")
        for field in [
            "integrated_review_gated_shadow_learning_cycle_defined",
            "l5_3_residual_consumed",
            "deterministic_review_gate_decision_generated",
            "learning_target_classification_generated",
            "projection_policy_update_candidate_generated",
            "shadow_projection_policy_patch_generated",
            "shadow_behavior_y_star_preview_generated",
            "shadow_updated_projection_cycle_generated",
            "shadow_cycle_cieu_fixture_generated",
            "original_vs_shadow_cycle_comparison_generated",
            "integrated_cieu_like_fixture_generated",
            "previous_residual_influenced_shadow_projection",
            "ready_for_controlled_canonical_learning_design",
            "shadow_patch_preview_only",
        ]:
            if shadow_learning_cycle.get(field) is not True:
                failures.append(f"shadow learning cycle summary must keep {field}=true")
        for field in [
            "candidate_approved",
            "candidate_applied",
            "canonical_policy_mutation_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "ready_for_l6_revenue_opportunity_discovery",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "cieu_persistence_enabled",
            "candidate_auto_approval_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "shadow_patch_live_application_enabled",
            "shadow_cycle_real_execution_performed",
            "shadow_cycle_db_write_performed",
            "integrated_cieu_db_write_performed",
        ]:
            if shadow_learning_cycle.get(field) is not False:
                failures.append(f"shadow learning cycle summary must keep {field}=false")
        if shadow_learning_cycle.get("review_gate_decision") != "eligible_for_shadow_update_candidate":
            failures.append("shadow learning cycle review gate must allow shadow update candidate only")
        if shadow_learning_cycle.get("next_required_milestone") != (
            "Controlled Canonical Learning Architecture v0"
        ):
            failures.append("shadow learning cycle summary must point to controlled canonical learning")

    cross_repo_governance = loaded.get(CROSS_REPO_GOVERNANCE)
    if cross_repo_governance:
        required_fields = [
            "cross_repo_governance_contract_proof_defined",
            "y_star_gov_surfaces_inventoried_read_only",
            "gov_mcp_surfaces_inventoried_read_only",
            "behavior_y_star_mapped_to_governance_contract",
            "pre_u_candidates_mapped_to_validator_expectations",
            "cieu_fixtures_mapped_to_prediction_delta_expectations",
            "gov_mcp_boundary_mapped",
            "non_bypass_invariants_defined",
            "bypass_risks_identified",
            "no_non_ystar_company_repo_modified",
            "no_mcp_server_or_tool_executed",
            "ready_for_l5_6_governed_mcp_dry_run_adapter",
            "ready_for_l6_revenue_opportunity_discovery",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "canonical_policy_mutation_enabled",
            "y_star_gov_modification_enabled",
            "gov_mcp_modification_enabled",
            "mcp_tool_execution_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
            "next_required_milestone",
            "warning",
        ]
        for field in required_fields:
            if field not in cross_repo_governance:
                failures.append(f"cross-repo governance summary missing field: {field}")
        for field in [
            "cross_repo_governance_contract_proof_defined",
            "y_star_gov_surfaces_inventoried_read_only",
            "gov_mcp_surfaces_inventoried_read_only",
            "behavior_y_star_mapped_to_governance_contract",
            "pre_u_candidates_mapped_to_validator_expectations",
            "cieu_fixtures_mapped_to_prediction_delta_expectations",
            "gov_mcp_boundary_mapped",
            "non_bypass_invariants_defined",
            "bypass_risks_identified",
            "no_non_ystar_company_repo_modified",
            "no_mcp_server_or_tool_executed",
            "ready_for_l5_6_governed_mcp_dry_run_adapter",
        ]:
            if cross_repo_governance.get(field) is not True:
                failures.append(f"cross-repo governance summary must keep {field}=true")
        for field in [
            "ready_for_l6_revenue_opportunity_discovery",
            "live_execution_enabled",
            "behavior_execution_enabled",
            "external_action_enabled",
            "network_enabled",
            "scheduler_enabled",
            "daemon_enabled",
            "cieu_persistence_enabled",
            "brain_writeback_enabled",
            "memory_ingestion_enabled",
            "candidate_auto_approval_enabled",
            "canonical_policy_mutation_enabled",
            "y_star_gov_modification_enabled",
            "gov_mcp_modification_enabled",
            "mcp_tool_execution_enabled",
            "semantic_truth_scoring_enabled",
            "raw_runtime_artifact_reading_enabled",
            "revenue_opportunity_discovery_enabled",
        ]:
            if cross_repo_governance.get(field) is not False:
                failures.append(f"cross-repo governance summary must keep {field}=false")
        if cross_repo_governance.get("next_required_milestone") != (
            "L5.6 Governed MCP Dry-Run Adapter v0"
        ):
            failures.append("cross-repo governance summary must point to L5.6")

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
    elif command == "autonomous-cycle":
        cmd_autonomous_cycle(data)
    elif command == "legacy-triage":
        cmd_legacy_triage(data)
    elif command == "observation-loop":
        cmd_observation_loop(data)
    elif command == "readonly-tool":
        cmd_readonly_tool(data)
    elif command == "tool-bridge":
        cmd_tool_bridge(data)
    elif command == "work-proposal":
        cmd_work_proposal(data)
    elif command == "dashboard-refresh":
        cmd_dashboard_refresh(data)
    elif command == "recurring-loop":
        cmd_recurring_loop(data)
    elif command == "manual-tick":
        cmd_manual_tick(data)
    elif command == "field-functional":
        cmd_field_functional(data)
    elif command == "mission-projection":
        cmd_mission_projection(data)
    elif command == "field-projection":
        cmd_field_projection(data)
    elif command == "projection-cycle":
        cmd_projection_cycle(data)
    elif command == "shadow-learning-cycle":
        cmd_shadow_learning_cycle(data)
    elif command == "cross-repo-governance":
        cmd_cross_repo_governance(data)
    elif command == "governed-mcp-adapter":
        cmd_governed_mcp_adapter(data)
    elif command == "controlled-canonical-learning":
        cmd_controlled_canonical_learning(data)
    elif command == "approved-sandbox-update":
        cmd_approved_sandbox_update(data)
    elif command == "real-approval-boundary":
        cmd_real_approval_workflow(data)
    elif command == "approval-record-sandbox":
        cmd_approval_record_sandbox(data)
    elif command == "real-release-preflight":
        cmd_real_release_preflight(data)
    elif command == "release-simulation-sandbox":
        cmd_release_simulation_sandbox(data)
    elif command == "live-boundary-no-go":
        cmd_live_boundary_no_go(data)
    elif command == "meta-development-design":
        cmd_meta_development_design(data)
    elif command == "meta-development-mvp-artifact-sandbox":
        cmd_meta_development_mvp_artifact_sandbox(data)
    elif command == "governed-external-observation-boundary":
        cmd_governed_external_observation_boundary(data)
    elif command == "controlled-external-observation-sandbox":
        cmd_controlled_external_observation_sandbox(data)
    elif command == "real-read-only-observation-preflight":
        cmd_real_read_only_observation_preflight(data)
    elif command == "controlled-real-read-only-observation-pilot-design":
        cmd_controlled_real_read_only_observation_pilot_design(data)
    elif command == "controlled-observation-pilot-approval-packet":
        cmd_controlled_observation_pilot_approval_packet(data)
    elif command == "integrated-approval-record-and-pilot-readiness":
        cmd_integrated_approval_record_and_pilot_readiness(data)
    elif command == "agentic-evidence-discovery-trust-engine":
        cmd_agentic_evidence_discovery_trust_engine(data)
    elif command == "controlled-agentic-evidence-pilot-approval-dry-run":
        cmd_controlled_agentic_evidence_pilot_approval_dry_run(data)
    elif command == "tiny-real-read-only-agentic-evidence-observation-pilot":
        cmd_tiny_real_read_only_agentic_evidence_observation_pilot(data)
    elif command == "controlled-source-locator-resolution-tiny-observation-retry":
        cmd_controlled_source_locator_resolution_tiny_observation_retry(data)
    elif command == "governed-capability-gap-toolmaking-locator-resolver":
        cmd_governed_capability_gap_toolmaking_locator_resolver(data)
    elif command == "controlled-locator-resolver-enable-first-attempt":
        cmd_controlled_locator_resolver_enable_first_attempt(data)
    elif command == "controlled-seed-locator-or-search-resolver-enablement":
        cmd_controlled_seed_locator_or_search_resolver_enablement(data)
    elif command == "reviewed-seed-locator-injection-tiny-retry":
        cmd_reviewed_seed_locator_injection_tiny_retry(data)
    elif command == "budgeted-controlled-external-search-evidence-pilot":
        cmd_budgeted_controlled_external_search_evidence_pilot(data)
    elif command == "controlled-search-backend-page-read-enablement":
        cmd_controlled_search_backend_page_read_enablement(data)
    elif command == "unified-controlled-external-observation-evidence-loop":
        cmd_unified_controlled_external_observation_evidence_loop(data)
    elif command == "real-controlled-external-observation-mission-sprint":
        cmd_real_controlled_external_observation_mission_sprint(data)
    elif command == "real-evidence-conflict-resolution-sprint":
        cmd_real_evidence_conflict_resolution_sprint(data)
    elif command == "human-review-decision-boundary-sprint":
        cmd_human_review_decision_boundary_sprint(data)
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
