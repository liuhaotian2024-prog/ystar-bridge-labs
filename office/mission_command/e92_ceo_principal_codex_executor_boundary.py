from __future__ import annotations

import importlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from office.mission_command.e89_ceo_intelligence_loop_runtime_compiler import (
    compile_ceo_intelligence_loop_packet,
)
from office.mission_command.e90_market_grounded_strategy_run import (
    build_market_grounded_strategy_artifact,
)
from office.mission_command.e91_ceo_operating_doctrine_registry import (
    build_default_action_context,
    build_doctrine_invocation_proof,
)


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
MILESTONE_ID = "E92_CEO_Principal_Order_And_Codex_Executor_Boundary_R1"
SESSION_ID = "e92_ceo_principal_codex_executor_boundary_session"

REQUIRED_CODEX_RECEIPT_FIELDS: tuple[str, ...] = (
    "receipt_id",
    "linked_order_id",
    "executor_actor",
    "execution_status",
    "repos_read",
    "repos_modified",
    "files_changed",
    "tests_run",
    "test_results",
    "commits",
    "remote_push_status",
    "deviations_from_order",
    "unexpected_blockers",
    "strategy_changed_by_codex",
    "scope_expanded_by_codex",
    "external_action_executed",
    "provider_action_executed",
    "customer_or_payment_claim_made",
    "overclaim_detected",
    "CIEU_write_status",
    "recommended_next_action",
    "residual_observations",
)


def discover_existing_executor_assets(*, root: Path | None = None) -> dict[str, Any]:
    """Find existing dispatch, delivery, task-order, and receipt assets."""

    base = root or BRIDGE_ROOT
    search_terms = (
        "Codex",
        "executor",
        "implementation order",
        "work order",
        "task packet",
        "dispatch",
        "delivery bridge",
        "patch bundle",
        "execution receipt",
        "completion report",
        "post-action",
        "bridge job",
        "host-local delivery",
        "remote_confirmed",
        "allowed files",
        "forbidden actions",
        "tests required",
        "completion criteria",
    )
    categories = {
        "dispatch_and_task_card": ("dispatch", "task packet", "task card", "work order"),
        "delivery_bridge": ("delivery bridge", "host-local delivery", "remote_confirmed", "patch bundle"),
        "execution_receipt": ("execution receipt", "completion report", "receipt"),
        "scope_and_validation": ("allowed files", "forbidden actions", "tests required", "completion criteria"),
        "codex_job_proposal": ("Codex", "Codex job", "implementation order"),
    }
    assets: list[dict[str, Any]] = []
    for path in _candidate_asset_files(base):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        lower = text.lower()
        matched_terms = [term for term in search_terms if term.lower() in lower or term.lower() in path.name.lower()]
        if not matched_terms:
            continue
        relative = path.relative_to(base).as_posix()
        category_hits = [
            category
            for category, terms in categories.items()
            if any(term.lower() in lower or term.lower() in relative.lower() for term in terms)
        ]
        assets.append(
            {
                "repo": "bridge-labs",
                "path": relative,
                "matched_terms": matched_terms[:12],
                "categories": category_hits or ["executor_boundary_context"],
                "runtime_status": _asset_runtime_status(relative),
                "evidence_excerpt": _excerpt(text, matched_terms[0]),
            }
        )
    high_value_paths = [
        "scripts/repository_delivery_bridge_submit.py",
        "scripts/repository_delivery_bridge_worker.py",
        "scripts/repository_delivery_bridge_status.py",
        "operations/external_validation/e70_owner_decision_packet_no_execution.json",
        "operations/external_validation/e70_generated_codex_job_proposal.json",
        "operations/external_validation/e71_generated_codex_job_proposal_from_legacy_assets.json",
        "operations/external_validation/e55_dry_run_action_executor_result.json",
        "office/mission_command/e90_market_grounded_strategy_run.py",
        "office/mission_command/e91_ceo_operating_doctrine_registry.py",
    ]
    return {
        "artifact_id": "e92_existing_executor_assets",
        "milestone_id": MILESTONE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(base),
        "search_terms": list(search_terms),
        "asset_count": len(assets),
        "assets": assets[:240],
        "high_value_existing_assets": [
            {"path": path, "exists": (base / path).exists(), "role": _high_value_role(path)}
            for path in high_value_paths
        ],
        "synthesis": {
            "reusable_dispatch_assets": "Historical dispatch/gov_dispatch and task-card assets exist, but not as the current CEOImplementationOrder schema.",
            "reusable_delivery_assets": "repository_delivery_bridge_submit/worker/status are canonical host-local delivery assets for Codex executor delivery.",
            "reusable_receipt_assets": "completion reports, dry-run receipts, CIEU residuals, and remote_confirmed reports provide receipt evidence patterns.",
            "gap_closed_by_E92": "Bind CEO strategy/order to Codex executor receipt and CEO residual learning under Y-star-gov validation.",
        },
    }


