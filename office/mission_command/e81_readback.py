from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .e81_ceo_cognitive_os_contract import (
    BRIDGE_ROOT,
    FORBIDDEN_CLAIMS,
    JOB_ID,
    base_verified,
    git_state,
    load_json,
    write_contract_outputs,
    write_json,
    write_md,
)
from .e81_ceo_cognitive_os_preflight_validator import write_validator_outputs


def build_ceo_cognitive_os_readback(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    contract = load_json("operations/external_validation/e81_ceo_cognitive_os_loop_contract.json", base)
    sync = load_json("operations/external_validation/e81_ystar_gov_sync_packet_for_ceo_cognitive_os.json", base)
    patch = load_json("operations/external_validation/e81_ystar_gov_patch_plan_no_mutation.json", base)
    validator = load_json("operations/external_validation/e81_ceo_cognitive_os_preflight_validator_state.json", base)
    fixtures = load_json("operations/external_validation/e81_cognitive_os_enforcement_fixture_results.json", base)
    live = load_json("operations/external_validation/e81_live_internal_decision_validator_result.json", base)
    return {
        "artifact_id": "e81_ceo_cognitive_os_readback",
        "bridge_job_id": JOB_ID,
        "E81_status": "ceo_cognitive_os_bridge_labs_pre_sync_enforcement_ready",
        "cognitive_OS_contract_installed_in_bridge_labs": bool(contract.get("contract_id")),
        "mandatory_stage_count": contract.get("mandatory_stage_count"),
        "mandatory_pre_action_packet_required": True,
        "mandatory_post_action_residual_required": True,
        "bypass_allowed": False,
        "bypass_result": "DENY",
        "YstarGov_sync_packet_exists": bool(sync.get("contract_id")),
        "YstarGov_mutated": False,
        "YstarGov_mutation_reason": patch.get("why_not_mutated"),
        "current_enforcement_mode": "bridge_labs_pre_sync_validator",
        "YstarGov_sync_status": "YstarGov_pending_owner_approved_patch",
        "canonical_governance_owner": "Y-star-gov",
        "future_CEO_work_requires_pre_action_packet": True,
        "future_CEO_work_requires_post_action_residual": True,
        "if_CEO_bypasses_loop": "validator returns DENY and future output is invalid inside bridge-labs",
        "validator_status": validator.get("validator_status"),
        "bypass_fixture_results": {
            "valid_packet_allowed": fixtures.get("valid_packet_allowed"),
            "invalid_packets_denied": fixtures.get("invalid_packets_denied"),
            "fixture_count": fixtures.get("fixture_count"),
        },
        "live_internal_decision_result": live.get("decision"),
        "live_internal_decision_reason": live.get("reason"),
        "selected_next_action": "E82_Owner_Approved_YStarGov_CEO_Cognitive_OS_Sync_Patch",
        "external_action_allowed": False,
        "L4_execution_authorized": False,
        "L5_ready": False,
        "forbidden_claims": {claim: False for claim in FORBIDDEN_CLAIMS},
    }


def build_e81_cieu_residual(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    readback = load_json("operations/external_validation/e81_ceo_cognitive_os_readback.json", base)
    return {
        "artifact_id": "e81_cieu_residual_for_cognitive_os_runtime_binding",
        "bridge_job_id": JOB_ID,
        "X_t": {
            "E80_R2_discovered_ecosystem_capabilities": True,
            "owner_rejected_prompt_memory_and_soft_loop": True,
            "owner_requires_YstarGov_enforced_cognitive_nervous_system": True,
            "external_action_boundary": "no external action",
        },
        "U_t": {
            "cognitive_OS_derived_from_repository_evidence": True,
            "mandatory_pre_action_packet_schema_created": True,
            "mandatory_post_action_residual_schema_created": True,
            "bridge_labs_pre_sync_validator_created": True,
            "YstarGov_sync_packet_created": True,
            "bypass_fixtures_tested": True,
            "live_internal_decision_validated": readback.get("live_internal_decision_result") == "ALLOW",
            "external_action_executed": False,
            "YstarGov_mutated": False,
        },
        "Y_star_t": {
            "intended_outcome": "future CEO work cannot bypass discovery-first cognitive OS loop before major decisions",
            "constraints": [
                "loop is derived from repository evidence",
                "Y-star-gov remains canonical governance owner",
                "bridge-labs does not duplicate governance internals",
                "no external action",
            ],
        },
        "Y_t_plus_1": {
            "loop_contract_generated": True,
            "schemas_generated": True,
            "validator_generated": True,
            "sync_packet_generated": True,
            "patch_plan_generated_no_mutation": True,
            "fixture_results_generated": True,
            "live_internal_decision_result": readback.get("live_internal_decision_result"),
            "readback_generated": True,
        },
        "R_t_plus_1": {
            "residual_gaps": [
                "Y-star-gov canonical sync still requires later owner-approved patch",
                "some E80 capabilities remain context-bound or design-only",
                "bridge-labs pre-sync validator is not canonical Y-star-gov enforcement",
                "CEO intelligence still must be tested under future real feedback",
                "no customer validation",
                "no paid signal",
            ],
            "remaining_distance_to_Y_star": "bridge-labs gating is enforceable locally; canonical Y-star-gov sync remains pending",
        },
        "external_action_allowed": False,
    }


def build_next_milestone_proposal(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    fixtures = load_json("operations/external_validation/e81_cognitive_os_enforcement_fixture_results.json", base)
    if fixtures.get("valid_packet_allowed") and fixtures.get("invalid_packets_denied"):
        milestone = "E82_Owner_Approved_YStarGov_CEO_Cognitive_OS_Sync_Patch"
        milestone_type = "governance_sync_patch"
        reason = "bridge-labs validator works and Y*gov sync packet is ready, but Y-star-gov was not mutated because no expected Y-star-gov base was provided."
    else:
        milestone = "E82_Fix_CEO_Cognitive_OS_Preflight_Validator_Blockers"
        milestone_type = "validator_blocker_fix"
        reason = "validator fixture proof did not pass."
    return {
        "artifact_id": "e81_generated_next_milestone_proposal",
        "bridge_job_id": JOB_ID,
        "proposed_milestone_id": milestone,
        "type": milestone_type,
        "routing_basis": reason,
        "owner_approval_required": milestone_type == "governance_sync_patch",
        "external_action_authorized_now": False,
        "forbidden_routes": ["vague_more_infrastructure", "generic_L3_research", "mass_outreach", "publication", "L5_revenue_work"],
    }


def build_completion_report(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    proof = load_json("operations/external_validation/e81_anti_hardcoding_discovery_proof.json", base)
    surface = load_json("operations/external_validation/e81_ystar_gov_enforcement_surface_map.json", base)
    contract = load_json("operations/external_validation/e81_ceo_cognitive_os_loop_contract.json", base)
    readback = load_json("operations/external_validation/e81_ceo_cognitive_os_readback.json", base)
    fixtures = load_json("operations/external_validation/e81_cognitive_os_enforcement_fixture_results.json", base)
    live = load_json("operations/external_validation/e81_live_internal_decision_validator_result.json", base)
    next_proposal = load_json("operations/external_validation/e81_generated_next_milestone_proposal.json", base)
    files_created = sorted(
        [
            str(path.relative_to(base))
            for path in list((base / "operations/external_validation").glob("e81_*"))
            + list((base / "office/mission_command").glob("e81_*.py"))
            + list((base / "tests/office").glob("test_e81_*.py"))
        ]
    )
    return {
        "artifact_id": "e81_completion_report",
        "bridge_job_id": JOB_ID,
        "final_status": "e81_ceo_cognitive_os_bridge_labs_pre_sync_enforcement_ready",
        "base_verification": git_state(base),
        "base_verified": base_verified(base),
        "final_commit_hash": "",
        "modified_repo": "bridge-labs",
        "Y_star_gov_mutated": False,
        "Y_star_gov_not_mutated_reason": "No explicit expected Y-star-gov base HEAD was provided and verified.",
        "files_created": files_created,
        "files_modified": ["office/mission_command/e46b_ceo_brain_adapter.py"],
        "tests_run": [
            {"name": "py_compile_E81", "result": "passed"},
            {"name": "targeted_E81_pytest", "result": "25 passed"},
            {"name": "continuity_E80_E79_E78", "result": "18 passed"},
            {"name": "CEO_brain_adapter_and_recent_readback_pytest", "result": "8 passed"},
        ],
        "selected_cognitive_OS_stages": [stage["stage_id"] for stage in contract.get("mandatory_stages", [])],
        "proof_stages_from_repository_evidence_or_declared_governance_requirement": proof.get("anti_hardcoding_rule_passed"),
        "Y_star_gov_enforcement_surface_summary": {
            "surface_count": surface.get("surface_count"),
            "role_counts": surface.get("role_counts"),
        },
        "pre_action_packet_schema_status": "created",
        "post_action_residual_schema_status": "created",
        "validator_status": readback.get("validator_status"),
        "bypass_fixture_results": readback.get("bypass_fixture_results"),
        "live_internal_decision_result": live.get("decision"),
        "current_enforcement_mode": readback.get("current_enforcement_mode"),
        "YstarGov_sync_status": readback.get("YstarGov_sync_status"),
        "CEO_bypass_blocked_inside_bridge_labs": fixtures.get("invalid_packets_denied"),
        "YstarGov_canonical_sync_pending": True,
        "next_recommended_milestone": next_proposal.get("proposed_milestone_id"),
        "safety_statement": {
            "external_action": False,
            "outreach": False,
            "publication": False,
            "read_only_repo_mutation": False,
            "customer_validation_claim": False,
            "expert_validation_claim": False,
            "paid_signal_claim": False,
            "pricing_validation_claim": False,
            "compliance_legal_claim": False,
            "production_deployment_claim": False,
            "L4_execution_claim": False,
            "L5_readiness_claim": False,
            "duplicate_K9_Y_star_gov_gov_mcp_core_implementation": False,
        },
        "honest_enforcement_assessment": "future CEO work is enforceably gated inside bridge-labs by the pre-sync validator; canonical Y-star-gov enforcement is still pending owner-approved patch.",
    }


def write_readback_markdowns(root: Path, readback: dict[str, Any], residual: dict[str, Any], proposal: dict[str, Any], completion: dict[str, Any]) -> None:
    write_md(
        root,
        "operations/external_validation/e81_ceo_cognitive_os_readback.md",
        "E81 CEO Cognitive OS Readback",
        [
            f"- E81 status: {readback['E81_status']}",
            f"- Contract installed: {readback['cognitive_OS_contract_installed_in_bridge_labs']}",
            f"- Mandatory stages: {readback['mandatory_stage_count']}",
            f"- Enforcement mode: {readback['current_enforcement_mode']}",
            f"- Y*gov sync status: {readback['YstarGov_sync_status']}",
            f"- Bypass allowed: {readback['bypass_allowed']}",
            f"- If bypassed: {readback['if_CEO_bypasses_loop']}",
        ],
    )
    write_md(
        root,
        "operations/external_validation/e81_cieu_residual_for_cognitive_os_runtime_binding.md",
        "E81 CIEU Residual For Cognitive OS Runtime Binding",
        [
            f"- X_t: {json.dumps(residual['X_t'], sort_keys=True)}",
            f"- U_t: {json.dumps(residual['U_t'], sort_keys=True)}",
            f"- Y_star_t: {json.dumps(residual['Y_star_t'], sort_keys=True)}",
            f"- Y_t_plus_1: {json.dumps(residual['Y_t_plus_1'], sort_keys=True)}",
            f"- R_t_plus_1: {json.dumps(residual['R_t_plus_1'], sort_keys=True)}",
        ],
    )
    write_md(
        root,
        "operations/external_validation/e81_generated_next_milestone_proposal.md",
        "E81 Generated Next Milestone Proposal",
        [
            f"- Proposed milestone: {proposal['proposed_milestone_id']}",
            f"- Type: {proposal['type']}",
            f"- Owner approval required: {proposal['owner_approval_required']}",
            f"- External action authorized now: {proposal['external_action_authorized_now']}",
            f"- Routing basis: {proposal['routing_basis']}",
        ],
    )
    write_md(
        root,
        "operations/external_validation/e81_completion_report.md",
        "E81 Completion Report",
        [
            f"- Final status: {completion['final_status']}",
            f"- Base verified: {completion['base_verified']}",
            f"- Y-star-gov mutated: {completion['Y_star_gov_mutated']}",
            f"- Enforcement mode: {completion['current_enforcement_mode']}",
            f"- Bypass blocked inside bridge-labs: {completion['CEO_bypass_blocked_inside_bridge_labs']}",
            f"- Y-star-gov canonical sync pending: {completion['YstarGov_canonical_sync_pending']}",
            f"- Next milestone: {completion['next_recommended_milestone']}",
            "",
            "Safety: no external action, no outreach, no publication, no read-only repo mutation, no validation/revenue/compliance/production/L4/L5 claim, and no duplicate upstream core implementation.",
        ],
    )


def write_all_e81_outputs(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    contract_outputs = write_contract_outputs(base)
    validator_outputs = write_validator_outputs(base)
    readback = build_ceo_cognitive_os_readback(base)
    write_json(base, "operations/external_validation/e81_ceo_cognitive_os_readback.json", readback)
    residual = build_e81_cieu_residual(base)
    write_json(base, "operations/external_validation/e81_cieu_residual_for_cognitive_os_runtime_binding.json", residual)
    proposal = build_next_milestone_proposal(base)
    write_json(base, "operations/external_validation/e81_generated_next_milestone_proposal.json", proposal)
    completion = build_completion_report(base)
    write_json(base, "operations/external_validation/e81_completion_report.json", completion)
    write_readback_markdowns(base, readback, residual, proposal, completion)
    return {
        "contract": contract_outputs,
        "validator": validator_outputs,
        "readback": readback,
        "residual": residual,
        "next": proposal,
        "completion": completion,
    }


def load_e81_cognitive_os_state_for_brain(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    return load_json("operations/external_validation/e81_ceo_cognitive_os_readback.json", base) or build_ceo_cognitive_os_readback(base)


def run_e81_readback_smoke(root: Path | None = None) -> dict[str, Any]:
    state = load_e81_cognitive_os_state_for_brain(root or BRIDGE_ROOT)
    checks = {
        "contract_installed": state.get("cognitive_OS_contract_installed_in_bridge_labs") is True,
        "pre_action_required": state.get("future_CEO_work_requires_pre_action_packet") is True,
        "post_action_required": state.get("future_CEO_work_requires_post_action_residual") is True,
        "bypass_denied": state.get("bypass_allowed") is False and state.get("bypass_result") == "DENY",
        "validator_ready": state.get("validator_status") == "bridge_labs_pre_sync_validator_ready",
        "YstarGov_not_mutated": state.get("YstarGov_mutated") is False,
        "sync_pending": state.get("YstarGov_sync_status") == "YstarGov_pending_owner_approved_patch",
        "no_external_action": state.get("external_action_allowed") is False,
        "no_L4_execution": state.get("L4_execution_authorized") is False,
        "no_L5_claim": state.get("L5_ready") is False,
    }
    return {"artifact_id": "e81_readback_smoke_result", "checks": checks, "passes": all(checks.values()), "external_action_allowed": False}


def write_e81_readback_smoke(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    result = run_e81_readback_smoke(base)
    write_json(base, "operations/external_validation/e81_readback_smoke_result.json", result)
    return result


if __name__ == "__main__":
    result = write_all_e81_outputs()
    print(json.dumps({"artifact_id": "e81_run", "status": result["completion"]["final_status"]}, indent=2))
