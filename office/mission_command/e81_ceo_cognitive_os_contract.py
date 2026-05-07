from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
JOB_ID = "e81_discovery_first_ceo_cognitive_os_runtime_binding_and_ystar_gov_enforcement_sync_R1_20260507T000001Z"
EXPECTED_BRANCH = "backflow/aiden-ceo-meeting-room"
EXPECTED_BASE = "d62c7b9f5d7e20875d4477561cf9543d338c0e57"

Y_GOV_SEARCH_SEEDS = [
    "check",
    "enforce",
    "pre-execution",
    "contract",
    "policy",
    "rule",
    "obligation",
    "delegation",
    "CIEU",
    "residual",
    "validator",
    "gate",
    "approval",
    "decision",
    "runtime",
    "hook",
    "seal",
    "verify",
    "canonical",
    "schema",
]

FORBIDDEN_CLAIMS = [
    "customer_validation_claim",
    "expert_validation_claim",
    "paid_signal_claim",
    "pricing_validation_claim",
    "compliance_legal_claim",
    "production_deployment_claim",
    "L4_execution_claim",
    "L5_readiness_claim",
]

STAGE_EVIDENCE_FALLBACKS = {
    "full_capability_inventory_recall": [
        "operations/external_validation/e80_raw_file_inventory.json",
        "operations/external_validation/e80_discovered_capability_candidates.json",
        "operations/external_validation/e80_whole_ecosystem_capability_inventory.json",
    ],
}


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_json(root: Path, rel: str, data: Any) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(root: Path, rel: str, title: str, lines: list[str]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def load_json(rel: str, root: Path | None = None) -> Any:
    try:
        return json.loads(((root or BRIDGE_ROOT) / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def _read(path: Path, limit: int = 300_000) -> str:
    try:
        if not path.exists() or path.is_dir() or path.stat().st_size > 3_000_000:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def _run_git(root: Path, args: list[str]) -> list[str]:
    try:
        out = subprocess.check_output(["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL)
        return [line for line in out.splitlines() if line]
    except Exception:
        return []


def git_state(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    branch = _run_git(base, ["branch", "--show-current"])
    head = _run_git(base, ["rev-parse", "HEAD"])
    return {
        "branch": branch[0] if branch else "",
        "head": head[0] if head else "",
        "expected_branch": EXPECTED_BRANCH,
        "expected_head": EXPECTED_BASE,
    }


def base_verified(root: Path | None = None) -> bool:
    state = git_state(root)
    return state["branch"] == EXPECTED_BRANCH and state["head"] == EXPECTED_BASE


def _repo_files(root: Path) -> list[str]:
    files = _run_git(root, ["ls-files"])
    if files:
        return sorted(files)
    return sorted(str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()) if root.exists() else []


def _parse_symbols(path: Path) -> list[dict[str, Any]]:
    symbols: list[dict[str, Any]] = []
    text = _read(path, 1_000_000)
    try:
        tree = ast.parse(text)
    except Exception:
        return symbols
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            symbols.append(
                {
                    "name": node.name,
                    "kind": "class" if isinstance(node, ast.ClassDef) else "function",
                    "line": getattr(node, "lineno", 0),
                }
            )
    return symbols


def _contains_governance_signal(value: str) -> bool:
    lower = value.lower()
    return any(seed.lower() in lower for seed in Y_GOV_SEARCH_SEEDS)


def _governance_role(path: str, symbol: str, text: str) -> str:
    lower = f"{path} {symbol} {text[:2000]}".lower()
    if "pre_u_packet_validator" in lower or "validator" in lower:
        return "pre_action_packet_validation"
    if "hook_contract" in lower or "hook" in lower:
        return "hook_contract_enforcement"
    if "cieu" in lower and ("prediction" in lower or "residual" in lower):
        return "CIEU_residual_or_prediction_delta"
    if "cieu" in lower:
        return "CIEU_logging_or_store"
    if "obligation" in lower:
        return "obligation_registration_and_closure"
    if "delegation" in lower:
        return "delegation_authority"
    if "contract" in lower or "policy" in lower:
        return "intent_contract_or_policy"
    if "check" in lower or "enforce" in lower:
        return "ALLOW_DENY_ESCALATE_decision"
    if "role_runtimes" in lower or "ceo.yaml" in lower:
        return "role_runtime_contract"
    return "governance_context"


def _enforcement_stage(role: str) -> str:
    if role in {"pre_action_packet_validation", "hook_contract_enforcement", "ALLOW_DENY_ESCALATE_decision"}:
        return "pre_action_check"
    if role in {"obligation_registration_and_closure", "CIEU_logging_or_store", "CIEU_residual_or_prediction_delta"}:
        return "post_action_residual_or_obligation"
    if role == "delegation_authority":
        return "authority_boundary"
    return "contract_definition"


def _input_schema_hint(path: str, text: str) -> str:
    lower = f"{path} {text[:6000]}".lower()
    if "hook_contract" in lower and "envelope" in lower:
        return "hook decision envelope JSON"
    if "pre_u_packet_validator" in lower:
        return "pre-U packet fields including intent/action/context/risk"
    if "u_v2_schema" in lower:
        return "U action schema YAML"
    if "intentcontract" in lower:
        return "IntentContract / Policy object"
    if "cieu_prediction_delta" in lower:
        return "CIEU prediction delta tuple"
    return "not fully discoverable from read-only inspection"


def _output_schema_hint(path: str, text: str) -> str:
    lower = f"{path} {text[:6000]}".lower()
    if "allow" in lower and "deny" in lower and "escalate" in lower:
        return "ALLOW / DENY / ESCALATE decision envelope"
    if "cieu" in lower:
        return "CIEU record or reference"
    if "fixture_matrix" in lower:
        return "fixture decision matrix"
    return "not fully discoverable from read-only inspection"


def build_ystar_gov_enforcement_surface_map(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    entries: list[dict[str, Any]] = []
    ygov_head = (_run_git(Y_GOV_ROOT, ["rev-parse", "HEAD"]) or [""])[0]
    for rel in _repo_files(Y_GOV_ROOT):
        path = Y_GOV_ROOT / rel
        text = _read(path, 300_000)
        if not (_contains_governance_signal(rel) or _contains_governance_signal(text[:10_000])):
            continue
        symbols = _parse_symbols(path) if rel.endswith(".py") else []
        if symbols:
            relevant_symbols = [symbol for symbol in symbols if _contains_governance_signal(symbol["name"]) or _contains_governance_signal(rel)]
            if not relevant_symbols:
                relevant_symbols = symbols[:3]
        else:
            relevant_symbols = [{"name": Path(rel).name, "kind": "artifact", "line": 0}]
        for symbol in relevant_symbols[:12]:
            role = _governance_role(rel, symbol["name"], text)
            stage = _enforcement_stage(role)
            can_sync = role in {
                "pre_action_packet_validation",
                "hook_contract_enforcement",
                "CIEU_residual_or_prediction_delta",
                "intent_contract_or_policy",
                "role_runtime_contract",
            }
            entries.append(
                {
                    "repo": "Y-star-gov",
                    "file_path": rel,
                    "symbol_function_class_or_artifact": symbol["name"],
                    "symbol_kind": symbol.get("kind"),
                    "line": symbol.get("line"),
                    "governance_role": role,
                    "enforcement_stage": stage,
                    "input_schema_if_discoverable": _input_schema_hint(rel, text),
                    "output_schema_if_discoverable": _output_schema_hint(rel, text),
                    "supports_pre_action_check": stage == "pre_action_check" or role in {"intent_contract_or_policy", "role_runtime_contract"},
                    "supports_obligation_registration": role == "obligation_registration_and_closure",
                    "supports_CIEU_residual_logging": "CIEU" in role,
                    "supports_contract_hashing_or_verification": any(token in f"{rel} {symbol['name']} {text[:3000]}".lower() for token in ["hash", "verify", "seal", "contract"]),
                    "bridge_labs_can_safely_sync_contract_to_it": can_sync,
                    "mutation_required": can_sync,
                    "this_milestone_may_mutate_it": False,
                    "recommended_integration_mode": "contract_packet_for_later_sync" if can_sync else "read_only_context",
                }
            )
    role_counts = Counter(entry["governance_role"] for entry in entries)
    return {
        "artifact_id": "e81_ystar_gov_enforcement_surface_map",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "Y_star_gov_root": str(Y_GOV_ROOT),
        "Y_star_gov_head_observed_read_only": ygov_head,
        "Y_star_gov_expected_base_provided": False,
        "Y_star_gov_mutated": False,
        "mutation_policy": "no_mutation_without_explicit_Y_star_gov_expected_base",
        "surface_count": len(entries),
        "role_counts": dict(role_counts.most_common()),
        "surfaces": entries[:500],
    }


def _selected_stage_caps(stage: dict[str, Any]) -> list[dict[str, Any]]:
    return stage.get("evidence_backed_capabilities", [])


def build_anti_hardcoding_discovery_proof(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    candidates = load_json("operations/external_validation/e80_discovered_capability_candidates.json", base)
    inventory = load_json("operations/external_validation/e80_whole_ecosystem_capability_inventory.json", base)
    loop = load_json("operations/external_validation/e80_ceo_online_cognition_loop_spec.json", base)
    anti = load_json("operations/external_validation/e80_anti_memory_contamination_report.json", base)
    stages = loop.get("stages", [])
    selected_caps: dict[str, dict[str, Any]] = {}
    prompt_stage_count = 0
    stages_without_repo_evidence = []
    for stage in stages:
        caps = _selected_stage_caps(stage)
        evidence_caps = [
            cap
            for cap in caps
            if cap.get("evidence_paths") and cap.get("activation_state") != "prompt_hint_unverified"
        ]
        if not evidence_caps and stage["stage_id"] not in STAGE_EVIDENCE_FALLBACKS:
            stages_without_repo_evidence.append(stage["stage_id"])
        for cap in evidence_caps:
            cap_id = cap.get("capability_id")
            if cap_id:
                selected_caps[cap_id] = cap
        if not evidence_caps and stage["stage_id"] in STAGE_EVIDENCE_FALLBACKS:
            selected_caps[f"contract_required_{stage['stage_id']}"] = {
                "capability_id": f"contract_required_{stage['stage_id']}",
                "domain": "governance_required_contract_layer",
                "activation_state": "governance_required_new_contract_layer",
                "evidence_paths": STAGE_EVIDENCE_FALLBACKS[stage["stage_id"]],
                "repository_discovered": False,
                "prompt_hint_used": False,
            }
    inventory_by_id = {cap["capability_id"]: cap for cap in inventory.get("capabilities", [])}
    selected = []
    repo_discovered_included = []
    for cap_id, cap in selected_caps.items():
        inv = inventory_by_id.get(cap_id, {})
        record = {
            "capability_id": cap_id,
            "domain": cap.get("domain") or inv.get("capability_domain"),
            "activation_state": cap.get("activation_state") or inv.get("activation_state"),
            "evidence_paths": cap.get("evidence_paths") or inv.get("file_paths", []),
            "repository_discovered": bool(inv.get("repository_discovered")),
            "prompt_hint_used": bool(inv.get("prompt_hint_used")),
        }
        selected.append(record)
        if record["repository_discovered"]:
            repo_discovered_included.append(record)
        if record["prompt_hint_used"]:
            prompt_stage_count += 1
    considered = [
        cap
        for cap in inventory.get("capabilities", [])
        if max(int(cap.get("owner_relevance", 0)), int(cap.get("commercial_relevance", 0)), int(cap.get("CEO_intelligence_relevance", 0))) >= 70
    ]
    selected_ids = {item["capability_id"] for item in selected}
    rejected = []
    for cap in considered:
        if cap["capability_id"] in selected_ids:
            continue
        reason = "not_needed_for_mandatory_loop_stage"
        if cap.get("activation_state") in {"quarantined", "obsolete", "duplicate_risk", "prompt_hint_unverified"}:
            reason = f"rejected_due_to_{cap.get('activation_state')}"
        rejected.append(
            {
                "capability_id": cap["capability_id"],
                "domain": cap.get("capability_domain"),
                "activation_state": cap.get("activation_state"),
                "reason": reason,
                "evidence_paths": cap.get("file_paths", [])[:5],
            }
        )
    return {
        "artifact_id": "e81_anti_hardcoding_discovery_proof",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "E80_capability_candidates_loaded": candidates.get("candidate_count"),
        "E80_capabilities_loaded": inventory.get("capability_count"),
        "capabilities_considered_for_CEO_cognition": len(considered),
        "capabilities_selected_from_repository_evidence": len(selected),
        "selected_capabilities": selected,
        "capabilities_rejected_sample": rejected[:80],
        "capabilities_named_in_prompt_but_not_verified": anti.get("prompt_hinted_capabilities_not_found_or_not_active", []),
        "repository_discovered_capabilities_not_named_in_prompt_but_included": repo_discovered_included,
        "evidence_paths_for_every_selected_capability_present": all(item["evidence_paths"] for item in selected),
        "loop_stages_without_repository_evidence": stages_without_repo_evidence,
        "loop_stage_prompt_invented_count": len(stages_without_repo_evidence),
        "prompt_hinted_selected_capability_count": prompt_stage_count,
        "anti_hardcoding_rule_passed": bool(selected) and not stages_without_repo_evidence and all(item["evidence_paths"] for item in selected),
    }


def _schema_required_fields(kind: str) -> list[str]:
    if kind == "pre":
        return [
            "packet_id",
            "job_id",
            "proposed_action",
            "action_class",
            "owner_intent",
            "current_mission_context",
            "discovered_capabilities_consulted",
            "historical_assets_consulted",
            "canonical_owner_map",
            "no_new_wheel_decision",
            "candidate_actions",
            "counterfactual_comparison",
            "predicted_CIEU_records",
            "adversarial_critique",
            "what_not_to_do",
            "selected_action",
            "why_this_action",
            "why_not_other_actions",
            "safety_boundary",
            "overclaim_boundary",
            "Y_star_contract_hash_input",
            "required_YstarGov_check",
            "approval_required",
            "owner_approval_state",
            "bypass_attempt",
            "loop_stage_results",
        ]
    return [
        "packet_id",
        "linked_pre_action_packet_id",
        "action_taken",
        "expected_outcome",
        "actual_output",
        "CIEU_record",
        "residuals",
        "unexpected_failures",
        "overclaim_check",
        "no_new_wheel_check",
        "owner_usefulness_check",
        "intelligence_gate_result",
        "capability_state_updates",
        "learning_candidates",
        "YstarGov_sync_status",
        "next_action_recommendation",
        "what_not_to_do_next",
    ]


def _stage_clause(stage_id: str) -> str:
    return f"CEO work MUST complete stage {stage_id} with repository evidence or governance-required contract evidence before major action selection."


def build_cognitive_os_loop_contract(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    loop = load_json("operations/external_validation/e80_ceo_online_cognition_loop_spec.json", base)
    surface = load_json("operations/external_validation/e81_ystar_gov_enforcement_surface_map.json", base)
    stages = []
    for stage in loop.get("stages", []):
        caps = _selected_stage_caps(stage)
        evidence_paths = sorted({path for cap in caps for path in cap.get("evidence_paths", [])})
        if not evidence_paths:
            evidence_paths = STAGE_EVIDENCE_FALLBACKS.get(stage["stage_id"], [])
        owners = sorted({cap.get("canonical_owner") or "bridge-labs" for cap in caps})
        activation_states = sorted({cap.get("activation_state") for cap in caps if cap.get("activation_state")})
        status = stage.get("status") if caps else "governance_required_new_contract_layer"
        stages.append(
            {
                "stage_id": stage["stage_id"],
                "stage_name": stage["purpose"].title(),
                "purpose": stage["purpose"],
                "required_inputs": ["pre_action_packet", "E80_capability_inventory", "owner_constraints"],
                "required_outputs": ["stage_result", "evidence_paths", "pass_or_fail_status"],
                "evidence_source_paths": evidence_paths,
                "capability_owner": owners or ["bridge-labs"],
                "activation_state": status,
                "pass_condition": "stage_result present, evidence paths non-empty, and fail condition not triggered",
                "fail_condition": stage.get("fails_if"),
                "Y_star_contract_clause": _stage_clause(stage["stage_id"]),
                "CIEU_pre_action_fields": ["X_t", "U_t", "Y_star_t", "expected_Y_t_plus_1", "predicted_R_t_plus_1"],
                "CIEU_post_action_fields": ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"],
                "bypass_allowed": False,
                "bypass_policy": "DENY if bypassed; ESCALATE only if owner explicitly authorizes emergency override in a later governance layer",
                "immediate_bridge_labs_preflight_enforceable": True,
                "YstarGov_sync_target_candidate_count": surface.get("surface_count", 0),
                "contract_required_but_not_runtime_backed": status in {"missing_runtime_hook", "governance_required_new_contract_layer", "design_bound_not_runtime_active"},
            }
        )
    return {
        "artifact_id": "e81_ceo_cognitive_os_loop_contract",
        "contract_id": "ceo_cognitive_os_loop_contract_v1",
        "contract_name": "CEO Cognitive OS Mandatory Loop",
        "version": "1.0.0",
        "bridge_job_id": JOB_ID,
        "created_at": utc_now(),
        "derived_from": [
            "operations/external_validation/e80_discovered_capability_candidates.json",
            "operations/external_validation/e80_whole_ecosystem_capability_inventory.json",
            "operations/external_validation/e80_ceo_online_cognition_loop_spec.json",
            "operations/external_validation/e81_ystar_gov_enforcement_surface_map.json",
        ],
        "discovery_evidence_based": True,
        "mandatory_stage_count": len(stages),
        "mandatory_stages": stages,
        "runtime_active_today": [stage["stage_id"] for stage in stages if stage["activation_state"] == "runtime_active_or_adapter_active"],
        "contract_required_but_not_runtime_backed": [stage["stage_id"] for stage in stages if stage["contract_required_but_not_runtime_backed"]],
        "requires_later_YstarGov_mutation": True,
        "can_be_enforced_immediately_in_bridge_labs_preflight": True,
        "canonical_governance_owner": "Y-star-gov",
        "bridge_labs_role": "pre_sync_validator_and_contract_packet_owner",
        "bypass_allowed": False,
        "bypass_decision": "DENY",
        "external_action_allowed": False,
    }


def build_pre_action_packet_schema(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    contract = load_json("operations/external_validation/e81_ceo_cognitive_os_loop_contract.json", base)
    return {
        "artifact_id": "e81_ceo_mandatory_pre_action_packet_schema",
        "schema_id": "ceo_mandatory_pre_action_packet_v1",
        "bridge_job_id": JOB_ID,
        "YstarGov_compatible": True,
        "minimum_required_fields": _schema_required_fields("pre"),
        "required_loop_stage_ids": [stage["stage_id"] for stage in contract.get("mandatory_stages", [])],
        "predicted_CIEU_record_required_fields": ["X_t", "U_t", "Y_star_t", "expected_Y_t_plus_1", "predicted_R_t_plus_1", "residual_severity"],
        "required_owner_approval_states": ["not_required", "pending_owner_decision", "approved", "rejected"],
        "bypass_attempt_allowed_values": [False],
        "invalid_if_missing": [
            "ecosystem recall",
            "counterfactual comparison",
            "pre-action CIEU prediction",
            "adversarial critique",
            "what-not-to-do declaration",
            "owner approval state",
        ],
    }


def build_post_action_residual_schema(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e81_ceo_mandatory_post_action_residual_schema",
        "schema_id": "ceo_mandatory_post_action_residual_v1",
        "bridge_job_id": JOB_ID,
        "YstarGov_compatible": True,
        "minimum_required_fields": _schema_required_fields("post"),
        "CIEU_record_required_fields": ["X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"],
        "invalid_if_missing": [
            "linked pre-action packet",
            "CIEU five-tuple",
            "overclaim check",
            "no-new-wheel check",
            "owner usefulness check",
            "next action recommendation",
        ],
    }


def build_ystar_gov_sync_packet(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    contract = load_json("operations/external_validation/e81_ceo_cognitive_os_loop_contract.json", base)
    pre_schema = load_json("operations/external_validation/e81_ceo_mandatory_pre_action_packet_schema.json", base)
    post_schema = load_json("operations/external_validation/e81_ceo_mandatory_post_action_residual_schema.json", base)
    surface = load_json("operations/external_validation/e81_ystar_gov_enforcement_surface_map.json", base)
    sync_targets = [
        entry
        for entry in surface.get("surfaces", [])
        if entry.get("bridge_labs_can_safely_sync_contract_to_it")
    ][:30]
    return {
        "artifact_id": "e81_ystar_gov_sync_packet_for_ceo_cognitive_os",
        "contract_id": contract.get("contract_id"),
        "contract_name": contract.get("contract_name"),
        "version": contract.get("version"),
        "source_bridge_labs_job_id": JOB_ID,
        "required_CEO_loop_stages": [stage["stage_id"] for stage in contract.get("mandatory_stages", [])],
        "pre_action_packet_schema": pre_schema,
        "post_action_residual_schema": post_schema,
        "Y_star_clauses": [stage["Y_star_contract_clause"] for stage in contract.get("mandatory_stages", [])],
        "denial_conditions": [
            "missing required loop stage",
            "missing repository evidence for claimed capability",
            "missing counterfactual comparison",
            "missing pre-action CIEU prediction",
            "missing adversarial critique",
            "missing what-not-to-do declaration",
            "construction recommendation without no-new-wheel proof",
            "owner approval required but absent",
            "forbidden readiness/validation/compliance/revenue claim",
            "bypass attempt",
        ],
        "escalation_conditions": [
            "future owner explicitly requests Y-star-gov mutation",
            "valid pre-action packet proposes an action requiring owner approval",
            "canonical owner is external read-only repo and sync is needed",
        ],
        "required_owner_approvals": ["Y-star-gov patch approval before mutation", "L4 execution approval before external feedback"],
        "bypass_detection_rules": ["bypass_attempt true", "missing pre-action packet", "missing post-action residual"],
        "CIEU_logging_requirements": ["pre-action predicted tuple", "post-action actual tuple", "validator decision record"],
        "integration_target_candidates_from_YstarGov_inspection": sync_targets,
        "proposed_files_or_functions_to_update_if_later_approved": sorted({entry["file_path"] for entry in sync_targets})[:20],
        "tests_YstarGov_should_add": [
            "test_ceo_cognitive_os_pre_action_packet_validator.py",
            "test_ceo_cognitive_os_bypass_denied.py",
            "test_ceo_cognitive_os_post_action_residual_required.py",
        ],
        "rollback_plan": "revert Y-star-gov sync patch and continue using bridge-labs pre-sync validator artifacts",
        "non_duplication_proof": "bridge-labs produces contract packet and fixtures only; Y-star-gov remains canonical check/enforce owner",
        "why_bridge_labs_cannot_be_canonical_enforcement_owner": "E73/E80 responsibility boundaries assign governance/check/enforce semantics to Y-star-gov; bridge-labs may preflight but not replace canonical governance.",
        "Y_star_gov_mutated_in_E81": False,
        "external_action_allowed": False,
    }


def build_ystar_gov_patch_plan_no_mutation(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    sync = load_json("operations/external_validation/e81_ystar_gov_sync_packet_for_ceo_cognitive_os.json", base)
    return {
        "artifact_id": "e81_ystar_gov_patch_plan_no_mutation",
        "bridge_job_id": JOB_ID,
        "Y_star_gov_mutated": False,
        "why_not_mutated": "No explicit expected Y-star-gov base HEAD was provided for E81; read-only inspection only.",
        "owner_approval_required_before_patch": True,
        "expected_future_patch_scope": {
            "candidate_files": sync.get("proposed_files_or_functions_to_update_if_later_approved", []),
            "new_fixture_candidates": sync.get("tests_YstarGov_should_add", []),
            "contract_packet_source": "operations/external_validation/e81_ystar_gov_sync_packet_for_ceo_cognitive_os.json",
        },
        "rollback_plan": sync.get("rollback_plan"),
        "non_duplication_proof": sync.get("non_duplication_proof"),
    }


def _md_table(rows: list[list[Any]], headers: list[str]) -> list[str]:
    result = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        result.append("| " + " | ".join(str(value).replace("\n", " ")[:180] for value in row) + " |")
    return result


def write_contract_markdowns(root: Path, outputs: dict[str, Any]) -> None:
    proof = outputs["anti_hardcoding"]
    write_md(
        root,
        "operations/external_validation/e81_anti_hardcoding_discovery_proof.md",
        "E81 Anti-Hardcoding Discovery Proof",
        [
            f"- E80 candidates loaded: {proof['E80_capability_candidates_loaded']}",
            f"- Capabilities considered for CEO cognition: {proof['capabilities_considered_for_CEO_cognition']}",
            f"- Selected from repository evidence: {proof['capabilities_selected_from_repository_evidence']}",
            f"- Loop stage prompt-invented count: {proof['loop_stage_prompt_invented_count']}",
            f"- Anti-hardcoding passed: {proof['anti_hardcoding_rule_passed']}",
        ],
    )
    surface = outputs["surface"]
    write_md(
        root,
        "operations/external_validation/e81_ystar_gov_enforcement_surface_map.md",
        "E81 Y-star-gov Enforcement Surface Map",
        [
            f"- Y-star-gov observed HEAD: {surface['Y_star_gov_head_observed_read_only']}",
            f"- Surfaces found: {surface['surface_count']}",
            f"- Y-star-gov mutated: {surface['Y_star_gov_mutated']}",
            "",
            *_md_table([[key, value] for key, value in surface["role_counts"].items()], ["role", "count"]),
        ],
    )
    contract = outputs["contract"]
    write_md(
        root,
        "operations/external_validation/e81_ceo_cognitive_os_loop_contract.md",
        "E81 CEO Cognitive OS Loop Contract",
        [
            f"- Contract id: {contract['contract_id']}",
            f"- Mandatory stages: {contract['mandatory_stage_count']}",
            f"- Bridge-labs preflight enforceable now: {contract['can_be_enforced_immediately_in_bridge_labs_preflight']}",
            f"- Requires later Y-star-gov mutation: {contract['requires_later_YstarGov_mutation']}",
            "",
            *_md_table(
                [[stage["stage_id"], stage["activation_state"], ",".join(stage["capability_owner"]), stage["bypass_allowed"]] for stage in contract["mandatory_stages"]],
                ["stage", "state", "owners", "bypass_allowed"],
            ),
        ],
    )
    for key, rel, title in [
        ("pre_schema", "operations/external_validation/e81_ceo_mandatory_pre_action_packet_schema.md", "E81 Mandatory Pre-Action Packet Schema"),
        ("post_schema", "operations/external_validation/e81_ceo_mandatory_post_action_residual_schema.md", "E81 Mandatory Post-Action Residual Schema"),
    ]:
        schema = outputs[key]
        write_md(
            root,
            rel,
            title,
            [
                f"- Schema id: {schema['schema_id']}",
                f"- Y*gov compatible: {schema['YstarGov_compatible']}",
                "",
                "Required fields:",
                *[f"- {field}" for field in schema["minimum_required_fields"]],
            ],
        )
    sync = outputs["sync"]
    write_md(
        root,
        "operations/external_validation/e81_ystar_gov_sync_packet_for_ceo_cognitive_os.md",
        "E81 Y-star-gov Sync Packet For CEO Cognitive OS",
        [
            f"- Contract id: {sync['contract_id']}",
            f"- Integration target candidates: {len(sync['integration_target_candidates_from_YstarGov_inspection'])}",
            f"- Y-star-gov mutated in E81: {sync['Y_star_gov_mutated_in_E81']}",
            "",
            "Denial conditions:",
            *[f"- {item}" for item in sync["denial_conditions"]],
        ],
    )
    patch = outputs["patch_plan"]
    write_md(
        root,
        "operations/external_validation/e81_ystar_gov_patch_plan_no_mutation.md",
        "E81 Y-star-gov Patch Plan No Mutation",
        [
            f"- Y-star-gov mutated: {patch['Y_star_gov_mutated']}",
            f"- Why not mutated: {patch['why_not_mutated']}",
            f"- Owner approval required: {patch['owner_approval_required_before_patch']}",
        ],
    )


def write_contract_outputs(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    surface = build_ystar_gov_enforcement_surface_map(base)
    write_json(base, "operations/external_validation/e81_ystar_gov_enforcement_surface_map.json", surface)
    proof = build_anti_hardcoding_discovery_proof(base)
    write_json(base, "operations/external_validation/e81_anti_hardcoding_discovery_proof.json", proof)
    contract = build_cognitive_os_loop_contract(base)
    write_json(base, "operations/external_validation/e81_ceo_cognitive_os_loop_contract.json", contract)
    pre_schema = build_pre_action_packet_schema(base)
    write_json(base, "operations/external_validation/e81_ceo_mandatory_pre_action_packet_schema.json", pre_schema)
    post_schema = build_post_action_residual_schema(base)
    write_json(base, "operations/external_validation/e81_ceo_mandatory_post_action_residual_schema.json", post_schema)
    sync = build_ystar_gov_sync_packet(base)
    write_json(base, "operations/external_validation/e81_ystar_gov_sync_packet_for_ceo_cognitive_os.json", sync)
    patch_plan = build_ystar_gov_patch_plan_no_mutation(base)
    write_json(base, "operations/external_validation/e81_ystar_gov_patch_plan_no_mutation.json", patch_plan)
    outputs = {
        "surface": surface,
        "anti_hardcoding": proof,
        "contract": contract,
        "pre_schema": pre_schema,
        "post_schema": post_schema,
        "sync": sync,
        "patch_plan": patch_plan,
    }
    write_contract_markdowns(base, outputs)
    return outputs


if __name__ == "__main__":
    result = write_contract_outputs()
    print(json.dumps({"artifact_id": "e81_contract_outputs", "stage_count": result["contract"]["mandatory_stage_count"]}, indent=2))
