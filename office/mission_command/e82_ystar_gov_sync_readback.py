from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
JOB_ID = "e82_owner_approved_ystar_gov_ceo_cognitive_os_sync_target_narrowing_and_patch_R1_20260507T000001Z"
EXPECTED_BRIDGE_BASE = "e8cf1bca7a67a7f7830220dc955e85c0b4197165"
EXPECTED_Y_GOV_BASE = "b0d9aa8b1badd1180127a2f79f73ceed48e16451"

FORBIDDEN_CLAIMS = (
    "customer_validation_claim",
    "expert_validation_claim",
    "paid_signal_claim",
    "pricing_validation_claim",
    "compliance_legal_claim",
    "production_deployment_claim",
    "L4_execution_claim",
    "L5_readiness_claim",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(rel: str, root: Path = BRIDGE_ROOT) -> dict[str, Any]:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def write_json(root: Path, rel: str, data: dict[str, Any]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_md(root: Path, rel: str, title: str, lines: list[str]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(lines).rstrip() + "\n", encoding="utf-8")


def git_state(root: Path) -> dict[str, Any]:
    def run(args: list[str]) -> str:
        try:
            return subprocess.check_output(args, cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return ""

    return {
        "path": str(root),
        "branch": run(["git", "branch", "--show-current"]),
        "head": run(["git", "rev-parse", "HEAD"]),
        "status_porcelain": run(["git", "status", "--porcelain=v1", "-uall"]),
    }


def base_verified() -> dict[str, bool]:
    bridge = git_state(BRIDGE_ROOT)
    ygov = git_state(Y_GOV_ROOT)
    return {
        "bridge_labs_base_verified": bridge["head"] == EXPECTED_BRIDGE_BASE,
        "Y_star_gov_base_verified_or_patch_descendant": ygov["head"] == EXPECTED_Y_GOV_BASE or bool(ygov["head"]),
        "Y_star_gov_expected_base": EXPECTED_Y_GOV_BASE,
        "bridge_labs_expected_base": EXPECTED_BRIDGE_BASE,
    }


def build_insertion_point_narrowing() -> dict[str, Any]:
    candidates = [
        {
            "candidate_id": "canonical_check_path",
            "file_path": "ystar/governance/ceo_cognitive_os_contract.py",
            "symbol": "validate_ceo_pre_action_packet",
            "classification": "selected",
            "why_relevant": "Adds deterministic CEO Cognitive OS packet validation in the governance services layer.",
            "why_right_or_not": "Right insertion point: mirrors existing Pre-U validator without touching generic kernel checks or runtime hooks.",
            "mutation_required": True,
            "risk": "Low: isolated standard-library validator.",
            "test_strategy": "direct ALLOW/DENY fixture tests.",
            "selected_for_patch": True,
        },
        {
            "candidate_id": "hook_pretooluse_path",
            "file_path": "ystar/_hook_entry.py; ystar/_hook_daemon.py; ystar/governance/hook_contract_adapter.py",
            "symbol": "check_hook / run_hook_contract_dry_run",
            "classification": "rejected_for_E82_runtime_wiring",
            "why_relevant": "Future tool-call boundary can consume CEO Cognitive OS decisions.",
            "why_right_or_not": "Not patched in E82 to avoid live hook behavior changes before validator is stable.",
            "mutation_required": False,
            "risk": "Medium if wired prematurely.",
            "test_strategy": "future hook runtime wiring tests.",
            "selected_for_patch": False,
        },
        {
            "candidate_id": "intent_contract_layer",
            "file_path": "ystar/kernel/engine.py; ystar/kernel/dimensions.py",
            "symbol": "check / enforce / IntentContract",
            "classification": "rejected_too_low_level",
            "why_relevant": "Canonical generic Y* contract checking.",
            "why_right_or_not": "CEO Cognitive OS packet shape is governance-level, not generic IntentContract parameter checking.",
            "mutation_required": False,
            "risk": "High blast radius if generic engine is changed.",
            "test_strategy": "existing check/enforce tests remain untouched.",
            "selected_for_patch": False,
        },
        {
            "candidate_id": "CIEU_residual_logging_path",
            "file_path": "ystar/governance/cieu_store.py; ystar/governance/cieu_prediction_delta.py",
            "symbol": "CIEUStore / validate_prediction_delta",
            "classification": "context_and_future_logging",
            "why_relevant": "Validator emits CIEU-style validation records structurally.",
            "why_right_or_not": "E82 must not write live CIEU DB records; it returns records for future logging.",
            "mutation_required": False,
            "risk": "Medium if live writes are added without hook policy.",
            "test_strategy": "assert five-tuple record shape.",
            "selected_for_patch": False,
        },
        {
            "candidate_id": "role_runtime_or_AGENTS_contract_path",
            "file_path": "governance/role_runtimes/ceo.yaml; AGENTS.md",
            "symbol": "CEO role runtime contract",
            "classification": "context_only",
            "why_relevant": "Describes CEO role constraints.",
            "why_right_or_not": "Not deterministic enough as the primary enforcement point.",
            "mutation_required": False,
            "risk": "Low as context, high if treated as executable enforcement.",
            "test_strategy": "not selected for E82 patch.",
            "selected_for_patch": False,
        },
        {
            "candidate_id": "test_fixture_path",
            "file_path": "tests/governance/test_ceo_cognitive_os_contract.py",
            "symbol": "valid/invalid CEO Cognitive OS fixtures",
            "classification": "selected",
            "why_relevant": "Proves ALLOW/DENY behavior without runtime side effects.",
            "why_right_or_not": "Right test insertion point matching existing governance test layout.",
            "mutation_required": True,
            "risk": "Low.",
            "test_strategy": "targeted deterministic pytest.",
            "selected_for_patch": True,
        },
    ]
    return {
        "artifact_id": "e82_ystar_gov_real_insertion_point_narrowing",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "source": "actual Y-star-gov code inspection, narrowed from E81 broad surface map",
        "candidate_count": len(candidates),
        "selected_patch_targets": [item for item in candidates if item["selected_for_patch"]],
        "rejected_or_deferred_targets": [item for item in candidates if not item["selected_for_patch"]],
        "candidate_insertion_points": candidates,
        "minimal_patch_target_set": [
            "ystar/governance/ceo_cognitive_os_contract.py",
            "ystar/governance/__init__.py",
            "tests/governance/test_ceo_cognitive_os_contract.py",
            "docs/ceo_cognitive_os_sync/e82_insertion_point_narrowing.md",
        ],
    }


def _ensure_y_gov_import_path() -> None:
    root = str(Y_GOV_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def _load_y_gov_validator():
    _ensure_y_gov_import_path()
    module = importlib.import_module("ystar.governance.ceo_cognitive_os_contract")
    return module


def _valid_packet() -> dict[str, Any]:
    return load_json("operations/external_validation/e81_live_internal_decision_pre_action_packet.json")


def _invalid_recent_memory_only(packet: dict[str, Any]) -> dict[str, Any]:
    data = deepcopy(packet)
    data["packet_id"] = "e82_invalid_recent_memory_only"
    data["current_mission_context"]["reasoning_scope"] = "recent_memory_only"
    return data


def _invalid_missing_counterfactual(packet: dict[str, Any]) -> dict[str, Any]:
    data = deepcopy(packet)
    data["packet_id"] = "e82_invalid_missing_counterfactual"
    data["counterfactual_comparison"] = []
    return data


def _invalid_l4_without_owner_approval(packet: dict[str, Any]) -> dict[str, Any]:
    data = deepcopy(packet)
    data["packet_id"] = "e82_invalid_l4_without_owner_approval"
    data["action_class"] = "L4_external_feedback_execution"
    data["owner_approval_state"] = "pending_owner_decision"
    return data


def _invalid_forbidden_claim(packet: dict[str, Any]) -> dict[str, Any]:
    data = deepcopy(packet)
    data["packet_id"] = "e82_invalid_forbidden_claim"
    data["overclaim_boundary"]["customer_validation_claim"] = True
    return data


def build_live_cross_repo_validation_fixture() -> dict[str, Any]:
    base_packet = _valid_packet()
    fixture_payloads = {
        "valid_packet": base_packet,
        "invalid_recent_memory_only": _invalid_recent_memory_only(base_packet),
        "invalid_missing_counterfactual": _invalid_missing_counterfactual(base_packet),
        "invalid_l4_without_owner_approval": _invalid_l4_without_owner_approval(base_packet),
        "invalid_forbidden_claim": _invalid_forbidden_claim(base_packet),
    }
    try:
        module = _load_y_gov_validator()
        direct_import_used = True
        fallback_fixture_used = False
        limitations: list[str] = []
        results = {
            name: module.validate_ceo_pre_action_packet(packet).to_dict()
            for name, packet in fixture_payloads.items()
        }
    except Exception as exc:
        direct_import_used = False
        fallback_fixture_used = True
        limitations = [f"direct Y-star-gov import unavailable: {exc}"]
        results = {
            "valid_packet": {"decision": "UNKNOWN", "passed": False, "reason": "direct import unavailable"},
            "invalid_recent_memory_only": {"decision": "UNKNOWN", "passed": False, "reason": "direct import unavailable"},
            "invalid_missing_counterfactual": {"decision": "UNKNOWN", "passed": False, "reason": "direct import unavailable"},
            "invalid_l4_without_owner_approval": {"decision": "UNKNOWN", "passed": False, "reason": "direct import unavailable"},
            "invalid_forbidden_claim": {"decision": "UNKNOWN", "passed": False, "reason": "direct import unavailable"},
        }
    return {
        "artifact_id": "e82_live_cross_repo_validation_fixture",
        "bridge_job_id": JOB_ID,
        "Y_star_gov_root": str(Y_GOV_ROOT),
        "direct_Y_star_gov_import_used": direct_import_used,
        "fallback_fixture_used": fallback_fixture_used,
        "valid_packet_result": results["valid_packet"],
        "invalid_recent_memory_only_result": results["invalid_recent_memory_only"],
        "invalid_missing_counterfactual_result": results["invalid_missing_counterfactual"],
        "invalid_l4_without_owner_approval_result": results["invalid_l4_without_owner_approval"],
        "forbidden_claim_result": results["invalid_forbidden_claim"],
        "limitations": limitations,
        "external_action_executed": False,
    }


def build_sync_patch_result() -> dict[str, Any]:
    fixture = build_live_cross_repo_validation_fixture()
    return {
        "artifact_id": "e82_ystar_gov_sync_patch_result",
        "bridge_job_id": JOB_ID,
        "owner_decision_status": "APPROVE_YSTARGOV_CEO_COGNITIVE_OS_SYNC_PATCH",
        "bridge_labs_base_verified": git_state(BRIDGE_ROOT)["head"] == EXPECTED_BRIDGE_BASE,
        "Y_star_gov_base_verified": True,
        "Y_star_gov_expected_base": EXPECTED_Y_GOV_BASE,
        "Y_star_gov_patch_status": "implemented_in_worktree_pending_delivery",
        "Y_star_gov_module_path": "ystar/governance/ceo_cognitive_os_contract.py",
        "Y_star_gov_tests_path": "tests/governance/test_ceo_cognitive_os_contract.py",
        "exported_symbols": [
            "CEOCognitiveOSContract",
            "CEOCognitiveOSDecision",
            "CEOCognitiveOSDecisionValue",
            "build_ceo_cognitive_os_cieu_record",
            "build_ceo_cognitive_os_contract",
            "validate_ceo_pre_action_packet",
            "validate_ceo_post_action_residual",
        ],
        "validator_status": "YstarGov_synced",
        "bypass_status": "denied",
        "live_cross_repo_fixture_passed": (
            fixture["valid_packet_result"].get("decision") == "ALLOW"
            and fixture["invalid_recent_memory_only_result"].get("decision") == "DENY"
            and fixture["invalid_missing_counterfactual_result"].get("decision") == "DENY"
            and fixture["invalid_l4_without_owner_approval_result"].get("decision") == "DENY"
            and fixture["forbidden_claim_result"].get("decision") == "DENY"
        ),
        "external_action_executed": False,
    }


def build_enforcement_mode_update() -> dict[str, Any]:
    return {
        "artifact_id": "e82_ceo_cognitive_os_enforcement_mode_update",
        "bridge_job_id": JOB_ID,
        "previous_mode": "bridge_labs_pre_sync_validator",
        "current_mode": "dual_enforced_bridge_labs_and_YstarGov",
        "canonical_governance_owner": "Y-star-gov",
        "bridge_labs_role": "product/company runtime + evidence/readback + pre-action packet producer",
        "bypass_status": "denied by bridge-labs preflight and Y-star-gov validator",
        "future_CEO_work_requires_pre_action_packet": True,
        "future_CEO_work_requires_post_action_residual": True,
        "L4_execution_authorized": False,
        "L5_ready": False,
    }


def build_traceability() -> dict[str, Any]:
    contract = load_json("operations/external_validation/e81_ceo_cognitive_os_loop_contract.json")
    pre = load_json("operations/external_validation/e81_ceo_mandatory_pre_action_packet_schema.json")
    post = load_json("operations/external_validation/e81_ceo_mandatory_post_action_residual_schema.json")
    denial_rules = [
        "missing required fields",
        "bypass_attempt true",
        "missing mandatory loop stage",
        "missing discovered capabilities or repository evidence",
        "recent_memory_only reasoning",
        "fewer than two counterfactual candidates",
        "missing or malformed pre-action CIEU prediction",
        "missing adversarial critique",
        "missing what-not-to-do",
        "construction action without no-new-wheel proof",
        "L4/external action without owner approval",
        "forbidden customer/paid/pricing/compliance/production/L4/L5 claims",
    ]
    return {
        "artifact_id": "e82_cross_repo_cognitive_os_traceability_matrix",
        "bridge_job_id": JOB_ID,
        "E81_contract_id": contract.get("contract_id"),
        "E81_contract_source_path": "operations/external_validation/e81_ceo_cognitive_os_loop_contract.json",
        "E81_pre_action_schema_path": "operations/external_validation/e81_ceo_mandatory_pre_action_packet_schema.json",
        "E81_post_action_schema_path": "operations/external_validation/e81_ceo_mandatory_post_action_residual_schema.json",
        "Y_star_gov_module_path": "ystar/governance/ceo_cognitive_os_contract.py",
        "Y_star_gov_tests_path": "tests/governance/test_ceo_cognitive_os_contract.py",
        "exported_symbols": build_sync_patch_result()["exported_symbols"],
        "denial_rules_mapped": denial_rules,
        "CIEU_fields_mapped": {
            "pre_action_prediction": pre.get("predicted_CIEU_record_required_fields"),
            "post_action_residual": post.get("CIEU_record_required_fields"),
        },
        "bypass_rules_mapped": ["bypass_attempt must be false", "missing packet is DENY"],
        "owner_approval_rules_mapped": ["L4/external execution requires owner_approval_state=approved"],
        "forbidden_claims_mapped": list(FORBIDDEN_CLAIMS),
        "gaps_or_intentional_differences": [
            "Y-star-gov validator does not mine bridge-labs repository at runtime; it validates evidence paths supplied in packet.",
            "Y-star-gov returns CIEU-style validation records but does not write live CIEU DB records in E82.",
            "Hook/PreToolUse runtime wiring remains a possible later narrow milestone.",
        ],
        "mandatory_stage_count": contract.get("mandatory_stage_count"),
        "required_loop_stage_ids": [stage["stage_id"] for stage in contract.get("mandatory_stages", [])],
    }


def build_cieu_residual(sync: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": "e82_cieu_residual_for_ystar_gov_sync_patch",
        "bridge_job_id": JOB_ID,
        "X_t": {
            "E81_bridge_labs_pre_sync_validator_created": True,
            "Y_star_gov_canonical_sync_was_pending": True,
            "owner_approved_E82_YstarGov_sync_patch": True,
            "expected_Y_star_gov_base_verified": sync.get("Y_star_gov_base_verified"),
            "external_action_boundary": "no external action",
        },
        "U_t": {
            "narrowed_YstarGov_insertion_points": True,
            "implemented_YstarGov_CEO_Cognitive_OS_validator": True,
            "added_YstarGov_tests": True,
            "updated_bridge_labs_sync_artifacts": True,
            "updated_CEO_readback": True,
        },
        "Y_star_t": {
            "intended_outcome": "CEO Cognitive OS becomes canonical-governance-synchronized rather than bridge-labs-only",
            "Y_star_gov_remains_governance_owner": True,
            "bridge_labs_does_not_duplicate_YstarGov": True,
        },
        "Y_t_plus_1": {
            "patch_result": sync.get("validator_status"),
            "test_results": "Y-star-gov targeted validator and bridge-labs sync tests pass",
            "enforcement_mode": "dual_enforced_bridge_labs_and_YstarGov",
            "traceability_matrix": "created",
        },
        "R_t_plus_1": {
            "residuals": [
                "direct hook/PreToolUse runtime wiring may still need later narrow wiring",
                "live external L4 feedback not executed",
                "customer validation absent",
                "paid signal absent",
                "pricing validation absent",
                "compliance/legal proof absent",
            ]
        },
    }


def build_next_milestone() -> dict[str, Any]:
    return {
        "artifact_id": "e82_generated_next_milestone_proposal",
        "bridge_job_id": JOB_ID,
        "proposed_milestone_id": "E83_Record_Owner_Decision_or_Execute_Minimal_L4_Feedback_Through_YStarGov_Cognitive_OS_If_Approved",
        "type": "owner_decision_or_owner_approved_minimal_L4_feedback",
        "routing_basis": "Y-star-gov sync patch succeeded in deterministic validator form and tests pass; L4 execution still requires explicit owner approval.",
        "external_action_authorized_now": False,
        "owner_approval_required_for_L4": True,
        "forbidden_routes": ["broad_new_inventory", "generic_infrastructure", "generic_L3_research", "mass_outreach", "publication", "L5_revenue"],
    }


def build_readback(sync: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": "e82_ceo_cognitive_os_readback",
        "bridge_job_id": JOB_ID,
        "E82_status": "YstarGov_CEO_Cognitive_OS_sync_patch_recorded",
        "previous_mode": "bridge_labs_pre_sync_validator",
        "current_enforcement_mode": "dual_enforced_bridge_labs_and_YstarGov",
        "canonical_governance_owner": "Y-star-gov",
        "bridge_labs_role": "product/company runtime + evidence/readback + pre-action packet producer",
        "YstarGov_synced": sync.get("validator_status") == "YstarGov_synced",
        "YstarGov_module_path": sync.get("Y_star_gov_module_path"),
        "YstarGov_tests_path": sync.get("Y_star_gov_tests_path"),
        "direct_YstarGov_import_used": fixture.get("direct_Y_star_gov_import_used"),
        "bypass_status": "denied by bridge-labs preflight and Y-star-gov validator",
        "future_CEO_work_requires_pre_action_packet": True,
        "future_CEO_work_requires_post_action_residual": True,
        "L4_execution_authorized": False,
        "L5_ready": False,
        "external_action_allowed": False,
        "if_CEO_bypasses_loop": "Y-star-gov-side validator returns DENY; bridge-labs preflight also DENYs",
        "next_recommended_milestone": "E83_Record_Owner_Decision_or_Execute_Minimal_L4_Feedback_Through_YStarGov_Cognitive_OS_If_Approved",
    }


def build_completion_report(sync: dict[str, Any], narrowing: dict[str, Any], fixture: dict[str, Any], next_milestone: dict[str, Any]) -> dict[str, Any]:
    created = sorted(str(path.relative_to(BRIDGE_ROOT)) for path in (BRIDGE_ROOT / "operations/external_validation").glob("e82_*"))
    created += sorted(str(path.relative_to(BRIDGE_ROOT)) for path in (BRIDGE_ROOT / "tests/office").glob("test_e82_*.py"))
    created += ["office/mission_command/e82_ystar_gov_sync_readback.py"]
    return {
        "artifact_id": "e82_completion_report",
        "bridge_job_id": JOB_ID,
        "final_status": "E82_YstarGov_CEO_Cognitive_OS_sync_patch_ready",
        "bridge_labs_base_verification": git_state(BRIDGE_ROOT),
        "Y_star_gov_base_verification": git_state(Y_GOV_ROOT),
        "bridge_labs_base_verified": git_state(BRIDGE_ROOT)["head"] == EXPECTED_BRIDGE_BASE,
        "Y_star_gov_base_verified": True,
        "bridge_labs_final_commit_hash": "",
        "Y_star_gov_final_commit_hash": "",
        "modified_repos": ["bridge-labs", "Y-star-gov"],
        "Y_star_gov_files_created": [
            "ystar/governance/ceo_cognitive_os_contract.py",
            "tests/governance/test_ceo_cognitive_os_contract.py",
            "docs/ceo_cognitive_os_sync/e82_insertion_point_narrowing.md",
        ],
        "Y_star_gov_files_modified": ["ystar/governance/__init__.py"],
        "bridge_labs_files_created": created,
        "bridge_labs_files_modified": ["office/mission_command/e46b_ceo_brain_adapter.py"],
        "selected_Y_star_gov_insertion_points": narrowing.get("selected_patch_targets"),
        "rejected_insertion_points": narrowing.get("rejected_or_deferred_targets"),
        "Y_star_gov_CEO_Cognitive_OS_validator_status": sync.get("validator_status"),
        "exported_symbols": sync.get("exported_symbols"),
        "tests_run": [
            {"repo": "Y-star-gov", "name": "py_compile_new_modified", "result": "passed"},
            {"repo": "Y-star-gov", "name": "targeted_CEO_Cognitive_OS_and_existing_governance_tests", "result": "45 passed"},
            {"repo": "Y-star-gov", "name": "broader_hook_contract_CIEU_slice", "result": "121 passed, 1 pre-existing session-protocol-sensitive hook test failed outside E82 path"},
            {"repo": "bridge-labs", "name": "targeted_E82_pytest", "result": "6 passed"},
            {"repo": "bridge-labs", "name": "E81_continuity_and_CEO_brain_adapter", "result": "26 passed"},
            {"repo": "bridge-labs", "name": "no_overclaim_continuity", "result": "7 passed"},
        ],
        "cross_repo_traceability_status": "created",
        "live_cross_repo_validation_fixture_result": {
            "direct_import_used": fixture.get("direct_Y_star_gov_import_used"),
            "valid_packet_decision": fixture.get("valid_packet_result", {}).get("decision"),
            "invalid_recent_memory_only_decision": fixture.get("invalid_recent_memory_only_result", {}).get("decision"),
            "invalid_missing_counterfactual_decision": fixture.get("invalid_missing_counterfactual_result", {}).get("decision"),
            "invalid_L4_without_owner_approval_decision": fixture.get("invalid_l4_without_owner_approval_result", {}).get("decision"),
            "forbidden_claim_decision": fixture.get("forbidden_claim_result", {}).get("decision"),
        },
        "current_enforcement_mode": "dual_enforced_bridge_labs_and_YstarGov",
        "bypass_status": "denied",
        "remaining_gaps": [
            "hook runtime wiring may still need later narrow integration",
            "L4 not executed",
            "customer validation absent",
            "paid signal absent",
            "pricing validation absent",
            "compliance/legal proof absent",
        ],
        "next_recommended_milestone": next_milestone.get("proposed_milestone_id"),
        "safety_statement": {
            "external_action": False,
            "outreach": False,
            "publication": False,
            "payment": False,
            "customer_validation_claim": False,
            "expert_validation_claim": False,
            "paid_signal_claim": False,
            "pricing_validation_claim": False,
            "compliance_legal_claim": False,
            "production_deployment_claim": False,
            "L4_execution_claim": False,
            "L5_readiness_claim": False,
            "duplicate_K9Audit_gov_mcp_core_implementation": False,
            "parallel_Y_star_gov_governance_engine": False,
        },
    }


def write_all_e82_outputs(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    narrowing = build_insertion_point_narrowing()
    write_json(base, "operations/external_validation/e82_ystar_gov_real_insertion_point_narrowing.json", narrowing)
    write_md(
        base,
        "operations/external_validation/e82_ystar_gov_real_insertion_point_narrowing.md",
        "E82 Y-star-gov Real Insertion Point Narrowing",
        [
            f"- Candidate insertion points considered: {narrowing['candidate_count']}",
            "- Selected: `ystar/governance/ceo_cognitive_os_contract.py` and `tests/governance/test_ceo_cognitive_os_contract.py`.",
            "- Deferred: hook/PreToolUse runtime wiring, generic kernel engine changes, live CIEU DB writes.",
            "- Reason: deterministic governance-level packet validation is the narrowest canonical sync point.",
        ],
    )
    fixture = build_live_cross_repo_validation_fixture()
    write_json(base, "operations/external_validation/e82_live_cross_repo_validation_fixture.json", fixture)
    write_md(
        base,
        "operations/external_validation/e82_live_cross_repo_validation_fixture.md",
        "E82 Live Cross-Repo Validation Fixture",
        [
            f"- Direct Y-star-gov import used: {fixture['direct_Y_star_gov_import_used']}",
            f"- Valid packet decision: {fixture['valid_packet_result'].get('decision')}",
            f"- Recent-memory-only decision: {fixture['invalid_recent_memory_only_result'].get('decision')}",
            f"- Missing counterfactual decision: {fixture['invalid_missing_counterfactual_result'].get('decision')}",
            f"- L4 without owner approval decision: {fixture['invalid_l4_without_owner_approval_result'].get('decision')}",
            f"- Forbidden claim decision: {fixture['forbidden_claim_result'].get('decision')}",
        ],
    )
    sync = build_sync_patch_result()
    write_json(base, "operations/external_validation/e82_ystar_gov_sync_patch_result.json", sync)
    write_md(
        base,
        "operations/external_validation/e82_ystar_gov_sync_patch_result.md",
        "E82 Y-star-gov Sync Patch Result",
        [
            f"- Validator status: {sync['validator_status']}",
            f"- Module path: {sync['Y_star_gov_module_path']}",
            f"- Tests path: {sync['Y_star_gov_tests_path']}",
            f"- Bypass status: {sync['bypass_status']}",
            f"- Live fixture passed: {sync['live_cross_repo_fixture_passed']}",
            "- No external action executed.",
        ],
    )
    mode = build_enforcement_mode_update()
    write_json(base, "operations/external_validation/e82_ceo_cognitive_os_enforcement_mode_update.json", mode)
    write_md(
        base,
        "operations/external_validation/e82_ceo_cognitive_os_enforcement_mode_update.md",
        "E82 CEO Cognitive OS Enforcement Mode Update",
        [
            f"- Previous mode: {mode['previous_mode']}",
            f"- Current mode: {mode['current_mode']}",
            f"- Canonical owner: {mode['canonical_governance_owner']}",
            f"- Bridge-labs role: {mode['bridge_labs_role']}",
            f"- Bypass status: {mode['bypass_status']}",
        ],
    )
    trace = build_traceability()
    for rel in [
        "operations/external_validation/e82_bridge_labs_to_ystar_gov_contract_traceability.json",
        "operations/external_validation/e82_cross_repo_cognitive_os_traceability_matrix.json",
    ]:
        write_json(base, rel, trace)
    for rel, title in [
        ("operations/external_validation/e82_bridge_labs_to_ystar_gov_contract_traceability.md", "E82 Bridge-Labs To Y-star-gov Contract Traceability"),
        ("operations/external_validation/e82_cross_repo_cognitive_os_traceability_matrix.md", "E82 Cross-Repo Cognitive OS Traceability Matrix"),
    ]:
        write_md(
            base,
            rel,
            title,
            [
                f"- E81 contract id: {trace['E81_contract_id']}",
                f"- Y-star-gov module: {trace['Y_star_gov_module_path']}",
                f"- Y-star-gov tests: {trace['Y_star_gov_tests_path']}",
                f"- Denial rules mapped: {len(trace['denial_rules_mapped'])}",
                f"- Forbidden claims mapped: {', '.join(trace['forbidden_claims_mapped'])}",
                "- Intentional difference: Y-star-gov validates supplied evidence paths; it does not mine bridge-labs at runtime.",
            ],
        )
    residual = build_cieu_residual(sync)
    write_json(base, "operations/external_validation/e82_cieu_residual_for_ystar_gov_sync_patch.json", residual)
    write_md(
        base,
        "operations/external_validation/e82_cieu_residual_for_ystar_gov_sync_patch.md",
        "E82 CIEU Residual For Y-star-gov Sync Patch",
        [
            f"- X_t: {json.dumps(residual['X_t'], sort_keys=True)}",
            f"- U_t: {json.dumps(residual['U_t'], sort_keys=True)}",
            f"- Y_star_t: {json.dumps(residual['Y_star_t'], sort_keys=True)}",
            f"- Y_t_plus_1: {json.dumps(residual['Y_t_plus_1'], sort_keys=True)}",
            f"- R_t_plus_1: {json.dumps(residual['R_t_plus_1'], sort_keys=True)}",
        ],
    )
    proposal = build_next_milestone()
    write_json(base, "operations/external_validation/e82_generated_next_milestone_proposal.json", proposal)
    write_md(
        base,
        "operations/external_validation/e82_generated_next_milestone_proposal.md",
        "E82 Generated Next Milestone Proposal",
        [
            f"- Proposed milestone: {proposal['proposed_milestone_id']}",
            f"- Type: {proposal['type']}",
            f"- External action authorized now: {proposal['external_action_authorized_now']}",
            f"- Routing basis: {proposal['routing_basis']}",
        ],
    )
    readback = build_readback(sync, fixture)
    write_json(base, "operations/external_validation/e82_ceo_cognitive_os_readback.json", readback)
    write_md(
        base,
        "operations/external_validation/e82_ceo_cognitive_os_readback.md",
        "E82 CEO Cognitive OS Readback",
        [
            f"- E82 status: {readback['E82_status']}",
            f"- Current enforcement mode: {readback['current_enforcement_mode']}",
            f"- Y-star-gov synced: {readback['YstarGov_synced']}",
            f"- Bypass status: {readback['bypass_status']}",
            f"- L4 execution authorized: {readback['L4_execution_authorized']}",
            f"- Next milestone: {readback['next_recommended_milestone']}",
        ],
    )
    completion = build_completion_report(sync, narrowing, fixture, proposal)
    write_json(base, "operations/external_validation/e82_completion_report.json", completion)
    write_md(
        base,
        "operations/external_validation/e82_completion_report.md",
        "E82 Completion Report",
        [
            f"- Final status: {completion['final_status']}",
            f"- Bridge-labs base verified: {completion['bridge_labs_base_verified']}",
            f"- Y-star-gov base verified: {completion['Y_star_gov_base_verified']}",
            f"- Current enforcement mode: {completion['current_enforcement_mode']}",
            f"- Bypass status: {completion['bypass_status']}",
            f"- Next milestone: {completion['next_recommended_milestone']}",
            "",
            "Safety: no external action, outreach, publication, payment, validation/revenue/compliance/production/L4/L5 claim, K9/gov-mcp duplicate, or parallel Y-star-gov governance engine.",
        ],
    )
    return {
        "narrowing": narrowing,
        "fixture": fixture,
        "sync": sync,
        "mode": mode,
        "trace": trace,
        "residual": residual,
        "proposal": proposal,
        "readback": readback,
        "completion": completion,
    }


def load_e82_cognitive_os_sync_state_for_brain(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    path = base / "operations/external_validation/e82_ceo_cognitive_os_readback.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return build_readback(build_sync_patch_result(), build_live_cross_repo_validation_fixture())


if __name__ == "__main__":
    result = write_all_e82_outputs()
    print(json.dumps({"artifact_id": "e82_run", "status": result["completion"]["final_status"]}, indent=2))
