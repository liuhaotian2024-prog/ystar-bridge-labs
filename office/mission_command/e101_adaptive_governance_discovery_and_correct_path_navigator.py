from __future__ import annotations

import importlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
MILESTONE_ID = "E101_Adaptive_Governance_Discovery_And_Correct_Path_Navigator_R1"

OBLIGATION_RULES: tuple[dict[str, Any], ...] = (
    {
        "obligation_id": "six_d_brain_review",
        "required_when": ["market_strategy_required", "brain_strategy", "strategic_decision"],
        "correct_path": "run the 6D brain review, attach brain_provenance and six_d_brain_review, then revalidate",
    },
    {
        "obligation_id": "pricing_hypothesis_source_audit",
        "required_when": ["price_hypothesis_present", "first_cash_path_selected", "revenue_or_payment_related"],
        "correct_path": "state price as hypothesis, attach source basis, non-claims, and falsification test",
    },
    {
        "obligation_id": "right_to_win_analysis",
        "required_when": ["market_strategy_required", "route_selected"],
        "correct_path": "compare why Y*Bridge Labs is fit against alternatives and name weaknesses",
    },
    {
        "obligation_id": "strongest_validation_question",
        "required_when": ["L4_feedback_packet_prepared", "price_hypothesis_present", "market_strategy_required"],
        "correct_path": "produce one owner-gated no-send willingness-to-pay question",
    },
    {
        "obligation_id": "competitor_differentiation_map",
        "required_when": ["market_strategy_required", "product_shape_selected"],
        "correct_path": "name competitors and alternatives, then choose the narrow wedge",
    },
    {
        "obligation_id": "external_observation_or_staleness_boundary",
        "required_when": ["external_observation_required", "market_strategy_required"],
        "correct_path": "invoke public-read observation or mark evidence stale/insufficient",
    },
    {
        "obligation_id": "gov_mcp_dry_run_preflight",
        "required_when": ["provider_tool_boundary", "external_action_candidate"],
        "correct_path": "route provider/tool boundary through gov-mcp dry-run/no-send receipt",
    },
    {
        "obligation_id": "ceo_implementation_order",
        "required_when": ["codex_executor_boundary", "codex_prompt_generation"],
        "correct_path": "build CEOImplementationOrder before Codex prompt generation",
    },
    {
        "obligation_id": "post_action_residual",
        "required_when": ["major_action", "completed_action", "runtime_session"],
        "correct_path": "build post-action residual and CIEU learning candidate",
    },
    {
        "obligation_id": "new_governance_obligation_candidate",
        "required_when": ["new_capability_discovered", "residual_learning", "strategy_question_answered"],
        "correct_path": "convert the new repeatable capability into a governance obligation candidate",
    },
)