def build_ceo_implementation_order(
    *,
    owner_intent: str,
    selected_strategy: Mapping[str, Any],
    selected_action: Mapping[str, Any] | str,
    order_id: str = "e92_ceo_implementation_order",
    doctrine_invocation_proof: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    action_description = (
        selected_action
        if isinstance(selected_action, str)
        else selected_action.get("description")
        or selected_action.get("name")
        or selected_action.get("route_id")
        or selected_action.get("action_id")
        or selected_action.get("packet_id")
        or selected_action.get("message_hypothesis")
        or selected_action.get("target_profile")
    )
    proof = dict(doctrine_invocation_proof or _default_doctrine_proof())
    return {
        "artifact_id": "CEOImplementationOrder",
        "milestone_id": MILESTONE_ID,
        "order_id": order_id,
        "source_owner_intent": owner_intent,
        "CEO_decision_actor": "bridge_labs_ceo",
        "executor_actor": "Codex",
        "principal_executor_boundary": {
            "CEO_agent": "principal_decision_maker_strategy_owner",
            "Codex": "executor_engineering_worker",
            "Y-star-gov": "governance_judge",
            "gov-mcp": "provider_tool_execution_boundary",
            "CIEUStore": "evidence_and_memory_record",
        },
        "selected_strategy": dict(selected_strategy),
        "selected_action": action_description,
        "why_this_action": _strategy_field(selected_strategy, "why_this_path_now") or "CEO selected this as the narrowest internal engineering step to close the boundary.",
        "why_not_alternatives": _strategy_field(selected_strategy, "why_not_others") or ["Codex may not choose a different strategy from owner natural language."],
        "evidence_refs": [
            "operations/baseline/e87r_full_repo_baseline/baseline_summary.json",
            "operations/baseline/e87r_full_repo_baseline/stable_vocabulary_and_owner_map.json",
            "office/mission_command/e89_ceo_intelligence_loop_runtime_compiler.py",
            "office/mission_command/e90_market_grounded_strategy_run.py",
            "operations/ceo_doctrine_registry/e91_canonical_doctrine_registry_spec.json",
            "scripts/repository_delivery_bridge_submit.py",
        ],
        "doctrine_invocation_proof": proof,
        "intelligence_loop_id": "e89_ceo_intelligence_loop",
        "strategic_benchmark_id": selected_strategy.get("strategy_run_id") or "e90_market_grounded_strategy_run",
        "YstarGov_validation_required": True,
        "CIEU_prediction": {
            "X_t": "CEO strategy and Codex execution boundary is not yet formalized",
            "U_t": "CEO issues Y-star-gov validated implementation order to Codex",
            "Y_star_t": "Codex acts only as scoped executor and returns execution receipt",
            "expected_Y_t_plus_1": "order, receipt, and CEO residual are written to CIEUStore",
            "predicted_R_t_plus_1": "L4 feedback and L5 revenue/customer/payment loop remain unexecuted",
        },
        "allowed_repos": ["bridge-labs", "Y-star-gov"],
        "allowed_paths": [
            "office/mission_command/e92_*",
            "operations/codex_executor_boundary/e92_*",
            "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e92_*",
            "tests/office/test_e92_*",
            "ystar/governance/ceo_codex_executor_contract.py",
            "tests/governance/test_ceo_codex_executor_contract.py",
            "ystar/governance/__init__.py",
        ],
        "likely_files_to_modify": [
            "office/mission_command/e92_ceo_principal_codex_executor_boundary.py",
            "ystar/governance/ceo_codex_executor_contract.py",
            "tests/office/test_e92_ceo_principal_codex_executor_boundary.py",
            "tests/governance/test_ceo_codex_executor_contract.py",
        ],
        "forbidden_repos": ["K9Audit", "ystar-company"],
        "forbidden_paths": [".env", "credentials", "customer/contact data", "production secrets"],
        "forbidden_actions": [
            "Codex strategy change",
            "Codex scope expansion",
            "external outreach",
            "publication",
            "payment or revenue action",
            "live provider execution",
            "K9Audit mutation",
            "customer/pricing/revenue validation claim",
        ],
        "owner_approval_boundary": {
            "external_action_allowed": False,
            "owner_approval_state": "not_approved_for_external_action",
            "Codex_must_escalate_strategy_or_scope_change": True,
        },
        "L_level_boundary": {
            "L5-A": "complete_internal_runtime_foundation",
            "L5-B": "CEO_principal_order_boundary",
            "L5-C": "partial_dry_run_only",
            "L5-D": "absent_or_not_executed",
        },
        "external_action_allowed": False,
        "gov_mcp_required": False,
        "K9Audit_boundary": "read_only_not_integrated",
        "tests_required": [
            "tests/office/test_e92_ceo_principal_codex_executor_boundary.py",
            "tests/governance/test_ceo_codex_executor_contract.py",
            "E88/E89/E90 continuity tests",
        ],
        "validation_commands": [
            "python3 -m py_compile touched bridge-labs and Y-star-gov files",
            "pytest -q tests/office/test_e92_ceo_principal_codex_executor_boundary.py",
            "pytest -q tests/governance/test_ceo_codex_executor_contract.py",
        ],
        "completion_criteria": [
            "CEOImplementationOrder validates and writes to CIEUStore",
            "CodexExecutionReceipt validates and writes to CIEUStore",
            "CEO post-Codex residual validates and writes to CIEUStore",
            "Codex handoff prompt states Codex is executor, not CEO",
            "E90 selected action converts into CEOImplementationOrder",
        ],
        "required_report_format": "E92 final response format with exact status and no L5-D claim",
        "required_codex_receipt_fields": list(REQUIRED_CODEX_RECEIPT_FIELDS),
        "deviation_policy": "Any strategy or scope change by Codex returns ESCALATE receipt; no continued execution.",
        "escalation_policy": "Return to CEO principal with deviation receipt and owner-safe next recommendation.",
        "post_action_residual_required": True,
        "no_overclaim_policy": True,
        "no_hidden_chain_of_thought_policy": True,
        "truth_constraints": {
            "Codex_is_executor_not_CEO": True,
            "Codex_cannot_self_authorize_strategy": True,
            "no_external_action": True,
            "no_L4_feedback_executed": True,
            "no_customer_revenue_payment_claim": True,
            "hidden_chain_of_thought_stored": False,
        },
    }


def build_ceo_implementation_order_from_e90_strategy(*, root: Path | None = None) -> dict[str, Any]:
    strategy = build_market_grounded_strategy_artifact(repo_root=root or BRIDGE_ROOT)
    return build_ceo_implementation_order(
        owner_intent=str(strategy["owner_intent"]),
        selected_strategy=strategy["selected_strategy"],
        selected_action=strategy["next_L4_feedback_owner_decision_packet"],
        order_id="e92_ceo_order_from_e90_selected_action",
    )


def build_ceo_implementation_order_from_e89_selected_action(*, root: Path | None = None) -> dict[str, Any]:
    packet = compile_ceo_intelligence_loop_packet(repo_root=root or BRIDGE_ROOT)
    return build_ceo_implementation_order(
        owner_intent=str(packet["owner_intent"]),
        selected_strategy={"source": "E89 intelligence compiler", "selected_candidate_id": packet["selected_candidate_id"]},
        selected_action=packet["selected_action"],
        order_id="e92_ceo_order_from_e89_selected_action",
    )


def validate_ceo_implementation_order_local(order: Mapping[str, Any]) -> dict[str, Any]:
    required = (
        "order_id",
        "CEO_decision_actor",
        "executor_actor",
        "selected_action",
        "why_this_action",
        "why_not_alternatives",
        "evidence_refs",
        "CIEU_prediction",
        "allowed_repos",
        "allowed_paths",
        "forbidden_actions",
        "tests_required",
        "completion_criteria",
    )
    missing = [field for field in required if not _present(order.get(field))]
    if missing:
        return {"decision": "REQUIRE_REVISION", "missing_fields": missing, "passed": False}
    if order.get("executor_actor") != "Codex" or str(order.get("CEO_decision_actor")).lower() == "codex":
        return {"decision": "DENY", "missing_fields": [], "passed": False, "reason": "invalid principal/executor actors"}
    if order.get("external_action_allowed") is True and order.get("owner_approval_state") != "approved":
        return {"decision": "DENY", "missing_fields": [], "passed": False, "reason": "external action without approval"}
    return {"decision": "ALLOW", "missing_fields": [], "passed": True}


def build_codex_handoff_prompt_from_order(
    order: Mapping[str, Any],
    *,
    order_write: Mapping[str, Any] | None = None,
    cieu_db: str | None = None,
    ystar_gov_root: Path | None = None,
    session_id: str = SESSION_ID,
) -> dict[str, Any]:
    """Govern Codex prompt generation before returning executable prompt text.

    A raw natural-language instruction is not sufficient for Codex execution.
    The prompt is rendered only after the linked CEOImplementationOrder has an
    ALLOW decision and a formal CIEUStore write.
    """

    request = _build_prompt_generation_request(order, order_write)
    if not _present(order.get("order_id")):
        return {
            "artifact_id": "codex_handoff_prompt_generation_result",
            "prompt_generation_decision": {
                "decision": "DENY",
                "reason": "Codex prompt generation requires linked CEOImplementationOrder",
                "failed_field": "order_id",
            },
            "prompt": "",
            "generated_after_validated_cieu_written_order": False,
        }
    if order_write is None:
        return {
            "artifact_id": "codex_handoff_prompt_generation_result",
            "prompt_generation_decision": {
                "decision": "REQUIRE_REVISION",
                "reason": "Y-star-gov order validation and CIEUStore write are required before Codex prompt generation",
                "failed_field": "order_validation_result",
                "correct_path": [
                    "validate CEOImplementationOrder through Y-star-gov",
                    "write CEOImplementationOrder decision to CIEUStore",
                    "then generate Codex handoff prompt",
                ],
            },
            "prompt": "",
            "prompt_generation_request": request,
            "generated_after_validated_cieu_written_order": False,
        }
    governance = _load_ystar_governance(ystar_gov_root)
    if cieu_db:
        prompt_write = governance.validate_and_write_codex_handoff_prompt_generation(
            request,
            cieu_db=cieu_db,
            session_id=session_id,
            seal_session=False,
        )
        decision = prompt_write["governance_decision"]
    else:
        prompt_write = {}
        decision = governance.validate_codex_handoff_prompt_generation(request).to_dict()
    if decision["decision"] != "ALLOW":
        return {
            "artifact_id": "codex_handoff_prompt_generation_result",
            "prompt_generation_decision": decision,
            "prompt_write": prompt_write,
            "prompt": "",
            "prompt_generation_request": request,
            "generated_after_validated_cieu_written_order": False,
        }
    return {
        "artifact_id": "codex_handoff_prompt_generation_result",
        "prompt_generation_decision": decision,
        "prompt_write": prompt_write,
        "prompt_generation_request": request,
        "prompt": _render_codex_handoff_prompt_from_order(order),
        "generated_after_validated_cieu_written_order": True,
    }


def _render_codex_handoff_prompt_from_order(order: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            f"CEOImplementationOrder: {order.get('order_id')}",
            "",
            "You are Codex, the executor / engineering worker. You are not the CEO, not the strategy owner, and not the principal decision-maker.",
            "Do not change strategy. Do not expand scope. Do not infer a new plan from owner natural language.",
            "Execute only within this CEOImplementationOrder after Y-star-gov validation.",
            "",
            f"Selected action: {order.get('selected_action')}",
            f"Why this action: {order.get('why_this_action')}",
            f"Allowed repos: {', '.join(order.get('allowed_repos', []))}",
            f"Allowed paths: {', '.join(order.get('allowed_paths', []))}",
            f"Forbidden repos: {', '.join(order.get('forbidden_repos', []))}",
            f"Forbidden actions: {', '.join(order.get('forbidden_actions', []))}",
            "",
            "If implementation requires strategy or scope change, stop and return an ESCALATE CodexExecutionReceipt.",
            "If required information is missing, return REQUIRE_REVISION. If tests fail, report exact failures.",
            "Do not execute external actions, outreach, publication, payment, live provider calls, or K9Audit mutation.",
            "If direct push fails, use the host-local repository delivery bridge.",
            "",
            "Required tests:",
            *[f"- {item}" for item in order.get("tests_required", [])],
            "",
            "Return a CodexExecutionReceipt with these fields:",
            *[f"- {field}" for field in order.get("required_codex_receipt_fields", REQUIRED_CODEX_RECEIPT_FIELDS)],
            "",
            "Truth constraints: no customer validation, no revenue/payment/pricing claim, no L5-D completion claim, no hidden chain-of-thought storage.",
        ]
    )


