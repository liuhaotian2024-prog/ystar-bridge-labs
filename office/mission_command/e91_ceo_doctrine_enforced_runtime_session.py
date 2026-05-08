from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from typing import Any, Mapping

from office.mission_command.e91_ceo_operating_doctrine_registry import (
    build_default_action_context,
    build_doctrine_invocation_plan,
    build_doctrine_invocation_proof,
)
from office.mission_command.e101_adaptive_governance_discovery_and_correct_path_navigator import (
    adaptive_metadata_from_gate,
    enforce_adaptive_governance_before_runtime,
)


Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def load_ystar_governance(ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module("ystar.governance")


def enforce_doctrine_before_ceo_runtime(
    *,
    action_context: Mapping[str, Any],
    cieu_db: str,
    ystar_gov_root: Path | None = None,
    session_id: str | None = None,
    seal_session: bool = False,
) -> dict[str, Any]:
    """Validate/write doctrine plan and proof before any CEO major action continues."""

    governance = load_ystar_governance(ystar_gov_root)
    adaptive_invocation_proof = action_context.get("adaptive_governance_invocation_proof") if isinstance(action_context, Mapping) else None
    if adaptive_invocation_proof is None and action_context.get("test_mode") is True:
        adaptive_invocation_proof = {
            "proof_id": f"{action_context.get('action_id', 'unknown')}_test_mode_adaptive_proof",
            "satisfied_obligations": [
                "six_d_brain_review",
                "pricing_hypothesis_source_audit",
                "right_to_win_analysis",
                "strongest_validation_question",
                "competitor_differentiation_map",
                "external_observation_or_staleness_boundary",
                "gov_mcp_dry_run_preflight",
                "ceo_implementation_order",
                "post_action_residual",
            ],
            "evidence_refs": ["test_mode: existing E89/E90 deterministic fixtures and reports"],
        }
    adaptive_gate = enforce_adaptive_governance_before_runtime(
        action_context=action_context,
        cieu_db=cieu_db,
        runtime_artifact={"source_gate": "e91_doctrine_enforced_runtime_session"},
        invocation_proof=adaptive_invocation_proof,
        ystar_gov_root=ystar_gov_root,
        session_id=session_id,
        seal_session=False,
    )
    if not adaptive_gate["runtime_may_continue"]:
        return {
            "adaptive_governance_gate_passed": False,
            "doctrine_gate_passed": False,
            "blocked_at": "adaptive_governance",
            "adaptive_gate": adaptive_gate,
            "plan": {},
            "plan_write": {},
            "proof": {},
            "proof_write": {},
            "runtime_may_continue": False,
            "correct_path": adaptive_gate.get("correct_path", []),
        }

    plan = build_doctrine_invocation_plan(action_context)
    plan_write = governance.validate_and_write_ceo_doctrine_invocation_plan(
        plan,
        cieu_db=cieu_db,
        session_id=session_id,
        seal_session=False,
    )
    if plan_write["governance_decision"]["decision"] != "ALLOW":
        return {
            "doctrine_gate_passed": False,
            "blocked_at": "plan",
            "plan": plan,
            "plan_write": plan_write,
            "proof": {},
            "proof_write": {},
            "runtime_may_continue": False,
            "adaptive_gate": adaptive_gate,
        }

    proof = build_doctrine_invocation_proof(action_context)
    proof_write = governance.validate_and_write_ceo_doctrine_invocation_proof(
        proof,
        cieu_db=cieu_db,
        session_id=session_id,
        seal_session=seal_session,
    )
    passed = proof_write["governance_decision"]["decision"] == "ALLOW"
    return {
        "doctrine_gate_passed": passed,
        "blocked_at": "" if passed else "proof",
        "plan": plan,
        "plan_write": plan_write,
        "proof": proof,
        "proof_write": proof_write,
        "runtime_may_continue": passed,
        "adaptive_gate": adaptive_gate,
        "adaptive_metadata": adaptive_metadata_from_gate(adaptive_gate),
        "doctrine_metadata": {
            **adaptive_metadata_from_gate(adaptive_gate),
            **doctrine_metadata_from_gate(plan_write, proof_write, proof),
        },
    }


def doctrine_metadata_from_gate(
    plan_write: Mapping[str, Any],
    proof_write: Mapping[str, Any],
    proof: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "doctrine_registry_id": proof.get("registry_id", ""),
        "doctrine_invocation_plan_id": proof.get("doctrine_invocation_plan_id", ""),
        "doctrine_invocation_proof_id": proof.get("doctrine_invocation_proof_id", ""),
        "required_doctrines_satisfied": proof_write.get("governance_decision", {}).get("decision") == "ALLOW",
        "YstarGov_doctrine_decision": proof_write.get("governance_decision", {}).get("decision", ""),
        "external_observation_required": proof.get("action_context", {}).get("external_observation_required", False)
        if isinstance(proof.get("action_context"), Mapping)
        else False,
        "owner_decision_required": proof.get("action_context", {}).get("owner_decision_required", False)
        if isinstance(proof.get("action_context"), Mapping)
        else False,
        "no_send_invariant": True,
    }


def build_e89_doctrine_action_context() -> dict[str, Any]:
    return build_default_action_context(
        action_id="e89_ceo_intelligence_runtime_session",
        action_type="provider_tool_action",
        mission_type="intelligence_runtime",
        route_type="provider_tool_dry_run",
        provider_tool_boundary=True,
        market_strategy_required=False,
        external_observation_required=False,
        generation_mode="deterministic_fixture",
        test_mode=True,
    )


def build_e90_doctrine_action_context(*, test_mode: bool = True) -> dict[str, Any]:
    return build_default_action_context(
        action_id="e90_market_grounded_strategy_session",
        action_type="market_strategy",
        mission_type="market_strategy",
        route_type="external_feedback_candidate",
        provider_tool_boundary=True,
        market_strategy_required=True,
        external_observation_required=True,
        owner_decision_required=False,
        generation_mode="runtime_generated_structured_output",
        test_mode=test_mode,
        live_external_observation_required=not test_mode,
    )


__all__ = [
    "build_e89_doctrine_action_context",
    "build_e90_doctrine_action_context",
    "doctrine_metadata_from_gate",
    "enforce_doctrine_before_ceo_runtime",
    "load_ystar_governance",
]