def discover_adaptive_governance_obligations(
    *,
    action_context: Mapping[str, Any],
    runtime_artifact: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    artifact = runtime_artifact or {}
    signals = _signals(action_context, artifact)
    discovered = []
    required = []
    advisory = []
    for rule in OBLIGATION_RULES:
        matched = sorted(set(rule["required_when"]) & signals)
        if matched:
            obligation = {
                "obligation_id": rule["obligation_id"],
                "matched_signals": matched,
                "correct_path": rule["correct_path"],
            }
            discovered.append(obligation)
            if _is_required(rule["obligation_id"], action_context, signals):
                required.append(obligation)
            else:
                advisory.append(obligation)
    return {
        "signals": sorted(signals),
        "discovered_obligations": discovered,
        "required_obligations": required,
        "advisory_obligations": advisory,
    }


def build_obligation_invocation_proof(
    *,
    discovery: Mapping[str, Any],
    existing_proof: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    existing = existing_proof or {}
    supplied = set(existing.get("satisfied_obligations") or [])
    required_ids = [item["obligation_id"] for item in discovery.get("required_obligations", [])]
    auto_satisfied = _auto_satisfied_from_existing(existing)
    satisfied = sorted((supplied | auto_satisfied) & set(required_ids))
    missing = [item for item in required_ids if item not in satisfied]
    return {
        "proof_id": existing.get("proof_id") or "adaptive_governance_obligation_invocation_proof",
        "satisfied_obligations": satisfied,
        "missing_obligations": missing,
        "evidence_refs": list(existing.get("evidence_refs") or []),
        "customer_validation_claim": bool(existing.get("customer_validation_claim", False)),
        "pricing_validation_claim": bool(existing.get("pricing_validation_claim", False)),
        "revenue_claim": bool(existing.get("revenue_claim", False)),
        "payment_claim": bool(existing.get("payment_claim", False)),
        "external_action_executed": bool(existing.get("external_action_executed", False)),
    }


def build_correct_path_navigator(discovery: Mapping[str, Any], proof: Mapping[str, Any]) -> dict[str, Any]:
    missing = proof.get("missing_obligations") or []
    obligation_map = {item["obligation_id"]: item for item in discovery.get("required_obligations", [])}
    steps = [
        {
            "missing_obligation": obligation_id,
            "correct_path": obligation_map.get(obligation_id, {}).get(
                "correct_path",
                f"satisfy obligation {obligation_id} and rerun adaptive governance",
            ),
            "next_allowed_action": "repair_packet_only",
        }
        for obligation_id in missing
    ]
    return {
        "navigator_id": "adaptive_governance_correct_path_navigator_v1",
        "decision_style": "路牌式治理: repairable gaps return REQUIRE_REVISION with correct_path; hard false claims return DENY",
        "missing_obligation_count": len(missing),
        "steps": steps,
        "blocked_until_repaired": [
            "external_execution",
            "provider_execution",
            "customer_validation_claim",
            "revenue_or_payment_claim",
        ],
    }


def build_adaptive_governance_result(
    *,
    action_context: Mapping[str, Any],
    runtime_artifact: Mapping[str, Any] | None = None,
    invocation_proof: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    discovery = discover_adaptive_governance_obligations(
        action_context=action_context,
        runtime_artifact=runtime_artifact,
    )
    proof = build_obligation_invocation_proof(discovery=discovery, existing_proof=invocation_proof)
    navigator = build_correct_path_navigator(discovery, proof)
    return {
        "artifact_id": "e101_adaptive_governance_discovery_result",
        "milestone_id": MILESTONE_ID,
        "discovery_id": f"adaptive_governance::{action_context.get('action_id', 'unknown_action')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "action_context": dict(action_context),
        "discovered_obligations": discovery["discovered_obligations"],
        "required_obligations": discovery["required_obligations"],
        "advisory_obligations": discovery["advisory_obligations"],
        "obligation_invocation_proof": proof,
        "correct_path_navigator": navigator,
        "bypass_prevention": {
            "runtime_gate_required": True,
            "missing_result_decision": "REQUIRE_REVISION",
            "missing_obligation_decision": "REQUIRE_REVISION",
            "false_claim_decision": "DENY",
            "owner_bound_external_action_decision": "ESCALATE",
        },
        "truth_constraints": {
            "customer_validation_claim": False,
            "pricing_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "paid_signal_claim": False,
            "K9Audit_integration_claim": False,
            "live_provider_execution_claim": False,
        },
    }


def load_ystar_adaptive_governance(ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module("ystar.governance")


def enforce_adaptive_governance_before_runtime(
    *,
    action_context: Mapping[str, Any],
    cieu_db: str,
    runtime_artifact: Mapping[str, Any] | None = None,
    invocation_proof: Mapping[str, Any] | None = None,
    ystar_gov_root: Path | None = None,
    session_id: str | None = None,
    seal_session: bool = False,
) -> dict[str, Any]:
    governance = load_ystar_adaptive_governance(ystar_gov_root)
    result = build_adaptive_governance_result(
        action_context=action_context,
        runtime_artifact=runtime_artifact,
        invocation_proof=invocation_proof,
    )
    write = governance.validate_and_write_ceo_adaptive_governance_result(
        result,
        cieu_db=cieu_db,
        session_id=session_id,
        seal_session=seal_session,
    )
    decision = write.get("governance_decision", {}).get("decision")
    return {
        "adaptive_governance_gate_passed": decision == "ALLOW",
        "adaptive_governance_result": result,
        "adaptive_governance_write": write,
        "runtime_may_continue": decision == "ALLOW",
        "correct_path": write.get("governance_decision", {}).get("correct_path", []),
    }


def adaptive_metadata_from_gate(gate: Mapping[str, Any]) -> dict[str, Any]:
    result = gate.get("adaptive_governance_result") if isinstance(gate.get("adaptive_governance_result"), Mapping) else {}
    return {
        "adaptive_governance_discovery_id": result.get("discovery_id", ""),
        "adaptive_required_obligations": [
            item.get("obligation_id") for item in result.get("required_obligations", []) if isinstance(item, Mapping)
        ],
        "adaptive_governance_decision": gate.get("adaptive_governance_write", {}).get("governance_decision", {}).get("decision", ""),
        "correct_path_available": bool(gate.get("correct_path")),
    }


def _signals(action_context: Mapping[str, Any], artifact: Mapping[str, Any]) -> set[str]:
    signals = set()
    for key in (
        "market_strategy_required",
        "external_observation_required",
        "provider_tool_boundary",
        "owner_decision_required",
        "revenue_or_payment_related",
        "K9Audit_related",
        "codex_executor_boundary",
        "codex_prompt_generation",
        "completed_action",
        "new_capability_discovered",
        "residual_learning",
    ):
        if action_context.get(key) is True or artifact.get(key) is True:
            signals.add(key)
    action_type = str(action_context.get("action_type") or "")
    mission_type = str(action_context.get("mission_type") or "")
    route_type = str(action_context.get("route_type") or "")
    text = " ".join(str(value).lower() for value in [action_type, mission_type, route_type, artifact])
    if "market" in text or "strategy" in text:
        signals.update({"market_strategy_required", "strategic_decision", "route_selected"})
    if "price" in text or "$" in text or "cash" in text or "revenue" in text:
        signals.update({"price_hypothesis_present", "first_cash_path_selected"})
    if "l4" in text or "feedback" in text or "external" in text:
        signals.update({"L4_feedback_packet_prepared", "external_action_candidate"})
    if "competitor" in text or "product" in text:
        signals.update({"product_shape_selected"})
    if "brain" in text or "6d" in text:
        signals.add("brain_strategy")
    if "codex" in text or "prompt" in text:
        signals.update({"codex_executor_boundary", "codex_prompt_generation"})
    if action_context.get("L_level") in ("L4", "L5"):
        signals.add("external_action_candidate")
    if action_context.get("major_action", True):
        signals.update({"major_action", "runtime_session"})
    return signals


def _is_required(obligation_id: str, action_context: Mapping[str, Any], signals: set[str]) -> bool:
    if obligation_id in {"six_d_brain_review", "post_action_residual"}:
        return bool(action_context.get("major_action", True) or action_context.get("market_strategy_required"))
    if obligation_id == "new_governance_obligation_candidate":
        return bool(action_context.get("new_capability_discovered") or action_context.get("residual_learning"))
    return True


def _auto_satisfied_from_existing(existing: Mapping[str, Any]) -> set[str]:
    satisfied = set()
    if existing.get("brain_provenance") and existing.get("six_d_brain_review"):
        satisfied.add("six_d_brain_review")
    if existing.get("pricing_hypothesis_source_audit"):
        satisfied.add("pricing_hypothesis_source_audit")
    if existing.get("right_to_win_analysis"):
        satisfied.add("right_to_win_analysis")
    if existing.get("strongest_validation_question"):
        satisfied.add("strongest_validation_question")
    if existing.get("competitor_differentiation_map"):
        satisfied.add("competitor_differentiation_map")
    if existing.get("external_observation_status"):
        satisfied.add("external_observation_or_staleness_boundary")
    if existing.get("gov_mcp_receipt"):
        satisfied.add("gov_mcp_dry_run_preflight")
    if existing.get("ceo_implementation_order"):
        satisfied.add("ceo_implementation_order")
    if existing.get("post_action_residual"):
        satisfied.add("post_action_residual")
    if existing.get("new_governance_obligation_candidate"):
        satisfied.add("new_governance_obligation_candidate")
    return satisfied


__all__ = [
    "MILESTONE_ID",
    "OBLIGATION_RULES",
    "adaptive_metadata_from_gate",
    "build_adaptive_governance_result",
    "build_correct_path_navigator",
    "build_obligation_invocation_proof",
    "discover_adaptive_governance_obligations",
    "enforce_adaptive_governance_before_runtime",
    "load_ystar_adaptive_governance",
]