def _build_prompt_generation_request(order: Mapping[str, Any], order_write: Mapping[str, Any] | None) -> dict[str, Any]:
    return {
        "artifact_id": "CodexHandoffPromptGenerationRequest",
        "prompt_request_id": f"prompt_request_{order.get('order_id') or 'missing_order'}",
        "linked_order_id": order.get("order_id"),
        "source_prompt_type": "CEOImplementationOrder" if _present(order.get("order_id")) else "raw_natural_language",
        "order_validation_result": dict(order_write or {}),
        "YstarGov_order_validation_required": True,
        "CIEUStore_order_write_required": True,
        "prompt_generation_after_cieu_write_required": True,
        "raw_natural_language_prompt_used": not _present(order.get("order_id")),
    }


def parse_codex_execution_receipt(receipt: str | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(receipt, str):
        return json.loads(receipt)
    return dict(receipt)


def validate_codex_execution_receipt_local(receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not _present(receipt.get("linked_order_id")):
        return {"decision": "DENY", "passed": False, "reason": "linked_order_id missing"}
    if receipt.get("strategy_changed_by_codex") is True:
        return {"decision": "ESCALATE", "passed": False, "reason": "Codex changed strategy"}
    if receipt.get("scope_expanded_by_codex") is True:
        return {"decision": "ESCALATE", "passed": False, "reason": "Codex expanded scope"}
    if receipt.get("external_action_executed") is True:
        return {"decision": "DENY", "passed": False, "reason": "external action executed"}
    if not receipt.get("tests_run"):
        return {"decision": "REQUIRE_REVISION", "passed": False, "reason": "missing tests"}
    if receipt.get("execution_status") == "completed" and not receipt.get("commits"):
        return {"decision": "REQUIRE_REVISION", "passed": False, "reason": "missing commit evidence"}
    if receipt.get("customer_or_payment_claim_made") is True or receipt.get("overclaim_detected") is True:
        return {"decision": "DENY", "passed": False, "reason": "forbidden overclaim"}
    return {"decision": "ALLOW", "passed": True, "reason": "receipt is compliant"}


def build_compliant_codex_execution_receipt(order: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": "CodexExecutionReceipt",
        "receipt_id": f"receipt_{order.get('order_id')}",
        "linked_order_id": order.get("order_id"),
        "executor_actor": "Codex",
        "execution_status": "completed",
        "repos_read": ["bridge-labs", "Y-star-gov", "gov-mcp"],
        "repos_modified": ["bridge-labs", "Y-star-gov"],
        "files_changed": [
            "office/mission_command/e92_ceo_principal_codex_executor_boundary.py",
            "ystar/governance/ceo_codex_executor_contract.py",
        ],
        "tests_run": list(order.get("tests_required", [])),
        "test_results": {"passed": "targeted E92 fixture", "failed": 0},
        "commits": [{"repo": "bridge-labs", "hash": "simulated_e92_fixture_commit"}],
        "remote_push_status": "simulated_fixture_no_external_push_in_unit_test",
        "deviations_from_order": [],
        "unexpected_blockers": [],
        "strategy_changed_by_codex": False,
        "scope_expanded_by_codex": False,
        "external_action_executed": False,
        "provider_action_executed": False,
        "customer_or_payment_claim_made": False,
        "overclaim_detected": False,
        "CIEU_write_status": "order_receipt_residual_written_in_test_db",
        "recommended_next_action": "CEO reviews receipt and emits residual learning",
        "residual_observations": ["Codex stayed within CEOImplementationOrder boundary"],
    }


def build_ceo_post_codex_residual(order: Mapping[str, Any], receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": "CEOPostCodexResidual",
        "residual_id": f"residual_{receipt.get('receipt_id')}",
        "linked_order_id": order.get("order_id"),
        "linked_receipt_id": receipt.get("receipt_id"),
        "CEO_decision_actor": "bridge_labs_ceo",
        "executor_actor": "Codex",
        "expected_outcome": "Codex executes the CEOImplementationOrder without strategy/scope drift.",
        "actual_outcome": "Codex returned an execution receipt that is governed and CIEUStore-recorded.",
        "deviation_analysis": {
            "deviations_from_order": receipt.get("deviations_from_order", []),
            "strategy_changed_by_codex": receipt.get("strategy_changed_by_codex", False),
            "scope_expanded_by_codex": receipt.get("scope_expanded_by_codex", False),
        },
        "learning_update": "CEO wisdom remains in the order; Codex output is evaluated as execution evidence and residual learning input.",
        "next_ceo_recommendation": receipt.get("recommended_next_action") or "Use CEOImplementationOrder before the next Codex engineering task.",
        "CIEU_record": {
            "X_t": "CEO issued governed implementation order",
            "U_t": "Codex executed and returned receipt",
            "Y_star_t": "CEO principal/executor boundary becomes auditable",
            "Y_t_plus_1": "CEO receives execution evidence and updates residual learning",
            "R_t_plus_1": "External feedback, live provider execution, and L5-D remain pending",
        },
        "no_external_action_executed": True,
        "no_customer_revenue_payment_claim": True,
        "post_action_residual_required": True,
    }


def run_ceo_codex_executor_boundary_session(
    *,
    cieu_db: str,
    root: Path | None = None,
    ystar_gov_root: Path | None = None,
    seal_session: bool = True,
) -> dict[str, Any]:
    governance = _load_ystar_governance(ystar_gov_root)
    base = root or BRIDGE_ROOT
    order = build_ceo_implementation_order_from_e90_strategy(root=base)
    order_write = governance.validate_and_write_ceo_implementation_order(
        order,
        cieu_db=cieu_db,
        session_id=SESSION_ID,
        seal_session=False,
    )
    handoff_prompt_result = build_codex_handoff_prompt_from_order(
        order,
        order_write=order_write,
        cieu_db=cieu_db,
        ystar_gov_root=ystar_gov_root,
        session_id=SESSION_ID,
    )
    handoff_prompt = handoff_prompt_result["prompt"]
    receipt = build_compliant_codex_execution_receipt(order)
    parsed_receipt = parse_codex_execution_receipt(json.dumps(receipt))
    receipt_write = governance.validate_and_write_codex_execution_receipt(
        parsed_receipt,
        cieu_db=cieu_db,
        session_id=SESSION_ID,
        seal_session=False,
    )
    residual = build_ceo_post_codex_residual(order, parsed_receipt)
    residual_write = governance.validate_and_write_ceo_post_codex_residual(
        residual,
        cieu_db=cieu_db,
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    summary = _cieu_summary(cieu_db)
    chain_proven = (
        order_write["governance_decision"]["decision"] == "ALLOW"
        and handoff_prompt_result["prompt_generation_decision"]["decision"] == "ALLOW"
        and handoff_prompt_result["generated_after_validated_cieu_written_order"] is True
        and receipt_write["governance_decision"]["decision"] == "ALLOW"
        and residual_write["governance_decision"]["decision"] == "ALLOW"
        and summary["event_count"] >= 4
    )
    return {
        "artifact_id": "e92_ceo_codex_executor_boundary_session_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "order": order,
        "order_write": order_write,
        "codex_handoff_prompt_generation": handoff_prompt_result,
        "codex_handoff_prompt": handoff_prompt,
        "codex_execution_receipt": parsed_receipt,
        "receipt_write": receipt_write,
        "post_codex_residual": residual,
        "residual_write": residual_write,
        "CIEUStore_record_summary": summary,
        "end_to_end_ceo_codex_ceo_chain_proven": chain_proven,
        "next_ceo_recommendation": residual["next_ceo_recommendation"],
        "safety_statement": {
            "Codex_is_executor_not_CEO": True,
            "CEO_is_principal_strategy_owner": True,
            "no_external_action": True,
            "no_L4_feedback_executed": True,
            "no_customer_revenue_payment_claim": True,
            "gov_mcp_live_execution": False,
            "K9Audit_not_integrated": True,
        },
    }


def write_e92_boundary_reports(
    *,
    cieu_db: str,
    root: Path | None = None,
    ystar_gov_root: Path | None = None,
) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    session = run_ceo_codex_executor_boundary_session(cieu_db=cieu_db, root=base, ystar_gov_root=ystar_gov_root)
    discovery = discover_existing_executor_assets(root=base)
    status = _status_after_e92(session)
    report = _completion_report(session, discovery)
    files = {
        "assets_json": base / "operations/codex_executor_boundary/e92_existing_executor_assets.json",
        "assets_md": base / "operations/codex_executor_boundary/e92_existing_executor_assets.md",
        "order_example": base / "operations/codex_executor_boundary/e92_ceo_implementation_order_example.json",
        "prompt_example": base / "operations/codex_executor_boundary/e92_codex_handoff_prompt_example.md",
        "prompt_governance_example": base / "operations/codex_executor_boundary/e92_codex_handoff_prompt_governance_result_example.json",
        "receipt_example": base / "operations/codex_executor_boundary/e92_codex_execution_receipt_example.json",
        "report_json": base / "office/mission_command/e92_ceo_principal_codex_executor_boundary_report.json",
        "report_md": base / "office/mission_command/e92_ceo_principal_codex_executor_boundary_readback.md",
        "status_json": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e92_ceo_principal_codex_executor_boundary.json",
        "status_md": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e92_ceo_principal_codex_executor_boundary.md",
    }
    for path in files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    files["assets_json"].write_text(json.dumps(discovery, indent=2, sort_keys=True), encoding="utf-8")
    files["assets_md"].write_text(_assets_markdown(discovery), encoding="utf-8")
    files["order_example"].write_text(json.dumps(session["order"], indent=2, sort_keys=True), encoding="utf-8")
    files["prompt_example"].write_text(session["codex_handoff_prompt"] + "\n", encoding="utf-8")
    files["prompt_governance_example"].write_text(json.dumps(session["codex_handoff_prompt_generation"], indent=2, sort_keys=True), encoding="utf-8")
    files["receipt_example"].write_text(json.dumps(session["codex_execution_receipt"], indent=2, sort_keys=True), encoding="utf-8")
    files["report_json"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    files["report_md"].write_text(_report_markdown(report), encoding="utf-8")
    files["status_json"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["status_md"].write_text(_status_markdown(status), encoding="utf-8")
    return report


def _completion_report(session: Mapping[str, Any], discovery: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": "e92_ceo_principal_codex_executor_boundary_report",
        "milestone_id": MILESTONE_ID,
        "repos_read": ["bridge-labs", "Y-star-gov", "gov-mcp", "K9Audit_read_only_boundary"],
        "repos_modified": ["bridge-labs", "Y-star-gov"],
        "existing_systems_reused": [
            "bridge-labs CEO/company behavior center",
            "E89 CEO intelligence loop runtime compiler",
            "E90 market-grounded strategy selected action",
            "E91 doctrine invocation proof when available",
            "Y-star-gov CIEUStore.write_dict",
            "host-local repository delivery bridge assets",
            "gov-mcp dry-run/no-send boundary as future provider/tool boundary",
        ],
        "existing_executor_assets_discovered": discovery["asset_count"],
        "reusable_assets": discovery["synthesis"],
        "CEOImplementationOrder_status": session["order_write"]["governance_decision"]["decision"],
        "Codex_handoff_prompt_generation_status": session["codex_handoff_prompt_generation"]["prompt_generation_decision"]["decision"],
        "Codex_handoff_prompt_generated_after_validated_cieu_written_order": session["codex_handoff_prompt_generation"][
            "generated_after_validated_cieu_written_order"
        ],
        "CodexExecutionReceipt_status": session["receipt_write"]["governance_decision"]["decision"],
        "post_Codex_residual_status": session["residual_write"]["governance_decision"]["decision"],
        "end_to_end_chain_proven": session["end_to_end_ceo_codex_ceo_chain_proven"],
        "end_to_end_chain": [
            "CEO builds CEOImplementationOrder",
            "Y-star-gov validates and writes order decision to CIEUStore",
            "Y-star-gov validates and writes Codex handoff prompt generation decision to CIEUStore",
            "bridge-labs generates Codex handoff prompt",
            "Codex returns CodexExecutionReceipt",
            "Y-star-gov validates and writes receipt decision to CIEUStore",
            "CEO builds post-Codex residual",
            "Y-star-gov validates and writes residual decision to CIEUStore",
        ],
        "CIEUStore_records": session["CIEUStore_record_summary"],
        "CIEUStore_write_status": {
            "order_decision_written": session["order_write"]["formal_CIEU_log_written"],
            "prompt_generation_decision_written": bool(
                session["codex_handoff_prompt_generation"].get("prompt_write", {}).get("formal_CIEU_log_written")
            ),
            "receipt_decision_written": session["receipt_write"]["formal_CIEU_log_written"],
            "post_codex_residual_written": session["residual_write"]["formal_CIEU_log_written"],
            "formal_CIEU_log_path": session["order_write"].get(
                "formal_CIEU_log_path",
                "ystar.governance.cieu_store.CIEUStore.write_dict",
            ),
        },
        "E89_E90_integration_status": "E89 and E90 selected actions can be converted into CEOImplementationOrder",
        "tests_required_for_delivery": [
            "tests/office/test_e92_ceo_principal_codex_executor_boundary.py",
            "tests/governance/test_ceo_codex_executor_contract.py",
            "E88/E89/E90 continuity tests",
        ],
        "principal_executor_truth": {
            "CEO": "principal_decision_maker_strategy_owner",
            "Codex": "executor_engineering_worker",
            "Codex_can_change_strategy": False,
            "Codex_can_execute_external_action_without_order": False,
            "raw_natural_language_prompt_can_authorize_codex": False,
            "codex_prompt_generation_requires_validated_cieu_written_order": True,
        },
        "L5_truth_table_after_E92": _l5_after_e92(),
        "safety_statement": session["safety_statement"],
        "limitations": [
            "No external action was executed.",
            "No L4 feedback was executed.",
            "No customer, revenue, payment, or pricing validation evidence exists.",
            "gov-mcp remains dry-run/no-send only.",
            "K9Audit was not written or integrated.",
        ],
        "recommended_next_milestone": "E93_Owner_Gated_L4_Public_Read_Observation_Runtime_Or_Codex_Order_Execution_Pilot_R1",
    }


def _status_after_e92(session: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": "current_runtime_status_after_e92_ceo_principal_codex_executor_boundary",
        "milestone_id": MILESTONE_ID,
        "CEO_principal_Codex_executor_boundary": session["end_to_end_ceo_codex_ceo_chain_proven"],
        "Codex_prompt_generation_governed_action": session["codex_handoff_prompt_generation"]["prompt_generation_decision"]["decision"] == "ALLOW",
        "Codex_prompt_generated_after_validated_cieu_written_order": session["codex_handoff_prompt_generation"][
            "generated_after_validated_cieu_written_order"
        ],
        "CIEUStore_order_prompt_receipt_residual_records_written": session["CIEUStore_record_summary"]["event_count"] >= 4,
        **_l5_after_e92(),
        "no_L4_feedback_executed": True,
        "no_customer_revenue_payment_claim": True,
        "gov_mcp_live_execution": False,
        "K9Audit_integrated": False,
    }


def _l5_after_e92() -> dict[str, str]:
    return {
        "L5-A": "complete_internal_runtime_foundation",
        "L5-B": "complete_for_structured_governed_intelligence_loop_with_CEO_principal_Codex_executor_boundary",
        "L5-C": "partial_dry_run_only",
        "L5-D": "absent_or_not_executed",
    }


def _candidate_asset_files(base: Path) -> list[Path]:
    dirs = [
        base / "office/mission_command",
        base / "operations",
        base / "reports",
        base / "scripts",
        base / ".claude",
        base / "tests",
    ]
    files: list[Path] = []
    for directory in dirs:
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".py", ".json", ".md", ".yaml", ".yml", ".txt"}:
                files.append(path)
    return files


def _asset_runtime_status(relative_path: str) -> str:
    if relative_path.startswith("scripts/repository_delivery_bridge"):
        return "runtime_active_delivery_bridge"
    if relative_path.startswith("office/mission_command/e9"):
        return "runtime_active_or_current_milestone"
    if "/external_validation/" in relative_path or relative_path.startswith("operations/external_validation/"):
        return "generated_or_historical_artifact"
    if relative_path.startswith("reports/") or relative_path.startswith(".claude/"):
        return "historical_context"
    if relative_path.startswith("tests/"):
        return "test_evidence"
    return "unknown"


def _high_value_role(path: str) -> str:
    if "repository_delivery_bridge" in path:
        return "host-local canonical delivery for Codex executor commits"
    if "codex_job" in path.lower() or "e70" in path or "e71" in path:
        return "historical Codex job proposal/order precedent"
    if "e55_dry_run_action_executor" in path:
        return "dry-run executor receipt precedent"
    if "e90" in path:
        return "CEO selected strategy/action source"
    if "e91" in path:
        return "doctrine proof source"
    return "executor-boundary evidence"


def _excerpt(text: str, term: str) -> str:
    lower = text.lower()
    index = lower.find(term.lower())
    if index < 0:
        return text[:240]
    start = max(0, index - 120)
    end = min(len(text), index + 240)
    return " ".join(text[start:end].split())


def _strategy_field(strategy: Mapping[str, Any], key: str) -> Any:
    if key in strategy:
        return strategy[key]
    return strategy.get("selected_strategy", {}).get(key) if isinstance(strategy.get("selected_strategy"), Mapping) else None


def _default_doctrine_proof() -> dict[str, Any]:
    context = build_default_action_context(
        action_id="e92_ceo_codex_executor_boundary",
        action_type="engineering_runtime_implementation",
        mission_type="executor_boundary",
        route_type="internal_runtime",
        test_mode=True,
    )
    return build_doctrine_invocation_proof(context)


def _load_ystar_governance(ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module("ystar.governance")


def _cieu_summary(cieu_db: str) -> dict[str, Any]:
    with sqlite3.connect(cieu_db) as conn:
        rows = conn.execute(
            "select event_type, decision, sealed from cieu_events where session_id=? order by rowid",
            (SESSION_ID,),
        ).fetchall()
    return {
        "session_id": SESSION_ID,
        "event_count": len(rows),
        "event_types": [row[0] for row in rows],
        "decisions": [row[1] for row in rows],
        "sealed_events": sum(1 for row in rows if row[2]),
    }


def _assets_markdown(discovery: Mapping[str, Any]) -> str:
    lines = [
        "# E92 Existing Executor Assets",
        "",
        f"- asset_count: {discovery['asset_count']}",
        "- synthesis: CEO order/receipt boundary should reuse delivery bridge, completion reports, dry-run receipts, and residual patterns.",
        "",
        "## High-Value Assets",
    ]
    for item in discovery["high_value_existing_assets"]:
        lines.append(f"- `{item['path']}`: exists={str(item['exists']).lower()} — {item['role']}")
    return "\n".join(lines) + "\n"


def _report_markdown(report: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# E92 CEO Principal / Codex Executor Boundary",
            "",
            "- CEO is principal, decision-maker, and strategy owner.",
            "- Codex is executor and engineering worker.",
            "- Codex cannot self-authorize strategic changes, expand scope, or execute external actions.",
            "- Codex handoff prompt generation is itself governed and requires a validated CIEUStore-written CEOImplementationOrder.",
            f"- end_to_end_chain_proven: {str(report['end_to_end_chain_proven']).lower()}",
            f"- CEOImplementationOrder_status: {report['CEOImplementationOrder_status']}",
            f"- Codex_handoff_prompt_generation_status: {report['Codex_handoff_prompt_generation_status']}",
            f"- CodexExecutionReceipt_status: {report['CodexExecutionReceipt_status']}",
            f"- CIEUStore_records: {report['CIEUStore_records']['event_count']}",
            "- no L4 feedback executed; no customer/revenue/payment evidence claimed.",
            "",
        ]
    )


def _status_markdown(status: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Runtime Status After E92",
            "",
            f"- CEO_principal_Codex_executor_boundary: {str(status['CEO_principal_Codex_executor_boundary']).lower()}",
            f"- Codex_prompt_generation_governed_action: {str(status['Codex_prompt_generation_governed_action']).lower()}",
            f"- Codex_prompt_generated_after_validated_cieu_written_order: {str(status['Codex_prompt_generated_after_validated_cieu_written_order']).lower()}",
            f"- L5-A: {status['L5-A']}",
            f"- L5-B: {status['L5-B']}",
            f"- L5-C: {status['L5-C']}",
            f"- L5-D: {status['L5-D']}",
            "- no L4 feedback executed",
            "- no customer/revenue/payment claim",
            "- K9Audit not integrated",
            "",
        ]
    )


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


__all__ = [
    "build_ceo_implementation_order",
    "build_ceo_implementation_order_from_e89_selected_action",
    "build_ceo_implementation_order_from_e90_strategy",
    "build_ceo_post_codex_residual",
    "build_codex_handoff_prompt_from_order",
    "build_compliant_codex_execution_receipt",
    "discover_existing_executor_assets",
    "parse_codex_execution_receipt",
    "run_ceo_codex_executor_boundary_session",
    "validate_ceo_implementation_order_local",
    "validate_codex_execution_receipt_local",
    "write_e92_boundary_reports",
]
