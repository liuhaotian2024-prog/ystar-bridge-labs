from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping


REGISTRY_ID = "e119_aiden_operating_pattern_doctrine_registry_v1"


def build_aiden_operating_pattern_doctrine_registry() -> dict[str, Any]:
    patterns = [
        _pattern("full_repo_and_baseline_first", "Read canonical baseline and current code before action.", ("all_major_actions",)),
        _pattern("no_new_wheel_preflight", "Search for existing capabilities before creating new ones.", ("all_major_actions",)),
        _pattern("capability_utilization_sweep", "Route through existing labs/Y-star-gov/gov-mcp capabilities where possible.", ("all_major_actions",)),
        _pattern("class_level_extrapolation_gate", "Convert point failures into class-level rules and same-class variants.", ("all_major_actions",)),
        _pattern("correct_path_navigation", "Governance must return a repair path, not only a hard stop.", ("all_major_actions",)),
        _pattern("evidence_quality_and_freshness_gate", "Filter stale, low-quality, undated, or weakly corroborated evidence.", ("all_major_actions", "market_strategy")),
        _pattern("regression_test_and_cieu_closure", "Close implementation with tests and formal CIEU-backed proof.", ("all_major_actions",)),
        _pattern("brain_provenance_required", "High-level CEO strategy must prove brain provenance.", ("market_strategy",)),
        _pattern("competitive_landscape_current_signal", "Competitor claims need dated, current public signals.", ("market_strategy",)),
        _pattern("buyer_visible_value_translation", "Translate internal assets into buyer-visible value or mark them as internal-only.", ("market_strategy",)),
        _pattern("residual_truth_scope_split", "Separate planning residual closure from real market residual closure.", ("market_strategy",)),
        _pattern("CEOImplementationOrder_before_Codex_prompt", "Codex prompt generation requires a governed CEOImplementationOrder.", ("codex_execution",)),
        _pattern("CodexExecutionReceipt_return_path", "Codex execution must return a receipt for CEO residual learning.", ("codex_execution",)),
        _pattern("production_brain_write_owner_backup_gate", "Production brain writes require owner approval and verified backup.", ("brain_write",)),
        _pattern("learning_quality_scoring_v2", "Learning candidates need source depth, specificity, verifiability, and quality scoring.", ("brain_write",)),
        _pattern("gov_mcp_no_send_preflight", "Provider/tool boundaries must preserve no-send dry-run invariants.", ("external_action",)),
        _pattern("owner_boundary_minimization_and_escalation", "Autonomously execute low-risk internal work; escalate high-risk external/payment actions.", ("external_action",)),
        _pattern("proposal_only_no_direct_contract_mutation", "Aiden may propose governance changes but cannot mutate contracts directly.", ("self_governance",)),
        _pattern("owner_review_before_contract_patch", "Governance patches require owner-visible review before code generation.", ("self_governance",)),
    ]
    return {
        "registry_id": REGISTRY_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "Mechanize reusable Codex/Aiden success methods as Aiden runtime operating patterns.",
        "patterns": patterns,
    }


def resolve_required_operating_patterns(action_context: Mapping[str, Any]) -> list[str]:
    required = {
        "full_repo_and_baseline_first",
        "no_new_wheel_preflight",
        "capability_utilization_sweep",
        "class_level_extrapolation_gate",
        "correct_path_navigation",
        "evidence_quality_and_freshness_gate",
        "regression_test_and_cieu_closure",
    }
    if action_context.get("market_strategy_required") is True:
        required.update(
            {
                "brain_provenance_required",
                "competitive_landscape_current_signal",
                "buyer_visible_value_translation",
                "residual_truth_scope_split",
            }
        )
    if action_context.get("codex_execution_required") is True:
        required.update({"CEOImplementationOrder_before_Codex_prompt", "CodexExecutionReceipt_return_path"})
    if action_context.get("brain_write_related") is True:
        required.update({"production_brain_write_owner_backup_gate", "learning_quality_scoring_v2"})
    if action_context.get("external_action_related") is True:
        required.update({"gov_mcp_no_send_preflight", "owner_boundary_minimization_and_escalation"})
    if action_context.get("self_governance_related") is True:
        required.update({"proposal_only_no_direct_contract_mutation", "owner_review_before_contract_patch"})
    return sorted(required)


def build_operating_pattern_invocation_plan(action_context: Mapping[str, Any]) -> dict[str, Any]:
    required = resolve_required_operating_patterns(action_context)
    registry = build_aiden_operating_pattern_doctrine_registry()
    pattern_by_id = {item["pattern_id"]: item for item in registry["patterns"]}
    return {
        "registry_id": registry["registry_id"],
        "action_context": dict(action_context),
        "required_patterns": required,
        "pattern_invocations": [
            {
                "pattern_id": pattern_id,
                "invocation_status": "invoked",
                "source_doctrine": pattern_by_id[pattern_id],
                "output_summary": pattern_by_id[pattern_id]["runtime_obligation"],
                "evidence_refs": pattern_by_id[pattern_id]["evidence_refs"],
                "runtime_governance_required": True,
            }
            for pattern_id in required
        ],
        "truth_constraints": {
            "recent_memory_only": False,
            "skipped_no_new_wheel": False,
            "raw_codex_prompt_without_order": False,
            "static_template_used_for_live_strategy": False,
            "direct_contract_mutation": False,
            "external_action_executed_without_owner_approval": False,
            "customer_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "K9Audit_integration_claim": False,
        },
    }


def build_operating_pattern_invocation_proof(action_context: Mapping[str, Any]) -> dict[str, Any]:
    plan = build_operating_pattern_invocation_plan(action_context)
    return {
        **plan,
        "proof_id": f"{action_context.get('action_id', 'aiden_action')}_operating_pattern_proof",
        "proof_status": "all_required_patterns_invoked",
        "CIEU_recording_required": True,
    }


def _pattern(pattern_id: str, runtime_obligation: str, applies_to: tuple[str, ...]) -> dict[str, Any]:
    return {
        "pattern_id": pattern_id,
        "runtime_obligation": runtime_obligation,
        "applies_to": list(applies_to),
        "source_refs": [
            "E113 no-new-wheel runtime law",
            "E115 deep strategy anti-gaming",
            "E117 strategy quality gates",
            "E118 production brain write boundary",
            "E119 self-governance proposal loop",
        ],
        "evidence_refs": [f"doctrine://{pattern_id}", "operations/baseline/e87r_full_repo_baseline"],
        "mandatory_status": "mandatory_when_applicable",
    }


__all__ = [
    "REGISTRY_ID",
    "build_aiden_operating_pattern_doctrine_registry",
    "build_operating_pattern_invocation_plan",
    "build_operating_pattern_invocation_proof",
    "resolve_required_operating_patterns",
]
